from django.contrib.auth import get_user_model
from django.db import models

from blog.constants import DEFAULT_TITLE_LENGTH, DEFAULT_LOCATION_NAME_LENGTH

User = get_user_model()


class CreatedPublishedModel(models.Model):
    """
    Абстрактная модель.

    Добавляет к модели дату создания и
    положение флага "опубликовано" True/False.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )

    class Meta:
        abstract = True


class Category(CreatedPublishedModel):
    """Модель категории."""

    title = models.CharField(max_length=256, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        )
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:DEFAULT_TITLE_LENGTH]


class Location(CreatedPublishedModel):
    """Модель местоположения."""

    name = models.CharField(max_length=256, verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name[:DEFAULT_LOCATION_NAME_LENGTH]


class Post(CreatedPublishedModel):
    """Модель публикации."""

    title = models.CharField(max_length=256, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    image = models.ImageField('Фото', upload_to='posts_media', blank=True)
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория"
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:DEFAULT_TITLE_LENGTH]


class Comment(models.Model):
    """Модель комментария."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
