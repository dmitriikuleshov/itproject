"""Обработка страниц приложения vkapi"""
import os

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from main.models import VkAccount
from .visualization import Visualization
from .vk_tools import Vk


def user_info_view(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """
    Получение данных о пользователе, переданном по ссылке,
    высылка страницы с полученными данными.

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponse | HttpResponseRedirect
        Страница с информацией об аккаунте или перенаправление на главную

    """
    if 'theme' not in request.COOKIES:
        request.COOKIES['theme'] = 'light'

    vk = Vk(token='vk1.a._jPLHq2gfGMQ71O8xJt_TdopUo7vYIsnXzEDeZf_mVwFbZMdNdzxv2eHc8x1LOEgzp2Fp4UbvrJaiHKx_d65ckFFeKlo17oKeqve8o0iHmdyuIzvFfYq95xG_4yW4T9hD7sd2GyX7D4Bt0bB8qkk-73jNFrxgz5nj4Q2SWNY-fkl25YxkXPTYNgk6CrxvRnoOF-BrvwvHYNwjjhK7OogSw')
    link = request.GET.get('link')

    try:
        response = render(
            request,
            'vkapi/user-info.html',
            {
                'info': vk.get_info(link),
                'link': link,
                'theme': request.COOKIES['theme']
            })

        if (not VkAccount.objects.filter(link=link, creator=request.COOKIES['login']).exists() and
                not request.GET.get('save')):
            VkAccount(link=link, creator=request.COOKIES['login']).save()

        return response

    except (TypeError, IndexError):
        return render(
            request,
            'main/auth-index.html',
            {
                'error': True,
                'login': request.COOKIES['login'],
                'links': [{
                    'name': str(elem).split('/')[-1],
                    'link': elem
                } for elem in VkAccount.objects.filter(creator=request.COOKIES['login'])]
            }
        )


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
    response = redirect(f'/vk/?save=1&link={request.GET.get("link")}')

    if 'theme' not in request.COOKIES:
        request.COOKIES['theme'] = 'light'
    if request.COOKIES['theme'] == 'dark':
        response.set_cookie('theme', 'light')
    elif request.COOKIES['theme'] == 'light':
        response.set_cookie('theme', 'dark')

    return response


def mutual_friends_view(request: HttpRequest) -> HttpResponse:
    """
    Возвращает фрейм с графом дружеских связей

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponse | HttpResponseRedirect
        Фрейм с графом дружеских связей

    """
    visualization = Visualization(request.GET.get('link'))
    visualization.create_mutual_friends_graph('vkapi/templates/vkapi/mutual-friends-graph.html')
    return render(request, 'vkapi/mutual-friends-graph.html')


def activity_view(request: HttpRequest) -> HttpResponse:
    """
    Возвращает фрейм с графиком активности

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponse | HttpResponseRedirect
        Фрейм с графиком активности

    """
    visualization = Visualization(request.GET.get('link'))
    visualization.create_activity_graph('vkapi/templates/vkapi/activity-graph.html')
    return render(request, 'vkapi/activity-graph.html')


def subscriptions_view(request: HttpRequest) -> HttpResponse:
    """
    Возвращает фрейм со списком подписок пользователя

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponse | HttpResponseRedirect
        Фрейм со списком подписок пользователя

    """
    visualization = Visualization(request.GET.get('link'))
    return render(request, 'vkapi/subscriptions.html', {
        'user_subscriptions': visualization.get_user_subscriptions(),
        'group_subscriptions': visualization.get_group_subscriptions(),
    })
