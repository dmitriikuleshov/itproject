
"""Обработка страниц приложения vkapi"""
import shutil

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from main.models import VkAccount
from .visualization import Visualization


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
    if request.method == 'GET':
        link = request.GET.get('link')

        try:
            visualization = Visualization(link)
            visualization.create_activity_graph('vkapi/templates/vkapi/activity-graph.html')
            visualization.create_mutual_friends_graph('vkapi/templates/vkapi/mutual-friends-graph.html')

            context = {
                'first_name': visualization.user_info['first_name'],
                'last_name': visualization.user_info['last_name'],
                'birthday': visualization.user_info['birthday'],
                'city': visualization.user_info['city'],
                'user_subscriptions': visualization.get_user_subscriptions(),
                'group_subscriptions': visualization.get_group_subscriptions(),
                'toxicity': visualization.get_toxicity()
            }

            response = render(
                request,
                'vkapi/user-info.html',
                context
            )

            if not VkAccount.objects.filter(link=link, creator=request.COOKIES['login']).exists():
                VkAccount(link=link, creator=request.COOKIES['login']).save()

            return response

        except (TypeError, IndexError):
            return render(
                request,
                'main/auth-index.html',
                {
                    'error': True,
                    'login': request.COOKIES['login']
                }
            )
    else:
        return redirect('/')
