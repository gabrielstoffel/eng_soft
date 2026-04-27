from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

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
    logger.info("POST /banca.start", {"ata": req.ata, "student": req.nome.name})
    match banca_service.submit_petition(req):
        case Err(EmailError(message=msg, recipient=recipient)):
            logger.error("POST /banca.email_error", {"recipient": recipient, "message": msg})
            raise HTTPException(status_code=502, detail=f"Email to {recipient} failed: {msg}")
        case Err(PersistenceError(message=msg)):
            logger.error("POST /banca.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info("POST /banca.end", {"ata": req.ata, "decision_token": ok.value.decision_token})
            return ok.value


@router.get("/banca/decide/{token}")
def get_banca_summary(
    token: str,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
) -> BancaSummary:
    logger.info("GET /banca/decide.start", {"decision_token": token})
    match banca_service.get_summary(token):
        case Err(BancaNotFoundError(message=msg)):
            logger.warn("GET /banca/decide.not_found", {"decision_token": token})
            raise HTTPException(status_code=404, detail=msg)
        case Err(PersistenceError(message=msg)):
            logger.error("GET /banca/decide.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info("GET /banca/decide.end", {"decision_token": token, "status": ok.value.status})
            return ok.value


@router.post("/banca/decide/{token}/approve")
def approve_banca(
    token: str,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
) -> BancaDecisionResponse:
    logger.info("POST /banca/decide/approve.start", {"decision_token": token})
    match banca_service.approve(token):
        case Err(BancaNotFoundError(message=msg)):
            logger.warn("POST /banca/decide/approve.not_found", {"decision_token": token})
            raise HTTPException(status_code=404, detail=msg)
        case Err(BancaAlreadyDecidedError(message=msg, current_status=current_status)):
            logger.warn(
                "POST /banca/decide/approve.already_decided",
                {"decision_token": token, "current_status": current_status},
            )
            raise HTTPException(
                status_code=409,
                detail={"message": msg, "current_status": current_status},
            )
        case Err(DocumentGenerationError(message=msg)):
            logger.error("POST /banca/decide/approve.document_generation_error", {"message": msg})
            raise HTTPException(status_code=500, detail=msg)
        case Err(EmailError(message=msg, recipient=recipient)):
            logger.error(
                "POST /banca/decide/approve.email_error",
                {"recipient": recipient, "message": msg},
            )
            raise HTTPException(status_code=502, detail=f"Email to {recipient} failed: {msg}")
        case Err(PersistenceError(message=msg)):
            logger.error("POST /banca/decide/approve.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info(
                "POST /banca/decide/approve.end",
                {"decision_token": token, "status": "approved"},
            )
            return ok.value


@router.post("/banca/decide/{token}/reject")
def reject_banca(
    token: str,
    body: RejectRequest,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
) -> BancaDecisionResponse:
    logger.info("POST /banca/decide/reject.start", {"decision_token": token})
    match banca_service.reject(token, body.reason):
        case Err(BancaNotFoundError(message=msg)):
            logger.warn("POST /banca/decide/reject.not_found", {"decision_token": token})
            raise HTTPException(status_code=404, detail=msg)
        case Err(BancaAlreadyDecidedError(message=msg, current_status=current_status)):
            logger.warn(
                "POST /banca/decide/reject.already_decided",
                {"decision_token": token, "current_status": current_status},
            )
            raise HTTPException(
                status_code=409,
                detail={"message": msg, "current_status": current_status},
            )
        case Err(EmailError(message=msg, recipient=recipient)):
            logger.error(
                "POST /banca/decide/reject.email_error",
                {"recipient": recipient, "message": msg},
            )
            raise HTTPException(status_code=502, detail=f"Email to {recipient} failed: {msg}")
        case Err(PersistenceError(message=msg)):
            logger.error("POST /banca/decide/reject.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info(
                "POST /banca/decide/reject.end",
                {"decision_token": token, "status": "rejected"},
            )
            return ok.value
