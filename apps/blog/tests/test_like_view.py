from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from apps.blog.models import Like, Post


class LikeTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    cls.user = User.objects.create_user(
      username='test_user', 
      password='Test_UseR_1_Test'
    )
    cls.post_1 = Post.objects.create(
      title='Пост 1', 
      body='Содержание',
      author=cls.user
    )

  # Авторизация
  def setUp(self):
    self.client.force_login(self.user)

  # POST поставить лайк (200_OK)
  def test_put_like(self):
    url = reverse('post-like', kwargs={'pk': self.post_1.id})
    response = self.client.post(url)

    self.assertEqual(status.HTTP_200_OK, response.status_code)


  # POST убрать лайк (200_OK)
  def test_remove_like(self):
    Like.objects.create(
      user=self.user,
      post=self.post_1
    )
    url = reverse('post-like', kwargs={'pk': self.post_1.id})
    response = self.client.post(url)

    self.assertEqual(status.HTTP_200_OK, response.status_code)

  # POST нет такого поста (404_NOT_FOUND)
  def test_put_like_not_found(self):
    url = reverse('post-like', kwargs={'pk': 99999})
    response = self.client.post(url)

    self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class ViewTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    cls.user = User.objects.create_user(
      username='test_user', 
      password='Test_UseR_1_Test'
    )
    cls.post_1 = Post.objects.create(
      title='Пост 1', 
      body='Содержание',
      author=cls.user
    )

  # Авторизация
  def setUp(self):
    self.client.force_login(self.user)

  # GET Добавить просмотр (200_OK)
  def test_view_add(self):
    url = reverse('post-add-view', args=[self.post_1.pk])
    response = self.client.get(url)
    self.post_1.refresh_from_db()
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(self.post_1.views_count, 1)