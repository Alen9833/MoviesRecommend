from django.contrib import admin

from movie.models import User, Movie, Genre, Movie_hot, Movie_rating, Movie_similarity

admin.site.site_title = "电影推荐系统后台管理系统"
admin.site.site_header = "电影推荐系统-后台管理系统"
admin.site.index_title = "电影推荐系统"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 设置列表中显示的字段
    list_display = ['id', 'name', 'password', 'email', 'is_admin']
    # 搜索
    search_fields = ['name', 'email']
    # 过滤
    list_filter = ['is_admin']
    # 设置每页现实的数据量
    list_per_page = 12
    # 设置排序
    ordering = ['id']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    # 设置列表中显示的字段
    list_display = ['id', 'name']
    # 搜索
    search_fields = ['name']
    # 过滤
    # list_filter = ['name']
    # 设置每页现实的数据量
    list_per_page = 12
    # 设置排序
    ordering = ['id']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # 设置列表中显示的字段
    list_display = ['id', 'name', 'imdb_id', 'time', 'release_time', 'intro', 'director', 'writers', 'actors', ]
    # 搜索
    search_fields = ['name', 'intro', 'writers', 'actors']
    # # 过滤
    # list_filter = ['name', 'writers']
    # 设置每页现实的数据量
    list_per_page = 6
    # 设置排序
    ordering = ['id']


@admin.register(Movie_hot)
class Movie_hotAdmin(admin.ModelAdmin):
    # 设置列表中显示的字段
    list_display = ['id', 'movie', 'rating_number']
    # 搜索
    search_fields = ['movie__name']
    # # 过滤
    # list_filter = ['name', 'writers']
    # 设置每页现实的数据量
    list_per_page = 6
    # 设置排序
    ordering = ['-rating_number']


@admin.register(Movie_rating)
class Movie_ratingAdmin(admin.ModelAdmin):
    # 设置列表中显示的字段
    list_display = ['id', 'user', 'movie', 'score', 'comment']
    # 搜索
    search_fields = ['user__name', 'movie__name']
    # # 过滤
    # list_filter = ['name', 'writers']
    # 设置每页现实的数据量
    list_per_page = 6
    # 设置排序
    ordering = ['-score']


@admin.register(Movie_similarity)
class Movie_similarityAdmin(admin.ModelAdmin):
    # 设置列表中显示的字段
    list_display = ['id', 'movie_source', 'movie_target', 'similarity']
    # 搜索
    search_fields = ['movie_source__name', 'movie_source__name']
    # # 过滤
    # list_filter = ['name', 'writers']
    # 设置每页现实的数据量
    list_per_page = 6
    # 设置排序
    ordering = ['-similarity']
