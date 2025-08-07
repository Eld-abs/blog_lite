from rest_framework import serializers 
from apps.blog.models import Post, SubPost


class PostSerializer(serializers.ModelSerializer):
  author = serializers.HiddenField(default=serializers.CurrentUserDefault())
  author_display = serializers.ReadOnlyField(source='author.username')

  class Meta:
    model = Post
    fields = ['id', 'title', 'author', 'author_display', 'body', 'create_at', 'update_at']


class SubPostSerializer(serializers.ModelSerializer):
  id = serializers.IntegerField(required=False)

  class Meta:
    model = SubPost
    fields = ['id', 'title', 'post', 'body', 'create_at', 'update_at']
    extra_kwargs = {
      'post': {'required': False}
    }