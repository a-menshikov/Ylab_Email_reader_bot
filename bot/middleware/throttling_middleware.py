from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from config import DEFAULT_RATE_LIMIT


class ThrottlingMiddleware(BaseMiddleware):
    """Мидлвар для ограничения количества запросов."""

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super().__init__()

    async def on_process_message(
        self,
        message: types.Message,
        data: dict,
    ) -> None:
        """Проверка ограничения при выполнении."""
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        state_data: FSMContext = data.get('state')
        data = await state_data.get_data()
        limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
        key = getattr(
            handler,
            'throttling_key',
            f'{self.prefix}_{handler.__name__}_{message.chat.id}',
        ).format(**data)

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await message.reply(
                f'Эту операцию нельзя выполнить чаще чем 1 раз в {t.rate:.0f}'
                f' секунд.\nС прошлого выполнения прошло {t.delta:.0f} секунд.'
                f'\nПопробуйте снова через {t.rate:.0f} секунд.'
            )
            raise CancelHandler()
