from ninja import Schema


class ErrorSchema(Schema):
    """Схема для предоставления информации об ошибках"""

    error: str

    @classmethod
    def create(cls, error: Exception) -> 'ErrorSchema':
        error_msg = str(error)
        return cls(error=error_msg)
