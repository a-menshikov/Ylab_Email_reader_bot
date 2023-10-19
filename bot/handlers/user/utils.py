from typing import Callable

from config import APPROVE_MESSAGE, ONE_BOX_MESSAGE


async def approve_message(
    data: dict[str, list[dict[str, str]]],
) -> str:
    """Сообщение о подтверждении добавления ящика."""
    return APPROVE_MESSAGE.format(
        email=data['username'],
        filters='\n'.join(
            [f'{filter["filter_value"]} {filter["filter_name"]}'
             for filter in data['filters']]
        ),
    )


async def one_box_message(username: str, status: bool) -> str:
    """Сообщение о конкретном ящике."""
    return ONE_BOX_MESSAGE.format(
        email=username,
        status='Активен' if status else 'Неактивен',
    )


def rate_limit(limit: int, key: str) -> Callable:
    """Декоратор для ограничения количества запросов."""
    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        setattr(func, 'throttling_key', key)
        return func
    return decorator
