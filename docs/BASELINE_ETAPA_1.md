# Baseline reproduzivel — Etapa 1

Data da verificacao: 2026-09-01.

Este documento registra o estado encontrado sem alterar o comportamento do
experimento, as regras do paradigma ou as formulas das metricas. Nenhum
conteudo de CSV real ou registro identificavel do SQLite foi consultado ou
reproduzido.

## Fluxo atual

```text
stroop_go_nogo_ptbr.psyexp
  -> data/stroop_go_nogo_ptbr_<timestamp>_trials.csv
  -> scripts/importar_csv_sqlite.py
  -> database/stroop_results.sqlite3
  -> dashboard/app.py (Streamlit)
```

### PsychoPy

- Ponto de entrada: `stroop_go_nogo_ptbr.psyexp`, aberto no PsychoPy Builder.
- Condicoes: `condicoes/contagem_regressiva.csv`,
  `condicoes/pratica_stroop_go_nogo_ptbr.csv` e
  `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv`.
- O formulario visual cria metadados da sessao e `assessment_id`; o Flow executa
  pratica, bloco principal e resultados.
- A rotina principal acumula em memoria somente tentativas `main`. Ao encerrar,
  `write_official_csv()` grava um CSV de 21 colunas em `data/`, uma linha por
  tentativa principal. A pratica nao entra no CSV oficial.
- `stroop_go_nogo_ptbr_lastrun.py` e artefato gerado, ignorado e nao e fonte de
  manutencao.

### CSV e importacao

- Contrato: `docs/CSV_UNIFICADO.md`; validacao e importacao:
  `scripts/importar_csv_sqlite.py`.
- O importador exige ordem exata das 21 colunas, campos obrigatorios, tipos e
  dominios coerentes, consistencia dos metadados e das quatro regras de resposta.
- A importacao calcula apenas as metricas ja documentadas, cria o schema por
  `scripts/db_schema.sql` e grava avaliacao, metricas e tentativas numa transacao.
- `assessment_id` duplicado e recusado; `--force` substitui seus registros
  dependentes dentro da transacao. O CSV fonte nao e modificado.
- Ponto de entrada manual:
  `python scripts/importar_csv_sqlite.py data/ARQUIVO_trials.csv`.

### SQLite

- Caminho padrao: `database/stroop_results.sqlite3`.
- Responsabilidade: persistir metadados de avaliacao, metricas calculadas e
  tentativas, mantendo rastreabilidade por `assessment_id` e `source_file`.
- O diretorio inteiro e local e ignorado pelo Git.

### Streamlit

- Aplicacao: `dashboard/app.py`; launcher: `scripts/run_dashboard.py`, chamado
  por `abrir_dashboard.sh` ou `abrir_dashboard.bat`.
- Sem `--csv`, o launcher escolhe o `data/*_trials.csv` mais recentemente
  modificado, chama o importador e inicia o Streamlit pela `.venv`.
- O dashboard abre o SQLite com `mode=ro`, valida tabelas/colunas, monta uma
  linha agregada por avaliacao e oferece filtros, cards, graficos, tabela,
  detalhe por avaliacao e download manual da visao agregada filtrada.
- Dependencias ficam em `requirements.txt` e `dashboard/requirements.txt`;
  a execucao local requer Python, PsychoPy para o experimento e Streamlit para
  o dashboard. Nenhum servico Docker faz parte desta baseline.

### Testes e documentacao

- Execucao canonica: `python -m unittest discover -s tests -v`.
- Os sete modulos em `tests/test_*.py` cobrem contrato CSV, dashboard, condicoes
  e tempos, launcher multiplataforma, importacao SQLite, interface pre-pratica e
  resultados. Usam memoria ou diretorios/bancos temporarios; nao leem `data/`.
- A documentacao existente em `docs/` cobre contrato CSV, modelo de dados,
  importacao, dashboard, instalacao, uso, UX, decisoes, validacao e governanca.

## Esquema SQLite observado

O schema observado coincide com `scripts/db_schema.sql`. O SQLite tambem mantem
a tabela interna `sqlite_sequence` para as chaves `AUTOINCREMENT`.

### `assessments`

| Coluna | Tipo | Restricao |
|---|---|---|
| `assessment_id` | TEXT | chave primaria |
| `test_code` | TEXT | NOT NULL |
| `test_version` | TEXT | NOT NULL |
| `project` | TEXT | NOT NULL |
| `participant_id` | TEXT | NOT NULL |
| `participant_name` | TEXT | NOT NULL; dado pessoal local |
| `initials` | TEXT | opcional; potencialmente identificavel |
| `visit` | TEXT | NOT NULL |
| `evaluator` | TEXT | NOT NULL |
| `assessment_date` | TEXT | NOT NULL |
| `started_at` | TEXT | NOT NULL |
| `source_file` | TEXT | NOT NULL |
| `imported_at` | TEXT | NOT NULL |
| `import_status` | TEXT | NOT NULL |

Indices: chave primaria automatica e indices nao unicos em `participant_id`,
`project`, `assessment_date`, `visit` e `evaluator`.

### `assessment_metrics`

| Coluna | Tipo | Restricao |
|---|---|---|
| `metric_id` | INTEGER | chave primaria AUTOINCREMENT |
| `assessment_id` | TEXT | NOT NULL; FK para `assessments`, ON DELETE CASCADE |
| `metric_code` | TEXT | NOT NULL |
| `metric_label` | TEXT | NOT NULL |
| `metric_value` | REAL | NOT NULL |
| `unit` | TEXT | opcional |
| `calculated_at` | TEXT | NOT NULL |

Indice nao unico composto: (`assessment_id`, `metric_code`).

### `trial_results`

| Coluna | Tipo | Restricao |
|---|---|---|
| `trial_result_id` | INTEGER | chave primaria AUTOINCREMENT |
| `assessment_id` | TEXT | NOT NULL; FK para `assessments`, ON DELETE CASCADE |
| `block` | TEXT | NOT NULL |
| `trial_number` | INTEGER | NOT NULL |
| `word` | TEXT | NOT NULL |
| `ink_color` | TEXT | NOT NULL |
| `condition` | TEXT | NOT NULL |
| `correct_response` | TEXT | opcional |
| `key_pressed` | TEXT | opcional |
| `reaction_time` | REAL | opcional |
| `correct` | INTEGER | NOT NULL |
| `error_type` | TEXT | NOT NULL |

Indice nao unico composto: (`assessment_id`, `block`).

Relacionamento: uma linha em `assessments` possui zero ou mais linhas em
`assessment_metrics` e `trial_results`; ambas apontam para a avaliacao por
`assessment_id` e sao removidas em cascata. O schema nao possui relacionamento
direto entre uma metrica e uma tentativa.

## Integridade, contagens e backup

Verificacao do banco padrao em 2026-09-01:

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: nenhuma linha retornada;
- `assessments`: 4 linhas;
- `assessment_metrics`: 48 linhas;
- `trial_results`: 64 linhas;
- `sqlite_sequence`: 2 linhas internas de controle de `AUTOINCREMENT`.

Procedimento seguro validado, com o experimento e importador fechados:

```bash
mkdir -p database/backups
sqlite3 database/stroop_results.sqlite3 \
  ".timeout 5000" \
  ".backup 'database/backups/stroop_results_baseline_2026-09-01.sqlite3'"
sqlite3 -readonly database/backups/stroop_results_baseline_2026-09-01.sqlite3 \
  "PRAGMA integrity_check;"
```

Para validar sem expor dados, comparar somente `COUNT(*)` das tabelas entre
origem e copia. A copia desta baseline foi aberta, retornou `ok` e reproduziu
4/48/64 nas tres tabelas de dominio (e 2 linhas em `sqlite_sequence`). Tanto
`database/` quanto `backups/` sao ignorados; o backup nao deve ser movido para
uma area versionada.

## Baseline dos testes

Em 2026-09-01, `.venv/bin/python -m unittest discover -s tests -v` encontrou
73 testes: 73 aprovados, 0 falhas e 0 erros. A referencia de 61 esta defasada em
12 testes. O historico registra regressoes posteriores relacionadas ao formulario
visual, responsividade, cursor, geometria dos estimulos e nome seguro do CSV; nao
foi necessario alterar comportamento ou testes.

## Fixtures sinteticas

Antes desta etapa, os testes construíam CSVs sinteticos somente em memoria ou em
diretorios temporarios. Foram adicionadas fixtures versionaveis em
`tests/fixtures/csv/`: uma valida e tres invalidas, cobrindo coluna ausente,
tipo invalido e valor fora do dominio. Nenhuma fixture contem pessoa real.

## Limitacoes e riscos conhecidos

- Existem CSVs locais ignorados em `data/`, inclusive nomes baseados em IDs, e um
  banco local preenchido. Foram tratados como potencialmente identificaveis; seu
  conteudo nao foi aberto. Confirmar origem, base legal, retencao e acesso e uma
  responsabilidade operacional fora desta baseline.
- O schema usa `NOT NULL` e FKs, mas nao possui `CHECK` para dominios nem
  `UNIQUE` em (`assessment_id`, `metric_code`) ou em
  (`assessment_id`, `block`, `trial_number`). A validacao depende do importador.
- O importador aceita `practice` no validador, embora o contrato oficial atual
  determine somente `main`. O PsychoPy atual exporta somente `main`.
- Datas e timestamps sao armazenados como TEXT e validados apenas parcialmente.
- `source_file` e rastreavel, mas o schema nao armazena hash do CSV fonte.
- O dashboard carrega as tres tabelas completas em memoria e inclui nome local
  nos filtros/detalhes; isso exige uso estritamente local e cuidado com telas e
  exports.
- A validacao desta etapa e automatizada e estrutural. Nenhuma coleta Pilot foi
  iniciada, para evitar produzir ou manipular novos dados de participante.

## Limite da etapa

Nenhuma decisao metodologica ou de UX foi alterada. PostgreSQL, Docker, novas
metricas, migracoes, mudancas do experimento e qualquer trabalho da Etapa 2
ficaram explicitamente fora do escopo.
