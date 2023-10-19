from aiogram.dispatcher.handler import CancelHandler
from httpx import AsyncClient, ConnectError, Response, TimeoutException

from config import API_ERROR_MESSAGE
from loader import bot, logger


class ApiResponseClient:
    """Клиент для работы с API."""

    def __init__(self, api_url: str | None):
        self.api_url = api_url
        self.client: AsyncClient = AsyncClient()

    async def get_data(self, endpoint: str, telegram_id: int) -> Response:
        """GET запрос к API."""
        url = f'{self.api_url}/{endpoint}'
        try:
            response = await self.client.get(url)
            return response
        except (TimeoutException, ConnectError) as error:
            await bot.send_message(
                chat_id=telegram_id,
                text=API_ERROR_MESSAGE,
            )
            logger.error(f'API ERROR: {type(error)}')
            raise CancelHandler()

    async def post_data(
        self,
        endpoint: str,
        data: dict[str, str | int | bool | list[dict[str, str]]],
        telegram_id: int,
    ) -> Response:
        """POST запрос к API."""
        url = f'{self.api_url}/{endpoint}'
        try:
            response = await self.client.post(url, json=data)
            return response
        except (TimeoutException, ConnectError) as error:
            await bot.send_message(
                chat_id=telegram_id,
                text=API_ERROR_MESSAGE,
            )
            logger.error(f'API ERROR: {type(error)}')
            raise CancelHandler()

    async def patch_data(
        self,
        endpoint: str,
        data: dict[str, bool],
        telegram_id: int,
    ) -> Response:
        """PATCH запрос к API."""
        url = f'{self.api_url}/{endpoint}'
        try:
            response = await self.client.patch(url, json=data)
            return response
        except (TimeoutException, ConnectError) as error:
            await bot.send_message(
                chat_id=telegram_id,
                text=API_ERROR_MESSAGE,
            )
            logger.error(f'API ERROR: {type(error)}')
            raise CancelHandler()
