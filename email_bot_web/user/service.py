from infrastructure.error_messages import USER_ALREADY_EXIST
from infrastructure.exceptions import UserAlreadyExist
from infrastructure.repository import Repository
from user.models import BotUser


class ServiceBotUser:
    """Сервисный репозиторий для операций с пользователем."""

    def __init__(self):
        self.repo = Repository()

    async def create_user(self, telegram_id: int) -> tuple[BotUser, bool]:
        """Создать нового пользователя."""
        obj, created = await self.repo.user.create_user(telegram_id)
        if created:
            return obj
        raise UserAlreadyExist(USER_ALREADY_EXIST)

    async def is_user_exist(self, telegram_id: int) -> bool:
        """Проверить наличие пользователя в базе."""
        return await self.repo.user.is_user_exist(telegram_id)

    async def is_user_active(self, telegram_id: int) -> bool:
        """Проверить активность пользователя."""
        return await self.repo.user.is_user_active(telegram_id)
