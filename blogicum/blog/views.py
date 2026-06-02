from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from blog.constants import DEFAULT_POSTS_PER_PAGE
from blog.forms import CommentForm, PostForm, UserEditForm
from blog.mixins import OnlyAuthorMixin
from blog.models import Category, Comment, Post
from blog.utils import (
    get_published_posts,
    paginate_queryset,
    add_comment_count
)


class IndexListView(ListView):
    """Класс для отображения главной страницы."""

    model = Post
    template_name = "blog/index.html"
    paginate_by = DEFAULT_POSTS_PER_PAGE

    def get_queryset(self):
        return add_comment_count(
            get_published_posts(Post.objects.all())
        )


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
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Класс для создания комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Класс для изменения комментария его автором."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Класс для удаления комментария его автором."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.object.post.id})


def post_detail(request, post_id):
    """Метод для рендеринга отдельного поста."""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        post = get_object_or_404(
            get_published_posts(Post.objects.all()),
            pk=post_id
        )
    comments = post.comments.select_related("author").all().order_by(
        'created_at'
    )
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
        get_published_posts(
            profile.posts.all(),
            post_filter=request.user != profile
        )
    )
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
