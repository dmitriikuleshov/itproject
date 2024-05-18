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

    Returns
    -------
    HttpResponse
        Главная страница сайта

    """
    if 'theme' not in request.COOKIES:
        request.COOKIES['theme'] = 'light'

    login = ''
    if 'login' in request.COOKIES:
        login = request.COOKIES['login']

    if not login:
        return render(
            request,
            'main/index.html',
            {'theme': request.COOKIES['theme']}
        )
    return render(
        request,
        'main/auth-index.html',
        {
            'login': login,
            'links': [{
                'name': str(elem).split('/')[-1],
                'link': elem
            } for elem in VkAccount.objects.filter(creator=login)],
            'theme': request.COOKIES['theme']
        }
    )


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


def change_theme(request: HttpRequest) -> HttpResponseRedirect:
    """
    Установка темы страницы с помощью cookie

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

    if 'theme' not in request.COOKIES:
        request.COOKIES['theme'] = 'light'
    if request.COOKIES['theme'] == 'dark':
        response.set_cookie('theme', 'light')
    elif request.COOKIES['theme'] == 'light':
        response.set_cookie('theme', 'dark')

    return response
