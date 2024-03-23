from django import forms
from .models import User


class UserForm(forms.ModelForm):
    """Форма регистрации пользователя."""

    class Meta:
        model = User
        fields = ['login', 'password']

    login = forms.CharField(widget=forms.TextInput(), label='Логин')
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Подтверждение пароля')


class LoginForm(forms.ModelForm):
    """Форма входа в систему."""

    class Meta:
        model = User
        fields = ['login', 'password']

    login = forms.CharField(widget=forms.TextInput(), label='Логин')
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')
