"""Обработка html-форм приложения authentication"""

from django import forms

from .models import User


class LoginForm(forms.ModelForm):
    """Форма входа в систему."""

    class Meta:
        model = User
        fields = ['login', 'password']

    login = forms.CharField(widget=forms.TextInput(), label='Логин')
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')


class UserForm(LoginForm):
    """Форма регистрации пользователя."""

    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Подтверждение пароля')
