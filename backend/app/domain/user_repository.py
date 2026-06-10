from abc import ABC, abstractmethod

from app.domain.errors import PersistenceError
from app.domain.models import AdminUserRecord
from app.result import Result


class UserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> Result[AdminUserRecord | None, PersistenceError]: ...

    @abstractmethod
    def seed(self, users: list[AdminUserRecord]) -> Result[None, PersistenceError]:
        """Insert each user if its username is absent. Never overwrites an existing user."""
        ...
