# Importacao CSV para PostgreSQL

O comando `scripts/importar_csv_postgres.py` importa uma avaliacao por CSV,
selecionando o adaptador registrado pelo cabeçalho e reutilizando o contrato
normalizado descrito em [MULTIPLOS_INSTRUMENTOS.md](MULTIPLOS_INSTRUMENTOS.md).
O adaptador Stroop mantém o leitor, as validações, conversões e fórmulas do
importador SQLite.
O CSV permanece imutavel. O [backlog canonico](Projeto%20Stroop%20Test.md) define
estado e aceite; o [protocolo Codex CLI](WORKFLOW_CODEX_CLI.md) governa a execucao.

## Pre-requisitos e comandos

Usar a `.venv` existente com `psycopg` e PostgreSQL com as
[migrations versionadas](MIGRACOES_POSTGRESQL.md) aplicadas. O importador nao cria
schema nem aplica migrations automaticamente. Configurar `DATABASE_URL` no
ambiente da sessao, sem registrar a credencial em arquivos versionados ou logs.
Os exemplos abaixo usam exclusivamente a fixture sintetica versionada.

Validar estrutura, tipos, metadados e regras do CSV, sem conexao ou persistencia:

```bash
.venv/bin/python scripts/importar_csv_postgres.py tests/fixtures/csv/valido_minimo.csv --validate-only
```

Importar no PostgreSQL sintetico configurado por `DATABASE_URL`:

```bash
.venv/bin/python scripts/importar_csv_postgres.py tests/fixtures/csv/valido_minimo.csv
```

Substituir explicitamente uma avaliacao existente:

```bash
.venv/bin/python scripts/importar_csv_postgres.py tests/fixtures/csv/valido_minimo.csv --force
```

No Windows, usar `.venv\Scripts\python.exe` em lugar de `.venv/bin/python`.
`--validate-only` prevalece sobre `--force`: nunca substitui registros nem
consulta existencia no destino. Esse modo nao comprova conectividade, permissoes,
schema ou aceitacao das restricoes PostgreSQL.

## Transacao, duplicidade e rastreabilidade

Todas as gravacoes usam uma unica transacao: avaliacao, tentativas e metricas.
Falha antes do commit reverte as alteracoes, inclusive a exclusao efetuada por
`--force`. Lacunas em sequences podem ocorrer apos rollback e nao sao dados
parciais de uma avaliacao.

A chave de duplicidade e `assessment_id`, preservando o contrato legado. Repetir
uma importacao sem `--force` e recusado, sem mudar os dados, mesmo se o caminho
ou conteudo do arquivo tiver mudado. Nao ha deduplicacao por pessoa ou hash de
conteudo: arquivos com IDs de avaliacao distintos continuam sendo avaliacoes
distintas. Essa e a idempotencia de efeito desta CLI.

O importador bloqueia a tabela `assessments` em `SHARE ROW EXCLUSIVE MODE` antes
de consultar a chave, serializando importacoes concorrentes e coordenando com a
migracao legada. A PK tambem protege a unicidade. Esse bloqueio favorece
consistencia em volumes locais pequenos; importacoes longas podem atrasar outras
escritas. Nao foi introduzida infraestrutura de filas ou upload.

A origem fica em `assessments.source_file`, com a mesma representacao do caminho
usada pelo SQLite. `imported_at`, `import_status = valid` e `calculated_at`
registram o resultado confirmado. Essas colunas ficam no banco protegido e nao
sao impressas. Rejeicoes retornam codigo e mensagem segura na CLI; nao criam
registros parciais ou uma nova tabela de auditoria.

## Saida e codigos

A saida bem-sucedida contem somente status (`validated`, `imported` ou
`reimported`) e contagens de tentativas e metricas. Erros nao imprimem linhas,
metadados, caminhos, IDs, URL de conexao ou mensagens internas do PostgreSQL.

| Codigo | Significado |
|---|---|
| 0 | Importacao, reimportacao ou validacao sem persistencia aprovada |
| 1 | CSV invalido/indisponivel, configuracao ausente ou falha PostgreSQL |
| 2 | Argumentos de CLI invalidos |
| 3 | Avaliacao duplicada, sem `--force` |

Se a conexao cair durante o commit, o cliente pode nao saber se ele foi
confirmado. Repetir sem `--force` preserva a protecao contra duplicidade; nao
usar substituicao automatica como tentativa de recuperacao.

## Compatibilidade e limites

O importador SQLite, launchers e dashboard permanecem inalterados. O dashboard
continua lendo SQLite somente leitura. Nao houve mudanca no CSV, schema,
paradigma ou formulas; `practice` segue aceito por compatibilidade historica e
as metricas usam somente `main`, inclusive RT sem hits igual a `0.0` no banco.

A decisao operacional anunciada no plano da sessao foi incluir `--validate-only`
para conferir entradas sem depender do banco. A validacao reutiliza integralmente
o legado; nao cria novas regras clinicas nem endurece silenciosamente dominios.
Limitacoes anteriores, como datas em texto e ausencia de hash da fonte,
permanecem. As restricoes do PostgreSQL tambem podem recusar valores aceitos pelo
validador Python; nesse caso a transacao inteira e revertida.

## Verificacao reproduzivel

Configurar `TEST_DATABASE_URL` exclusivamente para um banco novo e descartavel
cujo nome comece por `stroop_etapa4_test`. Os testes apagam e recriam seu schema.
Nunca apontar essa variavel para banco operacional.

```bash
.venv/bin/python -m unittest discover -s tests -p test_importar_csv_postgres.py -v
.venv/bin/python -m unittest discover -s tests -v
docker compose --env-file .env.example config --quiet
git diff --check
```

Os testes usam fixtures e SQLite temporarios sinteticos, verificando paridade,
CSV imutavel, duplicidade, concorrencia, reimportacao, rollback, indisponibilidade
e saidas sanitizadas. Sem `TEST_DATABASE_URL`, skips de integracao nao comprovam
aceite integral. Nenhum acesso a dados reais ou OCI e necessario.
