# SigBah! — Architecture Reference

## Stack

- **Backend**: Python + FastAPI, managed with `uv`
- **Frontend**: Vite + React (plain JS, no TypeScript)
- **Database**: MongoDB
- **Mail**: Postfix → Mailpit (local capture only)
- **Infra**: Docker Compose (mail + MongoDB only — backend and frontend run locally)

## Backend Architecture

Clean architecture with four layers. Dependencies point inward only.

```
api/          → HTTP only: parse request, inject deps, map Result → HTTP status
application/  → Use cases: orchestrate services, return Result
domain/       → Contracts (ABCs) and typed errors — no framework knowledge
infrastructure/ → Concrete implementations (MongoDB, SMTP)
```

### Key files

| File                                           | Role                                                                   |
| ---------------------------------------------- | ---------------------------------------------------------------------- |
| `app/domain/models.py`                         | Pydantic models (BancaRequest, BancaResponse, MemberInfo, StudentInfo) |
| `app/domain/errors.py`                         | Typed errors: DocumentGenerationError, EmailError, PersistenceError    |
| `app/domain/banca_repository.py`               | BancaRepository ABC                                                    |
| `app/application/banca_service.py`             | BancaService — owns the full create use case                           |
| `app/infrastructure/mongo_banca_repository.py` | MongoDB impl of BancaRepository                                        |
| `app/deps.py`                                  | Centralized DI — all Depends providers live here                       |
| `app/logger.py`                                | Structured logger wrapper                                              |

## Patterns

### Result pattern

All service methods return `Result[T, E]` — never raise exceptions at the service boundary.

```python
from app.result import Ok, Err, Result

def do_something() -> Result[str, SomeError]:
    try:
        return Ok("value")
    except Exception as e:
        return Err(SomeError(message=str(e)))
```

Match on results in callers:

```python
match do_something():
    case Err() as err:
        return err
    case ok:
        value = ok.value
```

### Typed domain errors

Errors are dataclasses in `app/domain/errors.py`, all inheriting `BancaError`. The router maps each type to a specific HTTP status code.

### Dependency injection

`app/deps.py` holds module-level singletons wired to their concrete implementations. The router receives services via `Depends()`.

### Structured logging

Use `get_logger(__name__)` from `app/logger.py`. Every log call takes `event_kind` (dot-separated path) and `data` (dict).

```python
from app.logger import get_logger
logger = get_logger(__name__)

logger.info("some_function.start", {"message": value})
logger.error("some_function.error", {"message": str(e)})
```

Root logger is set to WARNING; `app.*` is set to INFO — third-party noise is suppressed automatically.

## Running locally

```bash
# Infrastructure (MongoDB + mail)
cd infrastructure && docker compose up -d

# Backend (.env in backend/ holds credentials)
cd backend && uv run uvicorn main:app --reload

# Frontend
cd frontend && npm run dev
```

## Environment variables

Backend reads from `backend/.env` (gitignored):

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=sigbah
MONGO_USERNAME=admin
MONGO_PASSWORD=secret
SMTP_HOST=localhost
SMTP_PORT=2525
```
