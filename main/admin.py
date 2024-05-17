"""Настройки панели администратора приложения main"""

from django.contrib import admin

from .models import VkAccount


class VkAccountAdmin(admin.ModelAdmin):
    readonly_fields = ('date_of_first_request',)


admin.site.register(VkAccount, VkAccountAdmin)
