"""Настройки панели администратора приложения authentication"""

from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('date_joined',)


admin.site.register(User, UserAdmin)
