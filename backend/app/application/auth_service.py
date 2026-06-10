from app.config import (
    AUTH_TOKEN_TTL_SECONDS,
    PPGENFIS_ADMIN_PASSWORD,
    PPGENFIS_ADMIN_USERNAME,
    PPGFIS_ADMIN_PASSWORD,
    PPGFIS_ADMIN_USERNAME,
)
from app.domain.errors import AuthError, PersistenceError
from app.domain.models import AdminUserRecord, LoginResponse
from app.domain.user_repository import UserRepository
from app.infrastructure.security import create_token, hash_password, verify_password
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def seed_default_users(self) -> Result[None, PersistenceError]:
        """Create the two per-PPG admin users if they don't exist yet (idempotent)."""
        users = [
            AdminUserRecord(
                username=PPGFIS_ADMIN_USERNAME,
                ppg="ppgfis",
                password_hash=hash_password(PPGFIS_ADMIN_PASSWORD),
            ),
            AdminUserRecord(
                username=PPGENFIS_ADMIN_USERNAME,
                ppg="ppgenfis",
                password_hash=hash_password(PPGENFIS_ADMIN_PASSWORD),
            ),
        ]
        return self._repo.seed(users)

    def login(self, username: str, password: str) -> Result[LoginResponse, AuthError | PersistenceError]:
        logger.info("auth.login.start", {"username": username})
        match self._repo.find_by_username(username):
            case Err() as err:
                return err
            case ok:
                user = ok.value

        if user is None or not verify_password(password, user.password_hash):
            logger.info("auth.login.invalid", {"username": username})
            return Err(AuthError(message="Usuário ou senha inválidos"))

        token = create_token({"sub": user.username, "ppg": user.ppg}, AUTH_TOKEN_TTL_SECONDS)
        logger.info("auth.login.success", {"username": username, "ppg": user.ppg})
        return Ok(LoginResponse(token=token, username=user.username, ppg=user.ppg))
