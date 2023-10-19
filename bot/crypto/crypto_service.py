from cryptography.fernet import Fernet

from config import CRYPTO_KEY


class Encryptor:
    """Класс для шифрования и дешифрования данных."""

    def __init__(self, key: str):
        self.encryptor: Fernet = Fernet(key.encode())

    def encrypt_data(self, plain_data: str) -> bytes:
        """Шифрует строку."""
        return self.encryptor.encrypt(plain_data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Дешифрует строку."""
        return self.encryptor.decrypt(encrypted_data).decode()


encryptor: Encryptor = Encryptor(CRYPTO_KEY)
