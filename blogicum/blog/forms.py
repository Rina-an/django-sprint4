from django import forms
from django.contrib.auth.models import User

from blog.models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для поста."""

    class Meta:
        model = Post
        exclude = ['author']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%d.%m.%Y %H:%M'),
        }


class CommentForm(forms.ModelForm):
    """Форма для комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={'cols': 80, 'rows': 5, 'class': 'form-control'}
            ),
        }


class UserEditForm(forms.ModelForm):
    """Форма для изменения данных пользователя."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
