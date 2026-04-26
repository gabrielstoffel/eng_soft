from pymongo import MongoClient
from pymongo.database import Database

from app.config import MONGO_DB, MONGO_PASSWORD, MONGO_URI, MONGO_USERNAME

_client: MongoClient | None = None


def get_db() -> Database:
    global _client
    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            username=MONGO_USERNAME or None,
            password=MONGO_PASSWORD or None,
        )
    return _client[MONGO_DB]
