# Descrições Essenciais dos Casos de Uso

---

## UC1

**Caso de uso:** Formalizar Pedido de Banca
**Ator:** Orientador
**Descrição:** Permite ao orientador registrar no sistema um pedido de banca para defesa de trabalho acadêmico, informando os dados necessários (aluno, tipo de trabalho, membros, suplentes, data pretendida). Ao formalizar, o sistema envia automaticamente um email ao Coordenador (para avaliação) e ao Secretário do PPG (para ciência).
**Pré-Condições:** Orientador possui acesso ao formulário de formalização.
**Pós-Condições:** Pedido de banca registrado e email enviado ao Coordenador e Secretário do PPG.

### Sequência Típica de Eventos (Fluxo Básico):

1. O orientador acessa o formulário de formalização de pedido de banca.
2. O sistema exibe o formulário com os campos a serem preenchidos.
3. O orientador preenche os dados do aluno (nome, matrícula, curso).
4. O orientador preenche o tipo de trabalho (TCC, dissertação, tese).
5. O orientador preenche os membros titulares e suplentes da banca.
6. O orientador preenche a data e horário pretendidos para a defesa.
7. O orientador submete o formulário.
8. O sistema valida os dados informados.
9. O sistema registra o pedido de banca.
10. _Include_ Enviar Email para Coordenador/Secretário do PPG (UC2).
11. O sistema exibe confirmação de que o pedido foi formalizado com sucesso.

### Sequências Alternativas:

**8a. Dados incompletos ou inválidos:**

1. O sistema informa quais campos estão incompletos ou inválidos.
2. O orientador corrige os dados.
3. Retorna ao passo 7.

### Requisitos Não-Funcionais:

- O formulário deve carregar em no máximo 3 segundos.

---

## UC3

**Caso de uso:** Aprovar Banca
**Ator:** Coordenador
**Descrição:** Permite ao coordenador avaliar um pedido de banca e decidir pela aprovação ou recusa. O orientador é sempre notificado do resultado. Caso aprovada, o sistema gera os documentos necessários.
**Pré-Condições:** Pedido de banca formalizado.
**Pós-Condições:** Pedido aprovado ou recusado, orientador notificado. Se aprovado, documentos gerados.

### Sequência Típica de Eventos (Fluxo Básico):

1. O coordenador acessa o formulário de avaliação do pedido de banca.
2. O sistema exibe os dados do pedido (aluno, orientador, membros, data) e o formulário de decisão.
3. O coordenador analisa os dados do pedido.
4. O coordenador seleciona a opção "Aprovar".
5. O coordenador submete o formulário.
6. O sistema registra a aprovação.
7. _Include_ Notificar Orientador (UC10).
8. _Extend_ Gerar Documentos (UC4) [condição: banca aprovada].
9. O sistema exibe confirmação da aprovação.

### Sequências Alternativas:

**4a. Coordenador recusa a banca:**

1. O coordenador seleciona a opção "Recusar".
2. O coordenador preenche o campo de justificativa da recusa.
3. O coordenador submete o formulário.
4. O sistema registra a recusa com a justificativa.
5. _Include_ Notificar Orientador (UC10).
6. O sistema exibe confirmação da recusa.

### Requisitos Não-Funcionais:

- O formulário deve carregar em no máximo 3 segundos.
- O Coordenador deve conseguir avaliar a banca sem sair da sua caia de email.

---

## UC7

**Caso de uso:** Pesquisar Bancas
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário pesquisar bancas cadastradas no sistema utilizando diferentes critérios (por orientador, por data) e visualizar os resultados em listagem paginada.
**Pré-Condições:** Secretário autenticado no sistema.
**Pós-Condições:** Resultados da pesquisa exibidos ao secretário.

### Sequência Típica de Eventos (Fluxo Básico):

1. O secretário acessa a listagem de bancas.
2. O sistema exibe as bancas cadastradas em listagem paginada, mostrando dados da banca.
3. O secretário digita no campo de busca.
4. O sistema filtra e exibe as bancas que correspondem ao critério informado.
5. O secretário seleciona uma banca da listagem.
6. O sistema exibe os detalhes completos da banca selecionada.

### Sequências Alternativas:

**3a. Pesquisa por data:**

1. O secretário seleciona um período (data início e data fim) nos filtros de data.
2. O sistema filtra e exibe as bancas dentro do período informado.
3. Retorna ao passo 5.

**4a. Nenhum resultado encontrado:**

1. O sistema informa que não foram encontradas bancas para o critério informado.
2. O secretário altera o critério de busca.
3. Retorna ao passo 3.

### Requisitos Não-Funcionais:

- A pesquisa deve retornar resultados em no máximo 5 segundos.
- A listagem deve suportar paginação com no mínimo 10 e no máximo 50 itens por página.

---

## UC11

**Caso de uso:** Enviar Documentos
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário enviar documentos relacionados à banca. Generaliza-se em Enviar Documentos da Banca (UC5) e Enviar Atestados (UC6).
**Pré-Condições:** Documentos disponíveis no sistema e secretário autenticado.
**Pós-Condições:** Documentos enviados aos destinatários.

### Sequência Típica de Eventos (Fluxo Básico):

1. O secretário acessa a opção de enviar documentos.
2. O sistema exibe a lista de bancas com documentos disponíveis para envio.
3. O secretário seleciona uma banca.
4. O sistema exibe os documentos disponíveis para envio.
5. O secretário seleciona o tipo de documento a enviar:
   5.1. Se for documentos da banca, ver subseção Enviar Documentos da Banca.
   5.2. Se for atestados, ver subseção Enviar Atestados.
6. O sistema registra o envio.
7. O sistema exibe confirmação de envio.

### Subseção: Enviar Documentos da Banca (UC5)

1. O sistema exibe os documentos da banca (atas, formulários de avaliação).
2. O secretário seleciona os destinatários (membros da banca).
3. O secretário confirma o envio.
4. O sistema envia os documentos aos membros selecionados.

### Subseção: Enviar Atestados (UC6)

1. O sistema exibe os atestados de participação gerados.
2. O secretário seleciona os membros que receberão os atestados.
3. O secretário confirma o envio.
4. O sistema envia os atestados aos membros selecionados.

### Sequências Alternativas:

**4a. Documentos ainda não gerados:**

1. O sistema informa que os documentos ainda não foram gerados para a banca selecionada.
2. O secretário retorna à lista de bancas.
3. Retorna ao passo 2.

**5.1.3a. Falha no envio de documentos da banca:**

1. O sistema informa que houve falha no envio.
2. O secretário pode tentar reenviar.
3. Retorna ao passo 5.1.2.

### Requisitos Não-Funcionais:

- O envio de documentos deve ser concluído em no máximo 10 segundos.
- O sistema deve registrar log de todos os envios realizados.

---

## UC9

**Caso de uso:** Gerar Relatório de Bancas
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário gerar relatórios sobre as bancas realizadas em um determinado período, contendo informações como quantidade de defesas, orientadores, resultados e datas.
**Pré-Condições:** Secretário autenticado no sistema e existem bancas registradas.
**Pós-Condições:** Relatório gerado e exibido ao secretário.

### Sequência Típica de Eventos (Fluxo Básico):

1. O secretário acessa a opção de gerar relatório de bancas.
2. O sistema exibe as opções de configuração do relatório (período, tipo).
3. O secretário informa o período desejado (data início e data fim).
4. O secretário solicita a geração do relatório.
5. O sistema busca as bancas realizadas no período informado.
6. O sistema gera e exibe o relatório com os dados: quantidade de defesas, orientadores, alunos, datas e resultados.

### Sequências Alternativas:

**6a. Nenhuma banca encontrada no período:**

1. O sistema informa que não existem bancas realizadas no período selecionado.
2. O secretário pode alterar o período.
3. Retorna ao passo 3.

**4a. Relatório detalhado:**

1. O secretário seleciona o tipo "detalhado".
2. O sistema gera o relatório incluindo informações adicionais: membros das bancas, notas, observações do coordenador.
3. Retorna ao passo 7.

### Requisitos Não-Funcionais:

- O relatório deve ser gerado em no máximo 10 segundos.
- O relatório deve estar disponível para download em formato PDF.
