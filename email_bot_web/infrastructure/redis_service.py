import pickle
from functools import wraps
from typing import Any, Callable

from django.conf import settings
from django.core.cache import cache


class RedisClient:
    """Сервис для работы с redis."""

    async def gen_key(self, telegram_id: int, box_id: int) -> str:
        """Генерация ключа."""
        return settings.REDIS_KEY_FORMAT.format(
            telegram_id=telegram_id,
            box_id=box_id,
        )

    async def get(self, key: str) -> str | None:
        """Получить значение по ключу."""
        value = cache.get(key)
        if value:
            return value
        return None

    async def set(
        self,
        key: str,
        value: str,
        timeout: int | None = None,
    ) -> None:
        """Установить значение по ключу."""
        cache.set(key, value, timeout)

    async def delete(self, key: str) -> None:
        """Удалить значение по ключу."""
        cache.delete(key)

    async def delete_many(self, keys: list[str]) -> None:
        """Удалить список ключей."""
        cache.delete_many(keys=keys)

    async def get_all_keys(self, pattern: str = '*') -> list[str]:
        """Получить все ключи по шаблону."""
        return cache.keys(pattern)

    def cache_result(
        self,
        key_format: str,
        timeout: int = settings.CACHE_TIMEOUT,
    ) -> Callable:
        """Декоратор для кэширования результатов функции."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                all_args = {**kwargs}
                for i, arg in enumerate(args):
                    all_args[func.__code__.co_varnames[i]] = arg
                cache_key = key_format.format(**all_args)
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return pickle.loads(cached_result)
                result = await func(*args, **kwargs)
                cache.set(cache_key, pickle.dumps(result), timeout)
                return result
            return wrapper
        return decorator

    def delete_cache(
        self,
        key_format_list: list[str],
    ) -> Callable:
        """Удалить все кэшированные результаты."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                all_args = {**kwargs}
                for i, arg in enumerate(args):
                    all_args[func.__code__.co_varnames[i]] = arg
                for key_format in key_format_list:
                    cache_key = key_format.format(**all_args)
                    cache.delete(cache_key)
                result = await func(*args, **kwargs)
                return result
            return wrapper
        return decorator


redis_client: RedisClient = RedisClient()
