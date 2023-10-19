import json
from http import HTTPStatus

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from api_client import ApiResponseClient
from config import (ALL_DOMAINS_ENDPOINT, ANOTHER_FILTER_MESSAGE,
                    API_ERROR_MESSAGE, CHOOSE_DOMAIN_MESSAGE,
                    ENTER_FILTERS_MESSAGE, ENTER_PASSWORD_MESSAGE,
                    ENTER_USERNAME_MESSAGE, ERROR_ALIAS_MESSAGE,
                    ERROR_DOMAIN_MESSAGE, ERROR_EMAIL_ENTER_MESSAGE, NEED_ONE,
                    NEW_BOX_ENDPOINT, PASSWORD_ACCEPTED_MESSAGE,
                    SUCCESS_NEW_BOX_MESSAGE)
from crypto.crypto_service import encryptor
from handlers.user.utils import approve_message
from handlers.user.validators import validate_email, validate_filter_alias
from keyboards import (Buttons, approve_markup, cancel_markup, domains_markup,
                       filter_loop_markup, main_markup)
from loader import bot, logger
from states import NewBoxState


async def new_box(
    message: types.Message,
    state: FSMContext,
    api: ApiResponseClient,
) -> None:
    """Добавление нового ящика."""
    logger.info(f'USER {message.from_user.id} new box command')
    domains = await api.get_data(
        endpoint=ALL_DOMAINS_ENDPOINT,
        telegram_id=message.from_user.id,
    )
    if domains.status_code != HTTPStatus.OK:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=API_ERROR_MESSAGE,
            reply_markup=main_markup(),
        )
        logger.error(f'USER {message.from_user.id} resive error')
    else:
        domains = json.loads(domains.text)['services']
        domains_titles = [domain['title'] for domain in domains]
        await NewBoxState.domain.set()
        await state.update_data(
            domains=domains,
            domains_titles=domains_titles,
        )
        await bot.send_message(
            chat_id=message.from_user.id,
            text=CHOOSE_DOMAIN_MESSAGE,
            reply_markup=domains_markup(domains_titles),
        )
        logger.info(f'USER {message.from_user.id} get domain list')


async def add_domain(message: types.Message, state: FSMContext) -> None:
    """Добавление домена."""
    logger.info(f'USER {message.from_user.id} add domain command')
    data = await state.get_data()
    domains = data['domains']
    domains_titles = data['domains_titles']
    domain_id: int = 0
    for domain in domains:
        if domain['title'] == message.text:
            domain_id = domain['id']
            break
    if domain_id:
        await state.update_data(
            domain_id=domain_id,
            prev_state=NewBoxState.domain,
        )
        await NewBoxState.username.set()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ENTER_USERNAME_MESSAGE,
            reply_markup=cancel_markup(),
        )
        logger.info(f'USER {message.from_user.id} get enter username')
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ERROR_DOMAIN_MESSAGE,
            reply_markup=domains_markup(domains_titles),
        )
        logger.error(f'USER {message.from_user.id} resive choose domain error')


async def add_username(message: types.Message, state: FSMContext) -> None:
    """Добавление адреса ящика."""
    logger.info(f'USER {message.from_user.id} add username command')
    text = message.text.strip()
    if await validate_email(text):
        await state.update_data(
            username=text,
            prev_state=NewBoxState.username,
        )
        await NewBoxState.password.set()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ENTER_PASSWORD_MESSAGE,
            reply_markup=cancel_markup(),
        )
        logger.info(f'USER {message.from_user.id} get enter password')
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ERROR_EMAIL_ENTER_MESSAGE,
            reply_markup=cancel_markup(),
        )
        logger.info(f'USER {message.from_user.id} resive validate error')


async def add_password(message: types.Message, state: FSMContext) -> None:
    """Добавление пароля ящика."""
    logger.info(f'USER {message.from_user.id} add password command')
    text = message.text.strip()
    crypted_password = encryptor.encrypt_data(text)
    await bot.delete_message(message.from_user.id, message.message_id)
    await state.update_data(
        password=crypted_password,
        prev_state=NewBoxState.password,
    )
    await NewBoxState.filters.set()
    await bot.send_message(
        chat_id=message.from_user.id,
        text=PASSWORD_ACCEPTED_MESSAGE + ENTER_FILTERS_MESSAGE,
        reply_markup=cancel_markup(),
    )
    logger.info(f'USER {message.from_user.id} get enter filters')


async def add_filter(message: types.Message, state: FSMContext) -> None:
    """Добавление фильтров ящика."""
    logger.info(f'USER {message.from_user.id} add filter command')
    text = message.text.strip().split(maxsplit=1)

    filter = text[0]
    if not await validate_email(filter):
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ERROR_EMAIL_ENTER_MESSAGE,
            reply_markup=cancel_markup(),
        )
        logger.info(f'USER {message.from_user.id} resive validate error')
        return

    if len(text) > 1:
        alias = text[1]
        if not await validate_filter_alias(alias):
            await bot.send_message(
                chat_id=message.from_user.id,
                text=ERROR_ALIAS_MESSAGE,
                reply_markup=cancel_markup(),
            )
            logger.info(f'USER {message.from_user.id} resive validate error')
            return
    else:
        alias = ''

    data = await state.get_data()
    data_filters = data.get('filters', [])
    current_filter = {
        'filter_value': filter,
        'filter_name': alias,
    }
    data_filters.append(current_filter)
    await state.update_data(
        filters=data_filters,
        prev_state=NewBoxState.filters,
    )
    await NewBoxState.filter_loop.set()
    await bot.send_message(
        chat_id=message.from_user.id,
        text=ANOTHER_FILTER_MESSAGE,
        reply_markup=filter_loop_markup(),
    )
    logger.info(f'USER {message.from_user.id} get filter_loop step')


async def filter_loop(message: types.Message, state: FSMContext) -> None:
    """Выбор после успешного добавления фильтра."""
    logger.info(f'USER {message.from_user.id} filter_loop command')
    if message.text == Buttons.ADD_FILTER.value:
        await state.update_data(prev_state=NewBoxState.password)
        await NewBoxState.filters.set()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ENTER_FILTERS_MESSAGE,
            reply_markup=cancel_markup(),
        )
        logger.info(f'USER {message.from_user.id} choose another filter step')
    elif message.text == Buttons.END.value:
        await state.update_data(prev_state=NewBoxState.filter_loop)
        await NewBoxState.approve.set()
        data = await state.get_data()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=await approve_message(data),
            reply_markup=approve_markup(),
        )
        logger.info(f'USER {message.from_user.id} choose approve step')


async def approve_and_create_new_box(
    message: types.Message,
    state: FSMContext,
    api: ApiResponseClient,
) -> None:
    """Подтверждение добавления ящика."""
    logger.info(f'USER {message.from_user.id} approve_and_create command')
    data = await state.get_data()
    new_box = {
        'email_service_id': data['domain_id'],
        'email_username': data['username'],
        'email_password': data['password'].decode(),
        'filters': data['filters'],
    }
    response = await api.post_data(
        endpoint=NEW_BOX_ENDPOINT.format(telegram_id=message.from_user.id),
        data=new_box,
        telegram_id=message.from_user.id,
    )
    if response.status_code == HTTPStatus.CREATED:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=SUCCESS_NEW_BOX_MESSAGE,
            reply_markup=main_markup(),
        )
        logger.info(f'USER {message.from_user.id} create new box')
    elif response.status_code == HTTPStatus.BAD_REQUEST:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=json.loads(response.text)['error'],
            reply_markup=main_markup(),
        )
        logger.info(f'USER {message.from_user.id} resive create box error')
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=API_ERROR_MESSAGE,
            reply_markup=main_markup(),
        )
        logger.error(f'USER {message.from_user.id} resive error')
    await state.reset_state()


async def back_step(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Возврат на предыдущее состояние."""
    data = await state.get_data()
    state_message_data = {
        'domain': {
            'prev_state': None,
            'text': CHOOSE_DOMAIN_MESSAGE,
            'reply_markup': domains_markup,
            'markup_args': [data['domains_titles']],
        },
        'username': {
            'prev_state': NewBoxState.domain,
            'text': ENTER_USERNAME_MESSAGE,
            'reply_markup': cancel_markup,
            'markup_args': [],
        },
        'password': {
            'prev_state': NewBoxState.username,
            'text': ENTER_PASSWORD_MESSAGE,
            'reply_markup': cancel_markup,
            'markup_args': [],
        },
        'filters': {
            'prev_state': NewBoxState.password,
            'text': ENTER_FILTERS_MESSAGE,
            'reply_markup': cancel_markup,
            'markup_args': [],
        },
        'filter_loop': {
            'prev_state': NewBoxState.filters,
            'text': ANOTHER_FILTER_MESSAGE,
            'reply_markup': filter_loop_markup,
            'markup_args': [],
        },
    }
    data = await state.get_data()
    prev_state: FSMContext = data.get('prev_state')
    if prev_state:
        await prev_state.set()
        await state.update_data(
            prev_state=state_message_data[prev_state._state]['prev_state'],
        )
        await bot.send_message(
            chat_id=message.from_user.id,
            text=state_message_data[prev_state._state]['text'],
            reply_markup=state_message_data[prev_state._state]['reply_markup'](
                *state_message_data[prev_state._state]['markup_args'],
            ),
        )


async def clear_filters(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Очистка фильтров."""
    logger.info(f'USER {message.from_user.id} clear filters command')
    await state.update_data(filters=[])
    await state.update_data(prev_state=NewBoxState.password)
    await NewBoxState.filters.set()
    await bot.send_message(
        chat_id=message.from_user.id,
        text=NEED_ONE + ENTER_FILTERS_MESSAGE,
        reply_markup=cancel_markup(),
    )


def register_new_box_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров в диспетчере."""
    dp.register_message_handler(
        new_box,
        text=Buttons.ADD.value,
        state=None,
    )
    dp.register_message_handler(add_domain, state=NewBoxState.domain)
    dp.register_message_handler(
        back_step,
        text=Buttons.BACK.value,
        state=[
            NewBoxState.username,
            NewBoxState.password,
            NewBoxState.filters,
            NewBoxState.approve,
        ],
    )
    dp.register_message_handler(add_username, state=NewBoxState.username)
    dp.register_message_handler(add_password, state=NewBoxState.password)
    dp.register_message_handler(add_filter, state=NewBoxState.filters)
    dp.register_message_handler(
        clear_filters,
        text=Buttons.CLEAR_FILTERS.value,
        state=NewBoxState.filter_loop,
    )
    dp.register_message_handler(
        filter_loop,
        text=[Buttons.ADD_FILTER.value, Buttons.END.value],
        state=NewBoxState.filter_loop,
    )
    dp.register_message_handler(
        approve_and_create_new_box,
        text=Buttons.APPROVE.value,
        state=NewBoxState.approve,
    )
