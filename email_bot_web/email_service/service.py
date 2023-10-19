from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from email_service.models import BoxFilter, EmailBox, EmailService
from email_service.schemas import EmailBoxIn
from infrastructure.crypto_service import encryptor
from infrastructure.error_messages import (
    BOX_ALREADY_EXIST,
    BOX_DOES_NOT_EXIST,
    DOMAIN_DOES_NOT_EXIST,
    USER_DOES_NOT_EXIST,
)
from infrastructure.exceptions import (
    BoxAlreadyExist,
    BoxDoesNotExist,
    DomainDoesNotExist,
    UserDoesNotExist,
)
from infrastructure.imap_service import IMAPClient, IMAPListener
from infrastructure.redis_service import redis_client
from infrastructure.repository import Repository


class ServiceEmailDomain:
    """Сервисный репозиторий для операций с почтовымы доменами."""

    def __init__(self):
        self.repo = Repository()

    async def get_domain_list(self) -> list[EmailService]:
        """Получить все почтовые сервисы."""
        return await self.repo.domain.get_domain_list()


class ServiceEmailBox:
    """Сервисный репозиторий для операций с почтовыми ящиками."""

    def __init__(self):
        self.repo = Repository()
        self.redis = redis_client

    async def start_listener(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        telegram_id: int,
        box_id: int,
    ) -> None:
        """Запустить слушатель."""
        listener = IMAPListener(
            host=host,
            port=port,
            username=username,
            password=password,
            telegram_id=telegram_id,
            box_id=box_id,
        )
        await listener.start()

    async def create_box(
        self,
        telegram_id: int,
        data: EmailBoxIn,
    ) -> tuple[EmailBox, list[BoxFilter]]:
        """Создать новый почтовый ящик."""
        try:
            email_domain = await self.repo.domain.get_domain_by_id(
                data.email_service,
            )
        except ObjectDoesNotExist:
            raise DomainDoesNotExist(DOMAIN_DOES_NOT_EXIST)
        try:
            user = await self.repo.user.get_user(telegram_id)
        except ObjectDoesNotExist:
            raise UserDoesNotExist(USER_DOES_NOT_EXIST)
        await IMAPClient.check_connection(
            host=email_domain.address,
            port=email_domain.port,
            username=data.email_username,
            password=encryptor.decrypt_data(data.email_password),
        )
        box_object, created = await self.repo.box.create_box(
            user=user,
            email_domain=email_domain,
            data=data,
        )
        if not created:
            raise BoxAlreadyExist(BOX_ALREADY_EXIST)
        filters_list = await self.repo.filter.create_filter_by_list(
            telegram_id=telegram_id,
            box_id=box_object.id,
            box_object=box_object,
            filter_list=data.filters,
        )
        await self.redis.set(
            await self.redis.gen_key(telegram_id, box_object.id),
            settings.ACTIVE_VALUE,
        )
        await self.start_listener(
            host=email_domain.address,
            port=email_domain.port,
            username=box_object.email_username,
            password=encryptor.decrypt_data(box_object.email_password),
            telegram_id=telegram_id,
            box_id=box_object.id,
        )
        return box_object, filters_list

    async def get_all_user_boxes(self, telegram_id: int) -> list[EmailBox]:
        """Получить все почтовые ящики пользователя."""
        if not await self.repo.user.is_user_exist(telegram_id):
            raise UserDoesNotExist(USER_DOES_NOT_EXIST)
        return await self.repo.box.get_all_user_boxes(telegram_id)

    async def get_box_with_filters(
        self,
        telegram_id: int,
        box_id: int,
    ) -> tuple[EmailBox, list[BoxFilter]]:
        """Получить почтовый ящик по идентификатору."""
        if not await self.repo.user.is_user_exist(telegram_id):
            raise UserDoesNotExist(USER_DOES_NOT_EXIST)
        try:
            return await self.repo.box.get_box_with_filters(
                telegram_id=telegram_id,
                box_id=box_id,
            )
        except ObjectDoesNotExist:
            raise BoxDoesNotExist(BOX_DOES_NOT_EXIST)

    async def change_box_status(
        self,
        telegram_id: int,
        box_id: int,
        status: bool,
    ) -> None:
        """Установить статус активности почтового ящика."""
        if status:
            await self.activate_box(telegram_id, box_id)
        else:
            await self.deactivate_box(telegram_id, box_id)

    async def activate_box(self, telegram_id: int, box_id: int) -> None:
        """Активировать почтовый ящик."""
        if not await self.repo.user.is_user_exist(telegram_id):
            raise UserDoesNotExist(USER_DOES_NOT_EXIST)
        try:
            box_object = await self.repo.box.get_box_by_id(
                box_id=box_id,
                telegram_id=telegram_id,
            )
        except ObjectDoesNotExist:
            raise BoxDoesNotExist(BOX_DOES_NOT_EXIST)
        await IMAPClient.check_connection(
            host=box_object.email_service.address,
            port=box_object.email_service.port,
            username=box_object.email_username,
            password=encryptor.decrypt_data(box_object.email_password),
        )
        await self.repo.box.change_box_status(
            box_id=box_id,
            status=True,
            telegram_id=telegram_id,
        )
        await self.redis.set(
            await self.redis.gen_key(telegram_id, box_id),
            settings.ACTIVE_VALUE,
        )
        await self.start_listener(
            host=box_object.email_service.address,
            port=box_object.email_service.port,
            username=box_object.email_username,
            password=encryptor.decrypt_data(box_object.email_password),
            telegram_id=telegram_id,
            box_id=box_id,
        )

    async def deactivate_box(self, telegram_id: int, box_id: int) -> None:
        """Дективировать почтовый ящик."""
        if not await self.repo.user.is_user_exist(telegram_id):
            raise UserDoesNotExist(USER_DOES_NOT_EXIST)
        await self.repo.box.change_box_status(
            box_id=box_id,
            status=False,
            telegram_id=telegram_id,
        )
        await self.redis.set(
            await self.redis.gen_key(telegram_id, box_id),
            settings.NON_ACTIVE_VALUE,
        )
