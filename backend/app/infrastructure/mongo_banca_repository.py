from datetime import datetime, timezone

from app.domain.banca_repository import BancaRepository
from app.domain.errors import PersistenceError
from app.domain.models import BancaRequest
from app.infrastructure.database import get_db
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class MongoBancaRepository(BancaRepository):
    def save(self, req: BancaRequest) -> Result[None, PersistenceError]:
        logger.info("save.start", {"ata": req.ata, "student": req.nome.name})
        try:
            doc = req.model_dump(mode="json")
            doc["created_at"] = datetime.now(timezone.utc)
            get_db()["bancas"].insert_one(doc)
            logger.info("save.end", {"ata": req.ata})
            return Ok(None)
        except Exception as e:
            logger.error("save.error", {"ata": req.ata, "message": str(e)})
            return Err(PersistenceError(message=str(e)))
