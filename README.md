# SigBah!

Sistema de Gestão de Bancas Acadêmicas — PPGFis / PPGEnFis (UFRGS)

## Local Email Setup

Postfix relays outgoing mail to Mailpit, which captures everything for inspection.

```
backend → localhost:2525 → postfix → mailpit:1025 → http://localhost:8025
```

### 1. Start the mail containers

```bash
cd infrastructure
docker compose up -d
```

### 2. Send a test email

```bash
cd backend
uv run main.py
```

### 3. View the email

Open [http://localhost:8025](http://localhost:8025) in your browser.

### Stop

```bash
cd infrastructure
docker compose down
```
