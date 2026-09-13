# Testes

Planejamento, estado e aceite: [backlog canonico](../docs/Projeto%20Stroop%20Test.md).
Operacao do desenvolvimento: [protocolo Codex CLI](../docs/WORKFLOW_CODEX_CLI.md).


Esta pasta contem testes de consistencia do experimento e da exportacao unificada.

Validacoes implementadas ou esperadas:

- colunas exigidas em CSVs de condicoes;
- compatibilidade entre condicoes e `.psyexp`;
- coerencia entre `word`, `ink_color`, `condition` e `correct_response`;
- formato do CSV unificado;
- classificacao de `hit`, `omission`, `correct_rejection` e `commission`.
- rejeicao de CSVs automaticos de loops como fonte oficial.
- balanceamento de 10 cores e tempos da Fase 3.
- Flow e navegacao das telas visuais pre-pratica.
- configuracao estatica da infraestrutura Docker local, isolamento de dados,
  healthcheck, volume e ponto de entrada do dashboard.
- schema e migrations PostgreSQL, rollback e migracao SQLite sintetica com
  paridade de relacionamentos, valores e identities.

Nao usar dados pessoais ou arquivos reais de participantes como fixtures versionados.

A importacao CSV PostgreSQL e coberta por `test_importar_csv_postgres.py`.
Veja [comandos e isolamento](../docs/IMPORTACAO_POSTGRESQL.md) para executar a
integracao em PostgreSQL descartavel com `TEST_DATABASE_URL`; skips nao aprovam
a suite integral.

`test_upload_local.py` cobre isolamento, retencao, validacao, launcher
autenticado e integracao sintetica de uploads concorrentes. Consulte
[UPLOAD_LOCAL.md](../docs/UPLOAD_LOCAL.md) para comandos e limites.

`test_authentication.py` cobre claims Google, expiracao, cadastro previo,
bloqueio, perfis, autorizacao negativa, limitacao de recusas, auditoria minima,
bootstrap e recuperacao, sempre com identidades sinteticas. Consulte
[AUTENTICACAO_E_PERMISSOES.md](../docs/AUTENTICACAO_E_PERMISSOES.md).

`test_hardening_producao.py` cobre isolamento de portas/redes, TLS fail-closed,
versoes fixadas, menor privilegio, limites Ampere A1, headers, rate limit,
logging minimo, criptografia/rotacao de backups, restauracao isolada, auditoria
de importacao e expurgo seletivo. Testes de banco exigem o mesmo PostgreSQL
descartavel da suite integral.
