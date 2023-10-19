from django.conf import settings

from email_service.service import ServiceEmailBox
from infrastructure.crypto_service import encryptor
from infrastructure.exceptions import (
    ImapAuthenticationFailed,
    ImapConnectionError,
    ServerUnavailable,
)
from infrastructure.imap_service import IMAPClient, logger
from infrastructure.redis_service import redis_client
from infrastructure.repository import Repository

box_service = ServiceEmailBox()
repo = Repository()


async def on_startup_imap_starter() -> None:
    """Используется для запуска прослушки
    всех активных ящиков при старте сервера."""
    logger.info('RUN on_startup_imap_starter')
    active_boxes = await repo.box.get_all_active_boxes()

    for box in active_boxes:
        if not box.user_id.is_active:
            continue
        try:
            await IMAPClient.check_connection(
                host=box.email_service.address,
                port=box.email_service.port,
                username=box.email_username,
                password=encryptor.decrypt_data(box.email_password),
            )
        except (
            ServerUnavailable,
            ImapConnectionError,
            ImapAuthenticationFailed,
        ):
            continue

        await redis_client.set(
            await redis_client.gen_key(box.user_id.telegram_id, box.id),
            settings.ACTIVE_VALUE,
        )

        await box_service.start_listener(
            host=box.email_service.address,
            port=box.email_service.port,
            username=box.email_username,
            password=encryptor.decrypt_data(box.email_password),
            telegram_id=box.user_id.telegram_id,
            box_id=box.id,
        )
    logger.info('END on_startup_imap_starter')
