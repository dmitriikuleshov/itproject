from django.db import models


class VkAccount(models.Model):
    """Модель записи ранее запрошенных аккаунтов в БД"""

    creator = models.CharField('Автор запроса', max_length=20, default='none')
    link = models.CharField('Аккаунт', max_length=200)
    date_of_first_request = models.DateField('Дата добавления', auto_now_add=True)

    def __str__(self):
        return self.link

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'
        db_table = verbose_name_plural
        ordering = ['-date_of_first_request']
