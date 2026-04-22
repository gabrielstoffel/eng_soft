# Step 2 Plan: SigBah! Implementation

## Context

SigBah! is an academic defense panel management system for UFRGS physics graduate programs (PPGFis/PPGEnFis). Step 1 produced the analysis (use cases, business description). Step 2's goal is to design the architecture, choose the tech stack, and implement the first use cases as working code.

Focus: **source code + architecture + package diagrams only** (no slides/demo prep).

---

## Tech Stack

| Component       | Choice                  | Why                                              |
|-----------------|-------------------------|--------------------------------------------------|
| Backend         | ASP.NET Core 8 Web API  | C# controllers, mature ecosystem, strong typing  |
| ORM             | Entity Framework Core   | Code-first, migrations, LINQ queries             |
| Database        | PostgreSQL              | Full-featured relational DB                      |
| DB Provider     | Npgsql.EFCore           | EF Core provider for PostgreSQL                  |
| Auth            | JWT (Bearer tokens)     | Standard for SPA + API separation                |
| Frontend        | React 18 + Vite         | Fast dev server, HMR, TypeScript support         |
| Language (FE)   | TypeScript              | Type safety across the frontend                  |
| UI Library      | MUI (Material UI) v5    | Rich pre-built components, fast to build forms   |
| HTTP Client     | Axios                   | Clean API for REST calls from React              |
| Routing (FE)    | React Router v6         | SPA routing                                      |
| Email           | Gmail SMTP              | Free, zero signup, App Password auth             |

---

## Architecture: Separated API + SPA

```
┌─────────────────────────┐     HTTP/JSON      ┌──────────────────────────┐
│     sigbah-web (SPA)    │ ◄──────────────────► │   sigbah-api (ASP.NET)  │
│  React + Vite + MUI     │                      │   Controllers           │
│  TypeScript             │                      │     → Services          │
│                         │                      │       → EF Core / DB    │
└─────────────────────────┘                      └──────────────────────────┘
```

**Backend layers** (dependencies flow top to bottom):

- **Controllers** — HTTP endpoints, request/response mapping, `[Authorize]` attributes
- **Services** — Business logic (create banca, approve, search)
- **Models/Entities** — EF Core entity classes
- **DTOs** — Request/response data transfer objects
- **Infrastructure** — DbContext, JWT config, Gmail SMTP email service

**Frontend layers**:

- **Pages** — Route-level components (one per screen)
- **Components** — Shared UI (Layout, ProtectedRoute)
- **API** — Axios client with JWT interceptor, typed API call functions
- **Contexts** — Auth state (JWT storage, current user)
- **Types** — TypeScript interfaces matching backend DTOs

---

## Package Structure

```
sigbah-api/
  SigBah.Api/
    Program.cs                    # App entry point, DI, middleware
    appsettings.json              # Connection string, JWT settings, SMTP config

    Controllers/
      AuthController.cs           # Login endpoint → returns JWT
      BancaController.cs          # UC1: create banca, list my bancas
      AprovacaoController.cs      # UC3: list pending, approve/reject
      PesquisaController.cs       # UC7: search bancas, view details

    Services/
      IBancaService.cs + BancaService.cs
      IAprovacaoService.cs + AprovacaoService.cs
      IAuthService.cs + AuthService.cs
      IEmailService.cs + EmailService.cs

    Models/
      Entities/
        Usuario.cs
        Banca.cs
        MembroBanca.cs
        Documento.cs              # Stub for Step 3
      Enums/
        TipoBanca.cs
        StatusBanca.cs
        TipoMembro.cs
        TipoPPG.cs
        TipoUsuario.cs

    DTOs/
      LoginRequest.cs
      LoginResponse.cs
      CriarBancaRequest.cs
      BancaResponse.cs
      AvaliarBancaRequest.cs
      PesquisaBancaRequest.cs

    Data/
      SigBahDbContext.cs          # EF Core DbContext
      Migrations/                 # EF Core migrations

    Infrastructure/
      JwtSettings.cs
      SmtpSettings.cs             # Gmail SMTP config (host, port, credentials)

  SigBah.Api.csproj

sigbah-web/
  src/
    main.tsx                      # Vite entry point
    App.tsx                       # Router setup

    api/
      client.ts                   # Axios instance with JWT interceptor
      bancaApi.ts                 # Banca-related API calls
      authApi.ts                  # Auth API calls

    components/
      Layout.tsx                  # AppBar, navigation, auth context
      ProtectedRoute.tsx          # Route guard by role

    pages/
      Login.tsx
      orientador/
        NovaBanca.tsx             # UC1: create banca form
        MinhasBancas.tsx          # List my bancas
      coordenador/
        Pendentes.tsx             # UC3: list pending bancas
        AvaliarBanca.tsx          # Approve/reject form
      secretario/
        PesquisaBancas.tsx        # UC7: search form + results
        DetalhesBanca.tsx         # View banca details

    types/
      index.ts                   # TypeScript interfaces matching DTOs

    contexts/
      AuthContext.tsx             # JWT storage + user state

  index.html
  vite.config.ts
  tsconfig.json
  package.json
```

---

## Data Model

**Usuario** - Id, Nome, Email, SenhaHash, Tipo (ORIENTADOR/COORDENADOR/SECRETARIO), Ppg (PPGFIS/PPGENFIS)

**Banca** - Id, Ppg, TipoBanca (MESTRADO/QUALIFICACAO/DOUTORADO), TituloTrabalho, NomeAluno, MatriculaAluno, CursoAluno, DataDefesa (date+time), Local (free text), Status (PENDENTE/APROVADA/RECUSADA), JustificativaRecusa, OrientadorId (FK), CoordenadorAvaliadorId (FK), DataSolicitacao, DataAvaliacao

**MembroBanca** - Id, BancaId (FK), Nome, Email, Instituicao, TipoMembro (TITULAR/SUPLENTE)

**Documento** (stub) - Id, BancaId (FK), TipoDocumento, GeradoEm, Enviado, EnviadoEm

---

## Use Cases to Implement

### UC1: Formalizar Pedido de Banca (Orientador)
- MUI form with: PPG, tipo_banca, titulo, aluno (nome + matrícula + curso), data_defesa (date + time), local (free text), membros (titulares + suplentes with nome, email, instituição)
- Validation: min 3 titulares, min 1 suplente, data >= 30 days ahead
- On submit: POST to API → create Banca (status=PENDENTE) + MembroBanca records
- Email notification to Coordenador AND Secretário via Gmail SMTP (UC2) — HTML email with banca details table
- Also: "Minhas Bancas" page listing the orientador's bancas
- After rejection: orientador must create a new banca from scratch (no clone/resubmit)

### UC7: Pesquisar Bancas (Secretario)
- Secretário sees only bancas from their own PPG
- Search by name (aluno or orientador) and/or date range
- Paginated results using MUI DataGrid (10-50 per page)
- Click a banca to see full details (all fields + members)

### UC3: Aprovar Banca (Coordenador)
- MUI table listing pending bancas (status=PENDENTE) from coordenador's PPG
- View banca details + approve/reject form (approve/reject only — no editing banca data)
- If rejected: require justificativa
- On submit: PUT to API → update status, record coordenador + timestamp
- Email notification to orientador via Gmail SMTP (UC10) — HTML email with result + justificativa if rejected
- Notification email includes direct link to evaluation page (NFR: coordenador can evaluate without leaving their inbox)

---

## Design Decisions

1. **Tipo de banca**: Mestrado / Qualificação / Doutorado (from business description, not TCC/Dissertação/Tese from UC spec)
2. **Email notifications**: HTML emails with styled info table (banca details, link to system)
3. **Email targets**: UC1 → Coordenador + Secretário (UC2). UC3 → Orientador (UC10)
4. **UC3 scope**: Approve/reject only — coordenador cannot modify banca data
5. **UC7 scope**: Secretário sees only bancas from their own PPG
6. **Navigation**: Role-specific landing pages after login (e.g., /orientador/minhas-bancas, /coordenador/pendentes)
7. **Local field**: Free text (orientador types room name, address, "Google Meet", etc.)
8. **Resubmission**: After rejection, orientador creates a new banca from scratch
9. **Notification email includes direct link** to evaluation page for coordenador

---

## Simplifications to Document

1. **Auth simplified** - pre-seeded users, no self-registration, no UFRGS institutional login
2. **Emails via Gmail SMTP** - using a Gmail account with App Password for sending notifications (convites, divulgacao, etc.)
3. **Document generation deferred** - UC4 not implemented, Documento model exists as stub
4. **Single PPG template** - both PPGFis/PPGEnFis use same rules, no PPG-specific customization
5. **Members as free text** - not selected from a database of professors
6. **No room scheduling** - out of scope (IEF building separate system)
7. **No file upload/download** - only banca metadata stored

---

## Implementation Order

### 1. Project skeleton
- `dotnet new webapi` for API, `npm create vite@latest` for frontend
- Configure CORS on API to allow frontend origin
- Basic health check endpoint, verify both dev servers run
- **Verify**: `dotnet run` serves API on :5000, `npm run dev` serves frontend on :5173

### 2. Data layer
- EF Core entities (Usuario, Banca, MembroBanca, Documento stub, enums)
- SigBahDbContext + PostgreSQL connection string
- Initial migration + seed data (3 users, ~5 bancas in various statuses)
- **Verify**: `dotnet ef database update` creates tables, seed runs

### 3. Auth
- JWT generation on login (AuthController + AuthService)
- `[Authorize]` attributes + role-based policies (Orientador, Coordenador, Secretario)
- React AuthContext + ProtectedRoute, Axios JWT interceptor
- Login page with MUI form
- **Verify**: Login returns token, protected endpoints reject unauthenticated requests

### 4. UC1 - Formalizar Pedido de Banca
- BancaController.Create + BancaService.CriarBanca
- NovaBanca.tsx with MUI form: PPG, tipo, titulo, aluno, data, local, members
- MinhasBancas.tsx with MUI table

### 5. UC3 - Aprovar Banca
- AprovacaoController + AprovacaoService
- Pendentes.tsx + AvaliarBanca.tsx

### 6. UC7 - Pesquisar Bancas
- PesquisaController + search methods in BancaService
- PesquisaBancas.tsx + DetalhesBanca.tsx

### 7. Polish
- Cross-test all use cases, fix bugs, ensure seed data creates clean demo state

---

## Verification

1. `dotnet run` starts API, `npm run dev` starts frontend
2. Login as orientador -> create a banca -> see it in "Minhas Bancas"
3. Login as coordenador -> see pending banca -> approve it
4. Login as secretario -> search for the banca by name and by date -> view details
5. Login as coordenador -> reject a different banca with justificativa
6. Login as orientador -> see status updated on "Minhas Bancas"

---

## Gmail SMTP Configuration

Prerequisites: enable 2-Step Verification on the Gmail account, then generate an **App Password** (Google Account → Security → App Passwords).

`appsettings.json` (credentials go in user-secrets or env vars, not committed):
```json
{
  "SmtpSettings": {
    "Host": "smtp.gmail.com",
    "Port": 587,
    "Username": "sigbah.ufrgs@gmail.com",
    "EnableSsl": true
  }
}
```

The App Password is stored via `dotnet user-secrets set "SmtpSettings:Password" "xxxx xxxx xxxx xxxx"` or via environment variable `SmtpSettings__Password`.

---

## Key Files (source of truth)
- `/ufrgs/engsoft/TemplateRelatorio.docx.md` - Full use case specs
- `/ufrgs/engsoft/homework-definition-step2.md` - Step 2 requirements
- `/ufrgs/engsoft/summary.md` - Interview with stakeholders (business rules)
