# Re-export for backward compatibility
from app.config import (  # noqa: F401
    FROM_ADDRESS,
    FRONTEND_BASE_URL,
    MONGO_DB,
    MONGO_PASSWORD,
    MONGO_URI,
    MONGO_USERNAME,
    SMTP_HOST,
    SMTP_PORT,
)
from app.config.ppg_profiles import get_profile  # noqa: F401

# Legacy aliases — use get_profile(ppg) instead
COORDENADOR_EMAIL = get_profile("ppgfis").coordenador_email
SECRETARY_EMAIL = get_profile("ppgfis").secretary_email
