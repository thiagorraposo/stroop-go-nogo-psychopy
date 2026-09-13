# Schema e migrations PostgreSQL — Etapa 4

Data: 2026-09-01.

Esta etapa versiona o schema PostgreSQL das tres tabelas de dominio e oferece
uma migracao explicita do SQLite legado. O importador SQLite e o dashboard
continuam no fluxo local legado. A CLI de [importacao CSV PostgreSQL](IMPORTACAO_POSTGRESQL.md)
usa este schema ja aplicado; o sequenciamento das transicoes e definido no
[backlog canonico](Projeto%20Stroop%20Test.md).

## Schema versionado

A migration inicial fica em `scripts/migrations/0001_initial.sql`. Ela cria:

- `assessments`;
- `assessment_metrics`;
- `trial_results`;
- chaves primarias, identities, relacionamentos com `ON DELETE CASCADE`;
- restricoes dos dominios ja aceitos pelo importador vigente;
- os sete indices documentados na baseline.

Textos, datas e timestamps permanecem como texto para preservar exatamente a
semantica e os valores do SQLite vigente. Valores numericos usam equivalentes
nativos PostgreSQL. Nenhuma formula ou metrica foi alterada.

O executor cria `schema_migrations`, usa lock transacional, recusa migrations
aplicadas que nao existam localmente e aplica o lote pendente em uma unica
transacao. Uma falha reverte schema e registro de versao.

## Aplicar migrations

Com o PostgreSQL local saudavel e uma URL configurada:

```bash
export DATABASE_URL='postgresql://USUARIO:SENHA@127.0.0.1:55432/BANCO'
python scripts/migrations.py
```

O comando informa somente a quantidade de migrations aplicadas. Uma nova
execucao sem arquivos pendentes retorna zero.

## Migrar SQLite legado

A migracao nunca e automatica. Informe explicitamente um SQLite de origem e um
PostgreSQL vazio com as migrations aplicadas:

```bash
python scripts/migrar_sqlite_postgres.py CAMINHO.sqlite3
```

O utilitario:

- abre o SQLite em modo somente leitura;
- valida integridade, relacionamentos, tabelas e colunas;
- recusa destino que ja contenha dados nas tabelas de dominio;
- copia avaliacoes antes de metricas e tentativas em uma unica transacao;
- preserva chaves e relacionamentos;
- ajusta as sequences das duas identities;
- executa rollback integral diante de erro;
- retorna somente contagens agregadas por tabela.

Antes de migrar qualquer banco operacional, deve existir autorizacao explicita
e procedimento de backup. Na Etapa 4, a validacao usou somente um SQLite
temporario inteiramente sintetico e um banco PostgreSQL descartavel.

## Evolucao

Consulte exclusivamente o [backlog canonico](Projeto%20Stroop%20Test.md) e o
[protocolo Codex CLI](WORKFLOW_CODEX_CLI.md) para proximas entregas e validacao.
