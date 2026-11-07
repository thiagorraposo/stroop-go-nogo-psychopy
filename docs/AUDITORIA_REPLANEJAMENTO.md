# Auditoria de base — 2026-11-04

Escopo: inspeção estática de fontes versionadas e documentação, sem execução de
aplicações, migrations, Docker, coleta, acesso à VPS ou dados reais. HEAD auditado:
`87f6a9c52043625a3474805dfc6680390ddfc151`. Esta é evidência de presença e estrutura,
não prova de funcionamento. Testes citados existem; não foram executados nesta fase.

## Git e proveniência

- Branch inicial `feat/evolucao-web`, rastreando origin na mesma HEAD; única
  alteração local inicial: AGENTS.md, parágrafo do responsável sobre pesquisa,
  público, VPS/domínio e proibição de deploy implícito. Conteúdo incorporado à
  revisão autorizada, sem apagar sua finalidade; sua origem preexistente fica registrada.
- `git fetch origin` executado; `main` e `origin/main` coincidem em `fe8f24f`.
  A branch auditada contém main como ancestral e trabalho posterior ainda não
  integrado. Base preservada para não perder correções/evidências; não houve pull,
  rebase, merge ou retorno automático à main. Branch documental criada dela:
  `docs/replanejamento-stroop-web`.
- Remoto origin GitHub consultado somente via fetch. Proteções/reviews e saúde
  remota não foram revalidadas. Nenhuma autorização de PR/merge/deploy é inferida.

## Diagnóstico

Há dois fluxos no código: PsychoPy → CSV → importador Python → SQLite/PostgreSQL
→ Streamlit; e React/TypeScript/Vite + jsPsych → FastAPI → PostgreSQL → dashboard
React. Portanto, uma migração do zero duplicaria componentes existentes. O novo
plano consolida, revalida e completa o produto; não descarta a implementação WEB.
O README anterior registrava publicação para testes sintéticos; disponibilidade
atual não foi consultada. Existência de código/runbook não comprova publicação.

## Inventário e destino

A classificação é o destino planejado, sem remoções nesta fase. REFATORAR exige
benefício confirmado na tarefa; não autoriza reescrita ampla. REMOVER POSTERIORMENTE
é condicional à cobertura e autorização específica de retirada.

| Componente / responsabilidade atual | Dependências | Situação observada e testes existentes | Destino, refatoração necessária e risco de substituição |
|---|---|---|---|
| `stroop_go_nogo_ptbr.psyexp`: Builder local, fluxo e exportador | PsychoPy, condições, código embarcado | XML e rotinas presentes; `tests/test_fase3_condicoes_tempos.py`, `test_csv_unificado.py`, `test_resultados.py` | PRESERVAR COMO LEGADO: referência metodológica; não converter automaticamente nem editar lastrun. Risco: assumir equivalência Web |
| `condicoes/*.csv`, `web_protocol.json`: pools e snapshot | Consumidos por Python e TS | 4 prática/16 principal, 2/2 e 8/8; `test_fase3_condicoes_tempos.py`, `web/src/experiment/practice.test.ts` | REUTILIZAR sem mudar regras; distinguir cor lógica, display histórico CSV e paleta renderizada |
| `stroop/domain/stroop.py`, `web_results.py`, `auth.py`: validação, 12 métricas, identidade | Biblioteca padrão | Domínio sem UI/driver; `test_nucleo_compartilhado.py`, `test_web_results.py`, `test_authentication.py` | REUTILIZAR. Sem hits: sentinela persistida 0.0 versus null no resumo; não unificar sem contrato |
| `stroop/ingestion/`: CSV e registro de instrumentos | Domínio | Normalização/validação compartilhadas; `test_csv_unificado.py`, `test_multiplos_instrumentos.py` | REUTILIZAR; instrumento demo é prova técnica, não novo instrumento científico |
| `stroop/application/`: importações, sessões, avaliações, administração, resultados | Domínio, persistência | Casos de uso concretos; `test_casos_uso_importacao.py`, `test_web_assessments.py`, `test_web_imports.py` | REUTILIZAR; REFATORAR somente duplicação comprovada. Risco: interfaces importarem CLIs |
| `stroop/persistence/`: SQL, transações, autorização | sqlite3/psycopg | Conclusão atômica e recibo/hash; writer/reader separados; `test_web_sessions.py`, `test_web_results.py`, `test_web_administration_provisioned.py` | REUTILIZAR; revalidar concorrência/privilégios. Não trocar schema por suposição |
| `api/`: FastAPI, transporte fechado, auth Google, sessões, consultas, administração/importação | Núcleo, google-auth, PostgreSQL, runtime ASGI | Rotas já implementadas; `test_api_base.py`, `test_web_oidc_callback.py`, `test_web_auth.py`, `test_web_export.py`, `test_web_security_review.py` | REUTILIZAR; confrontar contrato/OpenAPI/código. Risco: regressão de permissões ou exposição de claims |
| `web/src/experiment/`: máquina temporal customizada em plugins jsPsych | jsPsych, snapshot, performance.now/requestAnimationFrame, DOM | Prática, principal, HUD, interrupções e gates; `practice.test.ts`, `main.test.ts`, `summary.test.ts`, `ExperimentHost.test.tsx` | REUTILIZAR, validar cedo. React hospeda o motor; não dirige quadros. Risco temporal crítico |
| `web/src/App.tsx`, `api/`, `dashboard/`, `imports/` sob web/src | React, cliente HTTP, núcleo de visualização | Convites, participante, painel, filtros, contas, CSV; testes Vitest e `web/e2e/` | REFATORAR apenas limites de UI comprovadamente necessários; manter fluxos existentes. Sem cadastro independente de pessoas |
| `dashboard/` Streamlit, `dashboard/auth.py` | Fachada auth, consultas somente leitura, pandas/Streamlit | Modular e autenticado; `test_dashboard.py`, `test_dashboard_postgres.py`, `test_authentication.py` | SUBSTITUIR como interface final; PRESERVAR COMO LEGADO até M7/M10. REMOVER POSTERIORMENTE só mediante autorização; risco de perder capacidades/importação |
| `scripts/importar_csv_*`, launchers, doctor | Núcleo, bancos locais ou PG | CLIs e reexports preservados; `test_importar_csv_sqlite.py`, `test_importar_csv_postgres.py`, `test_fluxo_multiplataforma.py` | REUTILIZAR CSV complementar; preservar comandos locais e não alterar coletas |
| `scripts/analisar_stroop.py` | CSV local, regras históricas próprias | Sem hits usa None, domínio usa 0.0; `test_csv_unificado.py` | PRESERVAR COMO LEGADO; REFATORAR somente após contrato de ausência/arredondamento |
| `scripts/migrations/0001…0010`, `migrations.py`, `db_schema.sql`, provisionador | PostgreSQL, advisory lock, grants | Schema legado e WEB, OIDC/projetos/convites/proveniência/mapa/importações/contas; `test_postgres_migrations.py`, `test_web_database_provision.py` | REUTILIZAR; migrations existentes imutáveis, futuras aditivas; nenhuma executada aqui |
| Compose legado, Dockerfile.dashboard/proxy, nginx/nginx.conf | Docker, PG, TLS, Streamlit | Pilha legada separada; `test_infraestrutura_docker.py`, `test_hardening_producao.py` | PRESERVAR COMO LEGADO; REMOVER POSTERIORMENTE com autorização. Risco: confundir volumes/pilhas |
| compose.web.yaml, Dockerfile.api/web, web/deploy/, deploy/ | Docker, Nginx, HTTPS, secrets externos, papéis PG | Pilha WEB já isolada; `test_web_runtime.py`, `test_web_proxy_config.py`, smoke_web_compose.py | REUTILIZAR com revalidação, sem editar infraestrutura nesta fase |
| backup_postgres.py, replicate_web_backup.py, monitor_web.py e deploy/ | Criptografia, PG, SSH restrito, systemd opcional | Backup, réplica ciphertext, observação mínima; `test_backup_web.py`, `test_web_backup_replication.py`, `test_monitor_web.py`, `test_vps_rollback.py` | REUTILIZAR; templates não provam instalação/restauração. Risco de falsa recuperabilidade |
| .github/workflows/web.yml, verify_web_ci.py | Python/Node, PG descartável, Docker, navegadores | Pipeline completo existente; `test_verify_web_ci.py`; PR/main/manual, não push de branch | REUTILIZAR, revalidar M8. Não desabilitar; CI remota não consultada nesta auditoria |
| docs/ e AGENTS | Contratos científicos e histórico | Múltiplos estados e comandos antigos, paleta mal descrita, API chamada futura | REFATORAR documentalmente nesta fase, arquivar planos e usar backlog único |

Os caminhos abreviados `test_*.py` na tabela pertencem a `tests/`; nomes TS
pertencem à árvore indicada. Índice de testes: [tests/README](../tests/README.md).

## Limites funcionais e divergências resolvidas no planejamento

1. A identificação WEB atual é código pseudonimizado/visita no convite. Não há
   entidade autônoma de cadastro longitudinal de pessoas. Isso fica proposto,
   pendente de necessidade e privacidade; não criar tabela só para simetria.
2. `stroop/persistence/web_sessions.py` limita criação/resgate a projeto synthetic.
   Retirar essa barreira é decisão futura explícita, não simples correção técnica.
3. Tentativas ficam em RAM até conclusão (`POST /participant/complete`); servidor
   persiste 16 tentativas, métricas, proveniência e recibo numa transação. Retry do
   mesmo payload é idempotente; alteração de conteúdo conflita. Não há gravação
   incremental/offline nem retomada do principal após recarga. A regra aprovada
   invalida o principal interrompido e exige nova sessão/prática.
4. Fórmulas compatíveis não provam equivalência de temporização. Gates internos
   só conferem coerência do relato do navegador, não onset físico nem hardware.
5. Regras WEB D1–D6 já aprovadas são preservadas. Encerramento histórico reduzido
   de W16 inclui 20 cenários aprovados e 2 falhas Firefox, sem matriz física integral.
6. Arquitetura futura SQLite/Streamlit em decisões antigas é histórica; API e
   React não são mais diretórios vazios. A paleta CSV não é a paleta de renderização.
7. GitHub Flow anterior previa PR/merge; ordem atual autoriza commit/push e veda
   PR/merge automático. Não alterar proteções remotas para acomodar a nova política.

## Evidências históricas e atualidade

[Roadmap Wxx arquivado](legado/ROADMAP_WEB_2026-11-04.md),
[retomada arquivada](legado/RETOMADA_2026-11-04.md) e
[registro](REGISTRO_DE_ALTERACOES.md) conservam aceites e resultados anteriores.
Há registros de 369 testes Python/PG, build/ensaios e homologação W21; não foram
reexecutados aqui. W22 tinha transporte de réplica registrado, mas agenda,
restauração externa e atualização da publicação pendentes; W23 dependia disso.
Os 87% pertencem apenas às etapas 1–12 históricas. Nenhum desses números é
progresso automático do novo escopo. A validação atual é exclusivamente documental,
registrada no [backlog](Projeto%20Stroop%20Test.md).
