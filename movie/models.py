from django.db import models
from django.db.models import Avg


# 分类信息表
class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name="类型")

    class Meta:
        db_table = 'Genre'
        verbose_name = '电影类型'
        verbose_name_plural = '电影类型'

    def __str__(self):
        return self.name


# 电影信息表
class Movie(models.Model):
    name = models.CharField(max_length=256, verbose_name="电影名")
    imdb_id = models.IntegerField(verbose_name="imdb_id")
    time = models.CharField(max_length=256, blank=True, verbose_name="时长")
    genre = models.ManyToManyField(Genre, verbose_name="类型")
    release_time = models.CharField(max_length=256, blank=True, verbose_name="发行时间")
    intro = models.TextField(blank=True, verbose_name="简介")
    director = models.CharField(max_length=256, blank=True, verbose_name="导演")
    writers = models.CharField(max_length=256, blank=True, verbose_name="编剧")
    actors = models.CharField(max_length=512, blank=True, verbose_name="演员")
    # 电影和电影之间的相似度,A和B的相似度与B和A的相似度是一致的，所以symmetrical设置为True
    movie_similarity = models.ManyToManyField("self", through="Movie_similarity", symmetrical=False,
                                              verbose_name="相似电影")

    class Meta:
        db_table = 'Movie'
        verbose_name = '电影信息'
        verbose_name_plural = '电影信息'

    def __str__(self):
        return self.name

    # 获取平均分的方法
    def get_score(self):
        result_dct = self.movie_rating_set.aggregate(Avg('score'))  # 格式 {'score__avg': 3.125}
        try:
            result = round(result_dct['score__avg'], 1)  # 只保留一位小数
        except TypeError:
            return 0
        else:
            return result

    # 获取用户的打分情况
    def get_user_score(self, user):
        return self.movie_rating_set.filter(user=user).values('score')

    # 整数平均分
    def get_score_int_range(self):
        return range(int(self.get_score()))

    # 获取分类列表
    def get_genre(self):
        genre_dct = self.genre.all().values('name')
        genre_lst = []
        for dct in genre_dct.values():
            genre_lst.append(dct['name'])
        return genre_lst

    # 获取电影的相识度
    def get_similarity(self, k=5):
        # 默认获取5部最相似的电影的id
        similarity_movies = self.movie_similarity.all()[:k]
        return similarity_movies


# 电影相似度
class Movie_similarity(models.Model):
    movie_source = models.ForeignKey(Movie, related_name='movie_source', on_delete=models.CASCADE, verbose_name="来源电影")
    movie_target = models.ForeignKey(Movie, related_name='movie_target', on_delete=models.CASCADE, verbose_name="目标电影")
    similarity = models.FloatField(verbose_name="相似度")

    class Meta:
        # 按照相似度降序排序
        verbose_name = '电影相似度'
        verbose_name_plural = '电影相似度'


# 用户信息表
class User(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=256, verbose_name="密码")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    is_admin = models.BooleanField(default=False, verbose_name="是否管理员")
    rating_movies = models.ManyToManyField(Movie, through="Movie_rating")

    def __str__(self):
        return "<USER:( name: {:},password: {:},email: {:} )>".format(self.name, self.password, self.email)

    class Meta:
        db_table = 'User'
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'


# 电影评分信息表
class Movie_rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, verbose_name="用户")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False, verbose_name="电影")
    score = models.FloatField(verbose_name="分数")
    comment = models.TextField(blank=True, verbose_name="评论")

    class Meta:
        db_table = 'Movie_rating'
        verbose_name = '电影评分信息'
        verbose_name_plural = '电影评分信息'


# 最热门的一百部电影
class Movie_hot(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="电影名")
    rating_number = models.IntegerField(verbose_name="评分人数")

    class Meta:
        db_table = 'Movie_hot'
        verbose_name = '最热电影'
        verbose_name_plural = '最热电影'

# python manage.py makemigrations
# python manage.py migrate
