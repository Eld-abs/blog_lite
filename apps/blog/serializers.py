from rest_framework import serializers 
from apps.blog.models import Post, SubPost, Like


class PostSerializer(serializers.ModelSerializer):
  author = serializers.HiddenField(
    default=serializers.CurrentUserDefault(), 
    help_text="Автор поста (автоматически)"
  )
  author_display = serializers.ReadOnlyField(
    source='author.username', 
    help_text="Имя автора"
  )
  views_count = serializers.ReadOnlyField(
    help_text="Количество просмотров"
  )

  class Meta:
    model = Post
    fields = ['id', 'title', 'author', 'author_display', 'body', 'create_at', 'update_at', 'views_count']


class SubPostSerializer(serializers.ModelSerializer):
  id = serializers.ReadOnlyField(required=False)

  class Meta:
    model = SubPost
    fields = ['id', 'title', 'post', 'body', 'create_at', 'update_at']
    extra_kwargs = {
      'post': {'required': False}
    }


class SubPostWithIDSerializer(SubPostSerializer):
  id = serializers.IntegerField(required=False)


class LikeSerializer(serializers.ModelSerializer):
  user = serializers.HiddenField(default=serializers.CurrentUserDefault())
  post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

  class Meta:
    model = Like
    fields = ['user', 'post', 'create_at']