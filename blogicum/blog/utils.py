from django.core.paginator import Paginator

from blog.constants import DEFAULT_POSTS_PER_PAGE


def paginate_queryset(request, queryset):
    """Универсальная функция для пагинации."""
    paginator = Paginator(queryset, DEFAULT_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
