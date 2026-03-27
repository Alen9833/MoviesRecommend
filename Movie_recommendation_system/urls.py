from django.contrib import admin
from django.urls import path, include

from .views import index, star

urlpatterns = [
    path('admin/', admin.site.urls),  # 后台管理系统
    path('', index),  # 首页
    path('movie/', include('movie.urls')),  # 电影推荐系统子路由
]
