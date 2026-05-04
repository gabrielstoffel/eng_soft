# ATA DE REUNIÃO

**Data:** 23 de março de 2026
**Horário:** Início às 09h30min — Término: 10h17min
**Local:** Google Meet
**Assunto:** Levantamento de requisitos para o sistema de gerenciamento de bancas acadêmicas (Projeto de Engenharia de Software)

---

## 1. Participantes

| Nome | Função |
|------|--------|
| Antônio | Servidor do PPG Física — Instituto de Física (IEF/UFRGS) |
| Liane | Servidora do PPG Ensino de Física — Instituto de Física (IEF/UFRGS) |
| Fidel | Aluno integrante do projeto de Engenharia de Software |
| Gabriel | Aluno integrante do projeto de Engenharia de Software |
| João Victor | Aluno integrante do projeto de Engenharia de Software |
| Lucas | Aluno integrante do projeto de Engenharia de Software |
| Ricardo | Aluno integrante do projeto de Engenharia de Software |

**Coordenação da reunião:** Lucas Nogueira
**Redator da ata:** Lucas Nogueira

---

## 2. Ordem do Dia

- Processo atual de solicitação e aprovação de bancas nos PPGs do Instituto de Física
- Tipos de bancas e documentação necessária
- Fluxo de comunicação entre orientadores, secretarias e Comissão de Pós-Graduação (CPG)
- Agendamento de salas e recursos físicos
- Identificação de pontos de dor e oportunidades de automação
- Alinhamento de expectativas sobre o sistema a ser desenvolvido

---

## 3. Resumo das Discussões

### 3.1. Processo de solicitação de bancas

Liane explicou que o processo se inicia quando o orientador envia um e-mail ao e-mail institucional da secretaria do PPG, informando os membros propostos para a banca. A proposta é encaminhada à Comissão de Pós-Graduação (CPG) para aprovação ou submetida ao coordenador em regime ad referendum. Após a aprovação, a secretaria providencia a documentação: cartas-convite, folha de conceito, atestados de participação e ata.

Antônio complementou que o PPG Física possui perfis distintos de bancas: dissertação de mestrado, exame de qualificação ao doutorado e tese de doutorado. Cada tipo exige um conjunto diferente de documentos e número de participantes.

### 3.2. Sistema atual — CriaBancas

Antônio relatou que o PPG Ensino de Física possui um sistema próprio, desenvolvido anteriormente pela equipe de informática do Instituto e incorporado ao site institucional (em Plone). O PPG Física, por sua vez, migrou para um site em WordPress, o que gerou incompatibilidade com o sistema existente. Diante disso, foi desenvolvida uma versão inicial do sistema "CriaBancas" por bolsistas do PPG Física, utilizada até o presente momento. O sistema gera os documentos necessários, porém não possui funcionalidade de envio automático de e-mails.

### 3.3. Diferenças entre os dois PPGs

Ficou registrado que os dois programas de pós-graduação possuem regimentos, modelos de documentos e fluxos distintos.

- No PPG Física, o orientador preenche um formulário formal com a proposta de banca.
- No PPG Ensino de Física, o orientador envia as informações por e-mail, sem formulário padronizado.

Liane informou que tentou implementar um modelo de carta no seu PPG, mas os orientadores não aderiram.

Quanto à aprovação das bancas, Liane mencionou que no PPG Ensino de Física as propostas geralmente são aprovadas sem ressalvas. Antônio relatou que no PPG Física já houve casos de negativa ou solicitação de substituição de membros pela CPG, embora isso não tenha sido frequente recentemente.

### 3.4. Fluxo de comunicação e tipos de e-mail

Liane identificou três tipos de e-mail no fluxo de trabalho:

1. E-mail de divulgação da defesa (enviado a uma lista de distribuição);
2. E-mail de convite aos membros da banca, com carta-convite e folha de conceito;
3. E-mail posterior à banca, com atestado de participação, enviado após o recebimento da folha de conceito preenchida.

O sistema do PPG Ensino de Física já automatiza o envio do e-mail de divulgação, mas os convites individuais e os atestados são enviados manualmente em ambos os PPGs.

### 3.5. Membros titulares e suplentes

Antônio esclareceu que no PPG Física sempre há indicação de membros suplentes, os quais também recebem carta-convite formal. No PPG Ensino de Física, a indicação de suplentes é mais rara, pois os orientadores já confirmam a disponibilidade dos membros antes da solicitação formal.

### 3.6. Agendamento de salas e recursos

A reserva de salas (sala de videoconferência e Anfiteatro Antônio Cabral) é feita pela secretaria do PPG junto à gerência administrativa do IEF. Também é necessário agendar assessoria com a equipe de TI do Instituto para suporte técnico na transmissão remota.

Antônio mencionou que já ocorreram situações de indisponibilidade de sala, exigindo renegociação de data com o orientador. Foi informado que a informática do Instituto está desenvolvendo um sistema de gerenciamento de salas, porém ainda não implantado.

### 3.7. Aderência ao novo sistema

Antônio afirmou não haver resistência à adoção de um novo sistema, uma vez que os operadores diretos são ele próprio e uma bolsista. Liane concordou e ressaltou que a chefia é favorável à inovação. Ambos alertaram que o sistema não deve dificultar o trabalho dos orientadores, que atualmente utilizam um processo simples de envio por e-mail.

### 3.8. Frequência e volume de bancas

- Liane informou que o PPG Ensino de Física possui cerca de 60 alunos (30 no mestrado e 31 no doutorado), com volume variável — de uma banca por mês a cinco ou seis no mesmo mês, concentradas em períodos de final de semestre (julho e dezembro).
- Antônio informou que o PPG Física possui aproximadamente 100 alunos e demanda proporcionalmente maior, com picos de até cinco bancas em uma mesma semana.

### 3.9. Alteração de templates

Antônio esclareceu que os modelos de documentos não possuem frequência definida de alteração, sendo modificados apenas quando há mudança de regimento ou nova resolução institucional, o que ocorre esporadicamente.

---

## 4. Decisões e Encaminhamentos

| # | Deliberação | Responsável | Prazo | Status |
|---|-------------|-------------|-------|--------|
| 1 | Desenvolver sistema unificado para os dois PPGs, com seleção do programa na interface, carregando os modelos e fluxos específicos de cada um | Equipe do projeto (Lucas, Gabriel, João Victor, Ricardo, Fidel) | A definir | Aprovado |
| 2 | O sistema deverá contemplar: (a) formulário de preenchimento pelo orientador; (b) geração automática de documentos; (c) fluxo de aprovação interna pelo PPG e encaminhamento ao coordenador/CPG; (d) envio automático de e-mails (convites e consulta de sala) | Equipe do projeto | A definir | Aprovado |
| 3 | Enviar aos alunos do projeto os modelos de cartas-convite e documentos utilizados atualmente | Liane e Antônio | A definir | Pendente |
| 4 | Enviar resoluções e regulamentações dos PPGs referentes a bancas | Liane | A definir | Pendente |
| 5 | Manter comunicação contínua entre a equipe do projeto e os servidores dos PPGs para validação e feedback | Lucas, Liane e Antônio | Contínuo | Em andamento |

---

## 5. Encerramento

Nada mais havendo a tratar, Lucas agradeceu a participação de Liane e Antônio, bem como dos alunos integrantes do projeto, e a reunião foi encerrada.
