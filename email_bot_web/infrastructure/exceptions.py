class UserDoesNotExist(Exception):
    """Исключение отсутсвия пользователя в базе."""


class UserAlreadyExist(Exception):
    """Исключение наличия пользователя в базе."""


class DomainDoesNotExist(Exception):
    """Исключение отсутсвия почтового сервиса в базе."""


class BoxAlreadyExist(Exception):
    """Исключение наличия почтового ящика в базе."""


class BoxDoesNotExist(Exception):
    """Исключение отсутствия почтового ящика в базе."""


class ImapAuthenticationFailed(Exception):
    """Исключение аутентификации."""


class ImapConnectionError(Exception):
    """Исключение соединения при работе с почтовыми ящиками."""


class ServerUnavailable(Exception):
    """Исключение недоступности сервера."""
