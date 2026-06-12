from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError as PydanticValidationError

from app.application import attachment_service
from app.application.attachment_service import ATTACHMENT_KINDS, AttachmentUpload
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
from app.domain.models import (
    ApproveRequest,
    BancaDecisionResponse,
    BancaRequest,
    BancaSubmitResponse,
    BancaSummary,
    RejectRequest,
)
from app.infrastructure.database import get_db
from app.logger import get_logger
from app.result import Err

logger = get_logger(__name__)

router = APIRouter()


_PDF_CONTENT_TYPES = ("application/pdf", "application/x-pdf")

# Maximum total upload size per request (all attachments combined).
_MAX_UPLOAD_BYTES = 150 * 1024 * 1024  # 150 MB
_MAX_UPLOAD_LABEL = "150 MB"


async def _build_attachments(
    files: list[UploadFile] | None,
    kinds: list[str] | None,
    roles: list[str] | None,
) -> list[AttachmentUpload]:
    """Validate parallel files/kinds/roles form fields into AttachmentUpload list.

    `kinds` (and optional `roles`, used to bind a lattes_cv to its external
    member) are positional, parallel to `files`. Lengths must match exactly — a
    mismatch is rejected rather than silently truncated.
    """
    files = files or []
    kinds = kinds or []
    if len(files) != len(kinds):
        raise HTTPException(status_code=400, detail="files and kinds must have the same length")
    if roles is not None and len(roles) != len(files):
        raise HTTPException(status_code=400, detail="roles, when provided, must match files length")

    result: list[AttachmentUpload] = []
    total_bytes = 0
    for idx, (file, kind) in enumerate(zip(files, kinds)):
        if kind not in ATTACHMENT_KINDS:
            raise HTTPException(status_code=400, detail=f"Invalid attachment kind: {kind}")
        if file.content_type not in _PDF_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Attachment '{file.filename}' must be a PDF (got {file.content_type})",
            )
        # Reject oversized uploads before reading the whole file into memory when
        # the declared size already blows the budget; re-check after reading.
        if file.size is not None and total_bytes + file.size > _MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"O envio excede o limite de {_MAX_UPLOAD_LABEL}.")
        member_role = roles[idx] if roles and roles[idx] else None
        content = await file.read()
        total_bytes += len(content)
        if total_bytes > _MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"O envio excede o limite de {_MAX_UPLOAD_LABEL}.")
        result.append(
            AttachmentUpload(
                filename=file.filename,
                content=content,
                content_type=file.content_type,
                kind=kind,
                member_role=member_role,
            )
        )
    return result


@router.post("/banca")
async def submit_banca(
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
    payload: str = Form(...),
    files: list[UploadFile] | None = File(None),
    kinds: list[str] | None = Form(None),
    roles: list[str] | None = Form(None),
) -> BancaSubmitResponse:
    """Submit a banca petition with its PDF attachments in one multipart request.

    `payload` is the banca request as a JSON string; the files travel alongside
    so they can be attached to the email sent to the coordenador.
    """
    try:
        req = BancaRequest.model_validate_json(payload)
    except PydanticValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=[{"msg": err["msg"], "loc": list(err["loc"])} for err in e.errors()],
        )

    attachments = await _build_attachments(files, kinds, roles)

    match banca_service.submit_petition(req, attachments):
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


@router.post("/banca/{token}/attachments")
async def upload_attachments(
    token: str,
    files: list[UploadFile] = File(...),
    kinds: list[str] = Form(...),
    roles: list[str] | None = Form(None),
):
    """Upload PDF attachments for an existing banca (lattes_cv, texto, press_release, artigo).

    The primary path attaches files at submission time (POST /banca); this remains
    for adding attachments to a banca that already exists.
    """
    db = get_db()

    # Reject orphan uploads: the token must reference an existing banca.
    if db["bancas"].find_one({"decision_token": token}, {"_id": 1}) is None:
        raise HTTPException(status_code=404, detail=f"Banca with token {token} not found")

    attachments = await _build_attachments(files, kinds, roles)
    saved = attachment_service.store_attachments(token, attachments)
    return {"uploaded": saved}
