from http import HTTPStatus

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from api_client import ApiResponseClient
from config import API_ERROR_MESSAGE, NEW_USER_ENDPOINT, SUCCESS_REG_MESSAGE
from keyboards import Buttons, main_markup, registration_markup
from loader import bot, logger
from states import RegistrationState


async def registration(
    message: types.Message,
    state: FSMContext,
    api: ApiResponseClient,
) -> None:
    """Регистрация нового пользователя."""
    logger.info(f'USER {message.from_user.id} registration command')
    telegram_id = message.from_user.id
    data = {
        'telegram_id': telegram_id,
    }
    response = await api.post_data(
        endpoint=NEW_USER_ENDPOINT,
        data=data,
        telegram_id=telegram_id,
    )
    if response.status_code == HTTPStatus.CREATED:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=SUCCESS_REG_MESSAGE,
            reply_markup=main_markup(),
        )
        await state.reset_state()
        logger.info(f'USER {message.from_user.id} create new user')
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=API_ERROR_MESSAGE,
            reply_markup=registration_markup(),
        )
        logger.error(f'USER {message.from_user.id} resive error')


def register_new_user_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров в диспетчере."""
    dp.register_message_handler(
        registration,
        text=Buttons.REG.value,
        state=RegistrationState.start,
    )
