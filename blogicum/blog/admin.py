from django.contrib import admin

from blog.models import Category, Location, Post, Comment


class Postline(admin.TabularInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "is_published",
        "created_at",
        "slug",
    )
    inlines = [Postline]
    list_editable = ("is_published",)
    search_fields = ("title",)
    list_filter = ("slug",)
    list_display_links = ("title",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_published",
        "created_at",
    )
    inlines = [Postline]
    list_editable = ("is_published",)
    search_fields = ("name",)
    list_display_links = ("name",)
    empty_value_display = "Не задано"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "text",
        "is_published",
        "created_at",
        "pub_date",
        "author",
        "location",
        "category",
    )
    list_editable = ("is_published",)
    search_fields = ("title",)
    list_display_links = ("title",)
    list_filter = (
        "author",
        "location",
        "pub_date",
    )
    empty_value_display = "Не задано"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "is_published",
        "created_at",
        "author"
    )
    list_editable = ("is_published",)
    search_fields = ("text",)
    list_display_links = ("text",)
    list_filter = (
        "author",
        "is_published"
    )
    empty_value_display = "Не задано"
