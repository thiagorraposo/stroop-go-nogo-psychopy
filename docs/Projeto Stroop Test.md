# Backlog completo — evolução do Stroop

Este documento e a unica fonte canonica para etapas, pesos, dependencias,
escopo, criterios de aceite, estado, progresso, proxima etapa e decisoes externas
pendentes. O [protocolo Codex CLI](WORKFLOW_CODEX_CLI.md) define como executar,
validar e registrar o trabalho; documentos auxiliares nao mantem outro backlog.

## Estado consolidado

- Etapas 1–10: concluidas.
- Progresso global: **87%**, soma de 5% + 7% + 11% + 8% + 13% + 8% + 10% + 10% + 8% + 7%, sem credito parcial.
- Suite registrada: **164 testes aprovados**; ver evidencias datadas abaixo.
- Etapa 11: **nao iniciada**, primeira etapa nao concluida e proxima etapa.
- Destino futuro de hospedagem: **OCI Always Free**, somente na Etapa 11.
- Bloqueios atuais: nenhum para a etapa concluida; decisoes dos instrumentos
  futuros e de producao permanecem listadas neste backlog.

## Dependencias e documentos de referencia

A ordem e sequencial: cada etapa N, de 2 a 12, exige todas as etapas anteriores
integralmente concluidas; a Etapa 1 e a base. Nenhuma execucao antecipa a seguinte.
Decisoes externas listadas neste documento devem ser resolvidas na sessao do
Codex CLI antes da acao que delas depende. Nao acessar/configurar OCI antes da
Etapa 11; atos de producao exigem autorizacao explicita nessa sessao.

Consultar a [baseline](BASELINE_ETAPA_1.md), os contratos do
[experimento](DECISOES_DO_EXPERIMENTO.md), [CSV](CSV_UNIFICADO.md) e
[modelo de dados](MODELO_DE_DADOS.md), os guias de
[Docker](INFRAESTRUTURA_DOCKER.md), [migrations](MIGRACOES_POSTGRESQL.md),
[importacao SQLite](IMPORTACAO_SQLITE.md) e [dashboard](../dashboard/README.md)
conforme o componente envolvido. Sao contratos tecnicos e evidencias, nao fontes
alternativas de etapas ou progresso.

## Evidencias da inspecao de 2026-09-13

- Git: `38fe362` registra baseline; `4e4ecbc`, modularizacao; `add5512`, Docker;
  `67b406b`, schema e migrations PostgreSQL.
- Fontes presentes: fixtures sinteticas, quatro modulos do dashboard,
  `compose.yaml`, `Dockerfile.dashboard`, `scripts/migrations/0001_initial.sql`,
  executor e migrador legado; testes cobrem fronteiras, leitura SQLite e paridade.
- Suite reexecutada com `TEST_DATABASE_URL` apontando para PostgreSQL 17.6
  descartavel em tmpfs: 92 aprovados, zero falhas, erros ou skips.
  `docker compose --env-file .env.example config --quiet`: aprovado.
  Sem alteracao funcional, build/smoke/persistencia nao foram repetidos nesta
  tarefa documental; os registros da Etapa 3 permanecem historicos.
- A integridade e o backup da Etapa 1 permanecem evidencias historicas datadas;
  nenhum banco operacional ou backup foi reaberto nesta reorganizacao.
- A origem do destino OCI e o backlog fornecido pelo usuario; disponibilidade,
  limites e regiao ainda dependem de verificacao na etapa autorizada.
- Divergencias do workflow antigo e verificacoes desta tarefa estao no
  [registro de alteracoes](REGISTRO_DE_ALTERACOES.md).

## Etapas e pesos




| Etapa | Entrega                          | Peso | Acumulado | Estado    |
| ----- | -------------------------------- | ---: | --------: | --------- |
| 1     | Baseline do sistema              |   5% |        5% | Concluída |
| 2     | Modularização do dashboard       |   7% |       12% | Concluída |
| 3     | Docker local                     |  11% |       23% | Concluída |
| 4     | Schema e migrations PostgreSQL   |   8% |       31% | Concluída |
| 5     | Importação CSV → PostgreSQL      |  13% |       44% | Concluída |
| 6     | Envio remoto de CSV              |   8% |       52% | Concluída |
| 7     | Suporte a múltiplos instrumentos |  10% |       62% | Concluída |
| 8     | Autenticação e permissões        |  10% |       72% | Concluída |
| 9     | Hardening de produção            |   8% |       80% | Pendente  |
| 10    | Dashboard usando PostgreSQL      |   7% |       87% | Pendente  |
| 11    | Deploy no OCI Always Free        |   6% |       93% | Pendente  |
| 12    | Automação e validação final      |   7% |      100% | Pendente  |

---

## Etapa 1 — Baseline

**Objetivo:** documentar e proteger o comportamento original.

### Entregas

- Mapear `PsychoPy → CSV → SQLite → Streamlit`.

- Documentar schema, métricas e comandos.

- Criar backup local do SQLite.

- Criar fixtures válidas e inválidas.

- Confirmar integridade do banco.

- Registrar riscos de privacidade.


### Aceite

- Backup íntegro.

- Fluxo documentado.

- Fixtures validadas.

- 73 testes aprovados.


**Estado:** concluída — 5%.

---

## Etapa 2 — Modularização do dashboard

**Objetivo:** separar interface, transformação e acesso aos dados.

### Entregas

- `dashboard/app.py` como composição.

- `dashboard/components.py`.

- `dashboard/transformations.py`.

- `dashboard/data_access.py`.

- Compatibilidade com launchers existentes.

- Camadas sem dependências circulares.


### Aceite

- Interface e resultados preservados.

- SQLite somente leitura.

- Nenhum acesso direto do dashboard aos CSVs.

- 77 testes aprovados.


**Estado:** concluída — 12% acumulados.

---

## Etapa 3 — Docker local

**Objetivo:** criar ambiente reproduzível para o dashboard e PostgreSQL.

### Entregas

- `compose.yaml`.

- `Dockerfile.dashboard`.

- `.dockerignore`.

- `.env.example`.

- Serviços Streamlit e PostgreSQL.

- Healthchecks.

- Volume persistente.

- PostgreSQL restrito a `127.0.0.1`.

- PsychoPy fora do Docker.


### Aceite

- Build e inicialização aprovados.

- Dashboard e PostgreSQL saudáveis.

- Persistência após reinicialização.

- 83 testes aprovados.


**Estado:** concluída — 23% acumulados.

---

## Etapa 4 — Schema e migrations PostgreSQL

**Objetivo:** modelar e migrar avaliações, métricas e tentativas.

### Entregas

- Migration inicial versionada.

- Executor transacional.

- Schema com PKs, FKs, restrições e índices.

- Migração SQLite → PostgreSQL.

- Ajuste de identities e sequences.

- Rollback e idempotência.

- Documentação operacional.


### Aceite

- Schema criado em banco vazio.

- Migração sintética preservando os dados.

- Destino preenchido recusado.

- Nenhum dado real aberto.

- 92 testes aprovados.


**Estado:** concluída — 31% acumulados.

---

# Importacao e evolucao seguinte

## Etapa 5 — Importação CSV → PostgreSQL

**Objetivo:** permitir que os CSVs atuais do Stroop sejam importados diretamente para o PostgreSQL.

### Backlog

- Criar importador PostgreSQL.

- Reutilizar as validações atuais do Stroop.

- Configurar conexão por `DATABASE_URL`.

- Executar cada importação em transação.

- Impedir gravações parciais.

- Implementar idempotência.

- Detectar avaliações duplicadas.

- Registrar origem e resultado da importação.

- Sanitizar logs e mensagens de erro.

- Avaliar na sessão da Etapa 5 a necessidade de modo de validação sem persistência; registrar a decisão antes de implementar esse modo.

- Manter o importador SQLite como legado temporário.

- Documentar comandos e códigos de saída.


### Testes

- CSV válido.

- Coluna ausente.

- Tipo inválido.

- Domínio inválido.

- Importação duplicada.

- Falha com rollback.

- Indisponibilidade do PostgreSQL.

- Paridade entre SQLite e PostgreSQL.

- Nenhum dado sensível em logs.


### Aceite

- Um CSV sintético gera no PostgreSQL as mesmas avaliações, métricas e tentativas esperadas.

- Repetir a importação não duplica dados.

- Arquivo inválido não produz escrita parcial.

- Suíte completa aprovada.


**Estado:** concluida — 44% acumulados.

Evidencias de 2026-09-13: `scripts/importar_csv_postgres.py` e
`tests/test_importar_csv_postgres.py`; 12 novos testes e suite integral com
104 aprovados, sem skips, em PostgreSQL 17.6 descartavel. Paridade com SQLite,
duplicidade concorrente, rollback e preservacao do CSV comprovados. Configuracao
Docker, CLI sem persistencia, links e `git diff --check` aprovados.

Decisao operacional da sessao: incluir `--validate-only` sem conexao; duplicatas
sao recusadas sem `--force`, preservando o contrato legado. Origem e resultado
usam as colunas existentes, sem nova migration. Comandos, codigos e limites em
[IMPORTACAO_POSTGRESQL.md](IMPORTACAO_POSTGRESQL.md). Etapa 6 nao iniciada.

---

## Etapa 6 — Envio remoto de CSV

**Objetivo:** receber arquivos produzidos em outros computadores ou planilhas.

**Estado:** concluida — 52% acumulados.

Inspecao de 2026-09-13: Git limpo no inicio; importador da Etapa 5 presente no
commit `0d34ce9`; suite integral reexecutada em PostgreSQL descartavel com
104 aprovados, zero falhas, erros ou skips. Configuracao Docker aprovada.

Decisao autorizada pelo usuario na sessao de 2026-09-13: implementar
uma area local separada do dashboard, limitada a `127.0.0.1`, um CSV UTF-8 de ate
5 MiB por envio, duplicatas recusadas sem sobrescrita, arquivo temporario isolado
excluido ao finalizar (sucesso ou erro) e registro apenas de identificador
aleatorio, origem "upload local", horario e status. A proposta nao autoriza
publicacao ou dados reais. Implementacao validada com dados sinteticos.

Autorizacao recebida; bloqueio de arquitetura e retencao resolvido.
O AGENTS.md exige decisao explicita sobre ambiguidades arquiteturais e de
privacidade que alterem o resultado. Retencao de dados operacionais reais
continua sendo uma decisao futura distinta.


### Backlog

- Criar uma área de upload controlada.

- Aceitar somente formatos autorizados.

- Limitar tamanho e quantidade de arquivos.

- Validar extensão, conteúdo, encoding e estrutura.

- Armazenar temporariamente em área isolada.

- Encaminhar arquivos válidos ao importador.

- Rejeitar arquivos inválidos com mensagem segura.

- Mostrar status: recebido, validado, importado ou rejeitado.

- Evitar exposição de caminhos internos.

- Definir política de retenção dos arquivos.

- Registrar origem e horário sem conteúdo sensível.

- Testar uploads simultâneos e duplicados.


### Restrição importante

Como a autenticação só será implementada na Etapa 8, o upload desta etapa deve permanecer restrito ao ambiente local ou desativado em produção.

### Aceite

- Upload sintético completo.

- Arquivos inválidos rejeitados.

- Nenhuma execução de conteúdo enviado.

- Nenhum arquivo residual fora da política definida.

- Integração com o importador PostgreSQL validada.


Evidencias de 2026-09-13: `scripts/upload_local.py`,
`tests/test_upload_local.py` e [operacao documentada](UPLOAD_LOCAL.md).
Suite integral: 118 aprovados, sem skips, falhas ou erros; 14 testes especificos.
Smoke HTTP com PostgreSQL descartavel comprovou pagina, upload sintetico,
duplicidade, rejeicao e ausencia de residuos apos processamento normal.
JavaScript validado por `node --check`; configuracao Docker e `git diff --check`
aprovados. Dashboard, schema, formulas, dependencias e PsychoPy preservados.
Limite operacional: queda de energia/encerramento forcado
exige limpeza dos temporarios daquela execucao antes de retomar, conforme o guia.

---

## Etapa 7 — Múltiplos instrumentos

**Objetivo:** permitir diferentes testes e fichas no mesmo sistema.

**Estado:** concluída — 62% acumulados.

Evidencias de 2026-09-13: criado contrato normalizado e registro de adaptadores
em `scripts/instrumentos.py`, com o Stroop preservado e um instrumento
demonstrativo sintético validando métricas separadas, coexistência em SQLite e
PostgreSQL e ausência de tentativas incompatíveis. O dashboard passou a
selecionar um instrumento por vez e adaptar cards, gráficos, tabelas, detalhe e
exportação conforme `dashboard/instrumentos.py`. A documentação de extensão
está em [MULTIPLOS_INSTRUMENTOS.md](MULTIPLOS_INSTRUMENTOS.md).

Suíte integral: 124 testes aprovados, zero falhas, erros ou skips, com
PostgreSQL 17.6 descartável e fixtures sintéticas. Configuração Docker,
compilação Python e `git diff --check` aprovados. Nenhuma regra clínica foi
inventada e a Etapa 8 não foi iniciada.

### Backlog

- Definir contrato comum de avaliações.

- Identificar instrumento por `test_code` e `test_version`.

- Criar registro de instrumentos suportados.

- Separar métricas por instrumento.

- Evitar comparações inválidas entre testes diferentes.

- Criar adaptadores específicos de importação.

- Permitir filtros por instrumento.

- Adaptar cards, gráficos, tabelas e exportações.

- Preservar integralmente o Stroop.

- Criar documentação para adicionar novos instrumentos.

- Validar a arquitetura com um segundo instrumento sintético.


### Instrumentos previstos

- Stroop Go/No-Go.

- DASS-21.

- TUG e TUG de dupla tarefa.

- Teste de subtração associado ao EEG.

- Digit Span.

- Bateria de Avaliação Frontal.


### Pendências externas

Para cada instrumento, a equipe deverá confirmar:

- campos obrigatórios;

- unidades;

- repetições;

- regras para valores ausentes;

- fórmulas;

- faixas de pontuação;

- interpretação;

- versão utilizada;

- dados identificáveis permitidos.


### Aceite

- Pelo menos dois instrumentos sintéticos coexistem sem mistura de métricas.

- Stroop permanece sem regressão.

- Novo instrumento pode ser adicionado por contrato documentado.

- Nenhuma regra clínica é inventada.


**Progresso após conclusão:** 62%.

---

## Etapa 8 — Autenticação e permissões

**Objetivo:** controlar acesso aos dados e às operações.

**Estado:** concluida — 72% acumulados.

Decisao autorizada pelo usuario em 2026-09-13: Google Identity por OIDC nativo
do Streamlit; acesso somente a identidades previamente cadastradas por `iss` +
`sub`; e-mail apenas auxiliar; perfis `consulta`, `importacao` e
`administracao` no PostgreSQL; sem autocadastro ou secrets versionados;
revalidacao de expiracao e bloqueio em toda operacao protegida.

Evidencias de 2026-09-13: `scripts/migrations/0002_authentication.sql`,
`dashboard/auth.py`, area protegida em `dashboard/app.py`, bootstrap e
recuperacao em `scripts/gerenciar_usuarios.py` e operacao documentada em
[AUTENTICACAO_E_PERMISSOES.md](AUTENTICACAO_E_PERMISSOES.md). A antiga rota
HTTP de upload sem OIDC foi removida; o comando publico abre a area autenticada
do Streamlit em `127.0.0.1`.

Testes especificos: 17 aprovados. Suite integral: 138 aprovados, zero falhas,
erros ou skips, com PostgreSQL 17.6 descartavel em tmpfs e identidades/dados
sinteticos. Configuracao Docker, dependencias, compilacao Python, 61 links,
secrets ignorados e `git diff --check` aprovados. Build da imagem e smoke final
com Authlib empacotada, healthcheck `ok` e pagina HTTP 200 aprovados. Nenhuma
credencial Google real foi criada, lida ou versionada; login real depende da
configuracao operacional do cliente OIDC. Etapa 9 concluida; Etapa 10 nao
iniciada.

### Backlog

- Definir modelo de usuários.

- Implementar autenticação.

- Usar armazenamento seguro de senhas ou provedor externo.

- Criar sessões seguras.

- Definir perfis mínimos:

    - consulta;

    - importação;

    - administração.

- Proteger upload, visualização e exportação.

- Implementar encerramento de sessão.

- Limitar tentativas de login.

- Separar credenciais da aplicação e do banco.

- Criar trilha de auditoria sem conteúdo clínico.

- Definir criação, bloqueio e recuperação de contas.

- Testar autorização negativa.


### Aceite

- Usuário só executa ações permitidas pelo seu perfil.

- Rotas e páginas protegidas não aparecem sem autenticação.

- Credenciais não são registradas em logs.

- Upload remoto pode ser habilitado com segurança básica comprovada.


**Progresso após conclusão:** 72%.

---

## Etapa 9 — Hardening de produção

**Objetivo:** preparar o sistema para exposição na internet.

### Backlog

- Separar configuração de desenvolvimento e produção.

- Executar contêineres com menor privilégio.

- Fixar versões das imagens e dependências.

- Restringir redes e portas.

- Configurar proxy reverso.

- Preparar HTTPS.

- Adicionar headers de segurança.

- Definir limites de CPU e memória.

- Limitar requisições e uploads.

- Sanitizar erros e logs.

- Criar backup automatizável do PostgreSQL.

- Validar restauração em ambiente isolado.

- Definir retenção de dados e backups.

- Criar healthchecks e monitoramento.

- Documentar resposta a incidentes.

- Atualizar threat model.

- Revisar tratamento de dados conforme LGPD e regras da pesquisa.


### Aceite

- Backup e restauração comprovados.

- Serviços internos não expostos publicamente.

- Secrets fora do repositório.

- Testes de segurança e configuração aprovados.

- Nenhum dado real usado na validação.


**Estado:** concluida — 80% acumulados.

Implementado nesta sessão: perfil de produção separado com Nginx fixado e
compatível com ARM64, somente HTTP/HTTPS públicos, redes internas para
dashboard/PostgreSQL, execução sem privilégios, limites configuráveis com
reserva para o sistema operacional, TLS externo obrigatório e recusa explícita
de certificado sintético fora de teste. Uploads temporários são eliminados e
rejeições preservam somente hash/status/erro fechado; logs e auditorias têm
retenção configurável; dados da pesquisa têm retenção mínima provisória de
cinco anos com pseudonimização e acesso restrito; incidentes são retidos por
cinco anos com fluxo de comunicação ANPD/titulares em três dias úteis quando
aplicável; backup diário criptografado, rotação de 30 gerações e restauração
mensal isolada foram documentados e comprovados com dados sintéticos. O
destino externo, domínio, certificado real e dimensionamento final permanecem
exclusivos da Etapa 11.

Evidências: `compose.production.yaml`, `Dockerfile.proxy`,
`scripts/backup_postgres.py`, `scripts/aplicar_retencao.py`, migrations 0003,
documentos de hardening, threat model, resposta a incidentes e tratamento de
dados, além dos testes específicos. Smoke descartável comprovou healthchecks,
migrações, isolamento de portas, proxy TLS sintético somente em `APP_ENV=test`
e recusa em produção. Nenhum dado real, segredo, domínio ou destino externo foi
usado.

---

## Etapa 10 — Dashboard usando PostgreSQL

**Objetivo:** concluir a troca operacional do SQLite pelo PostgreSQL.

### Backlog

- Adaptar `dashboard/data_access.py`.

- Usar `DATABASE_URL`.

- Criar credencial PostgreSQL somente leitura.

- Remover dependência operacional do SQLite.

- Substituir PRAGMAs por inspeções compatíveis.

- Preservar filtros, métricas, gráficos e exportações.

- Implementar consultas paginadas quando necessário.

- Revisar cache e conexões.

- Validar desempenho com volume sintético representativo.

- Testar o fluxo completo:
    `CSV → importador → PostgreSQL → dashboard`.

- Preparar procedimento controlado para migração real.

- Exigir backup antes de qualquer migração real.


### Aceite

- Dashboard funciona sem arquivo SQLite.

- Resultados são equivalentes aos valores de referência.

- Usuário do dashboard não consegue escrever no banco.

- Reinicialização não perde dados.

- Fluxo ponta a ponta aprovado.


**Estado:** concluida — 87% acumulados.

Implementado nesta sessão: `dashboard/data_access.py` agora consulta as três
tabelas PostgreSQL com cursor paginado, schema validado e transações somente
leitura. `DASHBOARD_DATABASE_URL` usa a conta `dashboard_ro` separada da
credencial de importação `DATABASE_URL`; o fallback SQLite local permanece
somente para compatibilidade. Filtros, métricas, gráficos, detalhe e
exportação foram preservados porque continuam consumindo o mesmo formato de
linhas.

Evidências: cinco testes de integração PostgreSQL cobrem paginação, equivalência
de formato, banco vazio, schema inválido e rejeição de escrita; uma role
PostgreSQL sintética com `GRANT SELECT` leu o dashboard e teve `CREATE TABLE`
recusado. O fluxo CSV sintético → importador PostgreSQL → dashboard retornou
uma avaliação e `accuracy=50.0`. O container reconstruído iniciou saudável,
leu PostgreSQL sem arquivo SQLite e manteve o root filesystem somente leitura.
Após reinicialização do ambiente Docker, a avaliação sintética permaneceu
presente (`assessments_after_restart=1`).
Suíte integral: 164 testes aprovados, zero falhas, erros ou skips. Nenhum dado
real foi usado.

---

## Etapa 11 — Deploy no OCI Always Free

**Objetivo:** hospedar o sistema no ambiente escolhido.

### Backlog

- Verificar limites e disponibilidade atuais do OCI.

- Escolher região e shape compatíveis.

- Validar arquitetura ARM64 ou AMD64.

- Criar instância.

- Configurar VCN, subnet e regras de entrada.

- Configurar firewall do sistema operacional.

- Instalar Docker e Compose.

- Transferir somente arquivos necessários.

- Configurar secrets fora do Git.

- Configurar volume persistente.

- Publicar somente HTTP/HTTPS.

- Configurar domínio e DNS, se disponível.

- Ativar HTTPS.

- Configurar reinicialização automática.

- Configurar backup externo ou estratégia de recuperação.

- Executar smoke test público.

- Testar reboot da instância.

- Documentar deploy, atualização e rollback.


### Aceite

- Sistema acessível por HTTPS.

- PostgreSQL não exposto à internet.

- Reinicialização recupera os serviços.

- Backup e restauração testados.

- Nenhum dado real enviado sem autorização.

- Plano de saída do OCI documentado.


**Progresso após conclusão:** 93%.

---

## Etapa 12 — Automação e encerramento operacional

**Objetivo:** automatizar o fluxo e validar o sistema completo.

### Backlog

- Definir necessidade de API de importação.

- Criar identidade exclusiva para automações.

- Autenticar chamadas automáticas.

- Implementar validação, idempotência e auditoria.

- Criar fila, quarentena ou política de repetição quando necessária.

- Evitar importações paralelas conflitantes.

- Automatizar migrations durante atualizações de forma segura.

- Preparar processo de atualização e rollback.

- Executar testes ponta a ponta.

- Simular falha do dashboard.

- Simular falha do PostgreSQL.

- Simular upload inválido.

- Simular restauração de backup.

- Revisar documentação completa.

- Criar manual de operação.

- Criar checklist de manutenção.

- Registrar limitações conhecidas.

- Realizar aceite final com dados exclusivamente sintéticos.


### Aceite

- Fluxo remoto completo e auditável.

- Recuperação de falhas comprovada.

- Documentação permite operar o sistema sem depender do desenvolvedor.

- Todos os testes aprovados.

- Nenhuma pendência crítica aberta.

- Workflow marcado como 100%.


**Progresso após conclusão:** 100%.

---

# Decisões externas necessárias

Antes de usar dados reais, ainda será necessário confirmar:

- quem poderá acessar o sistema;

- quais identificadores de participantes serão armazenados;

- política de retenção dos CSVs;

- política de retenção dos registros no banco;

- destino e retenção dos backups;

- autorização para migração do SQLite real;

- domínio que será utilizado;

- regras e fórmulas de cada instrumento;

- responsável por aprovar alterações clínicas;

- procedimento em caso de incidente ou vazamento;

- disponibilidade e limites atuais do OCI.


# Regras de conclusão

Uma etapa só conta no progresso quando:

- todo o seu escopo estiver implementado;

- testes específicos, suíte completa sem skips obrigatórios, verificações Docker aplicáveis e `git diff --check` forem aprovados;

- documentação e workflow forem atualizados;

- riscos e limitações forem registrados;

- nenhuma etapa posterior tiver sido antecipada;

- exatamente uma mensagem de commit for sugerida;

- nenhum `git add`, commit, tag ou push for executado.

Sem progresso parcial. Teste obrigatório indisponível ou falhando bloqueia o
aceite: manter o progresso, registrar a causa e indicar a decisão ou ação
necessária. Validar somente com dados sintéticos, sem dependência de outro chat.


**Próxima ação:** `continue o projeto` na sessão do Codex CLI.
