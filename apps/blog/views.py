from django.utils import timezone
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from drf_spectacular.utils import extend_schema

from apps.blog.models import Post, SubPost, Like
from apps.blog.serializers import (
  PostSerializer, 
  SubPostSerializer, 
  SubPostWithIDSerializer, 
  LikeSerializer
)
from apps.blog.pagination import PostPagination
from apps.blog.docs.post_doc import (
  LIST_POSTS_DOCS,
  RETRIEVE_POST_DOCS,
  ADD_VIEW_DOCS,
  DELETE_POST_DOCS,
  CREATE_POST_DOCS,
  UPDATE_POST_DOCS,
  PARTIAL_UPDATE_POST_DOCS,
  POST_VIEW_SET_DOCS)
from apps.blog.docs.subpost_doc import (
  DELETE_SUBPOST_DOCS,
  UPDATE_SUBPOST_DOCS,
  CREATE_SUBPOST_DOCS,
  RETRIEVE_SUBPOST_DOCS,
  LIST_SUBPOSTS_DOCS,
  SUBPOST_VIEW_SET_DOCS
)
from apps.blog.docs.like_doc import (
  LIKE_VIEW_SET_DOCS,
  ADD_RO_REMOVE_LIKE
)

@extend_schema(**POST_VIEW_SET_DOCS)
class PostViewSet(ModelViewSet):
  http_method_names = ['get', 'post', 'put', 'patch', 'delete']
  queryset = Post.objects.all()
  serializer_class = PostSerializer

  # Добавить пагинацию если работает: 'list'
  def paginate_queryset(self, queryset):
    if self.action == 'list':
      self.pagination_class = PostPagination
      return super().paginate_queryset(queryset)
    self.pagination_class = None
    return None
  
  @extend_schema(**LIST_POSTS_DOCS)
  def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)

  @extend_schema(**RETRIEVE_POST_DOCS)
  def retrieve(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)
  
  @extend_schema(**CREATE_POST_DOCS)
  def create(self, request, *args, **kwargs):
    data = request.data.copy()

    # Массовое создание постов
    if isinstance(data, list):
      now = timezone.now()
      for item in data:
        item['created_at'] = now
        item['updated_at'] = now
      serializer = self.get_serializer(data=data, many=True)
      serializer.is_valid(raise_exception=True)
      created_objects = self.perform_bulk_create(serializer.validated_data)
      output_serializer = self.get_serializer(created_objects, many=True)
      return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    # Продолжаем работу если только 1 пост
    subposts_data = data.get('subposts', None)

    # Есть ли субпосты вместе с постом
    if subposts_data is not None:
      if not isinstance(subposts_data, list):
        raise ValidationError({"massages": "subposts ожидается type: list"})
      request.data.pop('subposts', None)
      post_serializer = self.get_serializer(data=data)
      subpost_serializer = SubPostSerializer(
        data=subposts_data, 
        many=True
      )

      post_serializer.is_valid(raise_exception=True)
      subpost_serializer.is_valid(raise_exception=True)
      
      # Найдет ошибку: сделает откат базы
      with transaction.atomic():
        post = post_serializer.save()
        now = timezone.now()
        for item in subpost_serializer.validated_data:
          item['post'] = post
        SubPostViewSet.perform_bulk_create(subpost_serializer.validated_data)

        headers = self.get_success_headers(post_serializer.data)
      return Response(post_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    return super().create(request, *args, **kwargs)
  
  @extend_schema(**UPDATE_POST_DOCS)
  def update(self, request, *args, **kwargs):
    user = request.user
    subposts_data = request.data.get('subposts', None)
    request.data.pop('subposts', None)

    partial = kwargs.pop('partial', False)
    instance = self.get_object()
    post_serializer = self.get_serializer(instance, data=request.data, partial=partial)
    post_serializer.is_valid(raise_exception=True)

    post_id = kwargs['pk']
    post_obj = get_object_or_404(Post, id=post_id)

    if post_obj.author != user:
      raise PermissionDenied(f'Доступ к посту {post_obj.id} ограничен')

    # Есть ли субпосты вместе с постом
    if subposts_data is not None:
      if not isinstance(subposts_data, list):
        raise ValidationError({"massages": "subposts ожидается type: list"})

      with transaction.atomic():
        subpost_serializer = SubPostWithIDSerializer(data=subposts_data, many=True, partial=True)
        subpost_serializer.is_valid(raise_exception=True)

        all_new_ids = set()
        create_data = []
        update_data = []
        update_ids = set()

        post = post_serializer.save()

        for item in subpost_serializer.validated_data:
          item['post'] = post
          if 'id' not in item:
            create_data.append(item)
          else:
            update_data.append(item)
            update_ids.add(item['id'])
            all_new_ids.add(item['id'])

        old_subposts = SubPost.objects.filter(post=post)
        old_ids = set(sub.id for sub in old_subposts)

        if all_new_ids - old_ids:
          raise PermissionDenied(f'Субпост(ы): (id){all_new_ids - old_ids} Не принадлежат посту: {post.id}.')

        # delete
        delete_ids = old_ids - update_ids
        if delete_ids:
          SubPost.objects.filter(id__in=delete_ids, post=post).delete()

        # update
        if update_data:
          objs = SubPost.objects.filter(id__in=update_ids, post=post)
          obj_map = {obj.id: obj for obj in objs}
          fields_to_update = set()

          for data in update_data:
            obj = obj_map.get(data['id'])
            if not obj:
              continue
            for field, value in data.items():
              if field != 'id':
                setattr(obj, field, value)
                fields_to_update.add(field)

          if fields_to_update:
            SubPost.objects.bulk_update(obj_map.values(), fields_to_update)

        # create
        SubPostViewSet.perform_bulk_create(create_data)

    self.perform_update(post_serializer)
    if getattr(instance, '_prefetched_objects_cache', None):
      instance._prefetched_objects_cache = {}

    return Response(post_serializer.data)
  

  @extend_schema(**PARTIAL_UPDATE_POST_DOCS)
  def partial_update(self, request, *args, **kwargs):
    kwargs['partial'] = True
    return self.update(request, *args, **kwargs)
  
  @extend_schema(**ADD_VIEW_DOCS)
  @action(detail=True, methods=['get'], url_path='view')
  def add_view(self, request, pk):
    updated = Post.objects.filter(pk=pk).update(views_count=F('views_count')+1)
    if updated == 0:
      raise NotFound(f"Пост с id={pk} не найден")
    return Response(status=status.HTTP_200_OK)
  
  @extend_schema(**DELETE_POST_DOCS)
  def destroy(self, request, *args, **kwargs):
    return super().destroy(request, *args, **kwargs)
  
  def perform_bulk_create(self, serializer_validated_data):
    return Post.objects.bulk_create([Post(**item) for item in serializer_validated_data])


@extend_schema(**SUBPOST_VIEW_SET_DOCS)
class SubPostViewSet(ModelViewSet):
  http_method_names = ['list', 'get', 'post', 'put', 'delete', 'retrieve']
  queryset = SubPost.objects.all()
  serializer_class = SubPostSerializer

  
  @extend_schema(**LIST_SUBPOSTS_DOCS)
  def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)

  
  @extend_schema(**RETRIEVE_SUBPOST_DOCS)
  def retrieve(self, request, *args, **kwargs):
    return super().retrieve(request, *args, **kwargs)


  @extend_schema(**CREATE_SUBPOST_DOCS)
  def create(self, request, *args, **kwargs):
    post_id = self.request.data.get('post')
    user = self.request.user
    
    post = get_object_or_404(Post, id=post_id)
    if post.author != user:
      raise PermissionDenied(f'Вы не владелец поста: {post}')
    
    return super().create(request, *args, **kwargs)
  
  @extend_schema(**DELETE_SUBPOST_DOCS)
  def destroy(self, request, *args, **kwargs):
    return super().destroy(request, *args, **kwargs)

  @extend_schema(**UPDATE_SUBPOST_DOCS)
  def update(self, request, *args, **kwargs):
    return super().update(request, *args, **kwargs)

  def perform_bulk_create(serializer_validated_data):
    return SubPost.objects.bulk_create([SubPost(**item) for item in serializer_validated_data])


@extend_schema(**LIKE_VIEW_SET_DOCS)
class LikeViewSet(ModelViewSet):
  queryset = Like.objects.all()
  serializer_class = LikeSerializer

  @extend_schema(**ADD_RO_REMOVE_LIKE)
  @action(detail=True, methods=['post'])
  def like(self, request, *args, **kwargs):
    user = request.user
    post_id = kwargs['pk']

    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(user=user, post=post).first()
    if like:
      like.delete()
      return Response({'message': 'Лайк убран'})

    serializer = self.get_serializer(data={
      'post': post.id,
      'user': user.id
    })
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    return Response({'message': 'Вы поставили лайк'}, status=status.HTTP_200_OK)
  
