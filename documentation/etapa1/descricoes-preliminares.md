# Descrições Preliminares dos Casos de Uso

## UC1

**Caso de uso:** Formalizar Pedido de Banca
**Ator:** Orientador
**Descrição:** Permite ao orientador registrar no sistema um pedido de banca para defesa de trabalho acadêmico, informando os dados necessários (aluno, tipo de trabalho, membros, suplentes, data pretendida). Ao formalizar, o sistema envia automaticamente um email ao Coordenador (para avaliação) e ao Secretário do PPG (para ciência).
**Pré-Condições:** Orientador possui acesso à formulário de formalização.
**Pós-Condições:** Pedido de banca registrado e email enviado ao Coordenador e Secretário do PPG.

## UC2

**Caso de uso:** Enviar Email para Coordenador/Secretário do PPG
**Ator:** Sistema (incluído por UC1)
**Descrição:** O sistema envia automaticamente um email de notificação ao Coordenador e ao Secretário do PPG informando que um novo pedido de banca foi formalizado.
**Pré-Condições:** Pedido de banca foi formalizado (UC1).
**Pós-Condições:** Email enviado ao Coordenador e ao Secretário do PPG.

## UC3

**Caso de uso:** Aprovar Banca
**Ator:** Coordenador
**Descrição:** Permite ao coordenador avaliar um pedido de banca e decidir pela aprovação ou recusa. O orientador é sempre notificado do resultado. Caso aprovada, o sistema gera os documentos necessários.
**Pré-Condições:** Pedido de banca formalizado.
**Pós-Condições:** Pedido aprovado ou recusado, orientador notificado. Se aprovado, documentos gerados.

## UC4

**Caso de uso:** Gerar Documentos
**Ator:** Sistema (extend de UC3)
**Descrição:** Quando uma banca é aprovada, o sistema gera automaticamente os documentos necessários para a realização da banca (atas, formulários de avaliação, convite, etc).
**Pré-Condições:** Banca aprovada pelo coordenador (UC3).
**Pós-Condições:** Documentos da banca gerados e disponíveis no sistema.

## UC5

**Caso de uso:** Enviar Documentos da Banca
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário enviar os documentos oficiais da banca aos membros participantes. Especialização de Enviar Documentos (UC11).
**Pré-Condições:** Documentos da banca gerados no sistema.
**Pós-Condições:** Documentos da banca enviados aos membros participantes.

## UC6

**Caso de uso:** Enviar Atestados
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário enviar os atestados de participação aos membros da banca após a realização da defesa. Especialização de Enviar Documentos (UC11).
**Pré-Condições:** Banca realizada.
**Pós-Condições:** Atestados de participação enviados aos membros da banca.

## UC7

**Caso de uso:** Pesquisar Bancas
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário pesquisar bancas cadastradas no sistema utilizando diferentes critérios (por orientador, por data) e visualizar os resultados em listagem paginada.
**Pré-Condições:** Secretário autenticado no sistema.
**Pós-Condições:** Resultados da pesquisa exibidos ao secretário.

## UC8

**Caso de uso:** Editar Documentos
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário editar documentos relacionados às bancas, como corrigir informações em atas ou atualizar dados dos membros participantes.
**Pré-Condições:** Documento existente no sistema e secretário autenticado.
**Pós-Condições:** Documento atualizado no sistema.

## UC9

**Caso de uso:** Gerar Relatório de Bancas
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário gerar relatórios sobre as bancas realizadas em um determinado período, contendo informações como quantidade de defesas, orientadores, resultados e datas.
**Pré-Condições:** Secretário autenticado no sistema e existem bancas registradas.
**Pós-Condições:** Relatório gerado e exibido ao secretário.

## UC10

**Caso de uso:** Notificar Orientador
**Ator:** Sistema (incluído por UC3)
**Descrição:** O sistema envia automaticamente uma notificação ao orientador informando o resultado da avaliação do pedido de banca (aprovação ou recusa).
**Pré-Condições:** Coordenador finalizou a avaliação do pedido (UC3).
**Pós-Condições:** Orientador notificado do resultado.

## UC11

**Caso de uso:** Enviar Documentos
**Ator:** Secretário do PPG
**Descrição:** Permite ao secretário enviar documentos relacionados à banca. Generaliza-se em Enviar Documentos da Banca (UC5) e Enviar Atestados (UC6).
**Pré-Condições:** Documentos disponíveis no sistema e secretário autenticado.
**Pós-Condições:** Documentos enviados aos destinatários.
