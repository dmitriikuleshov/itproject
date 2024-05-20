"""URL-маршруты приложения authentication"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.reg_view, name='registration'),
    path('login', views.login_view, name='login'),
    path('change-theme', views.change_theme, name='login_change_theme')
]
