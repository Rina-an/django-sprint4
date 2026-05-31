from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.constants import DEFAULT_POSTS_PER_PAGE
from blog.forms import CommentForm, PostForm, UserEditForm
from blog.models import Category, Comment, Post
from blog.utils import paginate_queryset


# Получился какой-то ужас :(

def get_published_posts(queryset):
    """
    Метод для фильтрации публикаций по:
    - is_published=True
    - категория опубликована
    - дата публикации не позже текущего времени

    Также добавляем select_related для оптимизации запросов.
    """
    return queryset.select_related(
        "category",
        "author",
        "location"
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')


def add_comment_count(queryset):
    """Добавляет количество комментариев к постам. """
    return queryset.annotate(comment_count=Count('comments'))


class IndexListView(ListView):
    """Класс для отображения главной страницы."""

    model = Post
    template_name = "blog/index.html"
    paginate_by = DEFAULT_POSTS_PER_PAGE

    def get_queryset(self):
        return add_comment_count(
            get_published_posts(Post.objects.all())
        )


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для установления авторства постов."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """Класс для создания новой публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Класс для редактирования публикации ее автором."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Класс для удаления публикации ее автором."""

    model = Post
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Класс для создания комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = self.post_obj
        comment.save()

        return redirect(
            'blog:post_detail',
            post_id=self.post_obj.id
        )


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Класс для изменение комментария его автором."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Класс для удаления комментария его автором."""
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'post_id': self.object.post.id})


def post_detail(request, post_id):
    """Метод для рендеринга отдельного поста."""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        post = get_object_or_404(
            get_published_posts(Post.objects.all()),
            pk=post_id
        )
    comments = post.comments.all().order_by('created_at')
    context = context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    }
    return render(request, "blog/detail.html", context)


def category_posts(request, category_slug):
    """Метод для рендеринга постов по категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = add_comment_count(get_published_posts(category.posts.all()))
    context = {"category": category,
               'page_obj': paginate_queryset(request, posts)
               }
    return render(request, "blog/category.html", context)


def profile(request, username):
    """Метод для рендеринга страницы пользователя."""
    profile = get_object_or_404(User, username=username)
    posts = add_comment_count(
        Post.objects.filter(author=profile)
    ).order_by('-pub_date')
    context = {
        'profile': profile,
        'page_obj': paginate_queryset(request, posts),
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Метод для изменений данных пользователя."""
    form = UserEditForm(
        request.POST or None,
        instance=request.user
    )
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', context)
