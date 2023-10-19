from asgiref.sync import async_to_sync

from django.conf import settings
from django.contrib import admin, messages
from django.db.models import ProtectedError, QuerySet
from django.http import HttpRequest

from email_service.models import BoxFilter, EmailBox, EmailService
from email_service.service import ServiceEmailBox
from infrastructure.redis_service import redis_client

box_service = ServiceEmailBox()


@admin.action(description='Очистить кэш')
def delete_domain_cache(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[EmailService],
) -> None:
    """Удаление кэша связанного с доменом."""
    for domain in queryset:
        key = settings.DOMAIN_KEY.format(id=domain.id)
        async_to_sync(redis_client.delete)(key)
    async_to_sync(redis_client.delete)(settings.ALL_DOMAINS_KEY)


@admin.action(description='Удалить выбранные сервисы')
def delete_domains(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[EmailService],
) -> None:
    """Удаление выбранных доменов."""
    for domain in queryset:
        key = settings.DOMAIN_KEY.format(id=domain.id)
        async_to_sync(redis_client.delete)(key)
        try:
            domain.delete()
        except ProtectedError:
            message = (
                'Невозможно удалить почтовый сервис пока есть'
                ' связанные с ним почтовые ящики.'
            )
            messages.error(request, message)
    async_to_sync(redis_client.delete)(settings.ALL_DOMAINS_KEY)


@admin.action(description='Удалить выбранные ящики')
def delete_boxes(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[EmailBox],
) -> None:
    """Удаление выбранных ящиков."""
    for box in queryset:
        redis_keys = [
            settings.USER_BOXES_KEY.format(
                telegram_id=box.user_id.telegram_id,
            ),
            settings.BOX_FULL_KEY.format(
                telegram_id=box.user_id.telegram_id,
                box_id=box.id,
            ),
            settings.BOX_SIMPLE_KEY.format(
                telegram_id=box.user_id.telegram_id,
                box_id=box.id,
            ),
            settings.FILTERS_VALUE_KEY.format(
                telegram_id=box.user_id.telegram_id,
                box_id=box.id,
            ),
            settings.REDIS_KEY_FORMAT.format(
                telegram_id=box.user_id.telegram_id,
                box_id=box.id,
            )
        ]
        async_to_sync(redis_client.delete_many)(redis_keys)
    queryset.delete()
    messages.success(request, 'Ящики удалены')


@admin.action(description='Удалить выбранные фильтры')
def delete_filters(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[BoxFilter],
) -> None:
    """Удаление выбранных фильтров."""
    for filter in queryset:
        redis_keys = [
            settings.FILTERS_VALUE_KEY.format(
                telegram_id=filter.box_id.user_id.telegram_id,
                box_id=filter.box_id.id,
            ),
            settings.BOX_FULL_KEY.format(
                telegram_id=filter.box_id.user_id.telegram_id,
                box_id=filter.box_id.id,
            ),
        ]
        async_to_sync(redis_client.delete_many)(redis_keys)
    queryset.delete()
    messages.success(request, 'Фильтры удалены')


@admin.action(description='Деактивировать выбранные ящики')
def deactivate_boxes(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[EmailBox],
) -> None:
    """Деактивация выбранных ящиков."""
    for box in queryset:
        async_to_sync(box_service.deactivate_box)(
            telegram_id=box.user_id.telegram_id,
            box_id=box.id,
        )
    messages.success(request, 'Ящики деактивированы')


@admin.action(description='Активировать выбранные ящики')
def activate_boxes(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[EmailBox],
) -> None:
    """Активация выбранных ящиков."""
    for box in queryset:
        async_to_sync(box_service.activate_box)(
            telegram_id=box.user_id.telegram_id,
            box_id=box.id,
        )
    messages.success(request, 'Ящики активированы')
