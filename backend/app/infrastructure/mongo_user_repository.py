from app.domain.errors import PersistenceError
from app.domain.models import AdminUserRecord
from app.domain.user_repository import UserRepository
from app.infrastructure.database import get_db
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class MongoUserRepository(UserRepository):
    def find_by_username(self, username: str) -> Result[AdminUserRecord | None, PersistenceError]:
        try:
            doc = get_db()["admin_users"].find_one({"username": username})
            if doc is None:
                return Ok(None)
            return Ok(
                AdminUserRecord(
                    username=doc["username"],
                    ppg=doc["ppg"],
                    password_hash=doc["password_hash"],
                )
            )
        except Exception as e:
            logger.error("user.find_by_username.error", {"username": username, "message": str(e)})
            return Err(PersistenceError(message=str(e)))

    def seed(self, users: list[AdminUserRecord]) -> Result[None, PersistenceError]:
        try:
            collection = get_db()["admin_users"]
            collection.create_index("username", unique=True)
            created = []
            for user in users:
                result = collection.update_one(
                    {"username": user.username},
                    {"$setOnInsert": user.model_dump()},
                    upsert=True,
                )
                if result.upserted_id is not None:
                    created.append(user.username)
            logger.info("user.seed.end", {"created": created})
            return Ok(None)
        except Exception as e:
            logger.error("user.seed.error", {"message": str(e)})
            return Err(PersistenceError(message=str(e)))
