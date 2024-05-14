"""Обработка страниц приложения main"""

from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.http import HttpRequest
from .models import VkAccount


def index_view(request: HttpRequest) -> HttpResponse:
    """
    Высылка главной страницы, проверка,
    аутентифицирован ли пользователь, с помощью cookie

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса
    error: bool
        Флаг, отвечающий за вывод сообщения об ошибке

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


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
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
