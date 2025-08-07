from django.urls import path

from apps.blog.views import PostViewSet, SubPostViewSet, LikeViewSet


post_urlpatterns = [
  path('posts/', PostViewSet.as_view({'get': 'list', 'post': 'create'})),
  path('posts/<int:pk>/', PostViewSet.as_view(
    {
      'get': 'retrieve', 
      'put': 'update',
      'patch': 'partial_update',
      'delete': 'destroy'
    }
  )),  

  path('posts/<int:pk>/like/', LikeViewSet.as_view({'post': 'like'})),
  # path('posts/<int:pk>/view/', )
]

subpost_urlpatterns = [
  path('subposts/', SubPostViewSet.as_view({'get': 'list', 'post': 'create'})),
  path('subposts/<int:pk>/', SubPostViewSet.as_view(
    {
      'get': 'retrieve', 
      'put': 'update',
      'delete': 'destroy'
    }
  )),  
]

urlpatterns = [
] + post_urlpatterns + subpost_urlpatterns