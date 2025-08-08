from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.blog.views import PostViewSet, SubPostViewSet, LikeViewSet


router = DefaultRouter()

router.register(r'posts', PostViewSet, basename='post')
router.register(r'subposts', SubPostViewSet, basename='subpost')


urlpatterns = [
  path(
    'posts/<int:pk>/like/', 
    LikeViewSet.as_view({'post': 'like'}),
    name='post-like' 
  ),

  path('', include(router.urls))
]


# Снизу маршруты которые доступны
"""
post_urlpatterns = [
  path('posts/', PostViewSet.as_view(
    {
      'get': 'list', 
      'post': 'create'
    }
  )),
  path('posts/<int:pk>/', PostViewSet.as_view(
    {
      'get': 'retrieve', 
      'put': 'update',
      'patch': 'partial_update',
      'delete': 'destroy'
    }
  )),  

  path('posts/<int:pk>/like/', LikeViewSet.as_view({'post': 'like'})),
  path('posts/<int:pk>/view/', PostViewSet.as_view({'get': 'add_view'}))
]

subpost_urlpatterns = [
  path('subposts/', SubPostViewSet.as_view(
    {
      'get': 'list', 
      'post': 'create'
    }
  )),
  path('subposts/<int:pk>/', SubPostViewSet.as_view(
    {
      'get': 'retrieve', 
      'put': 'update',
      'delete': 'destroy'
    }
  )),  
]
"""