# SigBah! - Sistema de Gestao de Bancas Academicas

## Visao Geral

O **SigBah!** e um sistema web desenvolvido para as secretarias de pos-graduacao em Fisica (PPGFis) e Ensino em Fisica (PPGEnFis) da Universidade Federal do Rio Grande do Sul (UFRGS). Seu objetivo e simplificar o gerenciamento e envio de documentos referentes as bancas de dissertacao de mestrado, exame de qualificacao ao doutorado e tese de doutorado.

## Problema Atual

Todo o processo de gestao de bancas e realizado manualmente pelos secretarios dos programas, por meio de trocas de e-mails, edicao individual de documentos em editores de texto e controle em planilhas. Isso gera retrabalho, atrasos e risco de erros em informacoes criticas.

## Solucao

O SigBah! automatiza o fluxo completo: desde a solicitacao da banca pelo orientador ate a geracao e envio dos documentos finais, eliminando etapas manuais e centralizando todas as informacoes em um unico sistema.

O sistema e responsavel pela geracao automatica dos seguintes documentos:
- Cartas-convite
- Folha de conceito
- Atestados de participacao
- Ata da banca

Alem disso, envia automaticamente e-mails de:
1. Divulgacao da defesa para a lista de e-mails do programa
2. Convite aos membros da banca (titulares e suplentes) com carta-convite e folha de conceito
3. Atestado de participacao apos a apresentacao

---

## Tipo de Transacao

**Solicitacao/Resolucao** - O orientador solicita a criacao de uma banca (primeiro sentido), e o coordenador resolve a solicitacao, aprovando-a ou recusando-a (segundo sentido).

A transacao se inicia quando o orientador submete o formulario de formalizacao de pedido de banca, informando: tipo de banca, titulo do trabalho, dados do aluno, membros titulares e suplentes propostos, local, data e hora.

A transacao se encerra quando:
- **(a)** Em caso de aprovacao: os documentos sao gerados e enviados aos membros da banca
- **(b)** Em caso de recusa: o orientador e notificado com a justificativa

A transacao nao envolve pagamento ou compensacao financeira.

---

## Regras e Restricoes

- Somente orientadores vinculados ao PPGFis ou PPGEnFis podem solicitar bancas
- A solicitacao deve ser feita com antecedencia minima de **30 dias** em relacao a data pretendida para a defesa
- A banca deve ser composta por no minimo **3 membros titulares** e **1 suplente**
- Cada pedido so pode ser avaliado uma vez pelo coordenador; em caso de recusa, o orientador deve submeter uma nova solicitacao
- Uma vez que os documentos tenham sido gerados e enviados, a banca nao pode ser cancelada pelo orientador sem intervencao do secretario

---

## Papeis de Usuario

### Orientador
- Formaliza pedidos de banca por meio do formulario de solicitacao
- Recebe notificacoes sobre o andamento do processo (aprovacao ou recusa)
- Cadastrado no sistema pelo secretario do PPG a partir do registro de docentes vinculados ao programa

### Coordenador do PPG
- Avalia e resolve as solicitacoes de banca, aprovando ou recusando conforme o regimento
- Designado pela coordenacao do programa, com acesso configurado pelo secretario

### Secretario do PPG
- Gerencia os documentos gerados (edita, envia aos membros da banca, envia atestados)
- Cadastra orientadores e coordenadores
- Utiliza as funcionalidades de pesquisa e relatorios
- Cadastrado pelo administrador do sistema

---

## Acesso ao Sistema

Sistema web acessado por navegador (Chrome, Firefox, etc.), sem necessidade de instalacao de software adicional. Todos os perfis acessam pelo mesmo endereco web, sendo direcionados as funcionalidades correspondentes ao seu papel apos autenticacao.

---

## Recursos Compartilhados

O recurso principal sao as **solicitacoes de banca** e seus **documentos associados**.

Cada solicitacao gera documentos especificos conforme o tipo de banca:

| Tipo de Banca | Documentos Gerados |
|---|---|
| Dissertacao de Mestrado | Carta-convite, Folha de conceito, Ata |
| Exame de Qualificacao ao Doutorado | Carta-convite, Folha de conceito |
| Tese de Doutorado | Carta-convite, Folha de conceito, Ata |

Regras de liberacao:
- Documentos so podem ser enviados apos geracao pelo sistema
- Atestados so podem ser gerados e enviados apos a realizacao da defesa
- Documentos enviados sao registrados em log para controle

---

## Funcionalidades de Pesquisa

O sistema disponibiliza aos secretarios duas formas de pesquisa:

1. **Pesquisa por nome** (do aluno ou orientador): filtra e exibe as bancas correspondentes em listagem paginada
2. **Pesquisa por data**: seleciona um periodo (data inicio e data fim) e exibe as bancas dentro do intervalo

Ao selecionar uma banca da listagem, o sistema exibe os detalhes completos da solicitacao.

### Relatorio de Bancas

O secretario pode gerar um relatorio por periodo contendo:
- Totalizadores da quantidade de bancas solicitadas (por tipo e por situacao)
- Detalhamento de cada banca (aluno, orientador, tipo, data, situacao)

---

## Casos de Uso

| ID | Caso de Uso | Ator | Tipo |
|---|---|---|---|
| UC1 | Formalizar Pedido de Banca | Orientador | Primario |
| UC2 | Enviar Email para Coordenador/Secretario | Sistema | Include (UC1) |
| UC3 | Aprovar Banca | Coordenador | Primario |
| UC4 | Gerar Documentos | Sistema | Extend (UC3) |
| UC5 | Enviar Documentos da Banca | Secretario | Especializacao (UC11) |
| UC6 | Enviar Atestados | Secretario | Especializacao (UC11) |
| UC7 | Pesquisar Bancas | Secretario | Primario |
| UC8 | Editar Documentos | Secretario | Primario |
| UC9 | Gerar Relatorio de Bancas | Secretario | Primario |
| UC10 | Notificar Orientador | Sistema | Include (UC3) |
| UC11 | Enviar Documentos | Secretario | Generalizacao |

### UC1: Formalizar Pedido de Banca

**Ator:** Orientador
**Descricao:** Permite ao orientador registrar no sistema um pedido de banca, informando os dados necessarios (aluno, tipo de trabalho, membros, suplentes, data pretendida). Ao formalizar, o sistema envia automaticamente um email ao Coordenador e ao Secretario do PPG.
**Pre-Condicoes:** Orientador possui acesso ao formulario de formalizacao.
**Pos-Condicoes:** Pedido de banca registrado e email enviado ao Coordenador e Secretario do PPG.

**Fluxo Basico:**
1. O orientador acessa o formulario de formalizacao de pedido de banca.
2. O sistema exibe o formulario com os campos a serem preenchidos.
3. O orientador preenche os dados do aluno (nome, matricula, curso).
4. O orientador preenche o tipo de trabalho (TCC, dissertacao, tese).
5. O orientador preenche os membros titulares e suplentes da banca.
6. O orientador preenche a data e horario pretendidos para a defesa.
7. O orientador submete o formulario.
8. O sistema valida os dados informados.
9. O sistema registra o pedido de banca.
10. Include: Enviar Email para Coordenador/Secretario do PPG (UC2).
11. O sistema exibe confirmacao de que o pedido foi formalizado com sucesso.

**Fluxo Alternativo - 8a. Dados incompletos ou invalidos:**
1. O sistema informa quais campos estao incompletos ou invalidos.
2. O orientador corrige os dados.
3. Retorna ao passo 7.

### UC3: Aprovar Banca

**Ator:** Coordenador
**Descricao:** Permite ao coordenador avaliar um pedido de banca e decidir pela aprovacao ou recusa. O orientador e sempre notificado do resultado. Caso aprovada, o sistema gera os documentos necessarios.
**Pre-Condicoes:** Pedido de banca formalizado.
**Pos-Condicoes:** Pedido aprovado ou recusado, orientador notificado. Se aprovado, documentos gerados.

**Fluxo Basico:**
1. O coordenador acessa o formulario de avaliacao do pedido de banca.
2. O sistema exibe os dados do pedido (aluno, orientador, membros, data) e o formulario de decisao.
3. O coordenador analisa os dados do pedido.
4. O coordenador seleciona a opcao "Aprovar".
5. O coordenador submete o formulario.
6. O sistema registra a aprovacao.
7. Include: Notificar Orientador (UC10).
8. Extend: Gerar Documentos (UC4) [condicao: banca aprovada].
9. O sistema exibe confirmacao da aprovacao.

**Fluxo Alternativo - 4a. Coordenador recusa a banca:**
1. O coordenador seleciona a opcao "Recusar".
2. O coordenador preenche o campo de justificativa da recusa.
3. O coordenador submete o formulario.
4. O sistema registra a recusa com a justificativa.
5. Include: Notificar Orientador (UC10).
6. O sistema exibe confirmacao da recusa.

### UC7: Pesquisar Bancas

**Ator:** Secretario do PPG
**Descricao:** Permite ao secretario pesquisar bancas cadastradas utilizando diferentes criterios (por orientador, por data) e visualizar os resultados em listagem paginada.
**Pre-Condicoes:** Secretario autenticado no sistema.
**Pos-Condicoes:** Resultados da pesquisa exibidos ao secretario.

**Fluxo Basico:**
1. O secretario acessa a listagem de bancas.
2. O sistema exibe as bancas cadastradas em listagem paginada.
3. O secretario digita no campo de busca.
4. O sistema filtra e exibe as bancas que correspondem ao criterio informado.
5. O secretario seleciona uma banca da listagem.
6. O sistema exibe os detalhes completos da banca selecionada.

**Fluxo Alternativo - 3a. Pesquisa por data:**
1. O secretario seleciona um periodo (data inicio e data fim) nos filtros de data.
2. O sistema filtra e exibe as bancas dentro do periodo informado.
3. Retorna ao passo 5.

**Fluxo Alternativo - 4a. Nenhum resultado encontrado:**
1. O sistema informa que nao foram encontradas bancas para o criterio informado.
2. O secretario altera o criterio de busca.
3. Retorna ao passo 3.

### UC11: Enviar Documentos

**Ator:** Secretario do PPG
**Descricao:** Permite ao secretario enviar documentos relacionados a banca. Generaliza-se em Enviar Documentos da Banca (UC5) e Enviar Atestados (UC6).
**Pre-Condicoes:** Documentos disponiveis no sistema e secretario autenticado.
**Pos-Condicoes:** Documentos enviados aos destinatarios.

**Fluxo Basico:**
1. O secretario acessa a opcao de enviar documentos.
2. O sistema exibe a lista de bancas com documentos disponiveis para envio.
3. O secretario seleciona uma banca.
4. O sistema exibe os documentos disponiveis para envio.
5. O secretario seleciona o tipo de documento a enviar.
6. O sistema registra o envio.
7. O sistema exibe confirmacao de envio.

**Sub-fluxo: Enviar Documentos da Banca (UC5):**
1. O sistema exibe os documentos da banca (atas, formularios de avaliacao).
2. O secretario seleciona os destinatarios (membros da banca).
3. O secretario confirma o envio.
4. O sistema envia os documentos aos membros selecionados.

**Sub-fluxo: Enviar Atestados (UC6):**
1. O sistema exibe os atestados de participacao gerados.
2. O secretario seleciona os membros que receberao os atestados.
3. O secretario confirma o envio.
4. O sistema envia os atestados aos membros selecionados.

---

## Requisitos Nao-Funcionais

- O formulario deve carregar em no maximo 3 segundos
- A pesquisa deve retornar resultados em no maximo 5 segundos
- A listagem deve suportar paginacao com no minimo 10 e no maximo 50 itens por pagina
- O envio de documentos deve ser concluido em no maximo 10 segundos
- O sistema deve registrar log de todos os envios realizados

---

## Equipe

| Nome | E-mail |
|---|---|
| Fidel Antonio Silva Luz | fidelluz385@gmail.com |
| Gabriel Stoffel | gc.stoffel03@gmail.com |
| Joao Vitor Leffa Lummertz | joaolummertz1@gmail.com |
| Lucas Nogueira | lucas.caique@ufrgs.br |
| Ricardo Setton Alencar de Carvalho | rsacarvalho@inf.ufrgs.br |
