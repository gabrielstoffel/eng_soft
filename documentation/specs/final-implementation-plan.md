# Plano Final de Implementação — SigBah!

**Data:** 10/06/2026  
**Fontes:** `spec_novas_features_2026-05-22.md`, `Res.02_2025_CPG-BANCAS_assinado.pdf`, `formulario.bancasajustado.doc`, reunião 22/05/2026 (transcrição + anotações manuscritas), decisões do grupo.

---

## 1. Decisões Finais do Grupo

| Decisão | Detalhe |
|---|---|
| Status "aprovado sob condição" | **Descartado**. Adicionar campo de observação (texto livre) na aprovação. |
| Separação por PPG | Frontend com rotas separadas (`/ppgfis/...`, `/ppgenfis/...`), backend com núcleo compartilhado + perfil por PPG. |
| Observação no email ao coordenador | Os dois campos livres (desempenho + justificativa) devem aparecer no email ao coordenador. |
| Formulário espelha o `.doc` oficial | Campos do formulário oficial: Bolsista CNPq, PPG por membro, comentários, modalidade + videoconferência condicional. |
| Local / videoconferência | Segue estrutura do formulário oficial: modalidade (presencial/híbrida/remota) → campos condicionais + flag `remoto` por membro. |
| Engine de documentos | **Adiada**. Manter `criaBancas.py` (fpdf2) por enquanto. |
| Data e horário | São **sugestões** do orientador (não compromisso final). Labels: "Data sugerida" / "Horário sugerido". |
| Uploads | Armazenados via **GridFS** (MongoDB). Tipos: lattes_cv, texto, press_release, artigo. |

---

## 2. Requisitos Consolidados

### 2.1 Correções de Conformidade (Resolução 02/2025)

| # | Requisito | Situação Atual | Ação |
|---|---|---|---|
| C1 | Suplente interno **obrigatório** | `supl_int: optional` | Mudar para `required` |
| C2 | Antecedência mínima: 20 dias (mestrado), 30 dias (qualif./doutorado) | Sem validação | Adicionar validação backend + aviso frontend |
| C3 | Currículo Lattes dos membros externos (PDF obrigatório) | Sem upload | Implementar upload de anexos |
| C4 | PDF da dissertação/exame/tese (obrigatório) | Sem upload | Implementar upload |
| C5 | Press release (obrigatório mestrado e doutorado, não qualificação) | Sem upload | Implementar upload |
| C6 | Artigo publicado (obrigatório doutorado) | Sem upload | Implementar upload |

### 2.2 Mudanças no Formulário

| # | Requisito | Ação |
|---|---|---|
| F1 | Remover campo `ata` | Backend gera automaticamente (sequência por tipo+ppg) |
| F2 | Remover campo `data_convite` | Remover do modelo e frontend |
| F3 | Modalidade da defesa: presencial / híbrida / remota | Novo campo `modalidade` |
| F4 | Sala de preferência (se presencial ou híbrida) — texto livre | Campo condicional |
| F5 | Link de videoconferência (se remota ou híbrida) — texto livre, opcional | Campo condicional |
| F6 | Data e horário são **sugestões** (labels atualizados) | Renomear labels |
| F7 | Participação remota **por membro** (bool) | Novo campo `remoto` em `MemberInfo` |
| F8 | Comentários sobre o desempenho do estudante (texto livre) | Novo campo |
| F9 | Justificativa para a escolha dos membros (texto livre) | Novo campo |
| F10 | Título em inglês **não obrigatório** | Remover `required` |
| F11 | Bolsista CNPq (sim/não) + nível por membro | Novos campos em `MemberInfo` |
| F12 | PPG dos membros internos é implícito (= ppg da banca) | Sem campo no formulário |
| F13 | Upload de anexos (ver C3–C6) | Nova seção |

### 2.3 Campos PPGEnFis (ocultos no PPGFis)

| # | Campo | Aplica-se a | Obrigatório |
|---|---|---|---|
| E1 | Nome COMPLETO do aluno | Aluno | Sim |
| E2 | CPF | Aluno | Sim |
| E3 | Data de nascimento | Aluno | Sim |
| E4 | E-mail do aluno | Aluno | Sim |
| E5 | Lattes (link) | Membros | Obrigatório |
| E6 | Conclusão de doutorado: instituição + ano | Membros | Sim |

### 2.4 Decisão do Coordenador

| # | Requisito | Ação |
|---|---|---|
| D1 | Observação na aprovação (texto livre opcional) | Novo campo no endpoint + `BancaRecord` |
| D2 | Email ao coordenador: remover data/horário/local | Alterar `build_petition_html` |
| D3 | Email ao coordenador: incluir comentário desempenho + justificativa membros | Alterar `build_petition_html` |

### 2.5 Ata Automática

| # | Requisito | Ação |
|---|---|---|
| A1 | Número sequencial por tipo de banca + PPG, gerado pelo sistema | Counter atômico no MongoDB |

### 2.6 Email para Gerência na Aprovação

| # | Requisito | Ação |
|---|---|---|
| G1 | Ao aprovar, email à gerência (GIF) com data, horário, local, CC alias CPG | Novo template + disparo no `approve` |

### 2.7 Envio de Convites/Pareceres (Secretaria)

| # | Requisito | Ação |
|---|---|---|
| S1 | Botão por membro para enviar carta-convite | Endpoint + botão admin |
| S2 | Botão "Enviar todos" convites | Endpoint batch |
| S3 | Status por item: enviado / não enviado / data | Modelo + UI |
| S4 | Botão por examinador para enviar parecer | Endpoint + botão admin |
| S5 | Botão "Enviar todos" pareceres | Endpoint batch |

### 2.8 Separação por PPG

| # | Requisito | Ação |
|---|---|---|
| P1 | Campo `ppg` em `BancaRequest`/`BancaRecord` | Novo campo |
| P2 | Perfil de PPG no backend (emails, campos, validações) | `ppg_profiles.py` |
| P3 | Frontend: rotas `/ppgfis/new`, `/ppgenfis/new` | Nova estrutura de routing |
| P4 | Componentes compartilhados, diferenças declaradas por config | Config de campos por PPG |
| P5 | Admin filtra por PPG | Filtro na lista |

---

## 3. Modelo de Dados — Alterações

### 3.1 `BancaRequest`

```python
class BancaRequest(BaseModel):
    ppg: Literal["ppgfis", "ppgenfis"]
    nome: StudentInfo
    tipo: Literal[1, 2, 3]
    data: date                                 # data SUGERIDA
    horario: time                              # horário SUGERIDO
    # REMOVIDOS: ata, data_convite
    modalidade: Literal["presencial", "hibrida", "remota"]
    sala_preferencia: str | None = None        # obrigatório se presencial/híbrida
    link: str | None = None                    # texto livre (se remota/híbrida, opcional)
    orientador: MemberInfo
    coorientador: MemberInfo | None = None
    externo1: MemberInfo | None = None
    externo2: MemberInfo | None = None
    interno1: MemberInfo | None = None
    interno2: MemberInfo | None = None
    supl_int: MemberInfo | None = None         # required PPGFis, optional PPGEnFis (per profile)
    supl_ext: MemberInfo | None = None
    titulo: str
    titulo2: str | None = None                 # opcional
    comentario_desempenho: str | None = None
    justificativa_membros: str | None = None
```

### 3.2 `StudentInfo`

```python
class StudentInfo(BaseModel):
    gender: Literal[0, 1]
    name: str
    # PPGEnFis (opcionais no modelo, obrigatórios por perfil):
    cpf: str | None = None
    birth_date: date | None = None
    email: EmailStr | None = None
```

### 3.3 `MemberInfo`

```python
class MemberInfo(BaseModel):
    gender: Literal[0, 1]
    name: str
    institution: str
    location: str
    lang: Literal["pt", "en"]
    email: EmailStr | None = None
    remoto: bool = False                       # NOVO — participará remotamente?
    ppg: str | None = None                     # PPG do membro (membros locais)
    bolsista_cnpq: bool | None = None
    nivel_cnpq: str | None = None              # "1A", "1B", "1C", "1D", "2"
    # PPGEnFis (opcionais no modelo, obrigatórios por perfil):
    lattes: str | None = None                  # URL Lattes
    doctorate_institution: str | None = None
    doctorate_year: int | None = None
```

### 3.4 `BancaRecord`

```python
class BancaRecord(BaseModel):
    versions: list[BancaVersion]
    current_version: int
    decision_token: str
    status: BancaStatus                        # "pending" | "approved" | "rejected"
    rejection_reason: str | None = None
    approval_observation: str | None = None    # NOVO — texto livre na aprovação
    ata: int                                   # NOVO — gerado automaticamente
    ppg: str                                   # NOVO
    created_at: datetime
    decided_at: datetime | None = None
    invite_status: dict[str, InviteStatus] | None = None  # NOVO — por membro/doc
```

### 3.5 `ApproveRequest`

```python
class ApproveRequest(BaseModel):
    observation: str | None = None  # texto livre opcional
```

### 3.6 Contadores de Ata

```
Collection MongoDB: "ata_counters"
Documento: { "tipo": 1, "ppg": "ppgfis", "last_ata": 20 }
Operação atômica: findAndModify → incrementa e retorna próximo valor
```

### 3.7 Anexos

```python
class AttachmentInfo(BaseModel):
    kind: Literal["lattes_cv", "texto", "press_release", "artigo"]
    filename: str
    member_role: str | None = None   # Para lattes_cv: qual membro externo
    uploaded_at: datetime

# Storage: GridFS (MongoDB) — referenciado por decision_token + kind + role
```

---

## 4. Perfil de PPG

```python
@dataclass
class PpgProfile:
    ppg_id: str                        # "ppgfis" | "ppgenfis"
    name: str                          # "PPGFís" | "PPGEnFis"
    coordenador_email: str
    secretary_email: str
    cpg_alias_email: str               # CC nos emails
    gerencia_email: str                # GIF — agendamento de sala
    default_video_link: str | None     # PPGFis: link MCONF fixo; PPGEnFis: None
    required_student_fields: list[str] # PPGEnFis: ["cpf", "birth_date", "email"]
    required_member_fields: list[str]  # PPGEnFis: ["lattes", "doctorate_institution", "doctorate_year"]
    titulo_en_required: bool           # False para ambos
```

---

## 5. Alterações nos Emails

### 5.1 Email ao Coordenador (petição)

**Remover:** data, horário, local/link  
**Adicionar:** comentário desempenho, justificativa membros

```
Assunto: [SigBah!] Novo Pedido de Banca — {aluno}

Corpo:
- Aluno, Tipo, Título (PT), Title (EN se preenchido)
- Membros (tabela: função, nome, instituição, remoto?)
- Comentários sobre o desempenho do estudante: {texto}
- Justificativa para a escolha dos membros: {texto}
- Botão: "Acessar página de decisão"
```

### 5.2 Email à Gerência (GIF) — NOVO

Disparado na aprovação. CC para alias CPG do PPG.

```
Assunto: [SigBah!] Solicitação de Agendamento — Banca #{ata}

Corpo:
- Data sugerida: {data} às {horário}
- Local de preferência: {sala_preferencia}
- Modalidade: {presencial/híbrida/remota}
- Tipo: {tipo}
- Aluno: {nome}
- Orientador: {orientador}
- "Solicitamos o agendamento. Favor responder para {cpg_alias}."
```

### 5.3 Email ao Secretário (aprovação)

Mantém documentos em ZIP. Adiciona observação do coordenador se presente.

### 5.4 Aprovação — Endpoint

`POST /banca/decide/:token/approve` aceita body:
```json
{ "observation": "aguardando nova versão do press release" }
```

Observação salva em `BancaRecord.approval_observation` e incluída no email ao secretário.

---

## 6. Estrutura de Diretórios

### Backend

```
backend/app/
├── config/
│   ├── __init__.py              # Constantes (SMTP, Mongo, etc.)
│   └── ppg_profiles.py         # Perfis PPGFis e PPGEnFis
├── domain/
│   ├── models.py                # Modelos atualizados
│   ├── banca_repository.py
│   └── errors.py
├── application/
│   ├── banca_service.py         # Submissão, decisão, email gerência
│   ├── petition_service.py      # Templates de email HTML
│   ├── email_service.py         # SMTP sender (+ suporte CC)
│   ├── document_service.py      # Geração de docs (fpdf2 existente)
│   ├── invite_service.py        # NOVO — envio convites/pareceres
│   └── admin_banca_service.py
├── infrastructure/
│   ├── mongo_banca_repository.py
│   └── database.py
├── api/
│   ├── router.py                # Endpoints submissão/decisão/upload
│   └── admin_router.py          # Endpoints admin + envio convites
└── deps.py
```

### Frontend

```
frontend/src/
├── App.jsx                          # Router com rotas por PPG
├── pages/
│   ├── LandingPage.tsx              # NOVO — escolher PPG
│   ├── ppgfis/
│   │   └── NewBancaPage.tsx         # Wrapper com config PPGFis
│   ├── ppgenfis/
│   │   └── NewBancaPage.tsx         # Wrapper com config PPGEnFis
│   ├── NewBanca/
│   │   ├── form/
│   │   │   ├── BancaForm.tsx
│   │   │   ├── BancaGeneralSection.tsx
│   │   │   ├── BancaCompositionSection.tsx
│   │   │   ├── BancaModalitySection.tsx    # NOVO
│   │   │   ├── BancaCommentsSection.tsx    # NOVO
│   │   │   └── BancaAttachmentsSection.tsx # NOVO
│   │   ├── config.ts
│   │   └── ppg-config.ts           # NOVO — campos por PPG
│   ├── DecisionPage.jsx
│   └── admin/...
├── components/
│   ├── MemberField.tsx              # Estendido (+remoto, bolsista, ppg, lattes...)
│   └── ...
└── types/
    └── new-banca.ts                 # Schemas atualizados
```

### Rotas

```
/                         → Landing (escolha de PPG)
/ppgfis/new               → Formulário PPGFis
/ppgenfis/new             → Formulário PPGEnFis
/decide/:token            → Decisão do coordenador
/admin                    → Lista de bancas (filtro por PPG)
/admin/banca/:token       → Detalhe + envio convites/pareceres
```

---

## 7. Regras de Validação (Implementadas no Backend)

### PPGFis (Resolução 02/2025)

| Regra | Detalhe | Enforcement |
|---|---|---|
| Antecedência mínima | Mestrado ≥ 20 dias; Qualificação/Doutorado ≥ 30 dias | `_validate_antecedencia` |
| Suplente interno | Obrigatório todos os tipos | `_enforce_tipo_rules` via perfil |
| Composição | Mestrado: orient + 1ext + 2int; Qualif: 4+; Dout: orient + 2ext + 2int | `_enforce_tipo_rules` via perfil |
| Lattes externo | PDF obrigatório (upload) | Pendente (validação de anexos) |
| Texto PDF | Obrigatório | Pendente (validação de anexos) |
| Press release | Obrigatório Mestrado e Doutorado | Pendente (validação de anexos) |
| Artigo | Obrigatório Doutorado | Pendente (validação de anexos) |
| Título inglês | Opcional | Campo `titulo2: str | None` |
| Modalidade | `sala_preferencia` obrigatório se presencial/híbrida | `_validate_modalidade_fields` |
| Campos PPGEnFis | Não exigidos | `_validate_ppg_specific_fields` (skip) |

### PPGEnFis (Resoluções 2022/2023)

| Regra | Detalhe | Enforcement |
|---|---|---|
| Antecedência mínima | Mestrado ≥ 20; Qualif ≥ 30; **Doutorado ≥ 40 dias** | `_validate_antecedencia` |
| Suplente interno | Opcional | `_enforce_tipo_rules` via perfil |
| Composição | Mestrado/Qualif: 3 mín; Dout: 4 mín | `_enforce_tipo_rules` via perfil |
| Aluno: CPF | Obrigatório | `_validate_ppg_specific_fields` |
| Aluno: data nascimento | Obrigatório | `_validate_ppg_specific_fields` |
| Aluno: email | Obrigatório | `_validate_ppg_specific_fields` |
| Membros: Lattes (link) | Obrigatório | `_validate_ppg_specific_fields` |
| Membros: inst. conclusão dout. | Obrigatório | `_validate_ppg_specific_fields` |
| Membros: ano conclusão dout. | Obrigatório | `_validate_ppg_specific_fields` |
| Título inglês | Opcional | Campo `titulo2: str | None` |
| Modalidade | `sala_preferencia` obrigatório se presencial/híbrida | `_validate_modalidade_fields` |
| PPG dos membros internos | Implícito (= ppg da banca, não há campo no formulário) | — |

---

## 8. Fases de Implementação

### Fase 1 — Fundação (modelo + conformidade)

| # | Task | Arquivos |
|---|---|---|
| 1.1 | Adicionar `ppg` ao modelo e repositório | `models.py`, `mongo_banca_repository.py` |
| 1.2 | Criar `ppg_profiles.py` | `config/` |
| 1.3 | Remover `ata` e `data_convite` do `BancaRequest` | `models.py`, frontend schemas |
| 1.4 | Auto-geração de ata (counter atômico por tipo+ppg) | `mongo_banca_repository.py` |
| 1.5 | `supl_int` obrigatório | `models.py`, `config.ts` |
| 1.6 | Validação antecedência mínima (20/30 dias) | `models.py` |
| 1.7 | `titulo2` opcional | `models.py`, frontend |

### Fase 2 — Formulário Atualizado

| # | Task | Arquivos |
|---|---|---|
| 2.1 | Modalidade (presencial/híbrida/remota) + campos condicionais | `BancaGeneralSection.tsx` ou `BancaModalitySection.tsx`, `models.py` |
| 2.2 | `remoto: bool` por membro | `MemberField.tsx`, `MemberInfo` |
| 2.3 | Campos texto livre: desempenho + justificativa | `BancaCommentsSection.tsx`, `models.py` |
| 2.4 | Bolsista CNPq + nível por membro | `MemberField.tsx`, `MemberInfo` |
| 2.5 | PPG por membro local | `MemberField.tsx`, `MemberInfo` |
| 2.6 | Campos PPGEnFis em `StudentInfo` (CPF, nascimento, email) | `BancaGeneralSection.tsx`, `models.py` |
| 2.7 | Campos PPGEnFis em `MemberInfo` (lattes, doctorate_info) | `MemberField.tsx`, `models.py` |
| 2.8 | Config de campos por PPG (visibilidade/obrigatoriedade) | `ppg-config.ts`, `ppg_profiles.py` |

### Fase 3 — Rotas PPG Separadas

| # | Task | Arquivos |
|---|---|---|
| 3.1 | Landing page (escolha de PPG) | Nova página |
| 3.2 | Rotas `/ppgfis/new` e `/ppgenfis/new` | `App.jsx` |
| 3.3 | Pages PPG que instanciam form com config própria | `pages/ppgfis/`, `pages/ppgenfis/` |
| 3.4 | `ppg` incluído no payload de submissão | Frontend → API |
| 3.5 | Admin: filtro por PPG | `AdminBancaList.jsx` |

### Fase 4 — Emails e Decisão

| # | Task | Arquivos |
|---|---|---|
| 4.1 | Email coordenador: remover data/local, incluir campos livres | `petition_service.py` |
| 4.2 | Endpoint aprovação aceitar `ApproveRequest` com observation | `router.py`, `banca_service.py`, `models.py` |
| 4.3 | Email gerência na aprovação (dados agendamento + CC alias CPG) | `petition_service.py`, `banca_service.py` |
| 4.4 | `email_service.py` suportar CC | `email_service.py` |
| 4.5 | Observação incluída no email ao secretário | `petition_service.py` |

### Fase 5 — Upload de Anexos ✅

| # | Task | Arquivos | Status |
|---|---|---|---|
| 5.1 | Endpoint upload + storage (GridFS) | `router.py` | ✅ Implementado |
| 5.2 | Validação de anexos obrigatórios por tipo+ppg | `banca_service.py` | Pendente |
| 5.3 | Frontend: `BancaAttachmentsSection.tsx` | Nova seção | ✅ Implementado |
| 5.4 | Lattes vinculado ao membro externo (por role) | UI + backend | Pendente |

### Fase 6 — Envio de Convites/Pareceres

| # | Task | Arquivos |
|---|---|---|
| 6.1 | Modelo de status de envio por membro/documento | `models.py` |
| 6.2 | Endpoint enviar convite individual | `admin_router.py`, `invite_service.py` |
| 6.3 | Endpoint enviar todos convites | `admin_router.py` |
| 6.4 | Endpoint enviar parecer individual | `admin_router.py` |
| 6.5 | Endpoint enviar todos pareceres | `admin_router.py` |
| 6.6 | Frontend: botões + status (enviado/pendente/data) | `AdminBancaDetail.jsx` |

---

## 9. Pontos Pendentes (Confirmar com Cliente)

1. Aliases de email exatos por PPG (coordenador, CPG, gerência GIF) — configurar no `.env`.
2. ~~Link MCONF fixo do PPGFis~~ → **Resolvido**: link é texto livre, orientador digita o que quiser.
3. ~~Regras de composição PPGEnFis~~ → **Resolvido**: extraído das Resoluções 18/2022, 07/2023, 15/2023.
4. ~~Storage: GridFS vs. filesystem~~ → **Resolvido**: GridFS.
5. Momento da ata: atribuída na **submissão** (orientador vê imediatamente).

---

## 10. Critérios de Aceitação

1. Orientador acessa `/ppgfis/new`, preenche formulário sem ata/data_convite, submete com sucesso.
2. `supl_int` obrigatório — form não submete sem ele.
3. Data < 20 dias (mestrado) é rejeitada com mensagem.
4. Modalidade "híbrida" exige sala de preferência E programa de videoconferência.
5. Cada membro tem checkbox "remoto" — informação aparece nos documentos.
6. Email ao coordenador não contém data/local, mas contém desempenho + justificativa.
7. Coordenador aprova com observação — salva no record, aparece no email ao secretário.
8. Ata gerada sequencialmente (última mestrado=20 → próxima=21).
9. Na aprovação, email enviado à gerência com data/horário/local.
10. Admin filtra bancas por PPG.
11. Secretário clica "Enviar convite" por membro → email disparado → status "enviado" com data.
12. `/ppgenfis/new` exibe CPF, nascimento, Lattes que não aparecem em `/ppgfis/new`.

---

## Apêndice A — Regras de Composição PPGEnFis (Resoluções 2022/2023)

### Mestrado (Resolução 18/2022)

- Mínimo 3 doutores, máx 1 do Programa, ≥1 externo à UFRGS
- Suplentes: opcionais (até 1 por titular)
- Antecedência: 20 dias
- Dados por membro: Instituição, e-mail, CPF, data+inst conclusão doutorado

### Qualificação (Resolução 07/2023)

- Mínimo 3 doutores, máx 1 do Programa, ≥1 externo à UFRGS
- Suplentes: opcionais
- Antecedência: 30 dias

### Doutorado (Resolução 15/2023)

- Mínimo 4 doutores, máx 1 do Programa, ≥2 externos ao IF (≥1 ext UFRGS)
- Externos UFRGS devem ter concluído ≥1 orientação de Doutorado na área
- Suplentes: opcionais
- Antecedência: **40 dias**
- Artigo Qualis A obrigatório

---

## Apêndice B — ROLES_BY_TIPO por PPG

### PPGFis

```python
ROLES_BY_TIPO_PPGFIS = {
    1: {  # Mestrado
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "hidden",
        "interno1": "required",
        "interno2": "required",
        "supl_int": "required",
        "supl_ext": "optional",
    },
    2: {  # Qualificação
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "optional",
        "interno1": "required",
        "interno2": "required",
        "supl_int": "required",
        "supl_ext": "optional",
    },
    3: {  # Doutorado
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "required",
        "interno1": "required",
        "interno2": "required",
        "supl_int": "required",
        "supl_ext": "optional",
    },
}
```

### PPGEnFis

```python
ROLES_BY_TIPO_PPGENFIS = {
    1: {  # Mestrado — min 3 (max 1 programa, ≥1 ext UFRGS)
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "optional",
        "interno1": "required",
        "interno2": "optional",
        "supl_int": "optional",
        "supl_ext": "optional",
    },
    2: {  # Qualificação — min 3 (max 1 programa, ≥1 ext UFRGS)
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "optional",
        "interno1": "required",
        "interno2": "optional",
        "supl_int": "optional",
        "supl_ext": "optional",
    },
    3: {  # Doutorado — min 4 (max 1 programa, ≥2 ext IF, ≥1 ext UFRGS)
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "required",
        "interno1": "required",
        "interno2": "optional",
        "supl_int": "optional",
        "supl_ext": "optional",
    },
}
```

---

## Apêndice C — Correções ao Plano Principal

### C.1 Link de Videoconferência

Campo de link é **texto livre** (orientador digita MCONF, Zoom, etc.). Visível apenas se `modalidade` == `"remota"` ou `"hibrida"`. Sem select de programa.

### C.2 Aliases de Email via `.env`

Configurados em `backend/.env.example` (copiar para `.env`):

```env
# PPGFis
PPGFIS_COORDENADOR_EMAIL=coordenador.fis@if.ufrgs.br
PPGFIS_SECRETARY_EMAIL=secretario.fis@if.ufrgs.br
PPGFIS_CPG_ALIAS_EMAIL=cpgfis@if.ufrgs.br
PPGFIS_GERENCIA_EMAIL=gerencia@if.ufrgs.br

# PPGEnFis
PPGENFIS_COORDENADOR_EMAIL=coordenador.enfis@if.ufrgs.br
PPGENFIS_SECRETARY_EMAIL=secretario.enfis@if.ufrgs.br
PPGENFIS_CPG_ALIAS_EMAIL=ppgenfis@if.ufrgs.br
PPGENFIS_GERENCIA_EMAIL=gerencia@if.ufrgs.br
```

Lidos por `app/config/ppg_profiles.py` via `os.getenv()` com defaults. Arquivo `.env` é gitignored — cada dev copia de `.env.example`.

### C.3 Antecedência por PPG + Tipo

| PPG | Mestrado | Qualificação | Doutorado |
|---|---|---|---|
| PPGFis | 20 dias | 30 dias | 30 dias |
| PPGEnFis | 20 dias | 30 dias | **40 dias** |

### C.4 `BancaRequest` modelo final corrigido

```python
class BancaRequest(BaseModel):
    ppg: Literal["ppgfis", "ppgenfis"]
    nome: StudentInfo
    tipo: Literal[1, 2, 3]
    data: date                                 # sugerida
    horario: time                              # sugerido
    modalidade: Literal["presencial", "hibrida", "remota"]
    sala_preferencia: str | None = None        # obrigatório se presencial/híbrida
    link: str | None = None                    # texto livre (se remota/híbrida)
    orientador: MemberInfo
    coorientador: MemberInfo | None = None
    externo1: MemberInfo | None = None
    externo2: MemberInfo | None = None
    interno1: MemberInfo | None = None
    interno2: MemberInfo | None = None
    supl_int: MemberInfo | None = None         # required PPGFis, optional PPGEnFis
    supl_ext: MemberInfo | None = None
    titulo: str
    titulo2: str | None = None                 # opcional
    comentario_desempenho: str | None = None
    justificativa_membros: str | None = None
```

### C.5 Uploads (GridFS)

- Endpoint: `POST /banca/{token}/attachments` (multipart form-data)
- Storage: GridFS (`fs.files` + `fs.chunks`) para binários, collection `attachments` para metadata
- Tipos aceitos: `lattes_cv`, `texto`, `press_release`, `artigo`
- Obrigatoriedade por tipo de banca:
  - Lattes externos: sempre obrigatório
  - Texto PDF: sempre obrigatório
  - Press release: mestrado e doutorado
  - Artigo: doutorado apenas
- Frontend: `BancaAttachmentsSection.tsx` com inputs condicionais por tipo
- Dependência: `python-multipart` (adicionada ao projeto)
