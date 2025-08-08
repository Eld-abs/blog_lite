from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.blog.models import Post, SubPost
from apps.blog.serializers import PostSerializer
from apps.blog.pagination import PostPagination


def format_dt(dt):
  """
  Берет дату из БД, переводит её в таймзону из настоек Джанго

  :param: Дата из БД(обычно UTC)
  :return: Строка, время таймзона из настроек
  """
  local_dt = timezone.localtime(dt, timezone.get_current_timezone())
  return local_dt.isoformat()

class PostApiTestCase(APITestCase):
  # Создание объектов в базу данных
  @classmethod
  def setUpTestData(cls):
    cls.user = User.objects.create_user(
      username='test_user', 
      password='Test_UseR_1_Test'
    )
    cls.user_1 = User.objects.create_user(
      username='test_user_1',
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
    cls.post_3 = Post.objects.create(
      title='Пост 3', 
      body='Содержание',
      author=cls.user
    )
    cls.post_4 = Post.objects.create(
      title='Пост 4', 
      body='Содержание',
      author=cls.user
    )
    cls.post_5 = Post.objects.create(
      title='Пост 5', 
      body='Содержание',
      author=cls.user_1
    )

  # Авторизация
  def setUp(self):
    self.client.force_login(self.user)

  # GET (200_OK)
  def test_get(self):
    url = reverse('post-list')
    response = self.client.get(url)

    page_size = PostPagination.page_size
    posts = Post.objects.all()[:page_size]
    serializer_data = PostSerializer(posts, many=True).data

    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(serializer_data, response.data['results'])
  
  # GET (200_OK) нет погинации
  def test_get_not_pagination_class(self):
    Post.objects.all().delete()

    post_1 = Post.objects.create(
      title='Пост 1', 
      body='Содержание',
      author=self.user
    )

    url = reverse('post-list')
    response = self.client.get(url)

    page_size = PostPagination.page_size
    posts = Post.objects.all()[:page_size]
    serializer_data = PostSerializer(posts, many=True).data

    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(serializer_data, response.data['results'])

  # POST Одиночное создание (201_CREATED)
  def test_create_post(self):
    url = reverse('post-list')
    data = {
      'title': 'Новый пост 1',
      'body': 'Содержание',
    }

    response = self.client.post(url, data, format='json')
    new_post = Post.objects.filter(id=response.data['id']).first()

    self.assertEqual(f"{data['title']} {self.user}", str(new_post))
    self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    self.assertEqual(data['title'], response.data['title'])
    self.assertEqual(data['body'], response.data['body'])
    self.assertIn('id', response.data)

  # POST (400_BAD_REQUEST)
  def test_create_post_negetiv_1(self):
    url = reverse('post-list')
    data = {'body': 'Содержаение'}

    response = self.client.post(url, data, format='json')

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn('title', response.data)

  # POST массовое создание (201_CREATED)
  def test_create_mass_post(self):
    url = reverse('post-list')
    data = [
      {
        'title': 'Новый пост 1',
        'body': 'Содержание',
      },
      {
        'title': 'Новый пост 2',
        'body': 'Содержание',
      },
    ]

    response = self.client.post(url, data, format='json')
    self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    self.assertIn('id', response.data[0])
    self.assertIn('id', response.data[1])
    self.assertIn('create_at', response.data[0])
    self.assertIn('create_at', response.data[1])
    self.assertIn('update_at', response.data[0])
    self.assertIn('update_at', response.data[1])
    self.assertIn('views_count', response.data[0])
    self.assertIn('views_count', response.data[1])
    self.assertEqual(data[0]['body'], response.data[0]['body'])
    self.assertEqual(data[1]['body'], response.data[1]['body'])
    self.assertEqual(data[0]['title'], response.data[0]['title'])
    self.assertEqual(data[1]['title'], response.data[1]['title'])

  # POST Создание поста вместе с субпостами (201_CREATED)
  def test_create_post_and_subposts(self):
    url = reverse('post-list')
    data = {
        'title': 'Новый пост 1',
        'body': 'Содержание',
        'subposts': [
          {
            'title': 'Субпост 1',
            'body': 'Содержание'
          },
          {
            'title': 'Субпост 2',
            'body': 'Содержание'
          },
        ]
      }
    
    response = self.client.post(url, data, format='json')

    all_subposts = SubPost.objects.all()
    title_set = {data['subposts'][0]['title'], data['subposts'][1]['title']}
    subposts_set = {str(all_subposts[0].title), str(all_subposts[1].title)}

    self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    self.assertIn('id', response.data)
    self.assertIn('create_at', response.data)
    self.assertIn('update_at', response.data)
    self.assertIn('views_count', response.data)
    self.assertEqual(data['body'], response.data['body'])
    self.assertEqual(data['title'], response.data['title'])
    self.assertEqual(title_set, subposts_set)

  # PUT полное обновление (200_OK)
  def test_update_complate(self):
    post_1 = Post.objects.all().first()
    url = reverse('post-detail', args=[post_1.id])
    data = {
      'id': post_1.id,
      'title': 'Пост 1 обновлен',
      'body': 'Содержание обновлено',
    }

    response = self.client.put(url, data, format='json')
    
    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(data['id'], response.data['id'])
    self.assertEqual(data['title'], response.data['title'])
    self.assertEqual(data['body'], response.data['body'])
    self.assertEqual(post_1.views_count, response.data['views_count'])
    self.assertEqual(format_dt(post_1.create_at), response.data['create_at'])
    self.assertNotEqual(format_dt(post_1.update_at), response.data['update_at'])

  # PUT обновлене, нету доступа (403_FORBIDDEN)
  def test_update_not(self):
    post_1 = Post.objects.filter(author=self.user_1).first()
    url = reverse('post-detail', args=[post_1.id])
    data = {
      'id': post_1.id,
      'title': 'Пост 1 обновлен',
      'body': 'Содержание обновлено',
    }

    response = self.client.put(url, data, format='json')
    self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

  # PUT полное обновление вместе с суб постами(200_OK)
  def test_update_complate_post_and_subposts(self):
    post_1 = Post.objects.all().first()
    url = reverse('post-detail', args=[post_1.id])
    subpost_1 = SubPost.objects.create(
      title='Субпост',
      body='Содержаине',
      post=post_1
    )
    subpost_2 = SubPost.objects.create(
      title='Субпост',
      body='Содержаине',
      post=post_1
    )

    data_subpost_1 = {
      'id': subpost_1.id,
      'title': 'Новый Субпост 1',
      'body': 'Содержание новое'
    }
    data_subpost_2 = {
      'title': 'Обновленный 1',
      'body': 'Содержание'
    }

    data = {
      'id': post_1.id,
      'title': 'Обновленый пост 1',
      'body': 'Содержание',
      'subposts': [data_subpost_1, data_subpost_2]
    }

    response = self.client.put(url, data, format='json')
    
    update_subpost = SubPost.objects.filter(
      id=data_subpost_1['id']
    ).first()
    new_subpost = SubPost.objects.filter(
      title=data_subpost_2['title']
    ).first()
    none_subpost = SubPost.objects.filter(
      id=subpost_2.id
    ).first()
    
    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(data['id'], response.data['id'])
    self.assertEqual(data['title'], response.data['title'])
    self.assertEqual(data['body'], response.data['body'])
    self.assertEqual(post_1.views_count, response.data['views_count'])
    self.assertEqual(format_dt(post_1.create_at), response.data['create_at'])
    self.assertNotEqual(format_dt(post_1.update_at), response.data['update_at'])

    self.assertEqual(data_subpost_2['title'], new_subpost.title)
    self.assertEqual(data_subpost_2['body'], new_subpost.body)
    self.assertEqual(data_subpost_1['title'], update_subpost.title)
    self.assertEqual(data_subpost_1['body'], update_subpost.body)
    self.assertIsNone(none_subpost)


  # PATCH частичное обновление (200_OK)
  def test_update_partial(self):
    post_1 = Post.objects.all().first()
    url = reverse('post-detail', args=[post_1.id])
    data = {
      'id': post_1.id,
      'title': 'Пост 1 обновлен'
    }

    response = self.client.patch(url, data, format='json')

    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(data['id'], response.data['id'])
    self.assertEqual(data['title'], response.data['title'])
    self.assertEqual(post_1.body, response.data['body'])
    self.assertEqual(post_1.views_count, response.data['views_count'])
    self.assertEqual(format_dt(post_1.create_at), response.data['create_at'])
    self.assertNotEqual(format_dt(post_1.update_at), response.data['update_at'])

  # DELETE (204_NO_CONTENT)
  def test_delete(self):
    new_post = Post.objects.create(
      title='Пост 1', 
      body='Содержание',
      author=self.user
    )

    url = reverse('post-detail', args=[new_post.id])
    response = self.client.delete(url)

    post = Post.objects.filter(id=new_post.id).first()

    self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
    self.assertIsNone(post)
