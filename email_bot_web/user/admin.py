from django.contrib import admin
from django.db.models import Count
from django.http import HttpRequest

from user.admin_actions import activate_users, deactivate_users, delete_users
from user.models import BotUser


@admin.register(BotUser)
class UserAdmin(admin.ModelAdmin):
    """Админ-панель модели User."""

    fields = ('telegram_id', 'is_active')
    readonly_fields = ('telegram_id', 'is_active')
    list_display = ('telegram_id', 'is_active', 'box_count')
    list_filter = ('is_active',)
    actions = (delete_users, activate_users, deactivate_users)
    search_fields = ('telegram_id',)
    search_help_text = ('Поиск по телеграм ID')
    list_per_page = 50

    def get_queryset(self, request: HttpRequest) -> list[BotUser]:
        return BotUser.objects.all().annotate(box_count=Count('boxes'))

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    @admin.display(description='Ящики')
    def box_count(self, obj: BotUser) -> int:
        """Вывод количества ящков пользователя."""
        return obj.box_count
