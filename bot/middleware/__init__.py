from aiogram import Dispatcher

from .api_middleware import ApiMiddleware, BanMiddleware
from .throttling_middleware import ThrottlingMiddleware


def register_middlewares(dp: Dispatcher):
    dp.setup_middleware(ApiMiddleware())
    dp.setup_middleware(BanMiddleware())
    dp.setup_middleware(ThrottlingMiddleware())
