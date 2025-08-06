from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
  class Meta:
    verbose_name = 'Пост'
    verbose_name_plural = 'Посты'

  author = models.ForeignKey(
    User, 
    on_delete=models.CASCADE, 
    related_name='posts')
  title = models.CharField(max_length=250)
  body = models.TextField()
  create_at = models.DateTimeField(auto_now_add=True)
  update_at = models.DateTimeField(auto_now=True)
  views_count = models.PositiveIntegerField(default=0)

  def __str__(self):
    return f"{self.title} {self.author}"
  

class SubPost(models.Model):
  class Meta:
    verbose_name = 'Подпост'
    verbose_name_plural = 'Подпосты'

  post = models.ForeignKey(
    Post, 
    on_delete=models.CASCADE, 
    related_name='sub_posts')
  title = models.CharField(max_length=250)
  body = models.TextField()
  create_at = models.DateTimeField(auto_now_add=True)
  update_at = models.DateTimeField(auto_now=True)
  

class Like(models.Model):
  class Meta:
    verbose_name = 'Лайк'
    verbose_name_plural = 'Лайки'
    # Гарантирует: 1 user 1 лайк для 1 поста. IntegrityError(это ошибка вызов.)
    unique_together = ('user', 'post')

  user = models.ForeignKey(
    User, 
    on_delete=models.CASCADE, 
    related_name='likes')
  post = models.ForeignKey(
    Post, 
    on_delete=models.CASCADE, 
    related_name='likes')
  create_at = models.DateTimeField(auto_now_add=True)