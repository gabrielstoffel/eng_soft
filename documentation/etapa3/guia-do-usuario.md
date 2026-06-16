# Guia do Usuário — SigBah!

Sistema de geração de documentos e notificações de bancas dos programas de
pós-graduação **PPGFís** (Física) e **PPGEnFis** (Ensino de Física) do Instituto
de Física da UFRGS.

Este guia descreve o fluxo completo de uma banca e o que cada perfil —
**Orientador(a)**, **Coordenador(a)** e **Secretário(a)** — deve fazer.

---

## Visão geral do fluxo

```
Orientador(a)            Coordenador(a)              Secretário(a)
─────────────            ──────────────              ─────────────
1. Cadastra a banca  →   2. Recebe o pedido por  →   3. Recebe o aviso, baixa
   (formulário) e            e-mail e decide:           os documentos e envia
   anexa os PDFs            Aprovar ou Recusar          convites/pareceres
```

A cada submissão o sistema dispara **dois e-mails**: um para o **coordenador**
(com o link de decisão) e outro para o **secretário** (com o link do painel
administrativo). Após a decisão, o **orientador** é notificado do resultado.

> **PPGFís × PPGEnFis** — os dois programas usam o mesmo formulário, mas geram
> documentos diferentes. O PPGFís produz **ata, cartaz, cartas-convite,
> pareceres** e (na qualificação) o **relatório de avaliação**. O PPGEnFis gera
> apenas as **cartas-convite**.

---

## 1. Orientador(a)

O(a) orientador(a) é quem **cadastra a banca** e acompanha o resultado.

### Como cadastrar uma banca

1. Acesse o formulário do seu programa:
   - PPGFís: **`/ppgfis/new`**
   - PPGEnFis: **`/ppgenfis/new`**
2. **Etapa 1 — Identificação e agenda:**
   - Dados do(a) aluno(a) e o **tipo** de banca (Mestrado, Qualificação ou
     Doutorado). No PPGEnFis também são obrigatórios CPF, data de nascimento e
     e-mail do(a) aluno(a).
   - **Data e horário** sugeridos. A data deve respeitar a **antecedência mínima**
     do programa (ex.: 20 dias para mestrado); datas muito próximas são recusadas.
   - **Modalidade:** presencial e híbrida exigem **sala de preferência**; remota e
     híbrida pedem o **link** de videoconferência.
   - **Título** (e título em inglês, quando houver).
3. **Etapa 2 — Composição da banca:**
   - Informe os participantes por categoria (**Orientação / Internos / Externos**).
   - O **e-mail é obrigatório para todos os membros** — é o endereço que receberá
     a carta-convite/parecer.
   - No PPGEnFis, cada membro também exige **Lattes**, **instituição** e **ano de
     conclusão do doutorado**.
4. **Anexos:** envie os PDFs exigidos pela resolução (currículo Lattes dos
   externos, texto da dissertação/tese/exame, press release, artigo). O texto da
   dissertação/tese é o arquivo que acompanha as cartas-convite.
   - **Limite total de upload: 150 MB** por envio.
5. Clique em **Enviar**.

### Validação do formulário

- Campos obrigatórios não preenchidos ficam **destacados em vermelho** e a página
  rola até o primeiro erro. A mensagem é genérica ("Há campos obrigatórios não
  preenchidos.") — corrija os campos marcados.
- O campo **Lattes** aceita o endereço com ou sem `http(s)://`.

### O que você recebe por e-mail

- **Banca aprovada** — confirmação com os dados da banca e, quando houver, a
  **observação do coordenador**.
- **Pedido recusado** — com o **motivo** informado pelo coordenador. Ajuste e
  cadastre novamente.

---

## 2. Coordenador(a)

O(a) coordenador(a) **avalia** cada pedido de banca. **Não é preciso fazer login**
— a decisão é feita por um link individual enviado por e-mail.

### Como decidir

1. Ao ser submetida uma banca, você recebe o e-mail **"Novo Pedido de Banca —
   {tipo} — {aluno}"**, com os dados, os membros e os **anexos** (incluindo o
   texto da dissertação/tese).
2. Clique em **"Acessar página de decisão"**. A página (`/decide/{token}`) mostra
   todos os dados da banca.
3. Escolha:
   - **Aprovar** — você pode preencher uma **observação** opcional (ela é
     enviada ao orientador e à secretaria).
   - **Recusar** — informe o **motivo** (obrigatório). O orientador recebe o
     motivo por e-mail.

> O link de decisão é exclusivo de cada banca e dá acesso apenas àquele pedido.
> A página administrativa completa fica a cargo da secretaria.

### O que acontece após aprovar

O sistema notifica automaticamente:

- a **secretaria** (para gerar/baixar documentos e enviar convites),
- o **orientador** (confirmação + sua observação),
- a **gerência** (solicitação de agendamento de sala, com cópia para o CPG).

---

## 3. Secretário(a)

O(a) secretário(a) **operacionaliza** a banca pelo **painel administrativo**, com
acesso restrito ao seu programa.

### Acesso

1. Você recebe e-mails de aviso com o link **"Acessar painel administrativo"**
   (`/admin`) — tanto na submissão quanto na aprovação da banca.
2. Faça login com o **usuário e senha do seu programa**. O painel mostra
   **apenas as bancas do seu PPG**.

### Lista de bancas

- Filtre por **status** (Pendente / Aceita / Recusada), por número da **ata** ou
  por **busca livre** (aluno, orientador, título).
- Clique em **Ver** para abrir os detalhes.

### Detalhes da banca

Na tela de detalhes você pode:

- **Consultar** status, versões e todos os dados da banca.
- **Editar** (somente bancas **aceitas**): salvar cria uma **nova versão**,
  preservando o histórico.
- **Documentos** — selecionar e **baixar** os PDFs gerados (ata, cartaz, etc.;
  no PPGEnFis, as cartas-convite). É possível baixar individualmente ou em lote.
- **Envio de Convites e Pareceres** (disponível **após a aprovação**):
  - Os itens são organizados em abas por categoria: **Orientação / Internos /
    Externos**.
  - Marque os destinatários e use **Enviar Convites** ou **Enviar Pareceres**
    (botões separados). O sistema **pede confirmação** antes de enviar.
  - Cada e-mail leva a **carta-convite/parecer em PDF** mais o **PDF do texto**
    da dissertação/tese/exame (compactado em `.zip` se for muito grande).
  - A coluna **Status** mostra o que já foi enviado e quando. Membros sem e-mail
    aparecem como "sem e-mail" e não podem ser selecionados.

### E-mails que você recebe

- **Nova banca enviada para avaliação** — assim que o orientador submete (aviso;
  a decisão é do coordenador).
- **Documentos / Banca Aprovada** — após a aprovação, com o link do painel para
  baixar os documentos e enviar convites/pareceres.

---

## Observações gerais

- **Numeração das atas** — cada combinação de programa + tipo de banca tem sua
  própria sequência de atas, configurável pela coordenação técnica.
- **Assuntos dos e-mails** — identificam a banca pelo **tipo** e pelo **nome do
  aluno** (sem número de ata).
