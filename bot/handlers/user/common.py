from http import HTTPStatus

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from httpx import Response

from api_client import ApiResponseClient
from config import (API_ERROR_MESSAGE, CANCEL_MESSAGE, EXIST_ENDPOINT,
                    INSTRUCTIONS_MESSAGE, START_MESSAGE, START_UNREG_MESSAGE,
                    UNKNOWN_MESSAGE)
from keyboards import Buttons, main_markup, registration_markup
from loader import bot, logger
from states import RegistrationState


async def start_command(
    message: types.Message,
    state: FSMContext,
    api: ApiResponseClient,
) -> None:
    """Команды start/help."""
    logger.info(f'USER {message.from_user.id} start command')
    await state.reset_state()
    telegram_id = message.from_user.id
    response: Response = await api.get_data(
        endpoint=EXIST_ENDPOINT.format(telegram_id=telegram_id),
        telegram_id=telegram_id,
    )
    if response.status_code == HTTPStatus.OK:
        await bot.send_message(
            chat_id=telegram_id,
            text=START_MESSAGE,
            reply_markup=main_markup(),
        )
    elif response.status_code == HTTPStatus.NOT_FOUND:
        await bot.send_message(
            chat_id=telegram_id,
            text=START_UNREG_MESSAGE,
            reply_markup=registration_markup(),
        )
        await RegistrationState.start.set()
    else:
        await bot.send_message(
            chat_id=telegram_id,
            text=API_ERROR_MESSAGE,
        )


async def cancel_command(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Отмена операции."""
    logger.info(f'USER {message.from_user.id} cancel command')
    await state.reset_state()
    await bot.send_message(
        chat_id=message.from_user.id,
        text=CANCEL_MESSAGE,
        reply_markup=main_markup(),
    )


async def faq_command(
    message: types.Message,
) -> None:
    """Отправка инструкций."""
    logger.info(f'USER {message.from_user.id} faq command')
    await bot.send_message(
        chat_id=message.from_user.id,
        text=INSTRUCTIONS_MESSAGE,
    )


async def unknown_message(
    message: types.Message,
) -> None:
    """Неизвестная команда."""
    await bot.send_message(
        chat_id=message.from_user.id,
        text=UNKNOWN_MESSAGE,
    )


def register_common_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров в диспетчере."""
    dp.register_message_handler(
        start_command,
        commands=['start', 'help'],
        state='*',
    )
    dp.register_message_handler(
        cancel_command,
        text=Buttons.CANCEL.value,
        state='*',
    )
    dp.register_message_handler(
        faq_command,
        text=Buttons.INSTRUCTIONS.value,
        state=None,
    )
