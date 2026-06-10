# Revisão Adversarial — Implementação vs. Plano Final (commit `b4bcb8a`)

**Data da revisão:** 10/06/2026
**Escopo:** `feat: final spec impl 1st try` (`b4bcb8a`) contra `documentation/specs/final-implementation-plan.md`
**Objetivo deste documento:** guiar um próximo agente a refinar o código. Cada achado tem severidade, evidência (`arquivo:linha`), por que é um problema, e o que fazer.

> **Como usar:** ataque os achados na ordem das seções (🔴 Showstoppers → 🟠 Alto → 🟡 Médio → 🟢 Limpeza). Os dois showstoppers quebram o fluxo de aprovação inteiro — nada adianta antes deles. Não confie no "✅ Implementado" do plano: a Fase 5 está marcada como pronta mas a validação não existe, e a geração de documentos está quebrada.

---

## Status da correção (passada de refino)

| Achado | Estado | Notas |
|---|---|---|
| §2.1 `document_service` lê campos removidos | ✅ corrigido | `ata` agora vem do record; `data_convite`→`None`; `local_banca`→`sala_preferencia`; verificado gerando docs+zip |
| §2.2 validadores re-disparam na leitura | ✅ corrigido | regras movidas para `app/application/banca_validation.py`; modelo agora é só estrutural; reconstrução de banca com data passada não re-valida |
| §3.1 DecisionPage + `ata` no summary | ✅ corrigido | `BancaSummary` expõe `ata`/`ppg`; página mostra modalidade/sala/link/comentários/campos PPGEnFis/`remoto` |
| §3.2 anexos: validação + segurança | 🟡 parcial | token verificado, content-type PDF exigido, `member_role` gravado, sem truncação silenciosa. **Falta** enforcement de "todos obrigatórios presentes" (precisa de passo de finalização — ver nota) |
| §3.3 Fase 6 (convites/pareceres) | ✅ implementado | `InviteStatus` + `BancaRecord.invite_status`; `invite_service.py`; `GET/POST /admin/bancas/{token}/invites[/send]`; UI "Envio de Convites e Pareceres" em `AdminBancaDetail.jsx` (envio por membro, "enviar todos", status enviado/pendente/data). Cobre S1–S5 e critério #11 |
| §3.4 filtro admin por PPG | ✅ corrigido | endpoint aceita `ppg`; UI do admin tem seletor de programa |
| §3.5 emails antes do update atômico | ✅ corrigido | `approve` faz a transição `pending→approved` primeiro |
| §4.1 `bolsista_cnpq=false`→`null` | ✅ corrigido | `?? null` |
| §4.2 `PpgProfile` incompleto | ✅ corrigido | `required_student_fields`/`required_member_fields`/`titulo_en_required`/`default_video_link` + validação dirigida pelo perfil |
| §4.3 regras de composição da Resolução | ⏸️ não feito | só presença de slot; regras semânticas (max 1 programa, ≥1 ext UFRGS, Qualis A…) seguem pendentes |
| §4.4 `remoto` nos documentos | ✅ corrigido | instituição anotada com "(participação remota)" no tuple passado ao `criaBancas` |
| §4.5 injeção de HTML nos emails | ✅ corrigido | `html.escape()` em todo dado de usuário interpolado |
| §5 `config.py` morto / `.env`/`lang` | ✅ corrigido | `app/config.py` removido; `.env.example` alinhado; `lang` restrito a `pt`/`en` |
| §5 estado de anexos via `window` global | ⏸️ não feito | melhoria de baixa prioridade; exige mover para o estado do RHF |

**Nota §3.2:** o upload é seguro e tipado, mas a obrigatoriedade ("toda banca de doutorado precisa de artigo") ainda não bloqueia nada, porque uploads acontecem em chamada separada após a submissão. Enforcement completo precisa de um passo de finalização (ex.: `POST /banca/{token}/finalize` que verifique o conjunto de anexos contra `required_attachment_kinds(tipo)`), ou mover o upload para dentro do submit multipart.

---

## 0. Veredito em uma frase

O modelo de dados foi reescrito conforme a spec (campos novos, perfis por PPG, ata automática, anexos via GridFS), **mas as camadas que consomem o modelo não foram atualizadas junto** — a geração de documentos e a página de decisão ainda leem campos que foram removidos, e a validação de domínio foi colocada dentro do modelo Pydantic de forma que ela re-dispara na leitura do banco. O resultado: **submeter funciona, aprovar não, e bancas viram ilegíveis com o tempo.**

---

## 1. Matriz Plano × Implementação

Legenda: ✅ feito · 🟡 parcial · ❌ ausente/quebrado

| Fase | Item | Estado | Nota |
|---|---|---|---|
| 1 | `ppg` no modelo/repo, ata automática (counter atômico), `supl_int` obrigatório (PPGFis), antecedência, `titulo2` opcional | ✅ | `next_ata` atômico OK; `ata`/`data_convite` removidos do request |
| 2 | Modalidade + condicionais, `remoto`, comentários, bolsista CNPq, PPG por membro, campos PPGEnFis | 🟡 | UI e modelo existem; `remoto`/bolsista **não chegam nos documentos**; `bolsista=false` vira `null` |
| 3 | Landing, rotas `/ppgfis/new` e `/ppgenfis/new`, `ppg` no payload | 🟡 | Rotas OK; **filtro admin por PPG não existe** (P5) |
| 4 | Email coordenador sem data/local + campos livres; `ApproveRequest.observation`; email gerência; CC; obs ao secretário | ✅ | Bem feito, **mas** ver §2.1 (geração de doc quebra antes do email sair) e §3.5 (ordem de envio) |
| 5 | Upload GridFS + seção frontend | 🟡 | Endpoint e UI existem; **validação de obrigatórios (5.2) e lattes por membro (5.4) ausentes**; upload inseguro |
| 6 | Envio de convites/pareceres (S1–S5) | ❌ | **Totalmente ausente.** Sem `invite_service`, sem endpoints, `invite_status` foi removido do modelo |

### Critérios de aceitação (§10 do plano)

| # | Critério | Passa? |
|---|---|---|
| 1 | Submete `/ppgfis/new` sem ata/data_convite | ✅ |
| 2 | `supl_int` obrigatório bloqueia | ✅ (PPGFis) |
| 3 | Data < antecedência rejeitada | ✅ na submissão / ⚠️ ver §2.2 |
| 4 | Híbrida exige sala **E** programa de videoconferência | ❌ link é opcional (conflito spec, ver §3.6) |
| 5 | `remoto` aparece **nos documentos** | ❌ só no email do coordenador, não nos PDFs |
| 6 | Email coordenador sem data/local, com desempenho+justificativa | ✅ |
| 7 | Aprovar com observação salva e vai ao secretário | ✅ (se a geração de doc não quebrasse — ver §2.1) |
| 8 | Ata sequencial | ✅ |
| 9 | Email à gerência na aprovação | ✅ (idem §2.1) |
| 10 | Admin filtra por PPG | ❌ (ver §3.4) |
| 11 | Secretário envia convite por membro com status | ❌ (Fase 6 ausente) |
| 12 | `/ppgenfis/new` exibe CPF/nascimento/Lattes | ✅ |

---

## 2. 🔴 Showstoppers

### 2.1 `document_service` lê campos que não existem mais no `BancaRequest`

**Evidência:** `backend/app/application/document_service.py:45-47`
```python
data_convite=req.data_convite,   # REMOVIDO do modelo (F2)
ata=req.ata,                     # REMOVIDO (F1 — ata agora vive em BancaRecord)
local_banca=req.local_banca,     # REMOVIDO (substituído por modalidade/sala_preferencia)
```
Também `generate_documents` (`:167`) e `_zip_filename` (`:91`) usam `req.ata`.

**Por que é crítico:** todo `approve()` chama `generate_documents(req)` (`banca_service.py:103`). Como `BancaRequest` não tem mais esses atributos, isso levanta `AttributeError`, capturado como `DocumentGenerationError` → **HTTP 500 em toda aprovação**. O mesmo quebra o download de arquivos no admin (`generate_files`). A Fase 5 do plano marca isto como "✅ Implementado", mas o caminho está quebrado.

**O que fazer:**
- Atualizar a assinatura de `_build_banca`/`Banca(...)` para o novo modelo. `ata` deve ser passado de fora (vem do `BancaRecord`, não do request) — propague `record.ata` até `document_service`.
- Mapear `local_banca` → `sala_preferencia`/`modalidade`/`link` conforme o que `criaBancas.Banca` espera. Decidir o que vai no documento quando modalidade é remota/híbrida.
- Remover `data_convite` (não existe mais conceito de data de convite no modelo).
- Cobrir com um teste que de fato gere documentos a partir de um `BancaRequest` novo.

### 2.2 Validadores de domínio re-disparam na leitura do banco (e dependem de `date.today()`)

**Evidência:** `backend/app/domain/models.py:84-95` (`_validate_antecedencia`), `:71-82`, `:97-127`. Todos são `@model_validator(mode="after")`.

**Por que é crítico:** validadores Pydantic `mode="after"` rodam em **toda** construção do modelo — inclusive ao reconstruir do Mongo. O fluxo `_doc_to_record` (`mongo_banca_repository.py:202`) faz `BancaRecord(**doc)`, que valida `BancaVersion` → `BancaRequest` → roda `_validate_antecedencia` de novo contra `date.today()`.

Consequências concretas:
- Depois que a data sugerida da defesa passa, a banca **deixa de ser legível**: `find_by_token` cai no `except` → `PersistenceError` (HTTP 503); `list` engole no `try/except: continue` (`mongo_banca_repository.py:128-131`) e a banca **some silenciosamente** da lista do admin.
- `PUT /admin/bancas/{token}` (editar versão) re-valida antecedência contra hoje; editar uma banca aprovada perto/depois da data falha mesmo sendo dado histórico válido.

**O que fazer:** separar **validação de submissão** de **invariantes do modelo**. Opções:
- Mover `_validate_antecedencia`, `_enforce_tipo_rules`, `_validate_ppg_specific_fields`, `_validate_modalidade_fields` para o `BancaService.submit_petition` (e para o update do admin, com a regra apropriada), deixando o modelo só com tipos. É o que combina com a arquitetura limpa do projeto (regra de negócio na camada `application`, não no `domain` model).
- Ou guardar a data de referência junto da banca e validar contra ela — mas a separação de camadas é mais limpa e o `CLAUDE.md` empurra para isso.

---

## 3. 🟠 Alto

### 3.1 `DecisionPage.jsx` renderiza campos removidos; coordenador nunca vê a ata real

**Evidência:** `frontend/src/DecisionPage.jsx:136` (`req.ata`), `:179` (`req.data_convite`), `:186` (`req.local_banca`).
`BancaSummary` (`models.py:186-191`) **não expõe `ata`** — só `request/status/rejection_reason/approval_observation`. Logo `req.ata` é `undefined` → campo em branco.

**Impacto:** a página de decisão mostra "Data dos convites" e "Local" (conceitos mortos) vazios, não mostra a ata (que agora é do record), e não exibe modalidade/sala/`remoto`/comentários/campos PPGEnFis — justamente o que o coordenador precisa para decidir.

**O que fazer:** adicionar `ata` (e o que o coordenador deve ver) ao `BancaSummary`/endpoint; reescrever a seção "Dados Gerais" para o novo modelo (modalidade + sala/link condicionais, comentários, badge `remoto` por membro, campos PPGEnFis).

### 3.2 Validação de anexos obrigatórios ausente + upload inseguro

**Evidência:** `backend/app/api/router.py:99-128`; UI `BancaAttachmentsSection.tsx`.

Problemas:
- **Nada valida que os anexos obrigatórios por tipo+ppg foram enviados** (plano 5.2). O `required` nos `FileField` é puramente visual; a banca submete com zero anexos.
- O endpoint **não verifica que `token` corresponde a uma banca existente** → arquivos órfãos no GridFS para qualquer token arbitrário.
- **Sem validação de tipo de conteúdo**: aceita qualquer arquivo. `accept=".pdf"` é só dica de cliente.
- `zip(files, kinds)` (`:114`) **trunca silenciosamente** se as listas tiverem tamanhos diferentes — descasamento vira perda de dados sem erro.
- **`member_role` não é capturado** (plano 5.4 / `AttachmentInfo.member_role`): todos os lattes vão sob um único `kind` sem vínculo ao membro externo.
- Imports inline (`gridfs`, `datetime`) dentro da função (`:106-108`) — fora do padrão do projeto.

**O que fazer:** criar `AttachmentInfo` (está no plano §3.7, nunca foi criado), validar token + obrigatoriedade por perfil, validar content-type, parear arquivo↔kind↔role explicitamente (ex.: lista de objetos no multipart, não duas listas paralelas), mover imports para o topo.

### 3.3 Fase 6 (envio de convites/pareceres) totalmente ausente

**Evidência:** não existe `app/application/invite_service.py`; `admin_router.py` não tem endpoints de envio; `invite_status` foi **removido** do `BancaRecord` (estava no plano §3.4).

**Impacto:** critério #11 não atendido; toda a seção 2.7 do plano (S1–S5) pendente.

**O que fazer:** se Fase 6 está fora do escopo desta entrega, **dizer isso explicitamente** (o plano não marca a Fase 6 como adiada, ao contrário da Fase 5). Caso contrário, implementar modelo de status por membro/documento + endpoints individual/batch + UI.

### 3.4 Filtro admin por PPG não está conectado (critério #10)

**Evidência:** `BancaListFilters` tem `ppg` (`models.py:212`) e o repo filtra por ele (`mongo_banca_repository.py:122-123`), **mas** `GET /admin/bancas` (`admin_router.py:33-42`) não declara o parâmetro `ppg` nem o passa para `BancaListFilters`. O frontend `AdminBancaList.jsx` também não tem controle de PPG (só status/ata/student/orientador/q).

**O que fazer:** adicionar `ppg: str | None = None` ao endpoint e repassá-lo; adicionar o seletor de PPG na UI do admin.

---

## 4. 🟡 Médio

### 3.5 Emails de aprovação são enviados antes da atualização atômica de status

**Evidência:** `banca_service.py:103-127` — gera doc, envia ao secretário, envia à gerência, e **só então** `update_decision` (cujo guard atômico `status:"pending"` está no fim).

**Impacto:** duas chamadas concorrentes de `approve` (ou um retry após timeout) podem **gerar e enviar emails duas vezes** antes do guard pegar. O guard existe, mas tarde demais.

**O que fazer:** fazer o check-and-set de status **primeiro** (transição atômica `pending → approved`), e só então gerar/enviar; em falha de envio, decidir política (compensar/log). Garante idempotência.

### 4.1 `bolsista_cnpq = false` vira `null` na serialização

**Evidência:** `frontend/src/types/new-banca.ts:176` — `bolsista_cnpq: member.bolsista_cnpq || null`. Como `false || null === null`, perde-se a distinção entre "não é bolsista" e "não respondido". Mesmo risco para qualquer campo falsy.

**O que fazer:** serializar booleano explicitamente (`member.bolsista_cnpq ?? null`, ou manter `false`).

### 4.2 `PpgProfile` incompleto vs. spec §4 — regras PPGEnFis hardcoded no modelo

**Evidência:** `ppg_profiles.py:8-17` define só `roles_by_tipo` e `antecedencia_dias`. A spec §4 pede também `required_student_fields`, `required_member_fields`, `titulo_en_required`, `default_video_link`. Em vez disso, `models.py:97-127` hardcoda `if self.ppg == "ppgenfis": ...`.

**Impacto:** contraria P2/P4 ("diferenças declaradas por config"). Adicionar um terceiro PPG exigiria editar o modelo de domínio, não só o perfil.

**O que fazer:** mover a lista de campos obrigatórios para o `PpgProfile` e validar genericamente a partir dele (na camada de serviço, ver §2.2).

### 4.3 Regras de composição da Resolução não são realmente verificadas

**Evidência:** `_enforce_tipo_rules` (`models.py:71-82`) só checa presença/ocultação de slots. As regras do Apêndice A (máx. 1 do programa, ≥1 externo à UFRGS, ≥2 externos ao IF no doutorado, exigência de orientação concluída, artigo Qualis A) **não são implementadas**.

**Impacto:** a conformidade com a Resolução 02/2025 (objetivo C1–C6 + §7) é apenas parcial. Documentar como limitação conhecida ou implementar.

### 4.4 `remoto` e campos novos não chegam aos documentos (critério #5)

**Evidência:** `MemberInfo.to_tuple` (`models.py:22-23`) e `StudentInfo.to_tuple` (`models.py:33-34`) retornam as tuplas antigas. `document_service._build_banca` só passa `to_tuple()`. Logo `remoto`, `bolsista_cnpq`, `ppg`, `lattes`, `doctorate_*`, e (para PPGEnFis) `cpf` não entram nos PDFs.

**Impacto:** critério #5 ("informação [remoto] aparece nos documentos") falha — aparece só no email do coordenador (`petition_service.py:47`).

**O que fazer:** estender `to_tuple`/o contrato com `criaBancas` (junto com o conserto de §2.1).

### 4.5 Injeção de HTML nos emails

**Evidência:** `petition_service.py` interpola entrada do usuário sem escapar — `req.titulo`, `req.comentario_desempenho`, `req.justificativa_membros`, `member.name`, `observation`, `reason` (`build_rejection_html`).

**Impacto:** HTML injection nos emails (e potencial spoofing visual no cliente do coordenador/secretário).

**O que fazer:** escapar com `html.escape()` toda interpolação de dado do usuário nos templates.

---

## 5. 🟢 Limpeza / menores

- **`app/config.py` é código morto.** Coexiste com o pacote `app/config/` (`config/__init__.py`). Python resolve o **pacote**, então `config.py` (e seus aliases `COORDENADOR_EMAIL`/`SECRETARY_EMAIL`) nunca é importado. Remover o arquivo para evitar confusão. — `backend/app/config.py`
- **Estado de anexos via global `window.__sigbah_attachments`** (`BancaAttachmentsSection.tsx:46-48`, lido em `NewBancaPage.tsx:63`). Frágil: fora do estado do React Hook Form, não reseta com `form.reset`, atrapalha teste/SSR. Mover para o contexto do form.
- **`memberInfoSchema.lang: z.string()`** (`new-banca.ts:45`) não restringe a `"pt"|"en"` (o backend é `Literal["pt","en"]`). Apertar o schema.
- **Sem aviso de antecedência no frontend** (C2 pedia "aviso frontend"). Hoje o usuário só descobre no erro de submissão. Considerar aviso inline ao escolher a data.
- **`get_profile` levanta `KeyError`** em ppg desconhecido (`ppg_profiles.py:115`) — ok porque `ppg` é `Literal` na API, mas `_doc_to_record` faz `setdefault("ppg","ppgfis")` (`mongo_banca_repository.py:218`), mascarando dados legados de forma silenciosa.
- **`.env.example`** usa `MONGO_PASSWORD=secret` enquanto `CLAUDE.md` documenta `password`; alinhar.

---

## 6. Ordem sugerida de trabalho para o próximo agente

1. **§2.1** — consertar `document_service` para o novo modelo (desbloqueia aprovação e download). Adicionar teste de geração.
2. **§2.2** — tirar a validação de submissão de dentro do modelo Pydantic e levá-la para `BancaService`/admin update (para de quebrar leituras).
3. **§3.1** — corrigir `DecisionPage` + expor `ata` no `BancaSummary`.
4. **§3.4** — conectar filtro admin por PPG (critério #10, barato).
5. **§3.2** — validação + segurança dos anexos (`AttachmentInfo`, obrigatoriedade por perfil, content-type, vínculo de role).
6. **§3.5 / §4.1 / §4.2 / §4.4 / §4.5** — race de aprovação, serialização de booleano, perfil completo, campos nos documentos, escape de HTML.
7. **§3.3** — decidir e documentar escopo da Fase 6; implementar se in-scope.
8. **§5** — limpeza.

> Depois de §2.1 e §2.2, rode um teste end-to-end: submeter → aprovar → reabrir a banca pela lista do admin **com a data sugerida no passado**. Esse cenário exercita os dois bugs mais perigosos de uma vez.
