from django.contrib import admin

from apps.blog.models import Post, SubPost, Like
admin.site.register(Post)
admin.site.register(SubPost)
admin.site.register(Like)