"""URL-маршруты приложения main"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('logout', views.logout_view, name='logout'),
    path('change_theme', views.change_theme, name='change_theme')
]
