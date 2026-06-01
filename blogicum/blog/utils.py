from django.core.paginator import Paginator
from django.utils import timezone

from blog.constants import DEFAULT_POSTS_PER_PAGE


def paginate_queryset(
    request,
    queryset,
    items_per_page=DEFAULT_POSTS_PER_PAGE
):
    """Универсальная функция для пагинации."""
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_published_posts(queryset, post_filter=True):
    """
    Метод для фильтрации публикаций.

    Если post_filter=True, то фильтруем посты по:
    - is_published=True
    - категория опубликована
    - дата публикации не позже текущего времени

    Если post_filter=False:
    - возвращаем все посты.

    Также добавляем select_related для оптимизации запросов.
    """
    queryset = queryset.select_related(
        'category',
        'author',
        'location'
    )

    if post_filter is True:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    return queryset.order_by('-pub_date')
