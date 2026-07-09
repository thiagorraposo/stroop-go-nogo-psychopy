# Importacao para SQLite

Data: 2026-07-09.

## Objetivo

A Fase 7 implementa a importacao local do CSV unificado para SQLite:

```text
CSV unificado -> validacao -> SQLite local
```

O banco e local, descritivo e nao clinico. Ele nao gera diagnostico, norma, percentil, classificacao individual ou recomendacao clinica.

## Uso

Execute a partir da raiz do projeto:

```bash
python3 scripts/importar_csv_sqlite.py data/PARTICIPANT_ID.csv
```

Banco padrao:

```text
database/stroop_results.sqlite3
```

Para escolher outro banco:

```bash
python3 scripts/importar_csv_sqlite.py data/PARTICIPANT_ID.csv --db database/stroop_results.sqlite3
```

Para reimportar um `assessment_id` ja existente:

```bash
python3 scripts/importar_csv_sqlite.py data/PARTICIPANT_ID.csv --force
```

Sem `--force`, a importacao de um `assessment_id` ja existente e bloqueada.

## Schema

O schema fica em `scripts/db_schema.sql` e cria tres tabelas:

- `assessments`: uma linha por execucao importada.
- `trial_results`: uma linha por tentativa do CSV.
- `assessment_metrics`: uma linha por metrica calculada.

### assessments

- `assessment_id TEXT PRIMARY KEY`
- `test_code TEXT NOT NULL`
- `test_version TEXT NOT NULL`
- `project TEXT NOT NULL`
- `participant_id TEXT NOT NULL`
- `participant_name TEXT NOT NULL`
- `initials TEXT`
- `visit TEXT NOT NULL`
- `evaluator TEXT NOT NULL`
- `assessment_date TEXT NOT NULL`
- `started_at TEXT NOT NULL`
- `source_file TEXT NOT NULL`
- `imported_at TEXT NOT NULL`
- `import_status TEXT NOT NULL`

### trial_results

- `trial_result_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `assessment_id TEXT NOT NULL`
- `block TEXT NOT NULL`
- `trial_number INTEGER NOT NULL`
- `word TEXT NOT NULL`
- `ink_color TEXT NOT NULL`
- `condition TEXT NOT NULL`
- `correct_response TEXT`
- `key_pressed TEXT`
- `reaction_time REAL`
- `correct INTEGER NOT NULL`
- `error_type TEXT NOT NULL`

### assessment_metrics

- `metric_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `assessment_id TEXT NOT NULL`
- `metric_code TEXT NOT NULL`
- `metric_label TEXT NOT NULL`
- `metric_value REAL NOT NULL`
- `unit TEXT`
- `calculated_at TEXT NOT NULL`

## Indices

- `assessments(participant_id)`
- `assessments(project)`
- `assessments(assessment_date)`
- `assessments(visit)`
- `assessments(evaluator)`
- `assessment_metrics(assessment_id, metric_code)`
- `trial_results(assessment_id, block)`

## Validacoes

Antes de importar, o script valida:

- cabecalho canonico de 21 colunas;
- uma linha por tentativa;
- `block` em `practice` ou `main`;
- `condition` em `congruent` ou `incongruent`;
- `error_type` em `hit`, `omission`, `correct_rejection` ou `commission`;
- `correct` em `0` ou `1`;
- `correct_response = space` apenas em `congruent`;
- `correct_response` vazio em `incongruent`;
- `reaction_time` vazio quando nao houver resposta;
- `reaction_time` numerico positivo quando houver `key_pressed`;
- bloqueio de `reaction_time = 0`;
- campos obrigatorios de metadados nao vazios;
- mesmo `assessment_id` e metadados consistentes em todas as linhas.

O CSV original nunca e modificado.

## Metricas

As metricas sao calculadas apenas com linhas `block = main`:

- `accuracy = ((hits + correct_rejections) / total_valid_trials) * 100`
- `accuracy_go_trials = (hits / total_go_trials) * 100`
- `accuracy_no_go_trials = (correct_rejections / total_no_go_trials) * 100`
- `omission_errors`
- `omission_errors_percentage = (omission_errors / total_go_trials) * 100`
- `commission_errors`
- `response_time = mediana dos RTs dos hits validos`
- `total_trials`
- `total_go_trials`
- `total_no_go_trials`
- `hits`
- `correct_rejections`

Quando nao houver hits validos, `response_time` e gravado como `0.0` por restricao do schema atual (`metric_value REAL NOT NULL`).

## Transacao e duplicidade

A importacao usa transacao SQLite. Se qualquer insercao falhar, o rollback remove toda a importacao parcial.

Sem `--force`, o script bloqueia `assessment_id` ja existente. Com `--force`, remove a execucao anterior daquele `assessment_id` e reimporta o CSV validado.

## Privacidade

- SQLite fica em `database/`, pasta local ignorada pelo Git.
- Arquivos `.sqlite`, `.sqlite3` e `.db` nao devem ser versionados.
- `participant_name` e dado pessoal local e nao deve ser usado em nomes de arquivo, prints publicos, commits ou logs compartilhados.
- O banco e uma camada local de organizacao e auditoria, sem interpretacao clinica.

## Validacao pendente

A implementacao tem testes automatizados com CSVs temporarios ficticios. Ainda falta validacao manual em Pilot com um CSV real local, sem versionar dados.
