# Problemas encontrados e status

## Corrigidos

1. ~~Label `<<include>>` na seta de generalização~~ - Corrigido no PlantUML
2. ~~Inconsistência nos nomes (verbos)~~ - Todos padronizados para infinitivo
3. ~~"Geração de Documentos" usava substantivo~~ - Renomeado para "Gerar Documentos"
4. ~~Nenhuma relação `<<extend>>`~~ - Adicionado: Gerar Documentos extends Aprovar Banca
5. ~~Faltava 2o `<<include>>`~~ - Adicionado: Aprovar Banca includes Notificar Orientador
6. ~~Coordenador conectado a Enviar Email sem necessidade~~ - Removido (é comportamento automático via include)
7. ~~Generalização errada (Enviar != subtipo de Gerar)~~ - Reestruturado: Enviar Documentos como UC geral, com Enviar Atestados e Enviar Documentos da Banca como especializações
8. ~~Secretário conectado a Gerar Documentos (ambíguo)~~ - Conectado a Enviar Documentos

## A tratar nas descrições textuais (não no diagrama)

- Item e) 2 formas de pesquisa: detalhar na descrição de "Pesquisar Bancas"
- Item f) Dois sentidos da transação: recusa como fluxo alternativo de "Aprovar Banca"
