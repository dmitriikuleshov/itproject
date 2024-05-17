"""Обработка страниц приложения authentication"""

from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.http import HttpRequest

from .forms import UserForm, LoginForm
from .models import User


def reg_view(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """
    Отправка страницы регистрации, проверка
    нового пользователя на существование и
    корректность пароля, процедура регистрации,
    установка cookie.

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponse | HttpResponseRedirect
        Страница регистрации или перенаправление на главную

    """
    if 'theme' not in request.COOKIES:
        request.COOKIES['theme'] = 'light'

    user_form = UserForm()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            if not User.objects.filter(login=form.cleaned_data['login']).exists():
                if form.cleaned_data['confirm_password'] == form.cleaned_data['password']:
                    user = form.save(commit=False)
                    user.password = make_password(form.cleaned_data['password'])
                    user.save()
                    response = redirect('/')
                    response.set_cookie('login', form.cleaned_data['login'])
                    return response
                else:
                    error = 'Ошибка подтверждения пароля! Попробуйте снова.'
            else:
                error = 'Ошибка! Пользователь с указанным логином уже существует.'
        else:
            error = 'Ошибка! Поля заполнены некорректно.'

        return render(
            request,
            'authentication/registration.html',
            {
                'error': error,
                'user_form': user_form,
                'theme': request.COOKIES['theme']
            }
        )

    return render(
        request,
        'authentication/registration.html',
        {
            'user_form': user_form,
            'theme': request.COOKIES['theme']
        }
    )


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Вход в систему, проверка существования пользователя
    и корректности пароля, установка cookie.

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponse
        Страница входа в систему

    """
    login_form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            if User.objects.filter(login=login).exists():
                user = User.objects.get(login=login)
                if check_password(form.cleaned_data['password'], user.password):
                    response = redirect('/')
                    response.set_cookie('login', login)
                    return response
                else:
                    error = 'Введён некорректный пароль.'
            else:
                error = 'Пользователь не найден.'
        else:
            error = 'Ошибка! Поля заполнены некорректно.'

        if 'theme' not in request.COOKIES:
            request.COOKIES['theme'] = 'light'

        return render(
            request,
            'authentication/login.html',
            {
                'error': error,
                'login_form': login_form,
                'theme': request.COOKIES['theme']
            }
        )

    return render(
        request,
        'authentication/login.html',
        {
            'login_form': login_form,
            'theme': request.COOKIES['theme']
        }
    )


def change_theme(request: HttpRequest) -> HttpResponseRedirect:
    """
    Установка темы страницы с помощью cookie

    Parameters
    ----------
    request: HttpRequest
        Объект HTTP-запроса

    Returns
    -------
    HttpResponseRedirect
        Перенаправление на страницы аутентификации

    """
    if request.GET.get('page') == 'login':
        response = redirect('/auth/login')
    else:
        response = redirect('/auth')

    if 'theme' not in request.COOKIES:
        request.COOKIES['theme'] = 'light'
    if request.COOKIES['theme'] == 'dark':
        response.set_cookie('theme', 'light')
    elif request.COOKIES['theme'] == 'light':
        response.set_cookie('theme', 'dark')

    return response
