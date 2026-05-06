# SigBah! — Decisões Técnicas

Documento curto com as principais decisões técnicas tomadas no desenvolvimento do SigBah!, com a justificativa de cada uma.

## Stack

| Camada         | Escolha                                  | Justificativa                                                                                       |
| -------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Backend        | Python 3.12 + FastAPI                    | Tipagem via Pydantic, OpenAPI automático, ecossistema maduro para geração de PDF (`fpdf2`).         |
| Gerenciador    | `uv`                                     | Resolução e instalação de dependências consideravelmente mais rápidas que `pip`/`poetry`.           |
| Frontend       | Vite + React 19 (JS puro, sem TS)        | Build rápido, hot reload imediato; equipe optou por JS puro para reduzir fricção no escopo do TCC.  |
| Estilo         | TailwindCSS 4                            | Padronização visual sem CSS custom; integração nativa com Vite via `@tailwindcss/vite`.             |
| Formulários    | `react-hook-form` + `zod`/`joi`          | Validação declarativa no cliente, espelhando os contratos Pydantic do backend.                      |
| Roteamento     | `react-router-dom` 7                     | Rotas tipadas por caminho, suporte a parâmetros (`/decide/:token`, `/admin/banca/:token`).          |
| Banco          | MongoDB 7                                | Documentos da banca têm forma flexível (versões, manifestos de PDFs); evita migrations custosas.    |
| E-mail (dev)   | Postfix → Mailpit                        | Captura local de e-mails sem risco de envio externo durante desenvolvimento e demonstração.         |
| Infra local    | Docker Compose                           | Sobe Mongo + Postfix + Mailpit com um comando; backend/frontend rodam fora do container para DX.    |

## Arquitetura do backend

Arquitetura limpa em quatro camadas, com dependências apontando apenas para dentro:

```
api/            → HTTP: parse de request, injeção de dependências, mapeia Result → status HTTP
application/    → Casos de uso: orquestram serviços, devolvem Result
domain/         → Contratos (ABCs), modelos Pydantic e erros tipados — sem acoplamento a framework
infrastructure/ → Implementações concretas (MongoDB, SMTP)
```

**Por quê:** isola regra de negócio do framework e do banco, facilita testes unitários e troca de implementações (ex.: trocar Mongo sem mexer em casos de uso).

## Padrões adotados

### Result pattern

Métodos de serviço retornam `Result[T, E]` (`Ok` / `Err`) — não levantam exceções na fronteira do serviço.

**Por quê:** torna explícitos no tipo todos os caminhos de erro, evita exceções "invisíveis" subindo pela pilha e força o roteador a tratar cada caso.

### Erros de domínio tipados

Cada erro é uma `dataclass` em `app/domain/errors.py` herdando de `BancaError`. O roteador HTTP mapeia cada tipo a um status code específico (ex.: `DocumentGenerationError` → 500, `PersistenceError` → 503).

**Por quê:** desacopla a representação do erro (domínio) da sua expressão HTTP (API).

### Injeção de dependências centralizada

Todos os providers `Depends()` vivem em `app/deps.py` como singletons de módulo. Roteadores recebem serviços já construídos.

**Por quê:** ponto único para trocar implementações em testes; evita instanciação espalhada.

### Logging estruturado

Wrapper em `app/logger.py` exige `event_kind` (caminho separado por ponto, ex.: `banca_service.create.start`) e `data` (dict). Root logger em `WARNING`, namespace `app.*` em `INFO` — silencia ruído de bibliotecas terceiras.

**Por quê:** logs filtráveis por evento, sem strings livres; facilita observabilidade futura.

## Decisões de modelo de dados

- **Bancas aprovadas são uma lista ordenada de versões.** Editar gera nova versão somente se houver mudança de conteúdo.
  **Por quê:** preserva auditoria do que foi enviado a cada participante.
- **Cada versão expõe um manifesto de PDFs individuais** (Ata, Cartas de Convite, Pareceres, Cartaz, Relatoria). Download um a um ou como zip de seleção.
  **Por quê:** secretaria reenvia documentos pontuais sem regerar tudo.
- **Decisão do coordenador via token em URL** (`/decide/:token`), enviado por e-mail.
  **Por quê:** evita exigir login para um ator que interage com o sistema esporadicamente — atende ao requisito de "decidir sem sair da caixa de e-mail" (UC3).

## Decisões de frontend

- **Sem TypeScript.** Validação de payloads delegada a `zod`/`joi` em runtime.
  **Por quê:** reduz superfície de configuração para um time pequeno; tipos do backend já são autoritativos via OpenAPI.
- **Flag única `ENV=development`** controla todo comportamento de dev (atalhos, dados de teste, etc.), sem toggles por feature.
  **Por quê:** evita proliferação de flags e estados intermediários difíceis de raciocinar.

## Fluxo de e-mail

```
backend → localhost:2525 → postfix → mailpit:1025 → http://localhost:8025
```

Nada sai para a internet em ambiente local. O backend fala SMTP comum; trocar Mailpit por um relay real é configuração, não código.
