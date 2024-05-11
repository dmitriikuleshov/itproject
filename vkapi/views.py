"""Обработка страниц приложения vkapi"""

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import os

from .vk_tools import Vk
from main.models import VkAccount
from .graph_creator import create_friends_graph


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
        vk = Vk(token=os.environ['VK_TOKEN'])

        try:
            vk_info = vk.get_info(link)
            create_friends_graph('vkapi/templates/vkapi/friends-graph.html', vk_info)
            response = render(request, 'vkapi/user-info.html', vk_info)

            if not VkAccount.objects.filter(link=link, creator=request.COOKIES['login']).exists():
                VkAccount(link=link, creator=request.COOKIES['login']).save()

            return response

        except (TypeError, IndexError):
            return render(request, 'vkapi/user-info.html', {'error': True})
    else:
        return redirect('/')
