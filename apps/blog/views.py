from django.shortcuts import render
from django.utils import timezone
from django.db import transaction

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.blog.models import Post, SubPost, Like
from apps.blog.serializers import PostSerializer, SubPostSerializer
from apps.blog.pagination import PostPagination
from apps.blog.services import MassCreation

class PostViewSet(ModelViewSet):
  queryset = Post.objects.all()
  serializer_class = PostSerializer

  # Добавить пагинацию если работает: 'list'
  def paginate_queryset(self, queryset):
    if self.action == 'list':
      self.pagination_class = PostPagination
      return super().paginate_queryset(queryset)
    self.pagination_class = None
    return None
  
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
      self.perform_bulk_create(serializer.validated_data)
      return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Продолжаем работу если только 1 пост
    subposts_data = data.get('subposts', None)

    # Есть ли субпосты вместе с постом
    if subposts_data is not None:
      if not isinstance(subposts_data, list):
        raise ValidationError({"massages": "subposts ожидается type: list"})
      request.data.pop('subposts', None)
      post_serializer = self.get_serializer(data=data)
      subpost_serializer = SubPostSerializer(data=subposts_data, many=True)

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
  
  def update(self, request, *args, **kwargs):
    subposts_data = request.data.get('subposts', None)
    request.data.pop('subposts', None)

    partial = kwargs.pop('partial', False)
    instance = self.get_object()
    post_serializer = self.get_serializer(instance, data=request.data, partial=partial)
    post_serializer.is_valid(raise_exception=True)

    # Есть ли субпосты вместе с постом
    if subposts_data is not None:
      if not isinstance(subposts_data, list):
        raise ValidationError({"massages": "subposts ожидается type: list"})

      with transaction.atomic():
        subpost_serializer = SubPostSerializer(data=subposts_data, many=True, partial=True)
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
            print('getattr: ', getattr(item, 'id', None))
            print(item)
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
        print('old_ids: ', old_ids)
        print('update_ids: ', update_ids)
        print('delete_ids: ', delete_ids)
        print('update_data: ', update_data)
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
  
  
  def perform_bulk_create(self, serializer_validated_data):
    Post.objects.bulk_create([Post(**item) for item in serializer_validated_data])


class SubPostViewSet(ModelViewSet):
  queryset = SubPost.objects.all()
  serializer_class = SubPostSerializer

  def perform_bulk_create(serializer_validated_data):
    SubPost.objects.bulk_create([SubPost(**item) for item in serializer_validated_data])


# class LikeViewSet(ModelViewSet):
#   queryset = Like.objects.all()
#   seria