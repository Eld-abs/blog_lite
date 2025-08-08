from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from apps.blog.models import Post, SubPost

class SubPostApiTestCase(APITestCase):
  @classmethod
  def setUpTestData(cls):
    cls.user = User.objects.create_user(
      username='user', 
      password='Test_UseR_1_Test'
    )
    cls.user_1 = User.objects.create_user(
      username='user_1', 
      password='Test_UseR_1_Test'
    )
    cls.post_1 = Post.objects.create(
      title='Пост 1',
      body='Содержание',
      author=cls.user
    )
    cls.post_2 = Post.objects.create(
      title='Пост 2',
      body='Содержание',
      author=cls.user
    )
    cls.subpost_1 = SubPost.objects.create(
      post=cls.post_1,
      title='Подпост 1',
      body='Содержание'
    )

  def setUp(self):
    self.url_list = reverse('subpost-list')
    self.url_detail = reverse('subpost-detail', kwargs={'pk': self.subpost_1.id})

  # POST (201_CREATED)
  def test_create_subpost_success(self):
    self.client.force_login(self.user)
    data = {
      'post': self.post_1.id,
      'title': 'Подпост 1',
      'body': 'Содержание'
    }
    response = self.client.post(self.url_list, data)

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

  # POST (403_FORBIDDEN)
  def test_create_not_owner(self):
    self.client.force_login(self.user_1)
    data = {
      'post': self.post_2.id,
      'title': 'Подпост 1',
      'body': 'Содержание'
    }
    response = self.client.post(self.url_list, data)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

  # GET (200_OK)
  def test_get(self):
    self.client.force_login(self.user)
    response = self.client.get(self.url_list)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  # PUT (200_OK)
  def test_put(self):
    self.client.force_login(self.user)
    data = {
      'post': self.post_1.id,
      'title': 'Подпост обновлён',
      'body': 'Новый текст'
    }
    response = self.client.put(self.url_detail, data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  # DELETE (204_NO_CONTENT)
  def test_delete(self):
    self.client.force_login(self.user)
    response = self.client.delete(self.url_detail)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
