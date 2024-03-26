from django.shortcuts import render, redirect
import os

from .tools import Vk


def user_info_view(request):
    """
    Получение данных о пользователе, переданном по ссылке,
    высылка страницы с полученными данными.
    """
    if request.method == 'GET':
        link = request.GET.get('link')
        vk = Vk(token=os.environ['VK_TOKEN'])
        try:
            return render(request, 'vkapi/user-info.html', vk.get_info(link))
        except (TypeError, IndexError):
            return render(request, 'vkapi/user-info.html', {'error': True})
    else:
        return redirect('/')
