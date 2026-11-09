# Plataforma Stroop Web

Desenvolver uma plataforma Web modular para aplicação, gerenciamento e análise
de avaliações cognitivas, iniciando pelo Stroop Go/No-Go, com integridade de dados,
rastreabilidade metodológica, segurança e capacidade de expansão.

O repositório já contém React + TypeScript + Vite, motor jsPsych e API própria
Python/FastAPI com PostgreSQL, além da operação histórica PsychoPy/Streamlit.
O plano atual consolida e revalida essa implementação; não representa migração
concluída. A tarefa executa no navegador e envia resultados à API para cálculo
oficial/persistência. CSV é intercâmbio complementar. Docker/Nginx/HTTPS já têm
configuração versionada; sua existência não comprova disponibilidade publicada.

Fluxo alvo: avaliador autenticado → preparação de avaliação/convite → identificação
pseudonimizada → instruções → prática → tarefa no navegador → tentativas/API →
PostgreSQL → métricas → dashboard React → exportações autorizadas.

PsychoPy é referência histórica e metodológica; Streamlit será substituído como
interface operacional final, permanecendo preservado na transição. Uso educacional
e pesquisa exploratória, sem diagnóstico, norma, percentil clínico ou equivalência
psicométrica presumida. Fórmulas preservadas não certificam temporização física.
O código atual restringe projetos a ensaios sintéticos; uso real exige decisão e
validação próprias. Publicação para testes foi registrada historicamente, sem
verificação remota nesta auditoria.

Comece por:

- [Backlog canônico: marcos, tarefas, aceite e próxima ação](docs/Projeto%20Stroop%20Test.md).
- [Arquitetura atual/alvo e transição](docs/ARQUITETURA_WEB.md).
- [Requisitos e rastreabilidade](docs/REQUISITOS_E_RASTREABILIDADE.md).
- [Auditoria de código e limitações](docs/AUDITORIA_REPLANEJAMENTO.md).
- [Workflow Codex CLI](docs/WORKFLOW_CODEX_CLI.md), [AGENTS](AGENTS.md) e [contribuição](CONTRIBUTING.md).
- [Índice documental](docs/README.md), [API](api/README.md) e [Web](web/README.md).

`mostrar status` é somente leitura; `continue o projeto` executa o marco autorizado;
`validar marco atual` verifica sem novas funções; `replanejar` revisa o plano.
Branches/commits/pushes validados são autônomos; não criar PR/merge automaticamente.
Produção, main e dados reais exigem autorização específica. Esta entrega é
exclusivamente documental e para antes de qualquer implementação futura.

## Operação histórica preservada

As instruções abaixo mantêm os comandos públicos existentes. Não significam que
PsychoPy/Streamlit sejam a interface final da plataforma nem autorizam coleta real,
instalação de produção ou alteração de infraestrutura durante replanejamento.

## Uso em qualquer sistema

O PsychoPy precisa ser instalado separadamente para executar ou editar o experimento. O fluxo abaixo configura apenas o dashboard local, baseado em Python, Streamlit e SQLite.

Para usar sem Git, abra o repositorio no GitHub e escolha `Code` -> `Download ZIP`, descompacte o arquivo e abra um terminal dentro da pasta. Em repositorios privados, e necessario estar conectado a uma conta autorizada. Consulte o passo a passo em [`docs/operacao/USO_POR_ZIP_GITHUB.md`](docs/operacao/USO_POR_ZIP_GITHUB.md) e o fluxo cotidiano em [`docs/operacao/GUIA_DO_USUARIO.md`](docs/operacao/GUIA_DO_USUARIO.md).

No Windows:

1. Instale o Python 3.9 ou mais recente.
2. Execute `setup.bat`.
3. Execute `abrir_dashboard.bat`.

No Linux ou macOS:

1. Instale o Python 3.9 ou mais recente.
2. Execute `bash setup.sh`.
3. Execute `bash abrir_dashboard.sh`.

Para verificar o ambiente sem instalar dependencias, modificar dados, criar banco ou
abrir o dashboard, execute a partir da raiz do projeto:

```text
Windows:     py scripts\doctor.py
Linux/macOS: python3 scripts/doctor.py
```

O diagnostico informa `OK`, `ERRO` ou `AVISO` para os componentes necessarios e
mostra instrucoes de correcao especificas para cada plataforma.

Uso manual, a partir da raiz do projeto:

```text
python scripts/setup_env.py
python scripts/run_dashboard.py
```

O launcher importa o arquivo mais recente em `data/*_trials.csv` e abre o
dashboard. O acesso ao dashboard exige Google OIDC, usuario previamente
cadastrado e `AUTH_DATABASE_URL`; veja
[`docs/seguranca/AUTENTICACAO_E_PERMISSOES.md`](docs/seguranca/AUTENTICACAO_E_PERMISSOES.md). Use
`--csv CAMINHO` para selecionar outro CSV e `--force` para reimportar uma
avaliacao. Os CSVs e o banco permanecem locais em `data/` e `database/`;
`database/` nao deve ser enviada ao Git. Os resultados apresentados sao
descritivos, nao clinicos.

## Infraestrutura Docker de desenvolvimento

A infraestrutura Docker mantém containers separados para Streamlit e
PostgreSQL, sem instalar o PsychoPy na imagem. O dashboard usa PostgreSQL
quando a URL de leitura está configurada e preserva o fluxo SQLite local como
fallback.
Copie `.env.example` para `.env`, ajuste a senha ficticia e execute:

```bash
docker compose up --build -d --wait
```

Consulte [`docs/operacao/INFRAESTRUTURA_DOCKER.md`](docs/operacao/INFRAESTRUTURA_DOCKER.md) para
limites, validacao e encerramento seguro sem excluir o volume.

A preparacao de producao fica separada em `compose.production.yaml`, com Nginx,
TLS obrigatorio, servicos internos, limites e backup criptografado. Ela nao
configura nem autoriza deploy. Consulte
[`docs/operacao/HARDENING_PRODUCAO.md`](docs/operacao/HARDENING_PRODUCAO.md), o
[`threat model`](docs/seguranca/THREAT_MODEL.md) e a
[`resposta a incidentes`](docs/seguranca/RESPOSTA_A_INCIDENTES.md).

O schema PostgreSQL versionado e a migracao legada SQLite -> PostgreSQL sao
operacoes explicitas documentadas em
[`docs/dados/MIGRACOES_POSTGRESQL.md`](docs/dados/MIGRACOES_POSTGRESQL.md). O launcher e o
dashboard autenticado usam `DASHBOARD_DATABASE_URL` com leitura somente; o
fallback SQLite permanece apenas para uso local sem essa variável. A CLI separada de
[importacao CSV PostgreSQL](docs/dados/IMPORTACAO_POSTGRESQL.md) usa `DATABASE_URL` e
oferece `--validate-only` para conferir uma entrada sem persistir.

## Upload autenticado de CSV

A [area de upload autenticado](docs/dados/UPLOAD_LOCAL.md) recebe um CSV por operacao
para o PostgreSQL, com limite de 5 MiB, validacao e descarte do temporario.
Com OIDC, `DATABASE_URL`, `DASHBOARD_DATABASE_URL`, `AUTH_DATABASE_URL` e migrations configurados, execute
`.venv/bin/python scripts/upload_local.py --local` e abra
`http://127.0.0.1:8501`. Somente os perfis `importacao` e `administracao` veem
essa area. Em operação PostgreSQL, o dashboard de resultados usa a credencial
somente leitura descrita em [`docs/dados/DASHBOARD_POSTGRESQL.md`](docs/dados/DASHBOARD_POSTGRESQL.md).

## Arquivos

| Area | Responsabilidade |
|---|---|
| `stroop_go_nogo_ptbr.psyexp`, `condicoes/`, `assets/` | Experimento local e suas fontes |
| `stroop/` | Dominio, ingestao, casos de uso e persistencia reutilizaveis |
| `scripts/` | CLIs de importacao, migracoes, inicializacao e manutencao |
| `dashboard/` | Interface Streamlit existente |
| `api/` e `web/` | Adaptadores da nova versao WEB |
| `tests/` | Regressao e fixtures sinteticas |
| `docs/` | Contratos e guias agrupados por assunto |
| `nginx/`, Dockerfiles e Compose | Configuracao da infraestrutura |
| `data/`, `database/`, `backups/` | Artefatos locais ignorados pelo Git |

Consulte o [indice da documentacao](docs/README.md), o
[mapa de arquivos e compatibilidade](docs/ESTRUTURA_DO_PROJETO.md) e os
[comandos dos scripts](scripts/README.md) para os detalhes de cada area.

## Como abrir no Builder

1. Abra o PsychoPy.
2. Selecione a interface Builder.
3. Use `File > Open...` e escolha `stroop_go_nogo_ptbr.psyexp`.
4. Verifique se os arquivos em `condicoes/` estao acessiveis.

## Como executar em modo Pilot

1. Abra o experimento no Builder.
2. Use o modo `Pilot` para testar a tarefa sem tratar a execucao como coleta definitiva.
3. Preencha o formulario local de sessao quando solicitado.
4. Confirme a sequencia pre-pratica: abertura, tutorial, inicio da pratica, lembrete rapido e contagem regressiva.
5. Confirme se a pratica mostra feedback e se o bloco principal nao mostra feedback.
6. Use Pilot para verificacoes antes de qualquer coleta real.

## Como executar em modo Run

1. Abra o experimento no Builder.
2. Use o modo `Run` para coleta.
3. Preencha o formulario local de sessao.
4. O CSV unificado da execucao sera gravado em `data/`.
5. Nao versione arquivos gerados em `data/`.

## Condicoes

As palavras usadas sao `VERDE`, `AMARELO`, `ROSA`, `PRETO`, `VERMELHO`, `LARANJA`, `MARROM`, `ROXO`, `AZUL` e `CINZA`.

- `congruent`: palavra e cor correspondem; resposta correta e pressionar `Espaco`.
- `incongruent`: palavra e cor nao correspondem; resposta correta e nao pressionar nada.

Na versao `0.2.2`, cada tentativa da pratica tem:

- fixacao: 300 ms;
- estimulo/resposta: 2000 ms;
- intervalo vazio entre tentativas: 500 ms;
- feedback automatico: 500 ms apos cada tentativa.

Cada tentativa do bloco principal tem:

- fixacao: 300 ms;
- estimulo/resposta: 2500 ms;
- intervalo vazio entre tentativas: 950 ms.

A pratica tem 4 tentativas, com 2 Go/congruentes e 2 No-Go/incongruentes. O bloco principal tem 16 tentativas, com 8 Go/congruentes e 8 No-Go/incongruentes, totalizando cerca de 60 segundos exclusivamente no bloco principal. O fluxo completo e maior por incluir formulario, instrucoes, contagens, pratica e feedbacks.

Durante a pratica e o bloco principal ha um HUD discreto com precisao acumulada. O cronometro visual inicia apenas no comeco da primeira tentativa principal e segue ate o fim do intervalo da ultima tentativa principal. O bloco principal nao exibe texto instrucional durante as tentativas. A precisao ao vivo pode influenciar o comportamento do participante e e uma decisao de UX, nao uma configuracao metodologicamente neutra.

A interface usa tema escuro original com fundo `#0B1020`; os estimulos aparecem sobre um cartao claro para preservar contraste, sem adicionar branco como cor de estimulo.

## Dados

Os CSVs locais ficam em `data/`. Essa pasta e ignorada pelo Git para proteger dados de teste, execucao e participantes.

Cada execucao concluida normalmente gera um unico CSV oficial por tentativa no formato `data/stroop_go_nogo_ptbr_YYYY-MM-DD_HHhMMmSSs_trials.csv`. Nenhum metadado do participante entra no nome do arquivo. Nas execucoes atuais, apenas tentativas do bloco principal sao exportadas no CSV oficial, com `block = main`.

As colunas principais registradas por tentativa sao:

`project`, `participant_id`, `participant_name`, `initials`, `visit`, `evaluator`, `assessment_id`, `assessment_date`, `started_at`, `test_code`, `test_version`, `block`, `trial_number`, `word`, `ink_color`, `condition`, `correct_response`, `key_pressed`, `reaction_time`, `correct`, `error_type`.

`ink_color` usa nomes de cor simples (`green`, `yellow`, `pink`, `black`, `red`, `orange`, `brown`, `purple`, `blue`, `gray`) para manter o CSV unificado compativel com pandas, R e SPSS sem campos RGB com virgulas internas.

Nas execucoes atuais, o CSV oficial exporta apenas o bloco principal. A coluna `block` permanece no contrato e deve usar `main`; a pratica e executada no experimento, mas nao gera linhas no CSV oficial.

`error_type` usa:

- `hit`: pressionou `Espaco` corretamente em tentativa congruente;
- `omission`: deixou de responder em tentativa congruente;
- `correct_rejection`: nao respondeu corretamente em tentativa incongruente;
- `commission`: pressionou `Espaco` em tentativa incongruente.

## Analise

Depois de coletar dados, execute:

```bash
python3 scripts/analisar_stroop.py data/PARTICIPANT_ID.csv
```

O script valida o CSV unificado, calcula metricas descritivas do bloco principal e nao modifica o arquivo original. O contrato completo esta em `docs/experimento/CSV_UNIFICADO.md`.

## Importacao SQLite

Para importar um CSV validado para SQLite local:

```bash
python3 scripts/importar_csv_sqlite.py data/PARTICIPANT_ID.csv
```

Banco padrao:

```text
database/stroop_results.sqlite3
```

Use `--db` para escolher outro caminho e `--force` para reimportar um `assessment_id` ja existente. A pasta `database/` e local e ignorada pelo Git. A documentacao completa esta em `docs/dados/IMPORTACAO_SQLITE.md`.

## Camada de dados e dashboard

A arquitetura operacional é: PsychoPy -> CSV bruto unificado -> importador PostgreSQL -> dashboard Streamlit autenticado. O fluxo SQLite continua como fallback local.

Os contratos tecnicos estao em `docs/dados/DADOS_E_DASHBOARD.md`,
`docs/dados/MODELO_DE_DADOS.md`, `docs/experimento/CSV_UNIFICADO.md` e `docs/dados/IMPORTACAO_SQLITE.md`.
As antigas fases sao historicas; nao exigem dados reais para aceite do workflow.
Planejamento e progresso atuais ficam somente no [backlog canônico](docs/Projeto%20Stroop%20Test.md); o arquivo em legado/ é histórico congelado.

Para rodar o dashboard:

```bash
python3 -m pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

Banco operacional esperado:

```text
DASHBOARD_DATABASE_URL=postgresql://dashboard_ro:***@postgres:5432/stroop_production
```

O dashboard usa a conexão PostgreSQL somente leitura e exibe resultados
descritivos sem diagnóstico ou interpretação clínica. Sem a URL, usa o SQLite
local em modo somente leitura.

## Metadados da sessao

Antes da primeira tela, o experimento exibe um formulario local com `project`, `participant_id`, `participant_name`, `initials`, `visit` e `evaluator`. A data, hora, `assessment_id`, `test_code` e `test_version` sao gerados automaticamente.

Use `participant_id` como identificador tecnico principal. `participant_name` e dado pessoal local e nao deve aparecer em nome de arquivo, screenshots, exemplos publicos, logs ou commits. Nao informe nome completo, CPF, e-mail, telefone, endereco, idade ou sexo. As regras completas estao em `docs/experimento/FORMULARIO_DE_SESSAO.md`.

## Interface pre-pratica

A primeira parte da interface visual conduz o participante por abertura, tutorial da regra, introducao a pratica e lembrete rapido antes da contagem regressiva. As telas navegaveis aceitam clique, `Espaco` e `Enter`. Essa etapa nao registra linhas no CSV canonico e nao altera as tentativas Stroop.

## Estrutura do projeto

```text
stroop-test-web/
├── stroop_go_nogo_ptbr.psyexp
├── condicoes/                 # fontes das tentativas
├── assets/                    # recursos proprios
├── stroop/                    # domain, ingestion, application, persistence
├── scripts/                   # comandos e migrations existentes
├── dashboard/                 # Streamlit
├── api/                       # HTTP
├── web/                       # interface WEB
├── tests/                     # testes e fixtures sinteticas
├── docs/
│   ├── README.md              # indice
│   ├── arquitetura/
│   ├── experimento/
│   ├── dados/
│   ├── seguranca/
│   ├── operacao/
│   ├── desenvolvimento/
│   ├── legado/
│   ├── Projeto Stroop Test.md # backlog canônico
│   ├── ROADMAP_WEB.md         # ponte de navegação
│   ├── PROGRESS.md
│   └── ESTRUTURA_DO_PROJETO.md
├── nginx/
├── compose*.yaml
├── Dockerfile.*
└── setup.* / abrir_dashboard.*
```

Nota: a pasta existente `condicoes/` e preservada como diretoria de CSVs de condicoes do experimento. Ela cumpre o papel da pasta `conditions/` sem duplicar conteudo.
