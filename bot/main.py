from aiogram import Dispatcher
from aiogram.utils import executor

from handlers.user.common import register_common_handlers, unknown_message
from handlers.user.my_boxes import register_my_boxes_handlers
from handlers.user.new_box import register_new_box_handlers
from handlers.user.new_user import register_new_user_handlers
from loader import dp
from middleware import register_middlewares


def regiter_handlers(dp: Dispatcher) -> None:
    """Регистрация хэндлеров."""
    register_common_handlers(dp)
    register_new_user_handlers(dp)
    register_new_box_handlers(dp)
    register_my_boxes_handlers(dp)
    dp.register_message_handler(
        unknown_message,
        state=None,
    )


def regiter_middlewares(dp: Dispatcher) -> None:
    """Регистрация мидлваров."""
    register_middlewares(dp)


if __name__ == '__main__':
    regiter_handlers(dp)
    regiter_middlewares(dp)
    executor.start_polling(dp, skip_updates=True)
