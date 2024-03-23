from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    """
    Добавлено для того, чтобы дата регистрации
    отображалась в панели администратора.
    """

    readonly_fields = ('date_joined',)


admin.site.register(User, UserAdmin)
