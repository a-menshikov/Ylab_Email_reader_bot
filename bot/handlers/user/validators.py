import re


async def validate_email(email: str) -> bool:
    """Проверка текста на соответствие формату адреса электронной почты."""
    reg_exp = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+\.[a-zA-Z0-9-.]+$'
    if len(email) > 256 or '@' not in email:
        return False
    if not re.fullmatch(reg_exp, email):
        return False
    return True


async def validate_filter_alias(value: str) -> bool:
    """Проверка текста на соответствие формату псевдонима фильтра."""
    if len(value) > 128:
        return False
    return True
