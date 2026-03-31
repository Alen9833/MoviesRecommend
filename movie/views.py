import os.path
import time
import json
from collections import defaultdict

from django.contrib import messages
from django.db.models import Max, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views.generic import View, ListView, DetailView

from .ai_assistant import handle_chat as handle_ai_chat
from .forms import RegisterForm, LoginForm, CommentForm
from .models import User, Movie, Movie_rating, Movie_hot

BASE = os.path.dirname(os.path.abspath(__file__))


# 首页视图
class IndexView(ListView):
    model = Movie
    template_name = 'movie/index.html'
    paginate_by = 15
    context_object_name = 'movies'
    ordering = 'imdb_id'
    page_kwarg = 'p'

    def get_queryset(self):
        return Movie.objects.filter(imdb_id__lte=1000)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IndexView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages, 'right_pages': right_pages, 'current_page': current_page,
            'left_has_more': left_has_more, 'right_has_more': right_has_more
        }


# 热门电影视图
class PopularMovieView(ListView):
    model = Movie_hot
    template_name = 'movie/hot.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    def get_queryset(self):
        hot_movies = Movie_hot.objects.all().values("movie_id")
        movies = Movie.objects.filter(id__in=hot_movies).annotate(nums=Max('movie_hot__rating_number')).order_by(
            '-nums')
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PopularMovieView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True
        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages, 'right_pages': right_pages, 'current_page': current_page,
            'left_has_more': left_has_more, 'right_has_more': right_has_more
        }


# 分类、搜索、注册、登录等视图保持逻辑不变...
# (为了篇幅，此处省略与原文件一致的 TagView, SearchView, RegisterView, LoginView, UserLogout 代码)
# 请在实际文件中保留这些视图

# 电影分类视图 (保留原代码)
class TagView(ListView):
    model = Movie
    template_name = 'movie/tag.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    def get_queryset(self):
        if 'genre' not in self.request.GET.dict().keys() or self.request.GET.dict()['genre'] == "":
            movies = Movie.objects.all()
            return movies[100:200]
        else:
            movies = Movie.objects.filter(genre__name=self.request.GET.dict()['genre'])
            return movies[:100]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagView, self).get_context_data(*kwargs)
        if 'genre' in self.request.GET.dict().keys():
            genre = self.request.GET.dict()['genre']
            context.update({'genre': genre})
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True
        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {'left_pages': left_pages, 'right_pages': right_pages, 'current_page': current_page,
                'left_has_more': left_has_more, 'right_has_more': right_has_more}


# 搜索、注册、登录、登出逻辑...
class SearchView(ListView):
    model = Movie
    template_name = 'movie/search.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    def get_queryset(self):
        movies = Movie.objects.filter(name__icontains=self.request.GET.dict()['keyword'])
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        context.update({'keyword': self.request.GET.dict()['keyword']})
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True
        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {'left_pages': left_pages, 'right_pages': right_pages, 'current_page': current_page,
                'left_has_more': left_has_more, 'right_has_more': right_has_more}


class RegisterView(View):
    def get(self, request):
        return render(request, 'movie/register.html')

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('movie:index'))
        else:
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)
            return redirect(reverse('movie:register'))


class LoginView(View):
    def get(self, request):
        return render(request, 'movie/login.html')

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            pwd = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            user = User.objects.filter(name=name, password=pwd).first()
            if user:
                if remember:
                    request.session.set_expiry(None)
                else:
                    request.session.set_expiry(0)
                request.session['user_id'] = user.id
                return redirect(reverse('movie:index'))
            else:
                messages.info(request, '用户名或者密码错误!')
                return redirect(reverse('movie:login'))
        else:
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)
            return redirect(reverse('movie:login'))


def UserLogout(request):
    request.session.set_expiry(-1)
    return redirect(reverse('movie:index'))


# 电影详情视图
class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movie/detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login = True
        try:
            user_id = self.request.session['user_id']
        except KeyError:
            login = False

        pk = self.kwargs['pk']
        movie = Movie.objects.get(pk=pk)

        if login:
            user = User.objects.get(pk=user_id)
            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            score = 0
            comment = ''
            if rating:
                score = rating.score
                comment = rating.comment
            context.update({'score': score, 'comment': comment})

        similarity_movies = movie.get_similarity()
        context.update({'similarity_movies': similarity_movies, 'login': login})
        return context

    def post(self, request, pk):
        form = CommentForm(request.POST)
        if form.is_valid():
            score = form.cleaned_data.get('score')
            comment = form.cleaned_data.get('comment')
            user_id = request.session['user_id']
            user = User.objects.get(pk=user_id)
            movie = Movie.objects.get(pk=pk)

            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            if rating:
                rating.score = score
                rating.comment = comment
                rating.save()
            else:
                rating = Movie_rating(user=user, movie=movie, score=score, comment=comment)
                rating.save()
            messages.info(request, "评论成功!")
        else:
            messages.info(request, "评分不能为空!")
        return redirect(reverse('movie:detail', args=(pk,)))


# --- 【重点修改】历史评分与雷达图视图 ---
class RatingHistoryView(DetailView):
    model = User
    template_name = 'movie/history.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('user_id')
        if not user_id:
            return context

        user = User.objects.get(pk=user_id)
        # 获取用户评分记录，关联查询 movie 提高性能
        ratings = Movie_rating.objects.filter(user=user).order_by('-score').select_related('movie')

        # --- 计算雷达图数据 ---
        genre_weights = defaultdict(float)
        for r in ratings:
            # 获取电影类型（如果是ManyToMany，需要迭代）
            genres = r.movie.genre.all() if hasattr(r.movie.genre, 'all') else r.movie.get_genre()
            # 兼容处理：确保 genres 是列表
            if isinstance(genres, str):
                genres = [g.strip() for g in genres.split(',')]

            for g in genres:
                # 累加：评分越高，该维度权重越大
                genre_weights[str(g)] += float(r.score)

        # 排序并取前 6 个
        sorted_genres = sorted(genre_weights.items(), key=lambda x: x[1], reverse=True)[:6]

        radar_indicator = []
        radar_value = []
        if sorted_genres:
            # 动态计算 Max，防止雷达图顶满格或缩得太小
            max_val = max([item[1] for item in sorted_genres]) * 1.2
            radar_indicator = [{"name": item[0], "max": max_val} for item in sorted_genres]
            radar_value = [round(item[1], 1) for item in sorted_genres]

        context.update({
            'ratings': ratings,
            'radar_indicator': json.dumps(radar_indicator),
            'radar_value': json.dumps(radar_value),
        })
        return context


# 删除记录
def delete_recode(request, pk):
    movie = Movie.objects.get(pk=pk)
    user_id = request.session['user_id']
    user = User.objects.get(pk=user_id)
    rating = Movie_rating.objects.get(user=user, movie=movie)
    rating.delete()
    messages.info(request, f"删除 {movie.name} 评分记录成功！")
    return redirect(reverse('movie:history', args=(user_id,)))


# 推荐电影视图 (保持原代码)
class ChatView(View):
    ERROR_STATUS_MAP = {
        'UNAUTHORIZED': 401,
        'INVALID_REQUEST': 400,
        'MODEL_UNAVAILABLE': 503,
        'MODEL_BAD_RESPONSE': 502,
        'DATABASE_ERROR': 500,
        'INTERNAL_ERROR': 500,
    }

    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({
                'ok': False,
                'error_code': 'UNAUTHORIZED',
                'error_message': '用户未登录',
                'reply': '请先登录后再使用电影助手。',
                'movies': [],
            }, status=401)

        user = User.objects.filter(pk=user_id).first()
        if not user:
            return JsonResponse({
                'ok': False,
                'error_code': 'UNAUTHORIZED',
                'error_message': '登录状态已失效',
                'reply': '你的登录状态已失效，请重新登录后再使用电影助手。',
                'movies': [],
            }, status=401)

        try:
            payload = json.loads(request.body or '{}')
        except (TypeError, ValueError, json.JSONDecodeError):
            return JsonResponse({
                'ok': False,
                'error_code': 'INVALID_REQUEST',
                'error_message': '请求 JSON 格式错误',
                'reply': '请求格式不正确，请稍后重试。',
                'movies': [],
            }, status=400)

        message = payload.get('message', '')
        history = payload.get('history', [])
        if not isinstance(message, str) or not message.strip():
            return JsonResponse({
                'ok': False,
                'error_code': 'INVALID_REQUEST',
                'error_message': 'message 不能为空',
                'reply': '请输入你想问的内容。',
                'movies': [],
            }, status=400)
        if history is not None and not isinstance(history, list):
            return JsonResponse({
                'ok': False,
                'error_code': 'INVALID_REQUEST',
                'error_message': 'history 必须是数组',
                'reply': '上下文格式不正确，请稍后重试。',
                'movies': [],
            }, status=400)

        try:
            result = handle_ai_chat(message=message.strip(), history=history or [], user=user)
            if result.get('ok', True):
                return JsonResponse(result, status=200)

            error_code = result.get('error_code', 'INTERNAL_ERROR')
            status_code = self.ERROR_STATUS_MAP.get(error_code, 500)
            return JsonResponse(result, status=status_code)
        except Exception:
            return JsonResponse({
                'ok': False,
                'error_code': 'INTERNAL_ERROR',
                'error_message': '服务内部异常',
                'reply': '助手暂时出了点问题，请稍后再试。',
                'movies': [],
            }, status=500)


class RecommendMovieView(ListView):
    model = Movie
    template_name = 'movie/recommend.html'
    paginate_by = 15
    context_object_name = 'movies'
    ordering = 'movie_rating__score'
    page_kwarg = 'p'

    def __init__(self):
        super().__init__()
        self.K = 20
        self.N = 10
        self.cur_user_movie_qs = None

    def get_user_sim(self):
        user_sim_dct = dict()
        cur_user_id = self.request.session['user_id']
        cur_user = User.objects.get(pk=cur_user_id)
        other_users = User.objects.exclude(pk=cur_user_id)
        self.cur_user_movie_qs = Movie.objects.filter(user=cur_user)
        for user in other_users:
            user_sim_dct[user.id] = len(Movie.objects.filter(user=user) & self.cur_user_movie_qs)
        return sorted(user_sim_dct.items(), key=lambda x: -x[1])[:self.K]

    def get_recommend_movie(self, user_lst):
        movie_val_dct = dict()
        for user, _ in user_lst:
            movie_set = Movie.objects.filter(user=user).exclude(id__in=self.cur_user_movie_qs).annotate(
                score=Max('movie_rating__score'))
            for movie in movie_set:
                movie_val_dct.setdefault(movie, 0)
                movie_val_dct[movie] += movie.score
        return sorted(movie_val_dct.items(), key=lambda x: -x[1])[:self.N]

    def get_queryset(self):
        s = time.time()
        user_lst = self.get_user_sim()
        movie_lst = self.get_recommend_movie(user_lst)
        result_lst = [movie for movie, _ in movie_lst]
        e = time.time()
        print(f"算法推荐用时:{e - s}秒！")
        return result_lst

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RecommendMovieView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True
        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {'left_pages': left_pages, 'right_pages': right_pages, 'current_page': current_page,
                'left_has_more': left_has_more, 'right_has_more': right_has_more}