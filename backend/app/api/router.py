from datetime import datetime, timezone
from typing import Annotated

import gridfs
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.application.banca_service import BancaService
from app.deps import get_banca_service
from app.domain.errors import (
    BancaAlreadyDecidedError,
    BancaNotFoundError,
    DocumentGenerationError,
    EmailError,
    PersistenceError,
    ValidationError,
)
from app.infrastructure.database import get_db
from app.domain.models import (
    ApproveRequest,
    BancaDecisionResponse,
    BancaRequest,
    BancaSubmitResponse,
    BancaSummary,
    RejectRequest,
)
from app.logger import get_logger
from app.result import Err

logger = get_logger(__name__)

router = APIRouter()


@router.post("/banca")
def submit_banca(
    req: BancaRequest,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
) -> BancaSubmitResponse:
    match banca_service.submit_petition(req):
        case Err(ValidationError(details=details)):
            raise HTTPException(status_code=422, detail="; ".join(details))
        case Err(EmailError(message=msg, recipient=recipient)):
            raise HTTPException(status_code=502, detail=f"Email to {recipient} failed: {msg}")
        case Err(PersistenceError(message=msg)):
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            return ok.value


@router.get("/banca/decide/{token}")
def get_banca_summary(
    token: str,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
) -> BancaSummary:
    match banca_service.get_summary(token):
        case Err(BancaNotFoundError(message=msg)):
            raise HTTPException(status_code=404, detail=msg)
        case Err(PersistenceError(message=msg)):
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            return ok.value


@router.post("/banca/decide/{token}/approve")
def approve_banca(
    token: str,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
    body: ApproveRequest | None = None,
) -> BancaDecisionResponse:
    observation = body.observation if body else None
    match banca_service.approve(token, observation=observation):
        case Err(BancaNotFoundError(message=msg)):
            raise HTTPException(status_code=404, detail=msg)
        case Err(BancaAlreadyDecidedError(message=msg, current_status=cs)):
            raise HTTPException(status_code=409, detail={"message": msg, "current_status": cs})
        case Err(DocumentGenerationError(message=msg)):
            raise HTTPException(status_code=500, detail=msg)
        case Err(EmailError(message=msg, recipient=recipient)):
            raise HTTPException(status_code=502, detail=f"Email to {recipient} failed: {msg}")
        case Err(PersistenceError(message=msg)):
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            return ok.value


@router.post("/banca/decide/{token}/reject")
def reject_banca(
    token: str,
    body: RejectRequest,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
) -> BancaDecisionResponse:
    match banca_service.reject(token, body.reason):
        case Err(BancaNotFoundError(message=msg)):
            raise HTTPException(status_code=404, detail=msg)
        case Err(BancaAlreadyDecidedError(message=msg, current_status=cs)):
            raise HTTPException(status_code=409, detail={"message": msg, "current_status": cs})
        case Err(EmailError(message=msg, recipient=recipient)):
            raise HTTPException(status_code=502, detail=f"Email to {recipient} failed: {msg}")
        case Err(PersistenceError(message=msg)):
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            return ok.value


_ATTACHMENT_KINDS = ("lattes_cv", "texto", "press_release", "artigo")
_PDF_CONTENT_TYPES = ("application/pdf", "application/x-pdf")


@router.post("/banca/{token}/attachments")
async def upload_attachments(
    token: str,
    files: list[UploadFile] = File(...),
    kinds: list[str] = Form(...),
    roles: list[str] | None = Form(None),
):
    """Upload PDF attachments for a banca (lattes_cv, texto, press_release, artigo).

    `kinds` (and optional `roles`, used to bind a lattes_cv to its external member)
    are positional, parallel to `files`. The lengths must match exactly — a
    mismatch is rejected rather than silently truncated.
    """
    db = get_db()

    # Reject orphan uploads: the token must reference an existing banca.
    if db["bancas"].find_one({"decision_token": token}, {"_id": 1}) is None:
        raise HTTPException(status_code=404, detail=f"Banca with token {token} not found")

    if len(files) != len(kinds):
        raise HTTPException(status_code=400, detail="files and kinds must have the same length")
    if roles is not None and len(roles) != len(files):
        raise HTTPException(status_code=400, detail="roles, when provided, must match files length")

    fs = gridfs.GridFS(db)
    saved = []
    for idx, (file, kind) in enumerate(zip(files, kinds)):
        if kind not in _ATTACHMENT_KINDS:
            raise HTTPException(status_code=400, detail=f"Invalid attachment kind: {kind}")
        if file.content_type not in _PDF_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Attachment '{file.filename}' must be a PDF (got {file.content_type})",
            )
        member_role = roles[idx] if roles and roles[idx] else None
        content = await file.read()
        file_id = fs.put(content, filename=file.filename, content_type=file.content_type)
        db["attachments"].insert_one({
            "decision_token": token,
            "kind": kind,
            "member_role": member_role,
            "filename": file.filename,
            "gridfs_id": file_id,
            "uploaded_at": datetime.now(timezone.utc),
        })
        saved.append({"kind": kind, "member_role": member_role, "filename": file.filename})

    return {"uploaded": saved}
