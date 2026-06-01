from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для установления авторства постов."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user
