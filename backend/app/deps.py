from app.application.admin_banca_service import AdminBancaService
from app.application.auth_service import AuthService
from app.application.banca_service import BancaService
from app.application.invite_service import InviteService
from app.infrastructure.mongo_banca_repository import MongoBancaRepository
from app.infrastructure.mongo_user_repository import MongoUserRepository

_repo = MongoBancaRepository()
_user_repo = MongoUserRepository()
_banca_service = BancaService(_repo)
_admin_banca_service = AdminBancaService(_repo)
_invite_service = InviteService(_repo)
_auth_service = AuthService(_user_repo)


def get_banca_service() -> BancaService:
    return _banca_service


def get_admin_banca_service() -> AdminBancaService:
    return _admin_banca_service


def get_invite_service() -> InviteService:
    return _invite_service


def get_auth_service() -> AuthService:
    return _auth_service
