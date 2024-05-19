"""URL-маршруты приложения vkapi"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_info_view, name='user_info'),
    path('mutual-friends', views.mutual_friends_view, name='mutual_friends'),
    path('activity', views.activity_view, name='activity'),
    path('subscriptions', views.subscriptions_view, name='subscriptions'),
    path('change-theme', views.change_theme, name='vkapi_change_theme'),
    path('toxicity', views.toxicity_view, name='toxicity')
]
