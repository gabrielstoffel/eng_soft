# Especificação de Novas Features — SigBah!

**Data:** 22/05/2026 · **Prazo do projeto:** ~30 dias (meados de junho/2026)

O sistema atende **dois programas** que hoje operam como um núcleo único, mas têm **resoluções e regras distintas**: **PPGFis** (Física) e **PPGEnFis** (Ensino de Física).

> **Princípio de design (definido com o cliente):** **maximizar o compartilhamento** entre os dois PPGs. Núcleo (domínio, serviços e **fluxo de aprovação**) é **comum aos dois**; apenas as diferenças (campos exibidos, validações, links, e-mails, templates de documentos) são parametrizadas por PPG.

**Status atual:** protótipo local (Mailpit captura e-mails; admin sem login). Geração de documentos via `criaBancas.py` (fpdf2, layout 100% hard-coded) — **será substituída** (ver §B).

**Apoio de T.I.:** o **PPGEnFis dispõe de apoio do seu setor de T.I.** — relevante para hospedagem, integração e adoção (ver §7).

---

# Parte I — Mudanças arquiteturais

## A. Separação por PPG (rotas separadas, núcleo compartilhado)

**Atual:** não existe conceito de PPG. `BancaRequest`/`BancaRecord` não têm campo de programa; e-mails, link de videoconferência e documentos são fixos para PPGFis.

**Proposta — arquitetura:**

```
                 NÚCLEO COMPARTILHADO (backend)
   domain/models · services · fluxo de aprovação · admin · repositório
                          │
            ┌─────────────┴─────────────┐
        PPGFis profile             PPGEnFis profile
        • e-mails (CPG FIS,         • e-mails (CPG Ensino,
          coordenador, gerência)      coordenador, gerência)
        • link MCONF padrão         • (sem link padrão / próprio)
        • campos exibidos/oblig.    • +CPF, +nascimento, +Lattes oblig.,
        • templates de documentos     +conclusão doutorado, título EN opcional
                                     • templates de documentos
```

- **Backend (compartilhado):** introduzir `ppg: "ppgfis" | "ppgenfis"` em `BancaRequest`/`BancaRecord`. Toda lógica de serviço, **fluxo de aprovação** e persistência permanece única. As diferenças vivem em um objeto de **perfil de PPG** (config) resolvido por `app/deps.py`:
  - e-mails (coordenador, alias CPG, gerência);
  - link de videoconferência padrão;
  - conjunto/obrigatoriedade de campos (perfil de validação);
  - conjunto de templates de documentos.
- **Frontend (rotas separadas, componentes compartilhados):** páginas distintas por PPG, mas **reaproveitando as seções de formulário** ao máximo:
  ```
  /ppgfis/new    → FormFis     ┐ compartilham BancaGeneralSection,
  /ppgenfis/new  → FormEnFis    ┘ BancaCompositionSection, uploads, etc.
  ```
  A diferença entre formulários é **declarada por config** (quais campos/validações), não por duplicação de UI. A área admin filtra/segmenta por PPG.
- **Modelo de dados — superset compartilhado:** `StudentInfo`/`MemberInfo` passam a conter o superconjunto de campos; cada perfil de PPG define quais são exibidos e obrigatórios. Campos não usados por um PPG ficam vazios/ocultos.

**Arquivos:** `models.py` (campo `ppg`, supersets), `config.py` + `deps.py` (perfis de PPG), `router.py`/`admin_router.py` (parametrização por PPG), frontend (rotas + config de campos por PPG), `petition_service.py`/`email_service.py`/`document_service.py` (resolver recursos pelo perfil).

### Matriz: compartilhado vs. específico

| Aspecto | Compartilhado | PPGFis | PPGEnFis |
|---|---|---|---|
| **Fluxo de aprovação** (submissão→decisão→admin) | ✅ | — | — |
| Modelos de domínio / serviços / repositório | ✅ (superset) | — | — |
| Status, versionamento, geração/engine | ✅ | — | — |
| Campos do formulário | base comum | conjunto reduzido | +CPF, +nascimento, +Lattes oblig., +conclusão dout., título EN opcional |
| Link de videoconferência | mecanismo | MCONF fixo (default) | sem default / link próprio |
| E-mails (coordenador, CPG, gerência) | mecanismo | aliases PPGFis | aliases PPGEnFis |
| Templates de documentos | engine (§B) | templates PPGFis | templates PPGEnFis |

## B. Geração de documentos (substituir `criaBancas.py`)

**Atual (`backend/criaBancas/criaBancas.py` + `app/application/document_service.py`):**
- `fpdf2` com layout **100% imperativo/hard-coded**: coordenadas em mm, fontes, e **todo o texto institucional embutido em f-strings no código**. Mudar uma palavra exige editar Python.
- Acoplamento frágil: `document_service.py` **espelha** o mapa `FUNCAO` e os **nomes de arquivo** gerados — se um nome muda no `criaBancas`, `generate_files` quebra.
- QR code escrito em arquivo **compartilhado** (`qrcode.png`) → condição de corrida sob concorrência.
- Carregado via *hack* de `sys.path`, fora da arquitetura limpa.

**Escopo agora vs. depois:**
- **REQUERIDO agora:** o **mecanismo** de geração — preencher um `.docx` com placeholders `{{var_name}}` via Python e converter para PDF — funcionando para **ambos os PPGs**, com um conjunto de templates por PPG **versionados no repositório** (arquivos em `templates/`).
- **OPCIONAL/depois:** a **UI admin de upload/gestão/versionamento** de templates (§6). Inicialmente os `.docx` são editados/commitados pelos desenvolvedores; a edição self-service pela secretaria fica para uma fase posterior.

**Proposta — mecanismo (DOCX → PDF):**
- **Fluxo (ideia do cliente):** carregar um `.docx` que contém `{{var_name}}` no texto → preencher os valores diretamente no `.docx` via Python → gerar o PDF a partir do `.docx` preenchido.
- **Tecnologia:** `docxtpl` usa exatamente a sintaxe `{{var_name}}` (e `{% %}` para laços/condições) — render com um **contexto de dados**. Conversão para PDF via **LibreOffice headless** (`soffice --headless --convert-to pdf`).
- **Por que DOCX:** suporta os **formatos distintos por PPG** (incluindo o formato do PPGEnFis) e abre caminho para a edição self-service futura (§6) sem tocar em código.
- **Estrutura de templates** (por PPG e por tipo de documento), versionados no repo:
  ```
  templates/
    ppgfis/   ata.docx  carta_convite.docx  parecer.docx  cartaz.docx  relatoria.docx
    ppgenfis/ ata.docx  carta_convite.docx  parecer.docx  cartaz.docx  relatoria.docx
  ```
- **Interface estável (clean architecture):** definir uma ABC `DocumentEngine` em `domain/` com `render(kind, ppg, context) -> bytes`, implementada em `infrastructure/`. `document_service.py` passa a orquestrar a engine, **sem** espelhar nomes de arquivo nem mapas internos.
- **Problemas resolvidos:** fim do acoplamento por nome de arquivo; conteúdo separado do código; sem corrida do QR (gerar QR em buffer/temp por requisição); engine sob a árvore `app/`.
- **Documentos a suportar** (paridade com hoje): `ata`, `carta_convite` (1 por membro, **bilíngue pt/en** conforme `lang` do membro), `parecer` (por examinador), `cartaz` (paisagem, com **QR code** do link), `relatoria_avaliacao` (tipo 2). Seleção por tipo de banca e por PPG.
- **Bilíngue & QR:** placeholders condicionais no template para pt/en; QR gerado em runtime e injetado como imagem (`InlineImage` do docxtpl).

**Dependência operacional:** LibreOffice instalado no servidor/imagem (adicionar ao Docker/infra). Avaliar `docxtpl` + um wrapper de conversão. Remover `fpdf2` do caminho crítico (manter `qrcode` só para gerar a imagem do QR, se conveniente).

**Arquivos:** novo `domain/document_engine.py` (ABC), `infrastructure/docx_document_engine.py` (impl), refactor de `document_service.py`, `templates/` versionados, `pyproject.toml` (deps), infra (LibreOffice). Remover/aposentar `criaBancas/`.

---

# Parte II — Features de produto

> Tags: **[C]** compartilhado · **[Fis]** PPGFis · **[EnFis]** PPGEnFis

## 1. Formulário de solicitação (orientador)

### 1.1 [C] Remover número da ata do formulário
- **Atual:** `ata: int` obrigatório, preenchido pelo orientador.
- **Problema:** orientador não conhece o número da ata (informação interna).
- **Proposta:** remover do formulário; gerar automaticamente (ver §3.1).

### 1.2 [C] Remover "data dos convites"
- `data_convite` sai do formulário. A data do convite é a **data do sistema** no momento da geração/envio (confunde o orientador e pode mudar).

### 1.3 [C] Local de preferência → seleção + remota
- Renomear para **"Local de preferência"**. Caixa de seleção: *Sala de videoconferências* · *Anfiteatro* · *Banca remota* · *Outro* (texto livre). Cobre também a opção **remota ou presencial**.

### 1.4 [Fis] Link de videoconferência opcional/sugerido
- PPGFis usa **MCONF com link sempre igual** (default do perfil). Campo fica **opcional**, com observação: *"preencha apenas se NÃO for usar o link padrão do PPG"*. **[EnFis]** não tem default → orientador informa o link próprio.

### 1.5 [C] Anexos de documentos no formulário
- Adicionar uploads ao final do formulário:
  | Documento | Obrigatoriedade |
  |---|---|
  | **Currículo (Lattes) dos membros** | **Obrigatório** |
  | Texto/dissertação do aluno (PDF) | Opcional (aluno pode estar fechando o texto) |
  | Press release | Opcional |
  - *Disclaimer* nos opcionais: *"O não envio do manuscrito pode ocasionar aprovação sob condição."*
- Backend precisa de storage de anexos (modelo + repositório).

### 1.6 [C] Dois campos de texto livre
- Após os membros: (1) **comentário sobre o desempenho do estudante**; (2) **justificativa para a escolha dos membros**. Enviados ao coordenador.

### 1.7 [EnFis] Novos campos de dados
Específicos do PPGEnFis (parametrizados via perfil; ocultos/opcionais no PPGFis até confirmação):

| Campo | Aplica-se a | Obrigatório? |
|---|---|---|
| **Nome COMPLETO** | Aluno | Sim |
| **CPF** | Aluno | Sim |
| **Data de nascimento** | Aluno | Sim |
| **E-mail** | Aluno / membros | Sim |
| **Lattes** | Membros | **Obrigatório** (vincula §1.5) |
| **Conclusão de doutorado:** instituição (local) + **ano** | Membros | Sim |
| **Título em inglês** | Banca | **NÃO obrigatório** (hoje `titulo2` é obrigatório → tornar opcional) |

- **Atual:** `StudentInfo` = `gender, name`; `MemberInfo` = `gender, name, institution, location, lang, email`. Faltam CPF, nascimento, Lattes, conclusão doutorado (inst+ano). Implementar como superset + perfil (§A).

## 2. Decisão do coordenador

### 2.1 [C] Status "Aprovado sob condição"
- **Atual:** `BancaStatus` = pending|approved|rejected (binário).
- **Proposta:** adicionar **`approved_with_condition`** com condição em texto livre (ex.: "aguardando texto do aluno", "aguardando novo press release"). Documentos podem ser gerados e banca agendada; apenas o **envio de convites** (§4.1) fica bloqueado até resolver a pendência. Formaliza o que coordenadores já fazem por e-mail.

### 2.2 [C] Recusa menos burocrática
- Recusa só para **mérito** (membro sem experiência, falta de documento obrigatório). Erros simples (nome incompleto) → corrigir na edição (§4.3), não recusar. Evitar obrigar o orientador a refazer todo o pedido.

### 2.3 [C] E-mail ao coordenador sem data/local
- Coordenador avalia só o **mérito**. Remover data/horário/local do e-mail de petição; esses dados seguem para a gerência (§3.2).

## 3. Ata e agendamento de sala

### 3.1 [C] Número da ata automático
- Sequência **por tipo de banca** mantida no banco (última = 20 → próxima = 21). Atribuído pelo sistema (provavelmente na aprovação/geração). Sem intervenção do orientador.

### 3.2 [C] E-mail de solicitação de agendamento à gerência
- Ao aprovar (ou aprovar sob condição), além do e-mail ao secretário, disparar e-mail à **gerência (GIF)** com dados objetivos (data, horário, local de preferência) + mensagem padrão de solicitação, **CC para o alias CPG** do PPG (resposta retorna ao grupo). O trâmite de sala fica majoritariamente **fora** do sistema; ajustes posteriores via edição (§4.3).

## 4. Área administrativa (secretário)

### 4.1 [C] Enviar convites aos membros — **botão por membro**
- **Atual:** secretário recebe ZIP e distribui manualmente; envio automático **não implementado**.
- **Proposta:** na área admin, **um botão de envio ao lado de cada membro** (cada carta-convite), que dispara a carta-convite individual (com link quando aplicável) ao e-mail daquele membro.
- Complementar: botão **"Enviar todos"** para disparar de uma vez. Indicar estado por item (enviado / não enviado / data de envio).
- Bloqueado sob condição pendente (§2.1).
- **Base técnica:** o manifesto de documentos já tem entradas por membro (`carta_convite:<role>`) — reaproveitar para o envio individual.

### 4.2 [C] Enviar pareceres após a banca — **botão por parecer**
- Mesma lógica: **um botão de envio ao lado de cada parecer** (por examinador), para envio dos **pareceres aos professores após a banca**, mais um **"Enviar todos"**.
- **Base técnica:** manifesto já tem entradas `parecer:<role>` por examinador.

### 4.3 [C] Edição — ajustes
- Edição com versionamento **já existe** (`update_banca`, `BancaVersion`), mas só para `approved`. Permitir também para `approved_with_condition`. Validar campos obrigatórios faltantes (ex.: presidente da banca, citado como bug).

## 5. [C] E-mails via aliases CPG
- Usar o **alias CPG de cada PPG** (que distribui a secretário, coordenador e substituto) no envio/CC, garantindo captura de respostas (ex.: da gerência). Aliases configurados por perfil de PPG (§A).

## 6. [C] Templates editáveis pela secretaria — **OPCIONAL (depois)**
- **Base já vem da engine (§B):** os documentos são `.docx` por PPG/tipo, com `{{var_name}}`.
- **Agora:** os `.docx` ficam versionados no repo e são alterados pelos desenvolvedores.
- **Depois (opcional):** UI admin para **upload/versão de templates** por PPG, permitindo à secretaria editar sem depender de desenvolvimento.

## 7. Infra e produção (pós-MVP)
- **Auth** na área admin (hoje sem login).
- **Envio de e-mail real** (hoje Mailpit local).
- **LibreOffice** no servidor/imagem (dependência da engine §B).
- Hospedagem própria inicialmente; depois migrar para infra institucional. **PPGEnFis tem apoio do setor de T.I.** — usar como canal de integração/adoção. Dados sensíveis (CPF, nascimento) → atenção à **LGPD**.
- Adoção exige passar pela CPG e mudança cultural (orientador/aluno solicitam).

---

## Resumo priorizado

| # | Feature | Tag | Esforço | Prioridade |
|---|---|---|---|---|
| A | Separação por PPG (rotas + núcleo + perfis) | C | Alto | **Alta** |
| B | Mecanismo de documentos (`.docx` `{{var}}`→PDF) p/ ambos PPGs | C | Alto | **Alta** |
| 1.1 | Remover ata do formulário | C | Baixo | Alta |
| 1.2 | Remover data dos convites | C | Baixo | Alta |
| 1.3 | Local de preferência (select + remota) | C | Baixo | Alta |
| 1.4 | Link videoconf. opcional/sugerido | Fis | Baixo | Média |
| 1.5 | Anexos (currículo obrigatório) | C | Alto | Alta |
| 1.6 | Dois campos de texto livre | C | Baixo | Alta |
| 1.7 | Campos PPGEnFis (CPF, nascimento, Lattes, conclusão dout., título EN opcional) | EnFis | Médio | Alta |
| 2.1 | Status "aprovado sob condição" | C | Médio | Alta |
| 2.2 | Recusa menos burocrática | C | Baixo | Média |
| 2.3 | E-mail ao coordenador sem data/local | C | Baixo | Alta |
| 3.1 | Número da ata automático | C | Médio | Alta |
| 3.2 | E-mail de agendamento à gerência | C | Médio | Média |
| 4.1 | Enviar convites — botão por membro (+ enviar todos) | C | Médio | Alta |
| 4.2 | Enviar pareceres — botão por parecer (+ enviar todos) | C | Médio | Média |
| 4.3 | Edição p/ status condicional | C | Baixo | Média |
| 5 | E-mails via alias CPG | C | Baixo | Média |
| 6 | Templates editáveis via UI admin (upload) | C | Médio | **Opcional/depois** |
| 7 | Infra/produção (auth, e-mail real, LGPD, LibreOffice) | C | Alto | Baixa |

---

## Pendências a confirmar com o cliente

1. Momento exato de atribuição do **número da ata** (na aprovação? na geração?).
2. Aliases CPG, e-mails de coordenador e da **gerência (GIF)** de **cada PPG**.
3. Lista definitiva de **documentos obrigatórios vs. opcionais** por tipo de banca **e por PPG**.
4. Diferenças entre as **resoluções de PPGFis e PPGEnFis** (campos, documentos, ex.: press release).
5. **Formato dos templates `.docx`** de cada PPG (obter o formato da Liane/PPGEnFis) para popular a engine.
6. Como engajar o **setor de T.I. do PPGEnFis** (hospedagem/integração/LGPD).
