"""Обработка html-форм приложения authentication"""

from django import forms

from .models import User


class LoginForm(forms.ModelForm):
    """Форма входа в систему."""

    class Meta:
        model = User
        fields = ['login', 'password']

    login = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'text-field w-input',
        'maxlength': '256',
        'name': 'login_data',
        'data-name': 'login_data',
        'type': 'text',
        'id': 'login_data-2',
        'required': ''
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'text-field-2 w-input',
        'maxlength': '256',
        'name': 'password_data',
        'data-name': 'password_data',
        'type': 'password',
        'id': 'password_data-2',
        'required': ''
    }))


class UserForm(LoginForm):
    """Форма регистрации пользователя."""

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'text-field-2 w-input',
        'maxlength': '256',
        'name': 'password_data-3',
        'data-name': 'Password Data 3',
        'placeholder': '',
        'type': 'password',
        'id': 'password_data-3',
        'required': ''
    }))
