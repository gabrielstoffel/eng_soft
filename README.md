# SigBah!

Sistema de Gestão de Bancas Acadêmicas — PPGFis / PPGEnFis (UFRGS)

## Dependencies

- **Docker** — for the mail infrastructure
- **uv** — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **Node.js 20+** and **npm** — for the frontend

## Running

Each component runs in its own terminal.

### 1. Infrastructure

```bash
cd infrastructure
docker compose up -d
```

Starts MongoDB (persistence), Mailpit (email capture) and Postfix (SMTP relay).

### 2. Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

Backend reads from `backend/.env` (gitignored):

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=sigbah
MONGO_USERNAME=admin
MONGO_PASSWORD=password
SMTP_HOST=localhost
SMTP_PORT=2525
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

## URLs

| Service               | URL                       |
| --------------------- | ------------------------- |
| Frontend              | http://localhost:5173     |
| API                   | http://localhost:8000     |
| Email inbox (Mailpit) | http://localhost:8025     |
| MongoDB               | mongodb://localhost:27017 |

## Pages

| Route                 | Audience              | Purpose                                                                                     |
| --------------------- | --------------------- | ------------------------------------------------------------------------------------------- |
| `/`                   | Servidor / orientador | Submit a new banca petition                                                                 |
| `/decide/:token`      | Coordenador           | Approve or reject a pending petition (link arrives by e-mail)                               |
| `/admin`              | Servidor              | Search bancas in the database                                                               |
| `/admin/banca/:token` | Servidor              | View full state, edit (when status = aceita), and download/regenerate documents per version |

Approved bancas are stored as an ordered list of versions; editing creates a new version only when content changes. Each version exposes a manifest of individual PDFs (Ata, Cartas de Convite, Pareceres, Cartaz, Relatoria de Avaliação) that can be downloaded one at a time or as a zip of selected files.

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
