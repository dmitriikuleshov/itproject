from django.shortcuts import render, redirect


def index_view(request):
    """
    Высылка главной страницы,
    проверка, аутентифицирован ли пользователь,
    с помощью cookie
    """
    login = ''
    if 'login' in request.COOKIES:
        login = request.COOKIES['login']

    return render(request, 'main/index.html', {'login': login})


def logout_view(request):
    """
    Выход из учётной записи путём
    удаления cookie.
    """
    response = redirect('/')
    response.delete_cookie('login')
    return response
