from django.shortcuts import render, redirect
import os

from main.forms import LinkForm
from .tools import Vk


def user_info_view(request):
    """
    Получение данных о пользователе, переданном по ссылке,
    высылка страницы с полученными данными.
    """
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
        else:
            return redirect('/')
        vk = Vk(token=os.environ['VK_TOKEN'])
        try:
            return render(request, 'vkapi/user-info.html', vk.get_info(link))
        except (TypeError, IndexError):
            return render(request, 'vkapi/user-info.html', {'error': True})
    else:
        return redirect('/')
