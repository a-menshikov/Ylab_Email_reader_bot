import json
from http import HTTPStatus

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from api_client import ApiResponseClient
from config import (API_ERROR_MESSAGE, CHANGE_BOX_STATUS_ENDPOINT,
                    CHANGE_BOX_STATUS_THROTTLE_KEY, EMPTY_BOX_LIST_MESSAGE,
                    ERROR_BOX_CHOOSE_MESSAGE, ERROR_CHANGE_BOX_STATUS_MESSAGE,
                    MY_BOX_ENDPOINT, MY_BOXES_MESSAGE,
                    SUCCESS_CHANGE_BOX_STATUS_MESSAGE)
from handlers.user.utils import one_box_message, rate_limit
from keyboards import Buttons, main_markup, my_boxes_markup, one_box_markup
from loader import bot, logger
from states import MyBoxesState


async def get_my_boxes(
    message: types.Message,
    state: FSMContext,
    api: ApiResponseClient,
) -> None:
    """Получение списка ящиков."""
    logger.info(f'USER {message.from_user.id} get my boxes command')
    response = await api.get_data(
        endpoint=MY_BOX_ENDPOINT.format(telegram_id=message.from_user.id),
        telegram_id=message.from_user.id,
    )
    if response.status_code != HTTPStatus.OK:
        logger.error(f'USER {message.from_user.id} resive error')
        await bot.send_message(
            chat_id=message.from_user.id,
            text=API_ERROR_MESSAGE,
            reply_markup=main_markup(),
        )
        return
    boxes = json.loads(response.text)
    if not boxes:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=EMPTY_BOX_LIST_MESSAGE,
            reply_markup=main_markup(),
        )
        logger.info(f'USER {message.from_user.id} resive no boxes')
        return
    await MyBoxesState.start.set()
    username_list = [box['email_username'] for box in boxes]
    await state.update_data(
        username_list=username_list,
        boxes=boxes,
    )
    await bot.send_message(
        chat_id=message.from_user.id,
        text=MY_BOXES_MESSAGE,
        reply_markup=my_boxes_markup(username_list),
    )
    logger.info(f'USER {message.from_user.id} resive boxes')


async def get_one_box(message: types.Message, state: FSMContext) -> None:
    """Получение одного ящика."""
    logger.info(f'USER {message.from_user.id} get one box command')
    data = await state.get_data()
    boxes = data['boxes']
    username_list = data['username_list']
    box_id: int = 0
    box_status: bool = False
    box_username: str = ''
    for box in boxes:
        if box['email_username'] == message.text:
            box_id = box['id']
            box_status = box['is_active']
            box_username = box['email_username']
            break
    if not box_id:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ERROR_BOX_CHOOSE_MESSAGE,
            reply_markup=my_boxes_markup(username_list),
        )
        logger.info(f'USER {message.from_user.id} resive no one box')
    else:
        await MyBoxesState.one_box.set()
        await state.update_data(box_id=box_id, box_status=box_status)
        await bot.send_message(
            chat_id=message.from_user.id,
            text=await one_box_message(box_username, box_status),
            reply_markup=one_box_markup(box_status),
        )
        logger.info(f'USER {message.from_user.id} resive one box')


@rate_limit(limit=90, key=CHANGE_BOX_STATUS_THROTTLE_KEY)
async def change_box_status(
    message: types.Message,
    state: FSMContext,
    api: ApiResponseClient,
) -> None:
    """Изменение статуса ящика."""
    logger.info(f'USER {message.from_user.id} change box status command')
    data = await state.get_data()
    if message.text == Buttons.ACTIVATE.value and data['box_status'] is False:
        new_status = True
    elif message.text == Buttons.DEACTIVATE.value \
            and data['box_status'] is True:
        new_status = False
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=ERROR_CHANGE_BOX_STATUS_MESSAGE,
            reply_markup=one_box_markup(data['box_status']),
        )
        return
    response = await api.patch_data(
        endpoint=CHANGE_BOX_STATUS_ENDPOINT.format(
            telegram_id=message.from_user.id,
            box_id=data['box_id'],
        ),
        data={'status': new_status},
        telegram_id=message.from_user.id,
    )
    if response.status_code != HTTPStatus.OK:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=API_ERROR_MESSAGE,
            reply_markup=main_markup(),
        )
        logger.error(f'USER {message.from_user.id} resive error')
        await state.reset_state()
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=SUCCESS_CHANGE_BOX_STATUS_MESSAGE,
            reply_markup=main_markup(),
        )
        logger.info(f'USER {message.from_user.id} change box status success')
        await state.reset_state()


def register_my_boxes_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров в диспетчере."""
    dp.register_message_handler(
        get_my_boxes,
        text=Buttons.BOXES.value,
        state=None,
    )
    dp.register_message_handler(get_one_box, state=MyBoxesState.start)
    dp.register_message_handler(
        change_box_status,
        text=[Buttons.ACTIVATE.value, Buttons.DEACTIVATE.value],
        state=MyBoxesState.one_box,
    )
