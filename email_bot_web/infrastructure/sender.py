import logging
from http import HTTPStatus

import httpx
import requests
from django.conf import settings

logger = logging.getLogger('imap')


async def send_photo_to_telegram_async(
    image_bytes: bytes,
    telegram_id: int,
) -> None:
    """Отправка изображения в телеграм асинхронно."""
    data = {
        'chat_id': telegram_id,
    }
    files = {
        'photo': image_bytes,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.TG_API_IMAGE,
            data=data,
            files=files,
        )
    if response.status_code == HTTPStatus.OK:
        logger.info(f'USER {telegram_id}. TG_message sent successfully.')
    else:
        logger.error(f'USER {telegram_id}. TG_message error. {response.text}')


def send_photo_to_telegram_sync(
    image_bytes: bytes,
    telegram_id: int,
) -> None:
    """Отправка изображения в телеграм синхронно."""
    data = {
        'chat_id': telegram_id,
    }
    files = {
        'photo': image_bytes,
    }
    logger.info(f'USER {telegram_id}. Sending image.')
    response = requests.post(
        settings.TG_API_IMAGE,
        data=data,
        files=files,
    )
    if response.status_code == HTTPStatus.OK:
        logger.info(f'USER {telegram_id}. TG_message sent successfully.')
    else:
        logger.error(f'USER {telegram_id}. TG_message error. {response.text}')
