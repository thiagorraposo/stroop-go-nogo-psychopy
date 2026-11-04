# Estrutura do projeto

Mapa vigente da evolucao web. Decisao:
[ADR-001](arquitetura/ADR-001-evolucao-web.md). Estado e tarefas web:
[roadmap](ROADMAP_WEB.md). O [backlog legado](legado/Projeto%20Stroop%20Test.md)
continua governando a operacao PsychoPy/Streamlit existente.

## Arvore funcional

```text
stroop-cognifit/
├── stroop_go_nogo_ptbr.psyexp    # entrada PsychoPy preservada
├── condicoes/                  # CSVs-fonte e snapshot WEB compartilhado
├── assets/                     # material proprio
├── stroop/                     # nucleo Python reutilizavel
│   ├── domain/
│   │   ├── assessment.py       # NormalizedAssessment
│   │   ├── auth.py             # regras e erros de autenticacao
│   │   ├── errors.py           # excecoes de validacao
│   │   ├── web_results.py      # validacao temporal, normalizacao e hash canonico WEB
│   │   └── stroop.py           # contrato, validacao e metricas
│   ├── ingestion/
│   │   ├── stroop_csv.py       # leitura e conversao de tentativas
│   │   └── instruments.py      # registro e adaptadores de instrumentos
│   ├── application/
│   │   ├── auth.py             # autorizacao e bootstrap profissional
│   │   ├── web_sessions.py     # casos de uso de projetos, convites e sessoes
│   │   ├── web_results.py      # conclusao WEB e validacao transacional
│   │   ├── import_sqlite.py    # casos de uso locais
│   │   ├── import_postgres.py  # importacao e validacao sem CLI
│   │   ├── clock.py            # timestamp UTC compartilhado
│   │   └── errors.py           # erros publicos de importacao PostgreSQL
│   └── persistence/
│       ├── auth.py             # persistencia de usuarios e auditoria
│       ├── web_sessions.py     # SQL transacional de projetos e sessoes WEB
│       ├── sqlite.py           # conexao, SQL e transacao SQLite
│       ├── postgres.py         # conexao, lock, SQL e transacao PostgreSQL
│       └── web_auth.py         # transacoes OIDC e sessoes web
├── scripts/                    # CLIs e infraestrutura local existentes
│   ├── importar_csv_sqlite.py  # CLI e nomes anteriores reexportados
│   ├── importar_csv_postgres.py
│   ├── instrumentos.py        # compatibilidade com o registro extraido
│   ├── analisar_stroop.py      # analisador existente, preservado
│   ├── db_schema.sql           # schema SQLite, caminho preservado
│   ├── migrations.py
│   ├── migrations/             # migrations PostgreSQL, caminho preservado
│   │   ├── 0005_web_participant_sessions.sql
│   │   └── 0006_web_completed_results.sql
│   └── demais utilitarios
├── dashboard/                  # aplicacao Streamlit existente
│   ├── app.py                 # composicao da interface
│   ├── components.py
│   ├── transformations.py
│   ├── data_access.py
│   ├── auth.py
│   ├── instrumentos.py        # apresentacao, separado da ingestao
│   ├── requirements.txt
│   └── requirements.lock
├── api/                        # fronteira HTTP, autenticacao e sessoes WEB
│   ├── main.py                 # factory e composicao FastAPI
│   ├── auth.py                 # rotas OIDC, sessao, logout e CSRF
│   ├── sessions.py             # projetos, convites e ciclo de sessao participante
│   ├── assessments.py          # consulta profissional e exportacao autorizada
│   ├── results.py              # conclusao e recibo idempotente
│   ├── config.py               # configuracao validada por ambiente
│   ├── transport.py            # limites ASGI e erros de transporte
│   ├── health.py               # live/readiness
│   ├── google_oidc.py          # descoberta e validacao criptografica do provedor
│   ├── models.py / errors.py   # contratos de entrada e erros publicos
│   └── requirements*.txt       # dependencias e lock da API
├── web/                        # interface React/TypeScript
│   ├── src/App.tsx             # navegacao e acesso da equipe
│   ├── src/components/         # participante, motores/resumo e painel profissional
│   ├── src/api/                # transporte, sessao participante e consultas profissionais
│   ├── src/experiment/         # host, protocolo e motores jsPsych
│   ├── src/participant/        # coordenacao da sessao e payload em RAM
│   ├── src/dashboard/          # agregacoes descritivas sobre consultas autorizadas
│   ├── e2e/                   # navegador isolado e HTTPS real em integrated/
│   └── package*.json          # dependencias exatas e lockfile
├── tests/                      # unittest e fixtures sinteticas
├── docs/
│   ├── README.md              # indice de navegacao por assunto
│   ├── AGENTS.md              # instrucoes para documentacao
│   ├── arquitetura/           # decisoes arquiteturais
│   ├── experimento/           # protocolo, condicoes, CSV e UX
│   ├── dados/                 # modelo, importacao, migracoes e dashboard
│   ├── seguranca/             # acesso, ameacas, privacidade e incidentes
│   ├── operacao/              # instalacao, uso, Docker e hardening
│   ├── desenvolvimento/       # workflow, contrato HTTP, commits e prompts
│   ├── legado/                # backlog legado, baselines e propostas antigas
│   ├── ROADMAP_WEB.md         # unico estado da evolucao web
│   ├── PROGRESS.md            # memoria concisa de trabalho e retomada
│   ├── REGISTRO_DE_ALTERACOES.md
│   └── ESTRUTURA_DO_PROJETO.md # este mapa
├── nginx/                      # proxy existente
├── compose*.yaml               # legado e pilha WEB independente compose.web.yaml
├── deploy/                     # modelo WEB sem secrets; arquivos reais externos
├── Dockerfile.api / Dockerfile.web # imagens WEB e ignores dedicados
├── Dockerfile.dashboard
├── Dockerfile.proxy
├── .streamlit/                 # configuracao; secrets reais ignorados
├── setup.bat / setup.sh
├── abrir_dashboard.bat / abrir_dashboard.sh
├── requirements.txt
├── data/                       # saidas locais ignoradas
└── database/                   # bancos locais ignorados
```

## Direcao das dependencias

A [documentacao](README.md) e agrupada por assunto; roadmap, retomada, registro
e mapa continuam na raiz de `docs/`. A reorganizacao documental conserva os
caminhos operacionais de codigo, launchers, SQL, condicoes e infraestrutura.

`scripts` delega importacao a `stroop.application`, que coordena ingestao e
persistencia. `stroop.persistence` concentra SQL e drivers; nao importa CLIs ou
dashboard. O recurso SQLite continua em `scripts/db_schema.sql` sem importacao
de codigo de scripts. PostgreSQL exige migrations explicitas em seus caminhos
existentes. Nao ha repositorio generico nem unificacao de validadores distintos.

Ingestao conhece o dominio; dominio nao conhece interfaces, arquivos, HTTP ou
banco. Dominio e ingestao usam somente biblioteca padrao. SQLite pode ser usado
sem instalar drivers PostgreSQL; importar o caso PostgreSQL requer `psycopg`.

O dashboard permanece modular e em seu caminho publico. Seu registro visual
de instrumentos tem finalidade distinta do registro de ingestao. A base HTTP
esta organizada por fronteira de transporte (`api/`), regras reaproveitaveis
(`stroop/domain` e `stroop/application`) e persistencia (`stroop/persistence`).
`dashboard/auth.py` preserva a fachada publica do dashboard; SQL e drivers de
autenticacao ficam na persistencia. A base React em `web/` possui navegacao,
cliente HTTP, preparo, pratica e principal jsPsych com host experimental isolado;
`condicoes/web_protocol.json` e o snapshot comum a API/frontend. O motor segue
o protocolo/roadmap.
O mapa localiza arquivos, sem substituir o aceite registrado no roadmap.

## Mapa de extracao e compatibilidade

| Origem anterior | Fonte canonica atual | Compatibilidade |
|---|---|---|
| Constantes, validacao e metricas em `scripts/importar_csv_sqlite.py` | `stroop/domain/stroop.py` | Nomes reexportados pela CLI |
| Excecoes dos importadores e instrumentos | `stroop/domain/errors.py` | Mesmas classes reexportadas |
| `NormalizedAssessment` em `scripts/instrumentos.py` | `stroop/domain/assessment.py` | Reexportado pelo modulo anterior |
| Leitura CSV e conversao de tentativas no importador SQLite | `stroop/ingestion/stroop_csv.py` | Funcoes reexportadas pela CLI |
| Registro e adaptadores em `scripts/instrumentos.py` | `stroop/ingestion/instruments.py` | Modulo anterior reexporta os nomes |
| Casos de importacao nas CLIs SQLite/PostgreSQL | `stroop/application/import_sqlite.py` e `import_postgres.py` | Funcoes e excecoes publicas reexportadas pelas CLIs |
| SQL e transacoes nos importadores | `stroop/persistence/sqlite.py` e `postgres.py` | Schema/migrations, locks, transacoes e retornos preservados |

Nao houve mudanca de assinatura, formula, unidade, schema ou classificacao.
O analisador e os componentes embarcados do PsychoPy permanecem preservados,
sem consolidacao de suas diferencas historicas nesta etapa.

## Entradas operacionais preservadas

```bash
python scripts/run_dashboard.py
python scripts/importar_csv_sqlite.py CAMINHO.csv
python scripts/importar_csv_postgres.py CAMINHO.csv --validate-only
python scripts/doctor.py
.venv/bin/python -m unittest discover -s tests -v
```

Os atalhos da raiz e o uso por ZIP continuam descritos no
[guia de instalacao](operacao/INSTALACAO_MULTIPLATAFORMA.md). PsychoPy permanece fora do
Docker. SQL, Compose e proxy conservam caminhos para evitar migracao de
ambiente junto de uma extracao de codigo.

## Dados e artefatos gerados

`data/`, `database/`, backups, exports, logs, `.venv`, caches, secrets e
`*_lastrun.py` nao sao fontes de codigo. Permanecem ignorados pelo Git e nao
devem ser movidos, inspecionados como fixtures ou incorporados aos novos
diretorios. Os CSVs de `condicoes/` e `tests/fixtures/` sao fontes permitidas.
O `.gitignore` continua sendo a regra efetiva de versionamento.
