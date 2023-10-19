from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from ninja import Router

from api.v1.schemas import ErrorSchema
from email_service.schemas import (
    EmailBoxIn,
    EmailBoxOutBase,
    EmailBoxOutFull,
    EmailBoxStatusIn,
)
from email_service.service import ServiceEmailBox
from infrastructure.error_messages import USER_DOES_NOT_EXIST
from infrastructure.exceptions import (
    BoxAlreadyExist,
    BoxDoesNotExist,
    DomainDoesNotExist,
    ImapAuthenticationFailed,
    ImapConnectionError,
    ServerUnavailable,
    UserAlreadyExist,
    UserDoesNotExist,
)
from user.schemas import BotUserIn, BotUserOut, UserActiveOut
from user.service import ServiceBotUser

user_router = Router(tags=['Пользователь'])

user_service = ServiceBotUser()
box_service = ServiceEmailBox()


@user_router.post(
    '',
    response={
        HTTPStatus.CREATED: BotUserOut,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
    },
    summary='Новый пользователь',
)
async def user_registration(
    request: HttpRequest,
    data: BotUserIn,
) -> HttpResponse:
    """Регистрация нового пользователя."""
    try:
        user = await user_service.create_user(data.telegram_id)
        return HTTPStatus.CREATED, user
    except UserAlreadyExist as error:
        return HTTPStatus.BAD_REQUEST, ErrorSchema.create(error)


@user_router.get(
    '/{telegram_id}/exist',
    response={HTTPStatus.OK: None, HTTPStatus.NOT_FOUND: ErrorSchema},
    summary='Проверка существования пользователя в базе',
)
async def is_user_exist(
    request: HttpRequest,
    telegram_id: int,
) -> HttpResponse:
    """Проверить наличие пользователя в базе."""
    if await user_service.is_user_exist(telegram_id):
        return
    return HTTPStatus.NOT_FOUND, ErrorSchema(error=USER_DOES_NOT_EXIST)


@user_router.get(
    '/{telegram_id}/active',
    response={HTTPStatus.OK: UserActiveOut, HTTPStatus.NOT_FOUND: ErrorSchema},
    summary='Проверка статуса активности пользователя.',
)
async def is_user_active(
    request: HttpRequest,
    telegram_id: int,
) -> HttpResponse:
    """Проверить активность пользователя."""
    try:
        user_status = await user_service.is_user_active(telegram_id)
        return UserActiveOut(is_active=user_status)
    except UserDoesNotExist as error:
        return HTTPStatus.NOT_FOUND, ErrorSchema.create(error)


@user_router.post(
    '/{telegram_id}/boxes',
    response={
        HTTPStatus.CREATED: EmailBoxOutFull,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
        HTTPStatus.NOT_FOUND: ErrorSchema,
    },
    summary='Новый почтовый ящик пользователя',
)
async def box_registration(
    request: HttpRequest,
    telegram_id: int,
    data: EmailBoxIn,
) -> HttpResponse:
    """Регистрация нового почтового ящика."""
    try:
        box, filters = await box_service.create_box(
            telegram_id=telegram_id,
            data=data,
        )
    except (UserDoesNotExist, DomainDoesNotExist) as error:
        return HTTPStatus.NOT_FOUND, ErrorSchema.create(error)
    except (
        BoxAlreadyExist,
        ImapConnectionError,
        ImapAuthenticationFailed,
        ServerUnavailable,
    ) as error:
        return HTTPStatus.BAD_REQUEST, ErrorSchema.create(error)
    return HTTPStatus.CREATED, EmailBoxOutFull.create(box=box, filters=filters)


@user_router.get(
    '/{telegram_id}/boxes',
    response={
        HTTPStatus.OK: list[EmailBoxOutBase],
        HTTPStatus.NOT_FOUND: ErrorSchema,
    },
    summary='Все почтовые ящики пользователя',
)
async def get_all_user_boxes(
    request: HttpRequest,
    telegram_id: int,
) -> HttpResponse:
    """Получить все почтовые ящики пользователя."""
    try:
        return await box_service.get_all_user_boxes(telegram_id)
    except UserDoesNotExist as error:
        return HTTPStatus.NOT_FOUND, ErrorSchema.create(error)


@user_router.get(
    '/{telegram_id}/boxes/{box_id}',
    response={
        HTTPStatus.OK: EmailBoxOutFull,
        HTTPStatus.NOT_FOUND: ErrorSchema,
    },
    summary='Конкретный почтовый ящик',
)
async def get_box(
    request: HttpRequest,
    telegram_id: int,
    box_id: int,
) -> HttpResponse:
    """Получить почтовый ящик пользователя."""
    try:
        box, filters = await box_service.get_box_with_filters(
            telegram_id,
            box_id,
        )
        return EmailBoxOutFull.create(box=box, filters=filters)
    except (UserDoesNotExist, BoxDoesNotExist) as error:
        return HTTPStatus.NOT_FOUND, ErrorSchema.create(error)


@user_router.patch(
    '/{telegram_id}/boxes/{box_id}/change-status',
    response={
        HTTPStatus.OK: None,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
        HTTPStatus.NOT_FOUND: ErrorSchema,
    },
    summary='Изменить статус ящика для отслеживания',
)
async def change_box_status(
    request: HttpRequest,
    telegram_id: int,
    box_id: int,
    data: EmailBoxStatusIn,
) -> HttpResponse:
    """Изменить статус ящика для отслеживания."""
    try:
        await box_service.change_box_status(telegram_id, box_id, data.status)
    except (UserDoesNotExist, BoxDoesNotExist) as error:
        return HTTPStatus.NOT_FOUND, ErrorSchema.create(error)
    except (
        ImapAuthenticationFailed,
        ImapConnectionError,
        ServerUnavailable,
    ) as error:
        return HTTPStatus.BAD_REQUEST, ErrorSchema.create(error)
