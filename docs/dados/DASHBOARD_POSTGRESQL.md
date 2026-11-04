# Dashboard PostgreSQL — Etapa 10

O dashboard operacional lê `assessments`, `assessment_metrics` e
`trial_results` por `DASHBOARD_DATABASE_URL`. A conexão força transações
somente leitura e busca as tabelas em lotes (`DASHBOARD_PAGE_SIZE`, padrão 1000,
máximo 10000). `DATABASE_URL` continua reservado à importação autenticada.

## Credencial de leitura

Crie a conta fora do Git, usando um administrador do banco e um segredo mantido
no cofre institucional. O nome abaixo é apenas um exemplo:

```sql
CREATE ROLE stroop_dashboard_ro LOGIN PASSWORD '<segredo-fora-do-Git>';
GRANT CONNECT ON DATABASE stroop_production TO stroop_dashboard_ro;
GRANT USAGE ON SCHEMA public TO stroop_dashboard_ro;
GRANT SELECT ON TABLE assessments, assessment_metrics, trial_results
  TO stroop_dashboard_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO stroop_dashboard_ro;
```

O proprietário das tabelas deve executar os `ALTER DEFAULT PRIVILEGES`; eles
protegem tabelas de domínio criadas futuramente. Não conceder `INSERT`, `UPDATE`,
`DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`, `CREATE` ou privilégios de
superusuário. A conta usada para OIDC/auditoria e a conta de importação são
separadas da conta de consulta.

Defina a URL somente no ambiente do processo:

```text
DASHBOARD_DATABASE_URL=postgresql://stroop_dashboard_ro:<segredo>@postgres:5432/stroop_production
DASHBOARD_PAGE_SIZE=1000
```

Não coloque a URL em imagem, Git, logs, screenshots ou mensagens. Antes de
liberar a conta, confirme com uma sessão administrativa que
`has_table_privilege('stroop_dashboard_ro', 'public.assessments', 'SELECT')`
é verdadeiro e que a tentativa de `CREATE TABLE` com essa conta é recusada.

## Migração controlada

1. Faça backup PostgreSQL íntegro antes de qualquer migração.
2. Aplique migrations e importe um CSV sintético no banco descartável.
3. Configure a URL de leitura e compare contagens, métricas e filtros com a
   referência SQLite sintética.
4. Faça o smoke do dashboard sem o arquivo SQLite presente.
5. Só depois de aceite institucional, planeje a migração de dados reais; esta
   etapa não executa migração operacional nem altera dados existentes.

O fallback SQLite permanece disponível somente para o uso local sem
`DASHBOARD_DATABASE_URL`; ele continua abrindo o arquivo em modo somente leitura.
