# Пишу тесты так просто: чтобы на них не пришлось писать тесты

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from apps.blog.models import Post, SubPost, Like
from apps.blog.serializers import (
  PostSerializer, 
  SubPostSerializer, 
  SubPostWithIDSerializer,
  LikeSerializer
)


def format_dt(dt):
  """
  Берет дату из БД, переводит её в таймзону из настоек Джанго

  :param: Дата из БД(обычно UTC)
  :return: Строка, время таймзона из настроек
  """
  local_dt = timezone.localtime(dt, timezone.get_current_timezone())
  return local_dt.isoformat()

class PostSerializerTestCase(TestCase):
  def test_post(self):
    user = User.objects.create_user(
      username='test_user',
      password='Test_UseR_1_Test'
    )
    post_1 = Post.objects.create(
      title='Пост 1',
      body='Содержание',
      author=user
    )
    post_2 = Post.objects.create(
      title='Пост 2',
      body='Содержание',
      author=user
    )

    posts = [post_1, post_2]
    serializer = PostSerializer(posts, many=True)

    expected_data = [
      {
        'id': post_1.id,
        'title': 'Пост 1',
        'author_display': 'test_user',
        'body': 'Содержание',
        'create_at': format_dt(post_1.create_at),
        'update_at': format_dt(post_1.update_at),
        'views_count': 0
      },
      {
        'id': post_2.id,
        'title': 'Пост 2',
        'author_display': 'test_user',
        'body': 'Содержание',
        'create_at': format_dt(post_2.create_at),
        'update_at': format_dt(post_2.update_at),
        'views_count': 0
      }
    ]

    self.assertEqual(expected_data, serializer.data)


class SubPostSerializerTestCase(TestCase):
  def test_subpost(self):
    user = User.objects.create_user(
      username='test_user',
      password='Test_UseR_1_Test'
    )
    post_1 = Post.objects.create(
      title='Пост 1',
      body='Содержание',
      author=user
    )
    subpost_1 = SubPost.objects.create(
      title='СубПост 1',
      body='Содержание',
      post=post_1
    )
    subpost_2 = SubPost.objects.create(
      title='СубПост 2',
      body='Содержание',
      post=post_1
    )

    subposts = [subpost_1, subpost_2]
    serializer = SubPostSerializer(subposts, many=True)

    expected_data = [
      {
        'id': subpost_1.id,
        'title': 'СубПост 1',
        'post': post_1.id,
        'body': 'Содержание',
        'create_at': format_dt(subpost_1.create_at),
        'update_at': format_dt(subpost_1.update_at),
      },
      {
        'id': subpost_2.id,
        'title': 'СубПост 2',
        'post': post_1.id,
        'body': 'Содержание',
        'create_at': format_dt(subpost_2.create_at),
        'update_at': format_dt(subpost_2.update_at),
      }
    ]

    self.assertEqual(expected_data, serializer.data)

class SubPostWithIDSerializerTestCase(TestCase):
  def test_subpost(self):
    user = User.objects.create_user(
      username='test_user',
      password='Test_UseR_1_Test'
    )
    post_1 = Post.objects.create(
      title='Пост 1',
      body='Содержание',
      author=user
    )
    subpost_1 = SubPost.objects.create(
      id=1232,
      title='СубПост 1',
      body='Содержание',
      post=post_1
    )
    subpost_2 = SubPost.objects.create(
      title='СубПост 2',
      body='Содержание',
      post=post_1
    )

    subposts = [subpost_1, subpost_2]
    serializer = SubPostWithIDSerializer(subposts, many=True)

    expected_data = [
      {
        'id': subpost_1.id,
        'title': 'СубПост 1',
        'post': post_1.id,
        'body': 'Содержание',
        'create_at': format_dt(subpost_1.create_at),
        'update_at': format_dt(subpost_1.update_at),
      },
      {
        'id': subpost_2.id,
        'title': 'СубПост 2',
        'post': post_1.id,
        'body': 'Содержание',
        'create_at': format_dt(subpost_2.create_at),
        'update_at': format_dt(subpost_2.update_at),
      }
    ]

    self.assertEqual(expected_data, serializer.data)


class LikeSerializerTestCase(TestCase):
  def test_like(self):
    user = User.objects.create_user(
      username='test_user',
      password='Test_UseR_1_Test'
    )
    post_1 = Post.objects.create(
      title='Пост 1',
      body='Содержание',
      author=user
    )
    like = Like.objects.create(
      user = user,
      post = post_1
    )

    serializer = LikeSerializer(like)
    
    expected_data = {
        'post': post_1.id,
        'create_at': format_dt(like.create_at)
      }
    
    self.assertEqual(expected_data, serializer.data)

    