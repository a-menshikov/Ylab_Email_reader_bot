from ninja import ModelSchema, Schema

from user.models import BotUser


class BotUserIn(ModelSchema):
    """Схема для регистрации нового пользователя."""

    class Config:
        model = BotUser
        model_fields = ['telegram_id']


class BotUserOut(ModelSchema):
    """Схема для получения информации о пользователе."""

    class Config:
        model = BotUser
        model_fields = ['telegram_id', 'is_active']


class UserActiveOut(Schema):
    """Схема для получения статуса активности пользователя."""

    is_active: bool
