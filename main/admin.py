from django.contrib import admin

from .models import VkAccount


class VkAccountAdmin(admin.ModelAdmin):
    """
    Добавлено для того, чтобы дата первого запроса
    отображалась в панели администратора.
    """

    readonly_fields = ('date_of_first_request',)


admin.site.register(VkAccount, VkAccountAdmin)
