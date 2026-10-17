# Documentacao

Comece pelo [guia do usuario](operacao/GUIA_DO_USUARIO.md) para executar o
fluxo existente, ou pelo [mapa do projeto](ESTRUTURA_DO_PROJETO.md) para
localizar codigo, comandos publicos e contratos.

## Desenvolvimento e retomada

- [Roadmap WEB](ROADMAP_WEB.md): escopo, dependencias, criterios e estado.
- [Progresso e retomada](PROGRESS.md): ultima unidade e proxima acao.
- [Protocolo de trabalho](desenvolvimento/WORKFLOW_CODEX_CLI.md).
- [Validacao WEB e piloto](VALIDACAO_WEB.md).
- [CI WEB reproduzivel](desenvolvimento/CI_WEB.md).
- [Contrato HTTP WEB](desenvolvimento/CONTRATO_API_WEB.md).
- [Padrao de commits](desenvolvimento/PADRAO_DE_COMMITS.md).
- [Registro de alteracoes](REGISTRO_DE_ALTERACOES.md): evidencias datadas.
- [Instrucoes de documentacao](AGENTS.md).

## Mapa por assunto

| Pasta | Conteudo | Fontes principais |
|---|---|---|
| [arquitetura/](arquitetura/) | Decisoes e seus motivos | [Monolito modular](arquitetura/ADR-001-evolucao-web.md), [hospedagem na VPS](arquitetura/ADR-002-hospedagem-vps.md), [escopo legado WEB](arquitetura/ADR-003-escopo-legado-web.md) |
| [experimento/](experimento/) | Paradigma, tempos, condicoes, interface e exportacao | [Decisoes](experimento/DECISOES_DO_EXPERIMENTO.md), [protocolo WEB](experimento/PROTOCOLO_WEB.md), [CSV oficial](experimento/CSV_UNIFICADO.md), [UX](experimento/UX_DECISIONS.md) |
| [dados/](dados/) | Modelo, instrumentos, importacao, migracoes e consulta | [Modelo](dados/MODELO_DE_DADOS.md), [SQLite](dados/IMPORTACAO_SQLITE.md), [PostgreSQL](dados/IMPORTACAO_POSTGRESQL.md), [migrations](dados/MIGRACOES_POSTGRESQL.md) |
| [seguranca/](seguranca/) | Acesso, ameacas, tratamento de dados e incidentes | [Acesso WEB](seguranca/ACESSO_WEB.md), [autenticacao](seguranca/AUTENTICACAO_E_PERMISSOES.md), [threat model](seguranca/THREAT_MODEL.md), [tratamento](seguranca/TRATAMENTO_DE_DADOS.md) |
| [operacao/](operacao/) | Instalacao, uso, Docker e preparacao de producao | [Instalacao](operacao/INSTALACAO_MULTIPLATAFORMA.md), [uso por ZIP](operacao/USO_POR_ZIP_GITHUB.md), [Docker](operacao/INFRAESTRUTURA_DOCKER.md), [Docker WEB](operacao/WEB_DOCKER.md), [recuperacao WEB](operacao/WEB_RECUPERACAO.md), [hardening](operacao/HARDENING_PRODUCAO.md) |
| [desenvolvimento/](desenvolvimento/) | Workflow, contrato da API, commits e templates | [Protocolo](desenvolvimento/WORKFLOW_CODEX_CLI.md), [contrato HTTP](desenvolvimento/CONTRATO_API_WEB.md), [templates](desenvolvimento/prompts/) |
| [legado/](legado/) | Backlog da operacao existente, baselines e propostas anteriores | [Backlog legado](legado/Projeto%20Stroop%20Test.md), [baseline](legado/BASELINE_ETAPA_1.md), [consulta OCI historica](legado/OCI_ETAPA11.md) |

Cada contrato permanece em uma unica fonte. Este indice orienta a navegacao;
nao replica regras, tabelas de progresso ou criterios de aceite. O backlog
legado ainda rege suas etapas; a pasta `legado/` nao significa descontinuacao
do PsychoPy ou do Streamlit.
