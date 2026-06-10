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
    def next_ata(self, ppg: str, tipo: int) -> int:
        """Atomically increment and return the next ata number for ppg+tipo."""
        result = get_db()["ata_counters"].find_one_and_update(
            {"ppg": ppg, "tipo": tipo},
            {"$inc": {"last_ata": 1}},
            upsert=True,
            return_document=True,
        )
        return result["last_ata"]

    def save(self, req: BancaRequest) -> Result[str, PersistenceError]:
        logger.info("save.start", {"student": req.nome.name, "ppg": req.ppg})
        try:
            ata = self.next_ata(req.ppg, req.tipo)
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
                "approval_observation": None,
                "ata": ata,
                "ppg": req.ppg,
                "created_at": now,
                "decided_at": None,
            }
            get_db()["bancas"].insert_one(doc)
            logger.info("save.end", {"ata": ata, "decision_token": token})
            return Ok(token)
        except Exception as e:
            logger.error("save.error", {"message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def find_by_token(self, token: str) -> Result[BancaRecord, BancaNotFoundError | PersistenceError]:
        logger.info("find_by_token.start", {"decision_token": token})
        try:
            doc = get_db()["bancas"].find_one({"decision_token": token})
            if doc is None:
                return Err(BancaNotFoundError(message=f"Banca with token {token} not found"))
            record = self._doc_to_record(doc)
            return Ok(record)
        except Exception as e:
            logger.error("find_by_token.error", {"decision_token": token, "message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def update_decision(
        self, token: str, status: BancaStatus, reason: str | None = None, observation: str | None = None
    ) -> Result[None, BancaNotFoundError | BancaAlreadyDecidedError | PersistenceError]:
        logger.info("update_decision.start", {"decision_token": token, "target_status": status})
        try:
            update_fields: dict = {
                "status": status,
                "decided_at": datetime.now(timezone.utc),
            }
            if reason is not None:
                update_fields["rejection_reason"] = reason
            if observation is not None:
                update_fields["approval_observation"] = observation

            result = get_db()["bancas"].update_one(
                {"decision_token": token, "status": "pending"},
                {"$set": update_fields},
            )

            if result.matched_count == 0:
                existing = get_db()["bancas"].find_one({"decision_token": token}, {"status": 1})
                if existing is None:
                    return Err(BancaNotFoundError(message=f"Banca with token {token} not found"))
                current_status = existing.get("status", "unknown")
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

    def list(self, filters: BancaListFilters) -> Result[list[BancaListItem], PersistenceError]:
        logger.info("list.start", {"filters": filters.model_dump(exclude_none=True)})
        try:
            mongo_filter: dict = {}
            if filters.status is not None:
                mongo_filter["status"] = filters.status
            if filters.ppg is not None:
                mongo_filter["ppg"] = filters.ppg
            cursor = get_db()["bancas"].find(mongo_filter).sort("created_at", -1)

            items: list[BancaListItem] = []
            for doc in cursor:
                try:
                    record = self._doc_to_record(doc)
                except Exception:
                    continue
                req = record.request
                if filters.ata is not None and record.ata != filters.ata:
                    continue
                if filters.student and filters.student.lower() not in req.nome.name.lower():
                    continue
                if filters.orientador and filters.orientador.lower() not in req.orientador.name.lower():
                    continue
                if filters.q:
                    q = filters.q.lower()
                    haystack = f"{req.nome.name} {req.orientador.name} {req.titulo} {req.titulo2 or ''}"
                    if q not in haystack.lower():
                        continue
                items.append(
                    BancaListItem(
                        decision_token=record.decision_token,
                        ata=record.ata,
                        student_name=req.nome.name,
                        status=record.status,
                        current_version=record.current_version,
                        tipo=req.tipo,
                        data=req.data,
                        orientador_name=req.orientador.name,
                        ppg=record.ppg,
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
                return Err(BancaNotFoundError(message=f"Banca with token {token} not found"))

            current_status = existing.get("status", "unknown")
            if current_status != "approved":
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
            get_db()["bancas"].update_one(
                {"decision_token": token, "status": "approved"},
                {
                    "$push": {"versions": new_entry},
                    "$set": {"current_version": next_version},
                },
            )
            logger.info("append_version.end", {"decision_token": token, "new_version": next_version})
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
        if "current_version" not in doc:
            doc["current_version"] = max(v.get("version", 1) for v in doc["versions"])
        doc.setdefault("ata", 0)
        doc.setdefault("ppg", "ppgfis")
        doc.setdefault("approval_observation", None)
        return BancaRecord(**doc)
