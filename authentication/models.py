"""Модели базы данных приложения vkapi"""

from django.db import models


class User(models.Model):
    """Модель пользователя в БД."""

    login = models.CharField('Логин', max_length=20)
    password = models.CharField('Пароль', max_length=255, blank=True)
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = verbose_name_plural
        ordering = ['-date_joined']
