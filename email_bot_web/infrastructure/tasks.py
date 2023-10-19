import logging
import os
from io import BytesIO

from asgiref.sync import async_to_sync
from celery import shared_task
from django.conf import settings
from html2image import Html2Image
from PIL import Image

from infrastructure.redis_service import redis_client
from infrastructure.repository import Repository
from infrastructure.sender import send_photo_to_telegram_sync

logger = logging.getLogger('imap')
repo = Repository()


@shared_task(bind=True)
def email_html_to_image(self, html: str) -> bytes:
    """Генерация изображения."""
    logger.info('Generating image.')
    hti = Html2Image(browser='chromium', keep_temp_files=False)
    temp_file_path = 'temp_file.png'
    hti.screenshot(html_str=html, save_as=temp_file_path)
    with open(temp_file_path, 'rb') as f:
        image_bytes = f.read()
    os.remove(temp_file_path)
    logger.info('Image generated.')

    min_width = settings.IMAGE_MIN_WIDTH
    min_height = settings.IMAGE_MIN_HEIGHT
    padding = settings.IMAGE_PADDING

    logger.info('Cropping image.')
    image = Image.open(BytesIO(image_bytes))
    image = image.convert('RGBA')
    width, height = image.size

    for x in range(width):
        for y in range(height):
            r, g, b, a = image.getpixel((x, y))
            if r == 255 and g == 255 and b == 255:
                image.putpixel((x, y), (r, g, b, 0))

    bbox = image.getbbox()
    x_min, y_min, x_max, y_max = bbox
    x_min -= padding
    y_min -= padding
    x_max += padding
    y_max += padding
    cropped_image = image.crop((x_min, y_min, x_max, y_max))

    cropped_width, cropped_height = cropped_image.size

    if cropped_width < min_width:
        left = (cropped_width - min_width) // 2
        right = left + min_width
        cropped_image = cropped_image.crop((left, 0, right, cropped_height))
        cropped_width, cropped_height = cropped_image.size
    if cropped_height < min_height:
        top = (cropped_height - min_height) // 2
        bottom = top + min_height
        cropped_image = cropped_image.crop((0, top, cropped_width, bottom))

    buffer = BytesIO()
    cropped_image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    logger.info('Image ready to send.')
    return image_bytes


@shared_task(bind=True)
def send_image_to_telegram_task(
    self,
    image_bytes: bytes,
    telegram_id: int,
) -> None:
    """Отправка готовой картинки в телеграм."""
    send_photo_to_telegram_sync(image_bytes, telegram_id)


@shared_task()
def listening_status_synchronization():
    """Синхронизация статуса прослушивания почтового
    ящика между базой данных и кэшем."""
    boxes = async_to_sync(repo.box.get_all_boxes)()

    for box in boxes:
        cache_status_key = settings.REDIS_KEY_FORMAT.format(
            telegram_id=box.user_id.telegram_id,
            box_id=box.id,
        )

        if box.is_active:
            expected_status = settings.ACTIVE_VALUE
        else:
            expected_status = settings.NON_ACTIVE_VALUE

        cache_status_value = async_to_sync(redis_client.get)(cache_status_key)

        if cache_status_value is not None:
            if cache_status_value != expected_status:
                async_to_sync(redis_client.set)(
                    cache_status_key,
                    expected_status,
                )
