from abc import ABC, abstractmethod

from app.domain.errors import PersistenceError
from app.domain.models import BancaRequest
from app.result import Result


class BancaRepository(ABC):
    @abstractmethod
    def save(self, req: BancaRequest) -> Result[None, PersistenceError]: ...
