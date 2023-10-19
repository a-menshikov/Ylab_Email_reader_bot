from asgiref.sync import async_to_sync

from django.conf import settings
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest

from user.models import BotUser
from infrastructure.redis_service import redis_client
from infrastructure.repository import Repository

repo = Repository()


@admin.action(description='Удалить выбранных пользователей')
def delete_users(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[BotUser],
) -> None:
    """Удаление выбранных пользователей."""
    for user in queryset:
        redis_keys = async_to_sync(redis_client.get_all_keys)(
            pattern=settings.USER_KEYS_PATTERN.format(
                telegram_id=user.telegram_id,
            ),
        )
        async_to_sync(redis_client.delete_many)(redis_keys)
    queryset.delete()
    messages.success(request, 'Пользователи удалены')


@admin.action(description='Деактивировать выбранных пользователей')
def deactivate_users(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[BotUser],
) -> None:
    """Деактивация выбранных пользователей."""
    queryset.update(is_active=False)
    for user in queryset:
        boxes = async_to_sync(repo.box.get_all_user_boxes)(user.telegram_id)
        for box in boxes:
            box.is_active = False
            box.save()
        redis_keys = async_to_sync(redis_client.get_all_keys)(
            pattern=settings.USER_KEYS_PATTERN.format(
                telegram_id=user.telegram_id,
            ),
        )
        async_to_sync(redis_client.delete_many)(redis_keys)
    messages.success(request, 'Пользователи деактивированы')


@admin.action(description='Активировать выбранных пользователей')
def activate_users(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[BotUser],
) -> None:
    """Активация выбранных пользователей."""
    queryset.update(is_active=True)
    for user in queryset:
        redis_keys = async_to_sync(redis_client.get_all_keys)(
            pattern=settings.USER_KEYS_PATTERN.format(
                telegram_id=user.telegram_id,
            ),
        )
        async_to_sync(redis_client.delete_many)(redis_keys)
    messages.success(request, 'Пользователи активированы')
