from app.application.banca_service import BancaService
from app.infrastructure.mongo_banca_repository import MongoBancaRepository

_banca_service = BancaService(MongoBancaRepository())


def get_banca_service() -> BancaService:
    return _banca_service
