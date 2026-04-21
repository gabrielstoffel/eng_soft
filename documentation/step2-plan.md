# Step 2 Plan: SigBah! Implementation

## Context

SigBah! is an academic defense panel management system for UFRGS physics graduate programs (PPGFis/PPGEnFis). Step 1 produced the analysis (use cases, business description). Step 2's goal is to design the architecture, choose the tech stack, and implement the first use cases as working code. The team is comfortable with Python web frameworks.

Focus: **source code + architecture + package diagrams only** (no slides/demo prep).

---

## Tech Stack

| Component       | Choice              | Why                                          |
|-----------------|---------------------|----------------------------------------------|
| Framework       | Flask 3.x           | Lightweight, explicit, team knows it          |
| ORM             | Flask-SQLAlchemy    | Clean model definitions, easy queries         |
| Database        | SQLite (dev)        | Zero setup, swap to PostgreSQL later if needed|
| Templates       | Jinja2              | Built into Flask                              |
| Forms           | Flask-WTF           | Validation + CSRF out of the box              |
| Auth            | Flask-Login          | Simple session-based auth                     |
| Migrations      | Flask-Migrate       | Alembic wrapper for schema changes            |
| CSS             | Bootstrap 5 (CDN)   | Quick UI, no build tools                      |

---

## Architecture: Layered (MVC)

```
views (Blueprints)  -->  services (Business Logic)  -->  models (ORM)
       |                        |
       v                        v
    forms (WTForms)       infrastructure (email stubs, doc stubs)
```

Dependencies flow **left to right / top to bottom only**. Views never touch models directly.

---

## Package Structure

```
sigbah/
  __init__.py              # App factory (create_app)
  config.py                # Dev/Test/Prod configs

  models/
    __init__.py            # db instance
    enums.py               # TipoBanca, StatusBanca, TipoMembro, PPG
    usuario.py             # Usuario model (single table, tipo discriminator)
    banca.py               # Banca + MembroBanca models
    documento.py           # Documento model (stub for Step 3)

  services/
    __init__.py
    banca_service.py       # Create banca, search, get details
    aprovacao_service.py   # Approve/reject banca

  views/
    __init__.py
    auth.py                # Login/logout blueprint
    orientador.py          # UC1: Formalizar Pedido de Banca
    coordenador.py         # UC3: Aprovar Banca
    secretario.py          # UC7: Pesquisar Bancas

  forms/
    __init__.py
    banca_form.py          # FormalizarBancaForm
    aprovacao_form.py      # AprovarBancaForm
    pesquisa_form.py       # PesquisaBancaForm

  templates/
    base.html              # Bootstrap layout
    auth/login.html
    orientador/nova_banca.html
    orientador/minhas_bancas.html
    coordenador/pendentes.html
    coordenador/avaliar.html
    secretario/pesquisa.html
    secretario/detalhes_banca.html

  static/css/              # Custom CSS overrides

  infrastructure/
    __init__.py
    email.py               # Stub: logs instead of sending
    documentos.py          # Stub: placeholder for Step 3

seed.py                    # Populate DB with test data
run.py                     # Entry point
requirements.txt
```

---

## Data Model

**Usuario** - id, nome, email, senha_hash, tipo (ORIENTADOR/COORDENADOR/SECRETARIO), ppg (PPGFIS/PPGENFIS)

**Banca** - id, ppg, tipo_banca (MESTRADO/QUALIFICACAO/DOUTORADO), titulo_trabalho, nome_aluno, matricula_aluno, data_defesa, local, status (PENDENTE/APROVADA/RECUSADA), justificativa_recusa, orientador_id (FK), coordenador_avaliador_id (FK), data_solicitacao, data_avaliacao

**MembroBanca** - id, banca_id (FK), nome, email, instituicao, tipo_membro (TITULAR/SUPLENTE)

**Documento** (stub) - id, banca_id (FK), tipo_documento, gerado_em, enviado, enviado_em

---

## Use Cases to Implement

### UC1: Formalizar Pedido de Banca (Orientador)
- Form with: PPG, tipo_banca, titulo, aluno (nome+matricula), data_defesa, local, membros (titulares + suplentes)
- Validation: min 3 titulares, min 1 suplente, data >= 30 days ahead
- On submit: create Banca (status=PENDENTE) + MembroBanca records
- Stub email notification (log to console)
- Also: "Minhas Bancas" listing for the orientador

### UC7: Pesquisar Bancas (Secretario)
- Search by name (aluno or orientador) and/or date range
- Paginated results (10-50 per page)
- Click a banca to see full details (all fields + members)

### UC3: Aprovar Banca (Coordenador)
- List pending bancas (status=PENDENTE)
- View banca details + approve/reject form
- If rejected: require justificativa
- On submit: update status, record coordenador + timestamp
- Stub notification to orientador (log to console)

---

## Simplifications to Document

1. **Auth simplified** - pre-seeded users, no self-registration, no UFRGS institutional login
2. **Emails simulated** - UC2/UC10 log to console instead of sending SMTP
3. **Document generation deferred** - UC4 not implemented, Documento model exists as stub
4. **Single PPG template** - both PPGFis/PPGEnFis use same rules, no PPG-specific customization
5. **Members as free text** - not selected from a database of professors
6. **No room scheduling** - out of scope (IEF building separate system)
7. **No file upload/download** - only banca metadata stored

---

## Implementation Order

### 1. Project skeleton
- Git repo, `sigbah/` package, app factory, config, `run.py`, `requirements.txt`
- `base.html` with Bootstrap
- Verify: `python run.py` shows a page

### 2. Data layer
- All models (Usuario, Banca, MembroBanca, Documento stub, enums)
- Flask-Migrate initial migration
- `seed.py` with test data (3 users, ~5 bancas in various statuses)

### 3. Auth
- Flask-Login setup, login/logout routes
- Role-based decorators (`@orientador_required`, etc.)

### 4. UC1 - Formalizar Pedido de Banca
- `FormalizarBancaForm`, `banca_service.criar_banca()`, orientador blueprint + templates

### 5. UC3 - Aprovar Banca
- `AprovarBancaForm`, `aprovacao_service.avaliar_banca()`, coordenador blueprint + templates

### 6. UC7 - Pesquisar Bancas
- `PesquisaBancaForm`, search methods in `banca_service`, secretario blueprint + templates

### 7. Polish
- Cross-test all use cases, fix bugs, ensure seed.py creates clean demo state

---

## Verification

1. `python run.py` starts the app on localhost
2. Login as orientador -> create a banca -> see it in "Minhas Bancas"
3. Login as coordenador -> see pending banca -> approve it
4. Login as secretario -> search for the banca by name and by date -> view details
5. Login as coordenador -> reject a different banca with justificativa
6. Login as orientador -> see status updated on "Minhas Bancas"

---

## Key Files (source of truth)
- `/ufrgs/engsoft/TemplateRelatorio.docx.md` - Full use case specs
- `/ufrgs/engsoft/homework-definition-step2.md` - Step 2 requirements
- `/ufrgs/engsoft/summary.md` - Interview with stakeholders (business rules)
