from abc import ABC, abstractmethod

from app.domain.errors import BancaAlreadyDecidedError, BancaNotFoundError, PersistenceError
from app.domain.models import BancaRecord, BancaRequest, BancaStatus
from app.result import Result


class BancaRepository(ABC):
    @abstractmethod
    def save(self, req: BancaRequest) -> Result[str, PersistenceError]: ...

    @abstractmethod
    def find_by_token(
        self, token: str
    ) -> Result[BancaRecord, BancaNotFoundError | PersistenceError]: ...

    @abstractmethod
    def update_decision(
        self, token: str, status: BancaStatus, reason: str | None = None
    ) -> Result[None, BancaNotFoundError | BancaAlreadyDecidedError | PersistenceError]: ...
