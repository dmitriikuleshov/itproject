"""Обработка страниц приложения main"""

from django.shortcuts import render, redirect

from .models import VkAccount


def index_view(request):
    """
    Высылка главной страницы, проверка,
    аутентифицирован ли пользователь, с помощью cookie

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponse
        Главная страница сайта
    """
    login = ''
    if 'login' in request.COOKIES:
        login = request.COOKIES['login']

    if not login:
        return render(request, 'main/index.html')
    return render(request, 'main/auth-index.html',
                  {'login': login, 'links': VkAccount.objects.filter(creator=login)})


def logout_view(request):
    """
    Выход из учётной записи путём
    удаления cookie.

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponseRedirect
        Перенаправление на главную страницу
    """
    response = redirect('/')
    response.delete_cookie('login')
    return response
