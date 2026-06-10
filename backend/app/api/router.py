from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.application.banca_service import BancaService
from app.deps import get_banca_service
from app.domain.errors import (
    BancaAlreadyDecidedError,
    BancaNotFoundError,
    DocumentGenerationError,
    EmailError,
    PersistenceError,
)
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
):
    """Upload PDF attachments for a banca (lattes_cv, texto, press_release, artigo)."""
    from app.infrastructure.database import get_db
    import gridfs
    from datetime import datetime, timezone

    db = get_db()
    fs = gridfs.GridFS(db)

    saved = []
    for file, kind in zip(files, kinds):
        if kind not in ("lattes_cv", "texto", "press_release", "artigo"):
            raise HTTPException(status_code=400, detail=f"Invalid attachment kind: {kind}")
        content = await file.read()
        file_id = fs.put(content, filename=file.filename, content_type=file.content_type)
        db["attachments"].insert_one({
            "decision_token": token,
            "kind": kind,
            "filename": file.filename,
            "gridfs_id": file_id,
            "uploaded_at": datetime.now(timezone.utc),
        })
        saved.append({"kind": kind, "filename": file.filename})

    return {"uploaded": saved}
