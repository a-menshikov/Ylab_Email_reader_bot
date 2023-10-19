import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot: Bot = Bot(token=os.getenv('BOT_TOKEN'))
dp: Dispatcher = Dispatcher(bot, storage=MemoryStorage())

logger = logging.getLogger('bot_logger')

logger.setLevel(logging.INFO)

logger_handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs)d %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
)
logger_handler.setFormatter(formatter)
logger.addHandler(logger_handler)
