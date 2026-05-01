# Diagramas UML — SigBah!

## Arquivos

| Arquivo | Tipo | Descricao |
|---------|------|-----------|
| `package-diagram.puml` | Diagrama de Pacotes | Estilo arquitetural (Clean Architecture), subsistemas e dependencias |
| `use-case-diagram.puml` | Diagrama de Casos de Uso | Atores, casos de uso e relacionamentos (include, extend, generalizacao) |
| `sequence-uc1-submit.puml` | Diagrama de Sequencia | UC1: Formalizar Pedido de Banca |
| `sequence-uc3-approve.puml` | Diagrama de Sequencia | UC3: Aprovar Banca (aprovacao e recusa) |
| `class-diagram.puml` | Diagrama de Classes | Modelo de dominio (entidades, repositorio, servico, erros) |
| `deployment-diagram.puml` | Diagrama de Deployment | Disposicao fisica dos componentes (Docker, uvicorn, Vite) |

## Como renderizar

### Opcao 1: CLI (PlantUML)

```bash
# Instalar (Ubuntu/Debian)
sudo apt install plantuml

# Gerar PNGs de todos os diagramas
plantuml -tpng *.puml

# Gerar SVGs (melhor qualidade para relatorio)
plantuml -tsvg *.puml
```

### Opcao 2: VS Code

1. Instalar extensao "PlantUML" (jebbs.plantuml)
2. Abrir qualquer arquivo `.puml`
3. `Alt+D` para pre-visualizar

### Opcao 3: Online

1. Acessar https://www.plantuml.com/plantuml
2. Colar o conteudo do arquivo `.puml`
3. Clicar "Submit"

## Ferramenta CASE

Os arquivos `.puml` sao os fontes da ferramenta CASE (PlantUML), conforme exigido na especificacao da etapa 2. PlantUML gera diagramas UML padrao a partir de descricoes textuais.
