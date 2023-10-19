from django.contrib import admin
from django.db.models import Count
from django.http import HttpRequest

from email_service.admin_actions import (
    activate_boxes,
    deactivate_boxes,
    delete_domain_cache,
    delete_domains,
    delete_boxes,
    delete_filters,
)
from email_service.models import BoxFilter, EmailBox, EmailService


@admin.register(EmailBox)
class BoxAdmin(admin.ModelAdmin):
    """Админ-панель модели почтового ящика."""

    fields = ('user_id', 'email_service', 'email_username', 'is_active')
    readonly_fields = (
        'user_id',
        'email_service',
        'email_username',
        'is_active',
    )
    list_display = (
        'id',
        'user_id',
        'email_service',
        'email_username',
        'is_active',
        'filter_count',
    )
    list_filter = ('email_service', 'is_active', 'user_id')
    search_fields = ('email_username',)
    actions = (delete_boxes, activate_boxes, deactivate_boxes)
    ordering = ('id',)
    search_help_text = ('Поиск по имени пользователя')
    list_per_page = 50

    def get_queryset(self, request: HttpRequest) -> list[EmailBox]:
        return EmailBox.objects.all().annotate(filter_count=Count('filters'))

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    @admin.display(description='Фильтры')
    def filter_count(self, obj: EmailBox) -> int:
        """Вывод количества фильтров ящика."""
        return obj.filter_count


@admin.register(EmailService)
class EmailServiceAdmin(admin.ModelAdmin):
    """Админ-панель модели почтового сервиса."""

    list_display = ('id', 'title', 'slug', 'address', 'port')
    list_editable = ('slug', 'address', 'port', 'title')
    ordering = ('id',)
    list_per_page = 50
    actions = (delete_domain_cache, delete_domains)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(BoxFilter)
class FilterAdmin(admin.ModelAdmin):
    """Админ-панель модели фильтра почтового ящика."""

    list_display = ('id', 'box_id', 'filter_value', 'filter_name')
    readonly_fields = ('box_id', 'filter_value', 'filter_name')
    search_fields = ('filter_value',)
    actions = (delete_filters,)
    ordering = ('id',)
    search_help_text = ('Поиск по значению фильтра')
    list_per_page = 50

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False
