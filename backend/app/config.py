import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "sigbah")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
FROM_ADDRESS = os.getenv("SMTP_FROM", "sigbah@sigbah.local")
COORDENADOR_EMAIL = os.getenv("COORDENADOR_EMAIL", "coordenador@if.ufrgs.br")
SECRETARY_EMAIL = os.getenv("SECRETARY_EMAIL", "secretario@ufrgs.br")
