import json
from http import HTTPStatus

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import (BaseMiddleware,
                                            LifetimeControllerMiddleware)

from api_client import ApiResponseClient
from config import ACTIVE_ENDPOINT, API_URL, BAN_MESSAGE


class ApiMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ['error', 'update']

    async def pre_process(self, obj, data, *args):
        api_service = ApiResponseClient(API_URL)
        data['api'] = api_service


class BanMiddleware(BaseMiddleware):
    """Мидлвар для проверки бана пользователя."""

    async def on_process_message(
        self,
        message: types.Message,
        data: dict,
    ) -> None:
        """Проверка бана пользователя."""
        api_client = data['api']
        response = await api_client.get_data(
            endpoint=ACTIVE_ENDPOINT.format(telegram_id=message.from_user.id),
            telegram_id=message.from_user.id,
        )

        if response.status_code == HTTPStatus.OK \
                and not json.loads(response.text)['is_active']:
            await message.reply(
                text=BAN_MESSAGE,
            )
            raise CancelHandler()
