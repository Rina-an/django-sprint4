from django.views.generic import TemplateView
from django.shortcuts import render


class AboutPage(TemplateView):
    """
    Класс для статической страницы "О проекте".
    """

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """
    Класс для статической страницы "Правила".
    """

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Кастомная страница для 404 ошибки."""
    return render(request, 'pages/404.html', status=404)


def server_down(request):
    """Кастомная страница для 500 ошибки."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Кастомная страница для ошибки проверки CSRF."""
    return render(request, 'pages/403csrf.html', status=403)
