from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from .forms import UserForm, LoginForm
from .models import User


def auth_view(request):
    """
    Отправка страницы регистрации,
    проверка нового пользователя на существование
    и корректность пароля, процедура регистрации,
    установка cookie.
    """
    user_form = UserForm()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            if not User.objects.filter(login=form.cleaned_data['login']).exists():
                if form.cleaned_data['confirm_password'] == form.cleaned_data['password']:
                    user = form.save(commit=False)
                    user.password = make_password(form.cleaned_data['password'])
                    user.save()
                    response = render(request, 'authentication/successfully.html')
                    response.set_cookie('login', form.cleaned_data['login'])
                    return response
                else:
                    error = 'Ошибка подтверждения пароля! Попробуйте снова.'
            else:
                error = 'Ошибка! Пользователь с указанным логином уже существует.'
        else:
            error = 'Ошибка! Поля заполнены некорректно.'

        return render(request, 'authentication/authentication.html',
                      {'error': error, 'user_form': user_form})

    return render(request, 'authentication/authentication.html', {'user_form': user_form})


def login_view(request):
    """
    Вход в систему, проверка существования пользователя
    и корректности пароля, установка cookie.
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

        return render(request, 'authentication/login.html',
                      {'error': error, 'login_form': login_form})

    return render(request, 'authentication/login.html', {'login_form': login_form})
