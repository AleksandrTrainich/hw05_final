from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.all()
    # Если порядок сортировки определен в классе Meta модели,
    # запрос будет выглядить так:
    # post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, "paginator": paginator})


def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным
    # критериям объект из базы данных
    # или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)

    post_list = group.posts.all()

    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    context = {"group": group, "page": page, "paginator": paginator}
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    markup = {'title': 'Новая запись',
              'header': 'Написать новую статью',
              'button': "Добавить"}
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('index')
    context = {'form': form, 'markup': markup}
    return render(request, 'posts/new_post.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count = Post.objects.filter(author=author).count
    follower_count= Follow.objects.filter(author=author).count
    if  request.user.is_authenticated:
        following_count = Follow.objects.filter(user=request.user).count
        following = Follow.objects.filter(user = request.user, author = author).exists()
    else:
        following_count = None
        following = False
    author_user = request.user.username
    context = {"page": page,
               "author": author,
               "paginator": paginator,
               "count": count,
               "username": username,
               "author_user": author_user,
               'follower_count': follower_count,
               'following_count': following_count,
               'following': following}
    return render(request, 'profile.html', context)



def post_view(request, username, post_id):
    author = User.objects.get(username=username)
    posts = get_object_or_404(Post, author=author, pk=post_id)
    count = Post.objects.filter(author=author).count
    author_user = request.user.username
    comments = posts.сomments.all()
    form = CommentForm()
    
    context = {"posts": posts,
               "count": count,
               "author": author,
               "username": username,
               "author_user": author_user,
               'form': form,
               'comments': comments}
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if post.author == request.user and request.method != 'POST':
        markup = {'title': 'Редактирование записи',
                  'header': 'Редактровать статью',
                  'button': "Редактировать"}
        context = {'form': form,
                   'post': post,
                   'username': username,
                   'markup': markup}
        return render(request, 'posts/new_post.html', context)
    if request.method == 'POST' and form.is_valid():
        post.group = form.cleaned_data['group']
        post.text = form.cleaned_data['text']
        post.save()
        return redirect('post', username, post_id)
    else:
        return redirect('post', username, post_id)

@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
        return redirect('post', username, post_id)
    return redirect('post', username, post_id)

@login_required
def follow_index(request):
   
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)   
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})

@login_required
def profile_follow(request, username):
    
    author = get_object_or_404(User, username = username)
    if Follow.objects.filter(user = request.user, author=author).exists() or author == request.user:
       return redirect('profile', username)
    else: 
        user = request.user
        author = User.objects.get(username=username)
        Follow.objects.create(user = user, author=author)
        return redirect('profile', username)
    
@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(user = request.user, author = author)
    follow.delete()
    return redirect('profile', username)      
    