from django.shortcuts import render


# 首页
def index(request):
    return render(request, 'index.html')


# 打分
def star(request):
    return render(request, 'movie/star.html')
