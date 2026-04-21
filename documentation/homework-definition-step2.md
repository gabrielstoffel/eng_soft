# Trabalho Pratico - Enunciado da Etapa 2

## Iteracao de Investigacao

Nas etapas 2 e 3, o grupo DESENVOLVEDOR deve projetar e implementar parte da aplicacao para o seu ANALISTA, seguindo as especificacoes da etapa de analise. O projeto/implementacao deve obedecer a seguinte diretriz:

- A escolha de linguagem (orientada a objetos) ou uso de frameworks/bibliotecas/utilitarios fica a cargo do grupo desenvolvedor. **SEJA CUIDADOSO AO ESCOLHER AS TECNOLOGIAS E CONSIDERE A CURVA DE APRENDIZAGEM!** A linguagem de programacao deve ser Python.

O grupo Desenvolvedor construira os casos de uso prioritarios a sua aplicacao, considerando o que foi definido pelo grupo de analise. O grupo deve projetar e implementar uma aplicacao relativa aos casos de uso que explicitam as seguintes funcionalidades:

- Cadastrar recursos;
- Pesquisar recursos e visualizar suas propriedades;
- Selecionar um recurso para realizar a transacao;
- Realizar transacao comercial nos dois sentidos (ocupar e liberar recurso - emprestar e devolver, locar e devolver, oferecer e aceitar algo pela troca, oferecer lance/arrematar).

O grupo desenvolvedor pode assumir simplificacoes sobre os diferentes casos de uso relacionados a estas funcionalidades. Se assumirem, devem explicitar quais sao (ex.: disponibiliza apenas algum tipo especifico de recurso dentre os muitos solicitados, realiza uma transacao mas nao paga; selecao de uma entre as varias opcoes de troca, etc.). Converse com o seu cliente para entender bem o escopo e faca atas de reunioes caso sejam feitas alteracoes no escopo. Inclua uma listagem das simplificacoes feitas e prepare um slide para a apresentacao com estas simplificacoes.

Na Etapa 2, seu objetivo e escolher e familiarizar-se com a plataforma de implementacao, e esbocar sua arquitetura. Sua implementacao e a forma de atingir este objetivo. Escolha assim no minimo **UM** caso de uso que permita atingir este objetivo e implemente (codifique). Sugere-se pesquisar recurso de um lado da transacao, mas o grupo e livre para escolher um caso de uso qualquer (se ja quiser implementar mais casos de uso, podem fazer). Observe que se os casos de uso forem muito simples (ex.: cadastrar cliente e login), o grupo pode ter surpresas na etapa 3, quando descobrir que sua arquitetura nao e facilmente extensivel, ou que e bem mais dificil de usar o estilo arquitetural escolhido. Observe tambem a escolha de casos de uso que agregam valor para a arquitetura. Por exemplo, para pesquisar sobre um recurso, o caso de uso que o cadastra nao necessariamente deve ter sido implementado. Tente implementar mais de um caso de uso, pois estara adiantando trabalho para a etapa 3.

Na Etapa 3, seu objetivo sera desenvolver o modelo de projeto dos casos de uso prioritarios de sua aplicacao, e concluir a implementacao deste. Detalhes sobre esta etapa serao informados, apos a entrega da etapa 2.

---

## Entrega

### Entrega como DESENVOLVEDOR (um por grupo)

Enviar via moodle um arquivo compactado (formato zip), contendo:

- Arquivo do projeto da ferramenta CASE escolhida, contendo os diagramas desenvolvidos.
- Codigo fonte ou link para o codigo fonte ja desenvolvido.
- Atas de reunioes com os analistas.
- Apresentacao (conjunto de slides) incluindo:
  - Breve descricao do negocio.
  - Estilo arquitetural escolhido, justificando porque escolheu o estilo e apresentando o diagrama de pacotes.
  - Simplificacoes realizadas.
  - Casos de uso implementados.
  - Demonstracao dos casos de uso implementados em tempo real (sugere-se reservar mais tempo para a demonstracao).

**IMPORTANTE:** Nesta etapa nao havera entrega de relatorio, mas sim apresentacao presencial E demonstracao em tempo real (**PROIBIDO O USO DE VIDEOS DE DEMONSTRACAO**), alem da entrega dos slides.

---

## Restricoes e Diretrizes

O grupo desenvolvedor deve:

- Desenvolver uma arquitetura preliminar, sua divisao em sistemas, as interdependencias entre estas. Deve ser expresso utilizando **diagramas de pacotes**. A arquitetura deve deixar clara as responsabilidades de cada subsistema, suas dependencias, bem como as escolhas tecnologicas.
- Definir quais os casos de uso da Etapa 1 serao implementados, e as respectivas simplificacoes.
- **Opcional:** pode-se desenvolver um modelo de analise.
- **Opcional:** pode-se fazer o projeto detalhado de acordo com notacao UML.
- Implementar um ou mais casos de uso a sua escolha (sugiro implementar mais de um), dentre as funcionalidades anteriormente solicitadas.

> **Observacao 1.** A entrega de material opcional nao e esperada, mas sera valorizada na avaliacao (mas a nota maxima continua sendo 1,5 pontos de 5).

> **Observacao 2.** Os modelos de casos de uso devem ser atualizados sempre que surgirem duvidas que apontem problemas no modelo, alem das observacoes feitas pela professora. Mantenha o modelo de casos de uso atualizado, pois na etapa 3 deve ser submetida a versao final do modelo, que deve estar de acordo com o sistema desenvolvido. Como analista voce deve interagir com o cliente para manter os modelos atualizados.

---

### Entrega como ANALISTA (um por grupo)

O grupo deve corrigir o enunciado da etapa 1 (seu proprio relatorio com casos de uso e especificacao dos casos de uso), conforme apontamentos da professora e alteracoes feitas, atraves das reunioes com os clientes.

O relatorio deve incluir:

- Nome e e-mail dos integrantes do grupo.
- Listagem clara das alteracoes feitas no inicio do documento.
- Novo diagrama de casos de uso (se alterado). Se nao foi alterado, inclua uma nota informando que nao foi alterado.
- Nova especificacao textual dos casos de uso que sofreram alguma alteracao. Faca isso apenas para os 4 casos de uso mais importantes. A especificacao deve ser expandida (essencial). Os demais casos de uso nao precisam ser entregues. **DESTAQUE EM CORES TUDO QUE TIVER ALTERADO COM RELACAO A ETAPA 1.**

Todos os documentos desta entrega (Arquivo fonte do diagrama, link do codigo fonte, relatorio corrigido como analista e slides) devem ser entregues em um arquivo .zip na data definida no Moodle da disciplina. A imagem do diagrama de casos de uso deve constar no documento de analise.

**Fazer UMA entrega por grupo de trabalho!**
