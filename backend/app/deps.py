from app.application.admin_banca_service import AdminBancaService
from app.application.banca_service import BancaService
from app.application.invite_service import InviteService
from app.infrastructure.mongo_banca_repository import MongoBancaRepository

_repo = MongoBancaRepository()
_banca_service = BancaService(_repo)
_admin_banca_service = AdminBancaService(_repo)
_invite_service = InviteService(_repo)


def get_banca_service() -> BancaService:
    return _banca_service


def get_admin_banca_service() -> AdminBancaService:
    return _admin_banca_service


def get_invite_service() -> InviteService:
    return _invite_service
