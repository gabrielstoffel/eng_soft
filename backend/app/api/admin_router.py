from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.application.admin_banca_service import AdminBancaService
from app.deps import get_admin_banca_service
from app.domain.errors import (
    BancaNotEditableError,
    BancaNotFoundError,
    BancaVersionNotFoundError,
    DocumentGenerationError,
    PersistenceError,
)
from app.domain.models import (
    BancaAdminDetail,
    BancaListFilters,
    BancaListItem,
    BancaRequest,
    BancaStatus,
    BancaUpdateResponse,
    FileManifestEntry,
)
from app.logger import get_logger
from app.result import Err

logger = get_logger(__name__)

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/bancas")
def list_bancas(
    admin_service: Annotated[AdminBancaService, Depends(get_admin_banca_service)],
    status: BancaStatus | None = None,
    ata: int | None = None,
    student: str | None = None,
    orientador: str | None = None,
    q: str | None = None,
) -> list[BancaListItem]:
    filters = BancaListFilters(status=status, ata=ata, student=student, orientador=orientador, q=q)
    logger.info(
        "GET /admin/bancas.start",
        {"status": status, "ata": ata, "student": student, "orientador": orientador, "q": q},
    )
    match admin_service.list_bancas(filters):
        case Err(PersistenceError(message=msg)):
            logger.error("GET /admin/bancas.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info("GET /admin/bancas.end", {"count": len(ok.value)})
            return ok.value


@admin_router.get("/bancas/{token}")
def get_banca_detail(
    token: str,
    admin_service: Annotated[AdminBancaService, Depends(get_admin_banca_service)],
) -> BancaAdminDetail:
    logger.info("GET /admin/bancas/{token}.start", {"decision_token": token})
    match admin_service.get_detail(token):
        case Err(BancaNotFoundError(message=msg)):
            logger.warn("GET /admin/bancas/{token}.not_found", {"decision_token": token})
            raise HTTPException(status_code=404, detail=msg)
        case Err(PersistenceError(message=msg)):
            logger.error("GET /admin/bancas/{token}.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info(
                "GET /admin/bancas/{token}.end",
                {"decision_token": token, "versions": len(ok.value.versions)},
            )
            return ok.value


@admin_router.put("/bancas/{token}")
def update_banca(
    token: str,
    body: BancaRequest,
    admin_service: Annotated[AdminBancaService, Depends(get_admin_banca_service)],
) -> BancaUpdateResponse:
    logger.info("PUT /admin/bancas/{token}.start", {"decision_token": token})
    match admin_service.update_banca(token, body):
        case Err(BancaNotFoundError(message=msg)):
            logger.warn("PUT /admin/bancas/{token}.not_found", {"decision_token": token})
            raise HTTPException(status_code=404, detail=msg)
        case Err(BancaNotEditableError(message=msg, current_status=current_status)):
            logger.warn(
                "PUT /admin/bancas/{token}.not_editable",
                {"decision_token": token, "current_status": current_status},
            )
            raise HTTPException(
                status_code=409,
                detail={"message": msg, "current_status": current_status},
            )
        case Err(PersistenceError(message=msg)):
            logger.error("PUT /admin/bancas/{token}.persistence_error", {"message": msg})
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info(
                "PUT /admin/bancas/{token}.end",
                {
                    "decision_token": token,
                    "created_new_version": ok.value.created_new_version,
                    "current_version": ok.value.current_version,
                },
            )
            return ok.value


@admin_router.get("/bancas/{token}/files")
def list_banca_files(
    token: str,
    admin_service: Annotated[AdminBancaService, Depends(get_admin_banca_service)],
    version: Annotated[int | None, Query()] = None,
) -> list[FileManifestEntry]:
    logger.info(
        "GET /admin/bancas/{token}/files.start",
        {"decision_token": token, "version": version},
    )
    match admin_service.list_files(token, version):
        case Err(BancaNotFoundError(message=msg)):
            logger.warn("GET /admin/bancas/{token}/files.not_found", {"decision_token": token})
            raise HTTPException(status_code=404, detail=msg)
        case Err(BancaVersionNotFoundError(message=msg)):
            logger.warn(
                "GET /admin/bancas/{token}/files.version_not_found",
                {"decision_token": token, "version": version},
            )
            raise HTTPException(status_code=404, detail=msg)
        case Err(PersistenceError(message=msg)):
            logger.error(
                "GET /admin/bancas/{token}/files.persistence_error",
                {"decision_token": token, "message": msg},
            )
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            logger.info(
                "GET /admin/bancas/{token}/files.end",
                {"decision_token": token, "version": version, "count": len(ok.value)},
            )
            return ok.value


@admin_router.get("/bancas/{token}/files/download")
def download_banca_files(
    token: str,
    admin_service: Annotated[AdminBancaService, Depends(get_admin_banca_service)],
    id: Annotated[list[str], Query()] = [],
    version: Annotated[int | None, Query()] = None,
) -> StreamingResponse:
    logger.info(
        "GET /admin/bancas/{token}/files/download.start",
        {"decision_token": token, "version": version, "ids": id},
    )
    if not id:
        raise HTTPException(status_code=400, detail="No file ids provided.")

    match admin_service.download_files(token, id, version):
        case Err(BancaNotFoundError(message=msg)):
            logger.warn(
                "GET /admin/bancas/{token}/files/download.not_found",
                {"decision_token": token},
            )
            raise HTTPException(status_code=404, detail=msg)
        case Err(BancaVersionNotFoundError(message=msg, version=v)):
            logger.warn(
                "GET /admin/bancas/{token}/files/download.version_not_found",
                {"decision_token": token, "version": v},
            )
            raise HTTPException(status_code=404, detail=msg)
        case Err(DocumentGenerationError(message=msg)):
            logger.error(
                "GET /admin/bancas/{token}/files/download.document_generation_error",
                {"decision_token": token, "message": msg},
            )
            raise HTTPException(status_code=500, detail=msg)
        case Err(PersistenceError(message=msg)):
            logger.error(
                "GET /admin/bancas/{token}/files/download.persistence_error",
                {"decision_token": token, "message": msg},
            )
            raise HTTPException(status_code=503, detail=msg)
        case ok:
            buf, filename, mime = ok.value
            ascii_name = filename.encode("ascii", "replace").decode("ascii").replace("?", "_")
            disposition = f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}"
            logger.info(
                "GET /admin/bancas/{token}/files/download.end",
                {"decision_token": token, "filename": filename},
            )
            return StreamingResponse(
                buf,
                media_type=mime,
                headers={"Content-Disposition": disposition},
            )
