from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.application.banca_service import BancaService
from app.deps import get_banca_service
from app.domain.errors import DocumentGenerationError, EmailError, PersistenceError
from app.domain.models import BancaRequest, BancaResponse
from app.logger import get_logger
from app.result import Err

logger = get_logger(__name__)

router = APIRouter()


@router.post("/banca")
def create_banca(
    req: BancaRequest,
    banca_service: Annotated[BancaService, Depends(get_banca_service)],
) -> BancaResponse:
    logger.info("POST /banca.start", {"ata": req.ata, "student": req.nome.name})
    match banca_service.create(req):
        case Err(DocumentGenerationError(message=msg)):
            logger.error("POST /banca.document_generation_error", {"message": msg})
            raise HTTPException(status_code=500, detail=msg)
        case Err(EmailError(message=msg, recipient=recipient)):
            logger.error("POST /banca.email_error", {"recipient": recipient, "message": msg})
            raise HTTPException(status_code=502, detail=f"Email to {recipient} failed: {msg}")
        case Err(PersistenceError(message=msg)):
            logger.error("POST /banca.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info("POST /banca.end", {"ata": req.ata})
            return ok.value
