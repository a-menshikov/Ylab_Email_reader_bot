from django.conf import settings

from email_service.models import BoxFilter, EmailBox, EmailService
from email_service.schemas import BoxFilterBase, EmailBoxIn
from infrastructure.redis_service import redis_client
from user.models import BotUser


class RepositoryEmailDomain:
    """Репозиторий CRUD операций модели почтового сервиса."""

    def __init__(self):
        self.model = EmailService

    @redis_client.cache_result(key_format=settings.ALL_DOMAINS_KEY)
    async def get_domain_list(self) -> list[EmailService]:
        """Получить все почтовые сервисы."""
        return [domain async for domain in self.model.objects.all()]

    @redis_client.cache_result(key_format=settings.DOMAIN_KEY)
    async def get_domain_by_id(self, id: int) -> EmailService:
        """Получить почтовый сервис по идентификатору."""
        return await self.model.objects.aget(id=id)


class RepositoryBoxFilter:
    """Репозиторий CRUD операций модели фильтра почтового ящика."""

    def __init__(self):
        self.model = BoxFilter

    @redis_client.delete_cache(
        key_format_list=[
            settings.FILTERS_VALUE_KEY,
            settings.BOX_FULL_KEY,
            settings.USER_BOXES_KEY,
        ],
    )
    async def create_filter(
        self,
        telegram_id: int,
        box_id: int,
        box_object: EmailBox,
        filter_value: str,
        filter_name: str,
    ) -> tuple[BoxFilter, bool]:
        """Создать новый фильтр ящика."""
        return await self.model.objects.aget_or_create(
            box_id=box_object,
            filter_value=filter_value,
            filter_name=filter_name,
        )

    @redis_client.delete_cache(
        key_format_list=[
            settings.FILTERS_VALUE_KEY,
            settings.BOX_FULL_KEY,
            settings.USER_BOXES_KEY,
        ],
    )
    async def create_filter_by_list(
        self,
        telegram_id: int,
        box_id: int,
        box_object: EmailBox,
        filter_list: list[BoxFilterBase],
    ) -> list[BoxFilter]:
        """Создать фильтры ящика из списка."""
        obj_to_create = []
        for filter in filter_list:
            obj_to_create.append(self.model(
                box_id=box_object,
                filter_value=filter.filter_value,
                filter_name=filter.filter_name
            ))
        return await self.model.objects.abulk_create(obj_to_create)

    @redis_client.cache_result(key_format=settings.FILTERS_VALUE_KEY)
    async def get_box_filters_value_list(
        self,
        box_id: int,
        telegram_id: int,
    ) -> list[tuple[str]]:
        """Получить список значений фильтров почтового ящика."""
        return [(f['filter_value'], f['filter_name'])  # type: ignore
                async for f in self.model.objects.filter(box_id=box_id)
                .values('filter_value', 'filter_name').all()]


class RepositoryEmailBox:
    """Репозиторий CRUD операций модели почтового ящика."""

    def __init__(self):
        self.model = EmailBox

    async def create_box(
        self,
        user: BotUser,
        email_domain: EmailService,
        data: EmailBoxIn,
    ) -> tuple[EmailBox, bool]:
        """Создать новый почтовый ящик."""
        return await self.model.objects.aget_or_create(
            user_id=user,
            email_service=email_domain,
            email_username=data.email_username,
            email_password=data.email_password,
        )

    @redis_client.cache_result(key_format=settings.USER_BOXES_KEY)
    async def get_all_user_boxes(self, telegram_id: int) -> list[EmailBox]:
        """Получить все почтовые ящики пользователя."""
        query = self.model.objects.filter(user_id=telegram_id)
        return [box async for box in query]

    async def get_all_boxes(self) -> list[EmailBox]:
        """Получить все зарегистрированные почтовые ящики."""
        query = self.model.objects.all()
        return [box async for box in query]

    @redis_client.cache_result(key_format=settings.BOX_FULL_KEY)
    async def get_box_with_filters(
        self,
        box_id: int,
        telegram_id: int,
    ) -> tuple[EmailBox, list[BoxFilter]]:
        """Получить почтовый ящик cо связанными фильтрами."""
        box = await self.model.objects.select_related(
            'user_id',
            'email_service',
        ).prefetch_related('filters').aget(id=box_id, user_id=telegram_id)
        filters = [f async for f in box.filters.all()]
        return box, filters

    @redis_client.cache_result(key_format=settings.BOX_SIMPLE_KEY)
    async def get_box_by_id(self, box_id: int, telegram_id: int) -> EmailBox:
        """Получить почтовый ящик по идентификатору."""
        return await self.model.objects.select_related(
            'email_service',
        ).aget(id=box_id)

    @redis_client.delete_cache(
        key_format_list=[
            settings.BOX_FULL_KEY,
            settings.BOX_SIMPLE_KEY,
            settings.USER_BOXES_KEY,
        ],
    )
    async def change_box_status(
        self,
        box_id: int,
        status: bool,
        telegram_id: int,
    ) -> None:
        """Установить статус активности почтового ящика."""
        await self.model.objects.filter(id=box_id).aupdate(is_active=status)

    async def get_all_active_boxes(self) -> list[EmailBox]:
        """Получить все активные почтовые ящики со связанными объектами
        пользователя и почтового домена."""
        return [box async for box in self.model.objects
                .select_related('user_id', 'email_service')
                .filter(is_active=True).all()]
