import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "sigbah")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
FROM_ADDRESS = os.getenv("SMTP_FROM", "sigbah@sigbah.local")

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

# --- Admin auth ---
AUTH_SECRET = os.getenv("AUTH_SECRET", "dev-insecure-secret-change-me")
AUTH_TOKEN_TTL_SECONDS = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", str(8 * 60 * 60)))

# Seed credentials for the two per-PPG admin users (created on startup if absent).
PPGFIS_ADMIN_USERNAME = os.getenv("PPGFIS_ADMIN_USERNAME", "admin.fis")
PPGFIS_ADMIN_PASSWORD = os.getenv("PPGFIS_ADMIN_PASSWORD", "ppgfis123")
PPGENFIS_ADMIN_USERNAME = os.getenv("PPGENFIS_ADMIN_USERNAME", "admin.enfis")
PPGENFIS_ADMIN_PASSWORD = os.getenv("PPGENFIS_ADMIN_PASSWORD", "ppgenfis123")
