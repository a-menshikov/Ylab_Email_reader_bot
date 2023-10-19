from django.conf import settings

from infrastructure.error_messages import USER_DOES_NOT_EXIST
from infrastructure.exceptions import UserDoesNotExist
from infrastructure.redis_service import redis_client
from user.models import BotUser


class RepositoryBotUser:
    """Репозиторий CRUD операций модели пользователя."""

    def __init__(self):
        self.model = BotUser

    @redis_client.delete_cache(key_format_list=[settings.USER_EXISTS_KEY])
    async def create_user(self, telegram_id: int) -> tuple[BotUser, bool]:
        """Создать пользователя."""
        return await self.model.objects.aget_or_create(
            telegram_id=telegram_id
        )

    @redis_client.cache_result(key_format=settings.USER_EXISTS_KEY)
    async def is_user_exist(self, telegram_id: int) -> bool:
        """Проверить наличие пользователя в базе."""
        return await self.model.objects.filter(
            telegram_id=telegram_id).aexists()

    @redis_client.cache_result(key_format=settings.USER_IS_ACTIVE_KEY)
    async def is_user_active(self, telegram_id: int) -> bool:
        """Проверить активность пользователя."""
        user = await self.model.objects.filter(
            telegram_id=telegram_id).afirst()
        if not user:
            raise UserDoesNotExist(USER_DOES_NOT_EXIST)
        return user.is_active

    @redis_client.cache_result(key_format=settings.USER_KEY)
    async def get_user(self, telegram_id: int) -> BotUser:
        """Получить пользователя."""
        return await self.model.objects.aget(telegram_id=telegram_id)
