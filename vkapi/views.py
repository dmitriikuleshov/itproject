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
            vk_info = vk.get_info(link)
            vk_friends_info = vk.get_common_connections(link)
            visualization = Visualization(link)
            print("MUSIC", visualization.get_favourite_music())
            visualization.create_activity_graph('vkapi/templates/vkapi/activity-graph.html')

            create_mutual_friends_graph('vkapi/templates/vkapi/mutual-friends-graph.html',
                                        vk_info, vk_friends_info)
            response = render(request, 'vkapi/user-info.html', vk_info)

            if not VkAccount.objects.filter(link=link, creator=request.COOKIES['login']).exists():
                VkAccount(link=link, creator=request.COOKIES['login']).save()

            return response

        except (TypeError, IndexError) as e:
            raise e
            return render(request, 'vkapi/user-info.html', {'error': True})
    else:
        return redirect('/')
