import logging
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.api.admin_router import admin_router
from app.api.router import router
from app.deps import get_auth_service
from app.logger import get_logger

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("app").setLevel(logging.INFO)

_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed the per-PPG admin users (idempotent). Don't crash the app if the DB
    # is unreachable at boot — log and continue.
    try:
        get_auth_service().seed_default_users()
    except Exception as e:  # pragma: no cover - defensive
        _logger.error("startup.seed_admin_users.error", {"message": str(e)})
    yield


app = FastAPI(title="SigBah!", description="Banca document generation and email service", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
