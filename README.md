# SigBah!

Sistema de Gestão de Bancas Acadêmicas — PPGFis / PPGEnFis (UFRGS)

## Dependencies

- **Docker** — for the mail infrastructure
- **uv** — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **Node.js 20+** and **npm** — for the frontend

## Running

Each component runs in its own terminal.

### 1. Mail infrastructure

```bash
cd infrastructure
docker compose up -d
```

Starts Mailpit (email capture) and Postfix (SMTP relay).

### 2. Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

## URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| Email inbox (Mailpit) | http://localhost:8025 |

## Mail flow

```
backend → localhost:2525 → postfix → mailpit:1025 → http://localhost:8025
```

All outgoing email is captured by Mailpit — nothing reaches the internet.

## Stop

```bash
cd infrastructure
docker compose down
```
