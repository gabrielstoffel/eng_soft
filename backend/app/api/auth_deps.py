from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.admin_banca_service import AdminBancaService
from app.deps import get_admin_banca_service
from app.domain.errors import BancaNotFoundError, PersistenceError
from app.domain.models import CurrentUser
from app.infrastructure.security import decode_token
from app.result import Err

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUser:
    """Resolve the authenticated admin from the Bearer token, or 401."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Não autenticado")
    payload = decode_token(credentials.credentials)
    if payload is None or "sub" not in payload or "ppg" not in payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return CurrentUser(username=payload["sub"], ppg=payload["ppg"])


def require_banca_access(
    token: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    admin_service: Annotated[AdminBancaService, Depends(get_admin_banca_service)],
) -> CurrentUser:
    """Authenticate AND enforce PPG segmentation for a per-banca endpoint.

    A user may only act on bancas belonging to their own PPG; anything else is a
    404 (so existence of other-PPG bancas is not even revealed).
    """
    match admin_service.get_detail(token):
        case Err(BancaNotFoundError(message=msg)):
            raise HTTPException(status_code=404, detail=msg)
        case Err(PersistenceError(message=msg)):
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            if ok.value.ppg != user.ppg:
                raise HTTPException(status_code=404, detail=f"Banca with token {token} not found")
    return user
