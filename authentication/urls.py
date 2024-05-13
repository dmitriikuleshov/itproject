"""URL-маршруты приложения authentication"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.auth_view, name='authentication'),
    path('login', views.login_view, name='login')
]
