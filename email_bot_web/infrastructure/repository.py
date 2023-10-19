from email_service.repository import (
    RepositoryBoxFilter,
    RepositoryEmailBox,
    RepositoryEmailDomain,
)
from user.repository import RepositoryBotUser


class Repository:
    """Единый репозиторий CRUD операций."""

    def __init__(self):
        self.user = RepositoryBotUser()
        self.domain = RepositoryEmailDomain()
        self.box = RepositoryEmailBox()
        self.filter = RepositoryBoxFilter()
