from django.shortcuts import render, redirect
import os

from .vk_tools import Vk
from main.models import VkAccount
from .graph_creator import create_friends_graph, create_mutual_friends_graph
from .visualization import Visualization


def user_info_view(request):
    """
    Получение данных о пользователе, переданном по ссылке,
    высылка страницы с полученными данными.
    """
    if request.method == 'GET':
        link = request.GET.get('link')
        vk = Vk(token=os.environ['VK_TOKEN'])

        try:
            vk_friends_info = vk.get_common_connections(link)
            visualization = Visualization(link)
            visualization.get_favourite_music()
            visualization.get_toxicity()
            visualization.create_activity_graph('vkapi/templates/vkapi/activity-graph.html')

            create_mutual_friends_graph('vkapi/templates/vkapi/mutual-friends-graph.html',
                                        visualization.user_info, vk_friends_info)
            response = render(request, 'vkapi/user-info.html',
                              context={'first_name': visualization.user_info['first_name'],
                                       'last_name': visualization.user_info['last_name'],
                                       'birthday': visualization.user_info['birthday'],
                                       'city': visualization.user_info['city'],
                                       'user_subscriptions': visualization.get_user_subscriptions()})

            if not VkAccount.objects.filter(link=link, creator=request.COOKIES['login']).exists():
                VkAccount(link=link, creator=request.COOKIES['login']).save()

            return response

        except (TypeError, IndexError):
            return render(request, 'vkapi/user-info.html', {'error': True})
    else:
        return redirect('/')
