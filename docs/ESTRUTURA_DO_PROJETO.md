# Estrutura do projeto

Mapa vigente apos a preparacao da evolucao web. Decisao:
[ADR-001](arquitetura/ADR-001-evolucao-web.md). Estado e tarefas web:
[roadmap](ROADMAP_WEB.md). O [backlog legado](Projeto%20Stroop%20Test.md)
continua governando a operacao PsychoPy/Streamlit existente.

## Arvore funcional

```text
stroop-cognifit/
├── stroop_go_nogo_ptbr.psyexp    # entrada PsychoPy preservada
├── condicoes/                  # CSVs-fonte do experimento
├── assets/                     # material proprio
├── stroop/                     # nucleo Python reutilizavel
│   ├── domain/
│   │   ├── assessment.py       # NormalizedAssessment
│   │   ├── errors.py           # excecoes de validacao
│   │   └── stroop.py           # contrato, validacao e metricas
│   └── ingestion/
│       ├── stroop_csv.py       # leitura e conversao de tentativas
│       └── instruments.py      # registro e adaptadores de instrumentos
├── scripts/                    # CLIs e infraestrutura local existentes
│   ├── importar_csv_sqlite.py  # persistencia e nomes anteriores reexportados
│   ├── importar_csv_postgres.py
│   ├── instrumentos.py        # compatibilidade com o registro extraido
│   ├── analisar_stroop.py      # analisador existente, preservado
│   ├── db_schema.sql          # schema SQLite, caminho preservado
│   ├── migrations.py
│   ├── migrations/            # migrations PostgreSQL existentes
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
├── api/README.md               # fronteira HTTP planejada; sem implementacao
├── web/README.md               # interface planejada; sem implementacao
├── tests/                      # unittest e fixtures sinteticas
├── docs/
│   ├── arquitetura/           # decisoes arquiteturais
│   ├── ROADMAP_WEB.md         # unico estado da evolucao web
│   ├── PROGRESS.md            # memoria concisa de trabalho e retomada
│   └── contratos, guias e historico existentes
├── nginx/                      # proxy existente
├── compose*.yaml               # dev, producao e restauracao existentes
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

`scripts` e as interfaces consomem `stroop.ingestion` e `stroop.domain`.
Ingestao conhece o dominio; dominio nao conhece interfaces, arquivos, HTTP ou
banco. O nucleo extraido usa somente biblioteca padrao. Os importadores ainda
compoem transacoes e SQL existentes; separar essa persistencia da CLI esta no
roadmap, antes da API de escrita.

O dashboard permanece modular e em seu caminho publico. Seu registro visual
de instrumentos tem finalidade distinta do registro de ingestao. Nenhum codigo
da futura API ou interface foi criado nesta preparacao.

## Mapa de extracao e compatibilidade

| Origem anterior | Fonte canonica atual | Compatibilidade |
|---|---|---|
| Constantes, validacao e metricas em `scripts/importar_csv_sqlite.py` | `stroop/domain/stroop.py` | Nomes reexportados pela CLI |
| Excecoes dos importadores e instrumentos | `stroop/domain/errors.py` | Mesmas classes reexportadas |
| `NormalizedAssessment` em `scripts/instrumentos.py` | `stroop/domain/assessment.py` | Reexportado pelo modulo anterior |
| Leitura CSV e conversao de tentativas no importador SQLite | `stroop/ingestion/stroop_csv.py` | Funcoes reexportadas pela CLI |
| Registro e adaptadores em `scripts/instrumentos.py` | `stroop/ingestion/instruments.py` | Modulo anterior reexporta os nomes |

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
[guia de instalacao](INSTALACAO_MULTIPLATAFORMA.md). PsychoPy permanece fora do
Docker. SQL, Compose e proxy conservam caminhos para evitar migracao de
ambiente junto de uma extracao de codigo.

## Dados e artefatos gerados

`data/`, `database/`, backups, exports, logs, `.venv`, caches, secrets e
`*_lastrun.py` nao sao fontes de codigo. Permanecem ignorados pelo Git e nao
devem ser movidos, inspecionados como fixtures ou incorporados aos novos
diretorios. Os CSVs de `condicoes/` e `tests/fixtures/` sao fontes permitidas.
O `.gitignore` continua sendo a regra efetiva de versionamento.
