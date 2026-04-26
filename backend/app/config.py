import os

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
FROM_ADDRESS = os.getenv("SMTP_FROM", "sigbah@sigbah.local")
COORDENADOR_EMAIL = os.getenv("COORDENADOR_EMAIL", "coordenador@if.ufrgs.br")
SECRETARY_EMAIL = os.getenv("SECRETARY_EMAIL", "secretario@ufrgs.br")
