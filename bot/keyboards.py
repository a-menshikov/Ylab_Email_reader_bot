from enum import Enum
from typing import Generator

from aiogram.types import ReplyKeyboardMarkup

from config import DOMAINS_CHUNK_SIZE


class Buttons(Enum):
    """Кнопки бота."""
    REG = 'Регистрация ✅'
    CANCEL = 'Отмена ❌'
    BACK = 'Назад ⬅️'
    ADD = 'Добавить ящик 📩'
    BOXES = 'Мои ящики 📫'
    ADD_FILTER = 'Добавить фильтр 🆕'
    CLEAR_FILTERS = 'Очистить фильтры 🔄'
    END = 'Завершить ввод ✅'
    APPROVE = 'Подтвердить ✅'
    ACTIVATE = 'Активировать ▶️'
    DEACTIVATE = 'Деактивировать ⏹'
    INSTRUCTIONS = 'Инструкция 📄'


def chunck_buttons(buttons: list[str], size: int) -> Generator:
    """Разбивка списка кнопок на чанки."""
    for i in range(0, len(buttons), size):
        yield buttons[i:i + size]


def registration_markup() -> ReplyKeyboardMarkup:
    """Клавиатура регистрации."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(Buttons.REG.value)

    return markup


def cancel_markup() -> ReplyKeyboardMarkup:
    """Клавиатура отмены действия."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(Buttons.BACK.value)
    markup.add(Buttons.CANCEL.value)

    return markup


def main_markup() -> ReplyKeyboardMarkup:
    """Главная клавиатура."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(Buttons.ADD.value, Buttons.BOXES.value)
    markup.row(Buttons.INSTRUCTIONS.value)

    return markup


def domains_markup(domains: list[str]) -> ReplyKeyboardMarkup:
    """Клавиатура с доменами."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for row in chunck_buttons(domains, DOMAINS_CHUNK_SIZE):
        markup.row(*row)
    markup.add(Buttons.CANCEL.value)
    return markup


def filter_loop_markup() -> ReplyKeyboardMarkup:
    """Клавиатура успешного ввода фильтра."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(Buttons.ADD_FILTER.value, Buttons.END.value)
    markup.add(Buttons.CLEAR_FILTERS.value)
    markup.row(Buttons.CANCEL.value)
    return markup


def approve_markup() -> ReplyKeyboardMarkup:
    """Клавиатура подтверждения ввода."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(Buttons.APPROVE.value)
    markup.add(Buttons.BACK.value)
    markup.row(Buttons.CANCEL.value)
    return markup


def my_boxes_markup(username_list: list[str]) -> ReplyKeyboardMarkup:
    """Клавиатура проcмотра ящиков."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for username in username_list:
        markup.row(username)
    markup.add(Buttons.CANCEL.value)
    return markup


def one_box_markup(status: bool) -> ReplyKeyboardMarkup:
    """Клавиатура конкретного ящика."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    if status:
        markup.row(Buttons.DEACTIVATE.value)
    else:
        markup.row(Buttons.ACTIVATE.value)
    markup.add(Buttons.CANCEL.value)
    return markup
