from django.contrib import admin

from .models import Category, Location, Post


class Postline(admin.TabularInline):
    model = Post
    extra = 0


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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
