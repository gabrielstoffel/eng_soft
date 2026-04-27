import uuid
from datetime import datetime, timezone

from app.domain.banca_repository import BancaRepository
from app.domain.errors import BancaAlreadyDecidedError, BancaNotFoundError, PersistenceError
from app.domain.models import BancaRecord, BancaRequest, BancaStatus
from app.infrastructure.database import get_db
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class MongoBancaRepository(BancaRepository):
    def save(self, req: BancaRequest) -> Result[str, PersistenceError]:
        logger.info("save.start", {"ata": req.ata, "student": req.nome.name})
        try:
            token = str(uuid.uuid4())
            doc = {
                "request": req.model_dump(mode="json"),
                "decision_token": token,
                "status": "pending",
                "rejection_reason": None,
                "created_at": datetime.now(timezone.utc),
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
            doc.pop("_id", None)
            record = BancaRecord(**doc)
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
