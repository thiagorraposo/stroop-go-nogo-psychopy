# Scripts

Planejamento, estado e aceite: [backlog canonico](../docs/Projeto%20Stroop%20Test.md).
Operacao do desenvolvimento: [protocolo Codex CLI](../docs/WORKFLOW_CODEX_CLI.md).


Esta pasta contem scripts auxiliares para analise descritiva e manutencao local.

Para executar a analise a partir da raiz do projeto:

```bash
python3 scripts/analisar_stroop.py data/PARTICIPANT_ID.csv
```

`analisar_stroop.py` consome apenas um CSV unificado local em `data/`, distinguindo `practice` e `main` pela coluna `block`. O script valida o contrato oficial, calcula metricas descritivas do bloco principal e nao modifica o CSV bruto.

Os resultados sao descritivos e exploratorios. Eles nao sao interpretacao clinica, diagnostico ou comparacao normativa.

`setup_env.py` cria a `.venv` multiplataforma e instala as dependencias do dashboard. `run_dashboard.py` seleciona ou recebe um CSV oficial, chama o importador SQLite sem modificar o CSV e inicia o Streamlit. Consulte `docs/INSTALACAO_MULTIPLATAFORMA.md`.

`doctor.py` faz somente verificacoes de leitura no ambiente. Na raiz do projeto,
use `py scripts\doctor.py` no Windows ou `python3 scripts/doctor.py` no Linux e
macOS. Ele nao instala pacotes, nao modifica CSVs, nao cria o SQLite e nao abre o
dashboard.

`migrations.py` aplica o schema PostgreSQL versionado por `DATABASE_URL`.
`migrar_sqlite_postgres.py` faz uma migracao legada explicita e transacional
de um SQLite validado para um PostgreSQL vazio. Nenhum dos dois e chamado pelos
launchers publicos nesta etapa. Consulte `docs/MIGRACOES_POSTGRESQL.md`.

`importar_csv_postgres.py` importa CSV via `DATABASE_URL`, com transacao,
recusa de duplicidade, `--force` e `--validate-only`. O comando e separado do
launcher SQLite. Consulte [importacao PostgreSQL](../docs/IMPORTACAO_POSTGRESQL.md).

`upload_local.py --local` preserva o comando publico, mas agora abre a area de
importacao do dashboard somente em `127.0.0.1`, protegida por Google OIDC,
cadastro previo e perfil. `gerenciar_usuarios.py` faz somente o bootstrap inicial
e a recuperacao administrativa de emergencia; cadastros comuns ocorrem na area
administrativa autenticada. Consulte
[autenticacao](../docs/AUTENTICACAO_E_PERMISSOES.md) e
[upload](../docs/UPLOAD_LOCAL.md).

`aplicar_retencao.py` conta auditorias vencidas por padrao e, somente com
`--apply`, remove eventos operacionais com mais de 30 dias e OIDC com mais de
180 dias. Nunca remove tabelas da pesquisa. `backup_postgres.py` gera chave,
transmite `pg_dump` diretamente para AES-256-GCM, mantem 30 geracoes e restaura
em PostgreSQL isolado e descartavel. Operacao e limites:
[hardening de producao](../docs/HARDENING_PRODUCAO.md).
