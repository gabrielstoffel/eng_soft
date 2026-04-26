from functools import lru_cache

from app.application.banca_service import BancaService
from app.infrastructure.mongo_banca_repository import MongoBancaRepository


@lru_cache
def get_banca_service() -> BancaService:
    return BancaService(MongoBancaRepository())
