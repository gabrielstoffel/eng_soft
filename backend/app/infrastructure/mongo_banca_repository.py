import uuid
from datetime import datetime, timezone

from app.domain.banca_repository import BancaRepository
from app.domain.errors import (
    BancaAlreadyDecidedError,
    BancaNotEditableError,
    BancaNotFoundError,
    PersistenceError,
)
from app.domain.models import (
    BancaListFilters,
    BancaListItem,
    BancaRecord,
    BancaRequest,
    BancaStatus,
)
from app.infrastructure.database import get_db
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class MongoBancaRepository(BancaRepository):
    def save(self, req: BancaRequest) -> Result[str, PersistenceError]:
        logger.info("save.start", {"ata": req.ata, "student": req.nome.name})
        try:
            token = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            doc = {
                "versions": [
                    {
                        "version": 1,
                        "request": req.model_dump(mode="json"),
                        "created_at": now,
                    }
                ],
                "current_version": 1,
                "decision_token": token,
                "status": "pending",
                "rejection_reason": None,
                "created_at": now,
                "decided_at": None,
            }
            get_db()["bancas"].insert_one(doc)
            logger.info("save.end", {"ata": req.ata, "decision_token": token, "status": "pending"})
            return Ok(token)
        except Exception as e:
            logger.error("save.error", {"ata": req.ata, "message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def find_by_token(
        self, token: str
    ) -> Result[BancaRecord, BancaNotFoundError | PersistenceError]:
        logger.info("find_by_token.start", {"decision_token": token})
        try:
            doc = get_db()["bancas"].find_one({"decision_token": token})
            if doc is None:
                logger.warn("find_by_token.not_found", {"decision_token": token})
                return Err(BancaNotFoundError(message=f"Banca with token {token} not found"))
            record = self._doc_to_record(doc)
            logger.info("find_by_token.end", {"decision_token": token, "status": record.status})
            return Ok(record)
        except Exception as e:
            logger.error("find_by_token.error", {"decision_token": token, "message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def update_decision(
        self, token: str, status: BancaStatus, reason: str | None = None
    ) -> Result[None, BancaNotFoundError | BancaAlreadyDecidedError | PersistenceError]:
        logger.info("update_decision.start", {"decision_token": token, "target_status": status})
        try:
            update_fields: dict = {
                "status": status,
                "decided_at": datetime.now(timezone.utc),
            }
            if reason is not None:
                update_fields["rejection_reason"] = reason

            result = get_db()["bancas"].update_one(
                {"decision_token": token, "status": "pending"},
                {"$set": update_fields},
            )

            if result.matched_count == 0:
                existing = get_db()["bancas"].find_one(
                    {"decision_token": token},
                    {"status": 1},
                )
                if existing is None:
                    logger.warn("update_decision.not_found", {"decision_token": token})
                    return Err(BancaNotFoundError(message=f"Banca with token {token} not found"))
                current_status = existing.get("status", "unknown")
                logger.warn(
                    "update_decision.already_decided",
                    {"decision_token": token, "current_status": current_status},
                )
                return Err(
                    BancaAlreadyDecidedError(
                        message=f"Banca already decided (status={current_status})",
                        current_status=current_status,
                    )
                )

            logger.info("update_decision.end", {"decision_token": token, "status": status})
            return Ok(None)
        except Exception as e:
            logger.error("update_decision.error", {"decision_token": token, "message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def list(
        self, filters: BancaListFilters
    ) -> Result[list[BancaListItem], PersistenceError]:
        logger.info(
            "list.start",
            {
                "status": filters.status,
                "ata": filters.ata,
                "student": filters.student,
                "orientador": filters.orientador,
                "q": filters.q,
            },
        )
        try:
            mongo_filter: dict = {}
            if filters.status is not None:
                mongo_filter["status"] = filters.status
            cursor = get_db()["bancas"].find(mongo_filter).sort("created_at", -1)

            items: list[BancaListItem] = []
            for doc in cursor:
                try:
                    record = self._doc_to_record(doc)
                except Exception as parse_err:
                    logger.warn(
                        "list.skip_invalid_doc",
                        {
                            "decision_token": doc.get("decision_token"),
                            "message": str(parse_err),
                        },
                    )
                    continue
                req = record.request
                if filters.ata is not None and req.ata != filters.ata:
                    continue
                if filters.student and filters.student.lower() not in req.nome.name.lower():
                    continue
                if filters.orientador and filters.orientador.lower() not in req.orientador.name.lower():
                    continue
                if filters.q:
                    q = filters.q.lower()
                    haystack = " ".join(
                        [req.nome.name, req.orientador.name, req.titulo, req.titulo2]
                    ).lower()
                    if q not in haystack:
                        continue
                items.append(
                    BancaListItem(
                        decision_token=record.decision_token,
                        ata=req.ata,
                        student_name=req.nome.name,
                        status=record.status,
                        current_version=record.current_version,
                        tipo=req.tipo,
                        data=req.data,
                        orientador_name=req.orientador.name,
                        created_at=record.created_at,
                    )
                )
            logger.info("list.end", {"count": len(items)})
            return Ok(items)
        except Exception as e:
            logger.error("list.error", {"message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def append_version(
        self, token: str, req: BancaRequest
    ) -> Result[int, BancaNotFoundError | BancaNotEditableError | PersistenceError]:
        logger.info("append_version.start", {"decision_token": token})
        try:
            existing = get_db()["bancas"].find_one({"decision_token": token})
            if existing is None:
                logger.warn("append_version.not_found", {"decision_token": token})
                return Err(BancaNotFoundError(message=f"Banca with token {token} not found"))

            current_status = existing.get("status", "unknown")
            if current_status != "approved":
                logger.warn(
                    "append_version.not_editable",
                    {"decision_token": token, "current_status": current_status},
                )
                return Err(
                    BancaNotEditableError(
                        message=f"Banca cannot be edited (status={current_status})",
                        current_status=current_status,
                    )
                )

            record = self._doc_to_record(existing)
            next_version = record.current_version + 1
            new_entry = {
                "version": next_version,
                "request": req.model_dump(mode="json"),
                "created_at": datetime.now(timezone.utc),
            }
            result = get_db()["bancas"].update_one(
                {"decision_token": token, "status": "approved"},
                {
                    "$push": {"versions": new_entry},
                    "$set": {"current_version": next_version},
                },
            )
            if result.matched_count == 0:
                existing2 = get_db()["bancas"].find_one(
                    {"decision_token": token}, {"status": 1}
                )
                if existing2 is None:
                    return Err(BancaNotFoundError(message=f"Banca with token {token} not found"))
                current2 = existing2.get("status", "unknown")
                logger.warn(
                    "append_version.race_status_changed",
                    {"decision_token": token, "current_status": current2},
                )
                return Err(
                    BancaNotEditableError(
                        message=f"Banca cannot be edited (status={current2})",
                        current_status=current2,
                    )
                )

            logger.info(
                "append_version.end",
                {"decision_token": token, "new_version": next_version},
            )
            return Ok(next_version)
        except Exception as e:
            logger.error("append_version.error", {"decision_token": token, "message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def _doc_to_record(self, doc: dict) -> BancaRecord:
        doc = dict(doc)
        doc.pop("_id", None)
        if "versions" not in doc:
            legacy_request = doc.pop("request", None)
            doc["versions"] = [
                {
                    "version": 1,
                    "request": legacy_request,
                    "created_at": doc.get("created_at"),
                }
            ]
            doc["current_version"] = 1
        elif "current_version" not in doc:
            doc["current_version"] = max(v.get("version", 1) for v in doc["versions"])
        return BancaRecord(**doc)
