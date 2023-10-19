from ninja import ModelSchema, Schema

from email_service.models import BoxFilter, EmailBox, EmailService


class EmailDomainOut(ModelSchema):
    """Схема для почтового сервиса."""

    class Config:
        model = EmailService
        model_fields = ['id', 'title']


class EmailDomainList(Schema):
    """Схема для получения списка почтовых сервисов."""

    services: list[EmailDomainOut]


class BoxFilterBase(ModelSchema):
    """Схема для фильтра почтового ящика."""

    class Config:
        model = BoxFilter
        model_fields = ['filter_value', 'filter_name']


class EmailBoxIn(ModelSchema):
    """Схема для регистрации нового почтового ящика."""

    filters: list[BoxFilterBase]

    class Config:
        model = EmailBox
        model_fields = ['email_service', 'email_username', 'email_password']


class EmailBoxOutBase(ModelSchema):
    """Базовая схема для выдачи информации о почтовом ящике."""

    class Config:
        model = EmailBox
        model_fields = ['id', 'email_service', 'email_username', 'is_active']


class EmailBoxOutFull(EmailBoxOutBase):
    """Полная схема для выдачи информации о почтовом ящике."""

    filters: list[BoxFilterBase]

    @classmethod
    def create(
        cls,
        box: EmailBox,
        filters: list[BoxFilter],
    ) -> 'EmailBoxOutFull':
        return cls(
            id=box.id,
            email_service_id=box.email_service.id,
            email_username=box.email_username,
            is_active=box.is_active,
            filters=filters,
        )


class EmailBoxStatusIn(Schema):
    """Схема для изменения статуса почтового ящика."""

    status: bool
