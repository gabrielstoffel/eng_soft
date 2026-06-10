import io

from app.application import banca_validation, document_service
from app.domain.banca_repository import BancaRepository
from app.domain.errors import (
    BancaNotEditableError,
    BancaNotFoundError,
    BancaVersionNotFoundError,
    DocumentGenerationError,
    PersistenceError,
    ValidationError,
)
from app.domain.models import (
    BancaAdminDetail,
    BancaListFilters,
    BancaListItem,
    BancaRequest,
    BancaUpdateResponse,
    FileManifestEntry,
)
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class AdminBancaService:
    def __init__(self, repo: BancaRepository) -> None:
        self._repo = repo

    def list_bancas(self, filters: BancaListFilters) -> Result[list[BancaListItem], PersistenceError]:
        logger.info(
            "admin.list_bancas.start",
            {
                "status": filters.status,
                "ata": filters.ata,
                "student": filters.student,
                "orientador": filters.orientador,
                "q": filters.q,
            },
        )
        match self._repo.list(filters):
            case Err() as err:
                logger.error("admin.list_bancas.error", {"message": err.error.message})
                return err
            case ok:
                logger.info("admin.list_bancas.end", {"count": len(ok.value)})
                return Ok(ok.value)

    def get_detail(self, token: str) -> Result[BancaAdminDetail, BancaNotFoundError | PersistenceError]:
        logger.info("admin.get_detail.start", {"decision_token": token})
        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value
        detail = BancaAdminDetail(
            decision_token=record.decision_token,
            status=record.status,
            rejection_reason=record.rejection_reason,
            approval_observation=record.approval_observation,
            current_version=record.current_version,
            versions=record.versions,
            ata=record.ata,
            ppg=record.ppg,
            created_at=record.created_at,
            decided_at=record.decided_at,
        )
        logger.info(
            "admin.get_detail.end",
            {"decision_token": token, "versions": len(record.versions)},
        )
        return Ok(detail)

    def update_banca(
        self, token: str, new_req: BancaRequest
    ) -> Result[
        BancaUpdateResponse,
        ValidationError | BancaNotFoundError | BancaNotEditableError | PersistenceError,
    ]:
        # No-op contract: equality is computed via Pydantic-normalized JSON dump
        # of the latest stored version vs. the submitted request. Both sides go
        # through `BancaRequest.model_dump(mode="json")` so dates/times round-trip
        # identically. New scalar field types should be checked against this contract.
        logger.info("admin.update_banca.start", {"decision_token": token})

        errors = banca_validation.validate_edit(new_req)
        if errors:
            logger.info("admin.update_banca.validation_failed", {"decision_token": token, "errors": errors})
            return Err(ValidationError(message="; ".join(errors), details=errors))

        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value

        if record.status != "approved":
            logger.warn(
                "admin.update_banca.not_editable",
                {"decision_token": token, "current_status": record.status},
            )
            return Err(
                BancaNotEditableError(
                    message=f"Banca cannot be edited (status={record.status})",
                    current_status=record.status,
                )
            )

        latest = record.request
        if latest.model_dump(mode="json") == new_req.model_dump(mode="json"):
            logger.info(
                "admin.update_banca.no_op",
                {"decision_token": token, "current_version": record.current_version},
            )
            return Ok(
                BancaUpdateResponse(
                    created_new_version=False,
                    current_version=record.current_version,
                )
            )

        match self._repo.append_version(token, new_req):
            case Err() as err:
                logger.error(
                    "admin.update_banca.append_error",
                    {"decision_token": token, "message": err.error.message},
                )
                return err
            case ok:
                logger.info(
                    "admin.update_banca.end",
                    {"decision_token": token, "new_version": ok.value},
                )
                return Ok(
                    BancaUpdateResponse(
                        created_new_version=True,
                        current_version=ok.value,
                    )
                )

    def _resolve_version_request(
        self, token: str, version: int | None
    ) -> Result[
        tuple[BancaRequest, int],
        BancaNotFoundError | BancaVersionNotFoundError | PersistenceError,
    ]:
        """Return the (request, ata) for the requested version of a banca."""
        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value

        target_version = version if version is not None else record.current_version
        selected = next((v for v in record.versions if v.version == target_version), None)
        if selected is None:
            logger.warn(
                "admin.version_not_found",
                {"decision_token": token, "version": target_version},
            )
            return Err(
                BancaVersionNotFoundError(
                    message=f"Version {target_version} not found for banca {token}",
                    version=target_version,
                )
            )
        return Ok((selected.request, record.ata))

    def list_files(
        self, token: str, version: int | None = None
    ) -> Result[
        list[FileManifestEntry],
        BancaNotFoundError | BancaVersionNotFoundError | PersistenceError,
    ]:
        logger.info("admin.list_files.start", {"decision_token": token, "version": version})
        match self._resolve_version_request(token, version):
            case Err() as err:
                return err
            case ok:
                req, _ata = ok.value
        manifest = document_service.file_manifest(req)
        logger.info(
            "admin.list_files.end",
            {"decision_token": token, "version": version, "count": len(manifest)},
        )
        return Ok(manifest)

    def download_files(
        self, token: str, ids: list[str], version: int | None = None
    ) -> Result[
        tuple[io.BytesIO, str, str],
        BancaNotFoundError | BancaVersionNotFoundError | DocumentGenerationError | PersistenceError,
    ]:
        logger.info(
            "admin.download_files.start",
            {"decision_token": token, "version": version, "ids": ids},
        )
        match self._resolve_version_request(token, version):
            case Err() as err:
                return err
            case ok:
                req, ata = ok.value

        match document_service.generate_files(req, ids, ata):
            case Err() as err:
                return err
            case ok:
                logger.info(
                    "admin.download_files.end",
                    {"decision_token": token, "filename": ok.value[1]},
                )
                return Ok(ok.value)
