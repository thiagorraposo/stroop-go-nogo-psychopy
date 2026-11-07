# Modelo de dados

Base histórica: 2026-07-09. Revisão documental: 2026-11-04.
Schema e migrations não alterados nesta revisão. PostgreSQL é o banco operacional
alvo da plataforma; SQLite permanece adaptador local histórico. Modelo atual/alvo
em [ARQUITETURA_WEB](../ARQUITETURA_WEB.md), execução somente no
[backlog canônico](../Projeto%20Stroop%20Test.md).

Este documento define o modelo logico originalmente implementado no SQLite
local por `scripts/db_schema.sql`. A Etapa 4 reproduziu as mesmas tres tabelas no
PostgreSQL por migrations versionadas, mantendo textos e timestamps sem
conversao semantica. Consulte [MIGRACOES_POSTGRESQL.md](MIGRACOES_POSTGRESQL.md).

## Visao geral

O banco local deve representar tres niveis principais:

- `assessments`: uma linha por execucao completa da tarefa.
- `assessment_metrics`: uma linha por metrica calculada por execucao.
- `trial_results`: uma linha por tentativa individual da pratica ou bloco principal.

Relacionamentos:

- `assessments` 1:N `assessment_metrics`
- `assessments` 1:N `trial_results`

As tabelas de autenticacao da Etapa 8 ficam separadas desse dominio:

- `app_users`: autorizacao por `iss` + `sub`, e-mail auxiliar, perfil e bloqueio;
- `auth_audit_events`: horario, identidade OIDC, acao fixa, resultado e
  identificador aleatorio, sem conteudo clinico.

O contrato detalhado de acesso esta em
[AUTENTICACAO_E_PERMISSOES.md](../seguranca/AUTENTICACAO_E_PERMISSOES.md).

## Tabela assessments

Uma linha por execucao completa da tarefa.

| Campo | Tipo conceitual | Obrigatorio | Valores esperados e restricoes |
|---|---|---|---|
| `assessment_id` | texto/UUID | sim | fonte no experimento; identificador unico da execucao; chave primaria logica |
| `test_code` | texto curto | sim | fonte no experimento; valor inicial `stroop_go_nogo_ptbr` |
| `test_version` | texto curto | sim | versao do experimento/teste usada na execucao |
| `project` | texto | sim | fonte no formulario do experimento |
| `participant_id` | texto | sim | fonte no formulario do experimento; identificador pseudonimizado |
| `participant_name` | texto | sim | fonte no formulario do experimento; dado pessoal local |
| `initials` | texto | nao | fonte no formulario do experimento; opcional |
| `assessment_date` | data/hora | sim | fonte no experimento; gerada automaticamente |
| `visit` | texto | sim | fonte no formulario do experimento |
| `evaluator` | texto | sim | fonte no formulario do experimento; codigo ou iniciais profissionais |
| `started_at` | data/hora | sim | fonte no experimento; inicio da execucao |
| `source_file` | texto | sim | caminho ou nome do CSV bruto original |
| `imported_at` | data/hora | sim | data e hora da importacao |
| `import_status` | texto | sim | `valid` na importacao concluida |

Restricoes recomendadas:

- `assessment_id` deve ser unico.
- A combinacao `source_file` + identificador de conteudo deve impedir duplicidade acidental.
- `participant_id`, `participant_name`, `project`, `visit` e `evaluator` nao podem ser vazios.
- `participant_name` nao deve ser usado como identificador principal.
- `initials` nao deve ser usado como identificador principal.

## Tabela assessment_metrics

Uma linha por metrica calculada por avaliacao.

| Campo | Tipo conceitual | Obrigatorio | Valores esperados e restricoes |
|---|---|---|---|
| `metric_id` | inteiro autoincremental | sim | identificador unico da metrica |
| `assessment_id` | texto/UUID | sim | referencia a `assessments.assessment_id` |
| `metric_code` | texto curto | sim | codigo padronizado da metrica |
| `metric_label` | texto | sim | rotulo legivel para dashboard |
| `metric_value` | numero | sim | valor calculado |
| `unit` | texto curto | sim | `percent`, `count`, `seconds` ou equivalente documentado |
| `calculated_at` | data/hora | sim | data e hora do calculo |

Codigos obrigatorios:

| Codigo | Rotulo sugerido | Unidade | Formula ou origem |
|---|---|---|---|
| `accuracy` | Precisao total | `percent` | `((hits + correct_rejections) / total_valid_trials) * 100` |
| `accuracy_go_trials` | Precisao em Go | `percent` | `(hits / total_go_trials) * 100` |
| `accuracy_no_go_trials` | Precisao em No-Go | `percent` | `(correct_rejections / total_no_go_trials) * 100` |
| `omission_errors` | Erros de omissao | `count` | quantidade de tentativas Go sem resposta |
| `omission_errors_percentage` | Percentual de omissoes | `percent` | `(omission_errors / total_go_trials) * 100` |
| `commission_errors` | Erros de comissao | `count` | tentativas No-Go com Espaco |
| `response_time` | Tempo de resposta | `seconds` | mediana dos tempos de reacao dos hits validos |
| `total_trials` | Total de tentativas | `count` | total de tentativas validas |
| `total_go_trials` | Total de tentativas Go | `count` | tentativas congruentes |
| `total_no_go_trials` | Total de tentativas No-Go | `count` | tentativas incongruentes |
| `hits` | Hits | `count` | congruente + Espaco |
| `correct_rejections` | Rejeicoes corretas | `count` | incongruente sem resposta |

Toda nova metrica deve ter formula e unidade documentadas antes da implementacao.

## Tabela trial_results

Uma linha por tentativa individual do bloco principal ou pratica.

| Campo | Tipo conceitual | Obrigatorio | Valores esperados e restricoes |
|---|---|---|---|
| `trial_result_id` | inteiro autoincremental | sim | identificador unico da tentativa importada |
| `assessment_id` | texto/UUID | sim | referencia a `assessments.assessment_id` |
| `block` | texto curto | sim | `main` nas execucoes oficiais atuais; `practice` apenas em dados historicos/compatibilidade |
| `trial_number` | inteiro | sim | numero da tentativa dentro do bloco/CSV |
| `word` | texto | sim | palavra exibida, em caixa alta |
| `ink_color` | texto | sim | cor visual usada pelo PsychoPy |
| `condition` | texto curto | sim | `congruent` ou `incongruent` no CSV unificado oficial |
| `correct_response` | texto | nao | `space` para Go; vazio para No-Go |
| `key_pressed` | texto | nao | `space` ou vazio |
| `reaction_time` | numero | nao | tempo em segundos; vazio quando nao houver resposta |
| `correct` | inteiro/booleano | sim | `1`/`0` ou equivalente documentado |
| `error_type` | texto curto | sim | `hit`, `omission`, `correct_rejection` ou `commission` |

Esta tabela permite auditoria e analises futuras. O dashboard geral deve priorizar `assessments` e `assessment_metrics`, usando `trial_results` para detalhe, auditoria e visualizacoes especificas.

## Indices recomendados

- `assessments(participant_id)`
- `assessments(project)`
- `assessments(assessment_date)`
- `assessments(visit)`
- `assessments(evaluator)`
- `assessment_metrics(assessment_id, metric_code)`
- `trial_results(assessment_id, block)`

## Regras adicionais

- Campos de `assessments` como `assessment_id`, `project`, `participant_id`, `visit`, `evaluator`, `assessment_date`, `started_at`, `test_code` e `test_version` passam a existir desde o CSV bruto gerado pelo experimento.
- Bancos SQLite reais devem ser locais e ignorados pelo Git.
- O banco deve preservar rastreabilidade entre `assessment_id`, `source_file` e tentativas.
- Importacoes invalidas nao devem apagar dados validos ja importados.
- Reimportar uma execucao exige `--force`.

## Mapeamento do CSV unificado

| Coluna do CSV | Destino futuro |
|---|---|
| `project` | `assessments.project` |
| `participant_id` | `assessments.participant_id` |
| `participant_name` | `assessments.participant_name` |
| `initials` | `assessments.initials` |
| `visit` | `assessments.visit` |
| `evaluator` | `assessments.evaluator` |
| `assessment_id` | `assessments.assessment_id` e chave estrangeira em `trial_results` |
| `assessment_date` | `assessments.assessment_date` |
| `started_at` | `assessments.started_at` |
| `test_code` | `assessments.test_code` |
| `test_version` | `assessments.test_version` |
| `block` | `trial_results.block` |
| `trial_number` | `trial_results.trial_number` |
| `word` | `trial_results.word` |
| `ink_color` | `trial_results.ink_color` |
| `condition` | `trial_results.condition` |
| `correct_response` | `trial_results.correct_response` |
| `key_pressed` | `trial_results.key_pressed` |
| `reaction_time` | `trial_results.reaction_time` |
| `correct` | `trial_results.correct` |
| `error_type` | `trial_results.error_type` |

Campos como `source_file`, `imported_at` e `import_status` sao adicionados no processo de importacao para SQLite, sem modificar o CSV bruto original.

## Proveniencia de conclusoes WEB

A migration aditiva `0006_web_completed_results.sql` preserva as tabelas e linhas
legadas. Conclusoes WEB gravam as mesmas tentativas principais e metricas
canonicas em `assessments`, `trial_results` e `assessment_metrics`; nomes nao
sao coletados (`participant_name=NAO_COLETADO`, `initials=NULL`). `source_file`
recebe uma referencia tecnica `web:<session_id>`, sem alegar existencia de CSV.

`web_assessments` vincula uma unica avaliacao a sessao/projeto, identificando
plataforma, protocolo, versao do aplicativo, periodo de quadro, hash canonico,
instante de conclusao e recibo. `web_trial_observations` conserva condicao-fonte
e tempos observados em milissegundos; o RT canonico continua em segundos.
Ausencia desses metadados em linhas legadas nao autoriza inventar proveniencia
WEB. A FK impede que reimportacao `--force` sobrescreva uma conclusao WEB.

Semantica, idempotencia e unidades seguem o
[contrato HTTP](../desenvolvimento/CONTRATO_API_WEB.md); formulas continuam neste
modelo e em `stroop/domain/stroop.py`. Nao ha alteracao no CSV de 21 colunas.

## Consolidação da plataforma — estado observado em 2026-11-04

O modelo de três tabelas acima descreve o núcleo legado reutilizado. Não é todo
o banco operacional. As migrations 0002–0010 já acrescentam identidade/auditoria,
projetos e vínculos, transações/sessões OIDC, convites/sessões participantes,
proveniência WEB, mapa de legado e importações/gestão de contas. DDL e nomes
completos permanecem exclusivamente em `scripts/migrations/`; não recriar schema.

No fluxo WEB atual, sessão/convite precede resultado. A avaliação oficial só é
gravada após conclusão integral validada; 16 tentativas, 12 métricas, proveniência,
hash e recibo pertencem à mesma transação. Reenvio idêntico recupera recibo;
conteúdo diferente conflita. Não existe persistência de tentativas intermediárias
ou cadastro longitudinal autônomo de pessoas. Alterar isso depende de DEC-01/02,
não de completar tabelas supostamente ausentes. Projeto synthetic continua barreira.

### Ausência de tempo de resposta e apresentação

`stroop/domain/stroop.py` calcula métricas somente de main. Sem hits, response_time
persistido é a sentinela histórica **0.0 segundos**; não representa reação física
zero. O analisador CLI histórico retorna None; o resumo WEB retorna
response_time_seconds=null e a UI deve mostrar ausência (traço), sem imputar RT.
Arredondamento é apresentação; não quantizar medidas originais para hash/gate.
Não mudar sentinela, nulabilidade, fórmula ou unidade sem decisão de compatibilidade
explícita, requisitos e testes de regressão correspondentes.

Metadados técnicos WEB distinguem unidade bruta ms e RT canônico s; versão local
0.2.2 e WEB 0.2.2-web.1 são distintas, assim como versão de app e snapshot.
Resultados históricos não são associados a projeto por rótulo coincidente;
[ADR-003](../arquitetura/ADR-003-escopo-legado-web.md) exige mapa explícito.
Nenhuma coleta, importação, migration ou grant foi executado nesta revisão.


## Participação por projeto — decisão de 2026-11-05

Modelo de produto aprovado pelo responsável (DEC-01), implementado pela migration
aditiva `0011_web_incremental_sessions.sql`. Execução somente em PostgreSQL
descartável sintético e evidências em EV-M2 no backlog; sem migração operacional.
Pseudônimo/visita continuam como rótulos compatíveis nas interfaces existentes.

- Participante de projeto tem UUID técnico estável e pseudônimo único **dentro
  do projeto**, sem cadastro central de pessoa. Mesmo pseudônimo em projetos
  distintos não cria vínculo. Preservar a sensibilidade a maiúsculas dos rótulos
  atuais; não fundir códigos por normalização implícita.
- Visita tem UUID estável, pertence a um único participante/projeto e conserva
  rótulo único nesse participante. Um participante admite várias visitas;
  uma visita admite vários convites, sessões e avaliações, inclusive do mesmo
  instrumento. Não impor unicidade de resultado por participante/visita/teste.
- Convite tem UUID próprio, referencia projeto/participante/visita e instrumento/
  versão preparados. Cada emissão reserva uma sessão distinta; reemissão não
  reabre nem substitui a anterior. Avaliação oficial referencia a sessão única
  que a originou. Chaves estrangeiras compostas ou restrições equivalentes
  devem impedir vínculo cruzado entre projetos/participantes/visitas, inclusive
  por escrita direta com o papel de runtime.
- Identificadores técnicos e vínculos são imutáveis após emissão; correção de
  preparação exige novo convite, preservando o anterior. Concorrência na criação
  do mesmo pseudônimo/visita deve resolver para a mesma entidade, sem duplicação.
- Futuro cadastro longitudinal poderá acrescentar entidade e associação explícita
  aos participantes de projeto, com governança própria. Os UUIDs de visitas,
  sessões e avaliações permanecem. Não reservar identificador pessoal global,
  inferir correspondência ou coletar dados nominais nesta versão.

A alteração é aditiva, com mapeamento auditável das sessões WEB existentes;
sem apropriar legado por texto coincidente. Migrations existentes são imutáveis.
Retenção e eventual eliminação seguem decisão institucional DEC-03; preservação
operacional dos parciais não significa retenção ilimitada.

## Observações incrementais — desenho validado em 2026-11-05

Separar armazenamento de observações de execução das tabelas de resultados
oficiais. A sessão existe antes da primeira tentativa e permanece identificável
mesmo com zero observações. Cada observação principal pertence à sessão e à
posição 1–16 na ordem fixada; unicidade por sessão/posição, conteúdo imutável,
hash canônico e horário de recebimento no servidor. Proveniência inclui snapshot,
versões e relógio monotônico original, sem inventar campos ausentes.

Recibos e prefixo confirmado são persistidos na mesma transação das observações.
Estado de transporte (pendente/confirmado) é distinto da validade experimental.
Sessões não concluídas conservam observações recebidas, motivo conhecido,
origem do motivo (motor, servidor ou expiração), último recebimento e quantidade
confirmada. Ausência de aviso é incompletude de causa desconhecida, não prova de
blur, fechamento ou violação temporal específica. Sessão inválida pode também
estar incompleta; registrar ambos sem transformar isso em avaliação oficial.

Somente conclusão integral validada materializa `assessments`, tentativas e
métricas oficiais na transação existente adaptada. Dados parciais/ inválidos não
entram nas listagens, agregações, métricas ou CSV oficiais. Inspeção de parciais
exige canal profissional separado e autorização pelo mesmo projeto; sem nova
exportação de pesquisa implícita. Prática continua fora dos registros principais
e resultados oficiais. Payloads inseguros ou fora do schema são recusados; dados
estruturalmente válidos com falha metodológica podem ser preservados como
observações inválidas, sem aprovação para resultado.

O contrato de
transporte alvo validado pelo responsável está no [contrato HTTP](../desenvolvimento/CONTRATO_API_WEB.md),
a estratégia no [ADR-005](../arquitetura/ADR-005-persistencia-incremental.md),
e critérios de validade no [protocolo](../experimento/PROTOCOLO_WEB.md).

### Mapeamento físico aditivo de M2

| Entidade | Tabela / vínculo |
|---|---|
| Participante de projeto | `web_project_participants`, UUID e unicidade projeto/pseudônimo |
| Visita | `web_participant_visits`, UUID e FK composta de projeto/participante |
| Preparação | `web_invitations` acrescenta UUIDs de participante/visita e FKs compostas com os rótulos existentes |
| Observação parcial | `web_session_observations`, PK sessão/posição, FK composta para condição na ordem principal, JSON original e SHA-256 |
| Recibo parcial | `web_session_checkpoints`, sessão única, proveniência, prefixo confirmado/hash e recebimento UTC |
| Invalidação auditável | `web_session_invalidations`, sessão única, primeira razão/origem/instante observado, registro UTC e ator profissional opaco quando aplicável |

O backfill usa somente projeto/pseudônimo/visita de convites WEB existentes.
Não altera avaliações ou tentativas oficiais anteriores, não fabrica checkpoints
para resultados antigos e não preenche mapa de legado. A FK composta entre
`web_assessments` e convite impede atribuir o resultado a outro projeto.
Observações e invalidações são imutáveis para o writer de runtime; apenas o
recibo parcial pode avançar. O reader recebe SELECT nas colunas necessárias.

## Autenticação local — evolução aditiva planejada CHG-004

[ADR-006](../arquitetura/ADR-006-autenticacao-local.md) aprova conta local única;
nenhum DDL aplicado nesta revisão. Catálogo existente 0001–0011 imutável.
`app_users` e `web_professional_sessions` restringem issuer a Google em CHECK;
sessão exige `oidc_expires_at`. Portanto acrescentar apenas `password_hash` não
é migração suficiente e falsificar issuer/expiração Google é proibido.

WEB-021 deve produzir nova migration aditiva e contrato de grants antes de
executá-la em PG descartável. Representar principal técnico local imutável
(independente do username), credencial com username normalizado único, hash
Argon2id codificado, versão da credencial, estado e timestamps; sessão local
com hash único de token, principal, versão, criação, última atividade, teto
absoluto e revogação. Nunca senha recuperável, token bruto ou segredo default.
Identidade local separada não deve exigir reescrever identidades Google.
Estrutura comporta futuros principais; bootstrap garante somente uma conta
local nesta versão, inclusive sob concorrência; cadastro adicional não exposto.

A implementação deve resolver explicitamente referências de autorização e
proveniência hoje compostas por issuer/subject: criador de `web_projects`,
`web_project_members`, emissor de `web_invitations`, `web_csv_imports`,
`auth_audit_events`, `web_lock_emitter` (0008) e função de gestão de usuários
(0010). Adicionar referências/associações locais e funções adaptadas, mantendo
colunas/linhas/FKs históricas e integridade de origem; sem reassociar avaliações,
convites ou projetos à conta local por inferência. Documentar DDL/constraints e
matriz de compatibilidade old/new antes da migration. Vínculos locais são
concedidos explicitamente, não copiados de Google por e-mail/nome/equipe.

Reader não lê hash, credencial, contador ou sessão; writer tem somente operações
necessárias; owner/migrador e operador de recuperação são separados. Funções
privilegiadas exigem search_path seguro e EXECUTE mínimo; runtime não ganha
DDL/bootstrap irrestrito. Validar locks de último admin/emissor e a atomicidade
de rotação+revogação/login concorrente, sem mudar fórmulas ou schema científico.

Histórico OIDC, auditoria e dados existentes são preservados. Massa sintética
antiga deve continuar íntegra após upgrade; rollback de imagem usa schema
aditivo compatível sem down migration destrutiva. Backup inclui hashes sensíveis:
custódia criptografada, restauração isolada e revogação de sessões restauradas
antes de reabrir acesso, impedindo ressurgimento de credenciais revogadas; se
senha restaurada for antiga, redefinir por operador antes da abertura. Testar
sem tocar banco real. DDL/migração real exige autorização específica futura.

### DDL de implementação M6 — associação local

A evolução 0012 acrescenta o namespace real `urn:stroop:local` ao registro de
autorização `app_users`; não é issuer Google nem claim OIDC. `subject` local é
UUID imutável gerado no bootstrap. `web_local_credentials` associa esse par à
credencial, sem duplicar role/active. Assim FKs existentes de projetos, membros,
convites, importações e auditoria continuam válidas, sem UPDATE de histórico,
cópia de vínculos ou nova interpretação de identidade. `web_lock_emitter`
continua a bloquear a mesma linha de autorização. A estrutura de sessão local
é independente de `web_professional_sessions` e não usa prazo OIDC fictício.

Compatibilidade: 0001–0011 permanecem intactas; linhas Google continuam legíveis
pelo legado. Antes do corte, sessões OIDC continuam no mecanismo existente;
o corte de API será uma unidade posterior com regressão integrada. Rollback
antes do corte pode ignorar tabelas locais; depois do corte exige acesso fechado
até revisão específica, sem reativação OIDC ou down migration. Writer recebe
somente leitura/atualização de credencial existente, sessões e contador; não
INSERT/DELETE de credenciais nem DML de `app_users`. Bootstrap é exclusivo do
operador. Reader não recebe acesso às novas tabelas. Compatibilidade/grants da base isolada têm ensaio em EV-M6-021-BASE no
backlog; integração HTTP/HTTPS e aceite integral mantêm os gates de WEB-021.

### Gestão local transacional — evolução 0013

0013 substitui apenas a função restrita `web_manage_user`, sem reescrever
0001–0012 nem registros históricos. Sob a trava de gestão existente, o último
admin **local** ativo deve continuar disponível mesmo havendo admins Google
históricos. Alterar perfil ou bloquear alvo local revoga suas sessões na mesma
transação; reativação posterior não ressuscita esses cookies. Criação de
principal local pela função runtime é recusada, mantendo bootstrap exclusivo do
operador. Assinatura/grants permanecem; reader/writer não ganham DML de usuários
ou acesso adicional a hash. Aplicação/ensaios somente em PG sintético autorizado
de WEB-021, com regressões de último admin/concorrência e compatibilidade.

## Cadastros centrais, preparação completa e exportação avançada — evolução planejada CHG-005

Conforme [ADR-007](../arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md) e a revisão formal de `DEC-01` (2026-11-07), a plataforma passa a manter cadastros centrais de **pacientes** e **avaliadores responsáveis**, recuperando os campos do formulário original do PsychoPy Builder (`stroop_go_nogo_ptbr.psyexp`, rotina `formulario_sessao` / `controle_formulario_sessao`) e separando a identidade nominal dos resultados experimentais. Nenhuma migration existente (`0001`–`0013`) é reescrita; a evolução será materializada de forma aditiva em `WEB-045` (`0014_central_patients_evaluators.sql`), sem execução nesta missão documental.

### Tabela de correspondência com o formulário original do PsychoPy

Fontes auditadas no repositório: `stroop_go_nogo_ptbr.psyexp` (linhas 106–108 e 342–370), [CSV_UNIFICADO.md](../experimento/CSV_UNIFICADO.md), `services/session_invitation.py` e `persistence/postgres_sessions.py`.

| Campo original (`psyexp` / CSV) | Significado no domínio | Origem no PsychoPy local | Campo / entidade na plataforma WEB (`CHG-005`) | Obrigatoriedade | Regra de validação | Persistência no PostgreSQL |
|---|---|---|---|---|---|---|
| `project` | Projeto ou estudo ao qual a sessão pertence | Digitado manualmente em `formulario_sessao` (`form_values['project']`) | Seleção do projeto autorizado (`project_id` UUID → `web_projects.code`) | Obrigatório | Projeto existente, ativo (`web_projects.active = true`) e com vínculo ativo para a conta operadora | `web_projects(id, code, name)`, `web_invitations.project_id`, `assessments.project` |
| `participant_id` | Identificador estável do participante | Digitado manualmente em `formulario_sessao` (`form_values['participant_id']`) | Gerado automaticamente pelo sistema no cadastro central (`web_patients.participant_code`, ex.: `PAT-YYYYMMDD-NNNNNN`) e selecionado na preparação sem digitação manual | Obrigatório (gerado pelo sistema) | Regex `^[A-Za-z0-9_-]{2,64}$`, único globalmente em `web_patients.participant_code` e por projeto em `web_project_participants(project_id, participant_id)` | `web_patients(id, participant_code)`, `web_project_participants(id, project_id, participant_id, patient_id)`, `web_invitations.participant_id`, `assessments.participant_id` |
| `participant_name` | Nome completo do paciente/participante | Digitado manualmente em `formulario_sessao` (`form_values['participant_name']`) | Cadastrado em `web_patients.full_name` e selecionado na preparação da avaliação | Obrigatório no cadastro central de pacientes | Texto após `strip()` com `2 <= len <= 120`, sem caracteres de controle; normalizado para busca fonética/sem acento | `web_patients.full_name` (segregado da tabela científica; snapshot/vínculo via `patient_id` em `web_project_participants` e `web_invitations`) |
| `initials` | Iniciais do paciente para conferência visual/operacional | Digitado manualmente em `formulario_sessao` (`form_values['initials']`, opcional) | Cadastrado/sugerido em `web_patients.initials` e exibido/confirmado na preparação da sessão | Opcional | Texto após `strip()` com `0 <= len <= 16`, sem caracteres de controle | `web_patients.initials` e `web_invitations.participant_initials` |
| `visit` | Identificação da visita ou onda de coleta (ex.: `V1`, `basal`, `retorno_30d`) | Digitado manualmente em `formulario_sessao` (`form_values['visit']`) | Informado/selecionado na preparação da avaliação (`visit`) | Obrigatório | Texto após `strip()` com `1 <= len <= 64`, sem caracteres de controle | `web_participant_visits(id, project_id, participant_uuid, visit_label)`, `web_invitations.visit_label`, `assessments.visit` |
| `evaluator` | Avaliador(a) responsável pela preparação e condução da sessão | Digitado manualmente em `formulario_sessao` (`form_values['evaluator']`) | Selecionado a partir do cadastro central de avaliadores (`web_evaluators.id` / `evaluator_code` / `full_name`), distinto da conta local de login | Obrigatório | Avaliador existente e ativo (`web_evaluators.active = true`); `full_name` `2 <= len <= 120`, `evaluator_code` `^[A-Za-z0-9_-]{2,64}$` gerado pelo sistema | `web_evaluators(id, evaluator_code, full_name)`, `web_invitations(evaluator_uuid, evaluator_id)`, `web_assessments.evaluator_uuid`, `assessments.evaluator` |
| `test_code` | Código do instrumento cognitivo aplicado | Fixado na inicialização (`'stroop_go_nogo_ptbr'`) | Selecionado na preparação da avaliação entre instrumentos registrados no catálogo (`test_code`) | Obrigatório | Instrumento registrado em `domain/instruments.py` (padrão `stroop_go_nogo_ptbr`) | `web_invitations.test_code`, `assessments.test_code` |
| `test_version` | Versão metodológica do instrumento | Fixado na inicialização (`'0.2.2'`) | Gerado automaticamente pelo sistema a partir do catálogo (`0.2.2-web.1`) | Automático (não editável) | Imutável por versão do instrumento | `web_invitations.test_version`, `assessments.test_version` |
| `assessment_id` | Identificador único da avaliação concluída | Gerado automaticamente (`str(uuid.uuid4())`) | Gerado automaticamente pelo sistema ao materializar a avaliação oficial | Automático (não editável) | UUID v4 único | `assessments.assessment_id`, `web_assessments.assessment_id` |
| `assessment_date` | Data civil de início da avaliação (`YYYY-MM-DD`) | Gerado automaticamente (`_started_at.date().isoformat()`) | Derivado automaticamente de `started_at` no servidor | Automático (não editável) | Data ISO `YYYY-MM-DD` | `assessments.assessment_date` |
| `started_at` | Timestamp ISO 8601 do início efetivo da sessão | Gerado automaticamente (`_started_at.isoformat()`) | Gerado automaticamente pelo servidor na ativação/início | Automático (não editável) | Timestamp ISO 8601 UTC | `web_participant_sessions.started_at`, `assessments.started_at` |

### Modelo lógico e separação de entidades (`CHG-005`)

A arquitetura diferencia explicitamente sete níveis de domínio, evitando fusão entre cadastro pessoal e execução experimental:

1. **Paciente (`web_patients`):**
   - `id UUID PRIMARY KEY` (identificador interno imutável gerado pelo sistema).
   - `participant_code TEXT NOT NULL UNIQUE` (código legível estável gerado automaticamente pelo sistema, ex.: `PAT-20261107-000001`, compatível com `^[A-Za-z0-9_-]{2,64}$`).
   - `full_name TEXT NOT NULL` (`CHECK (char_length(btrim(full_name)) BETWEEN 2 AND 120)`).
   - `normalized_name TEXT NOT NULL` (nome normalizado sem acentos e em minúsculas para pesquisa e detecção de possíveis duplicidades/homônimos).
   - `initials TEXT NOT NULL DEFAULT ''` (`CHECK (char_length(btrim(initials)) <= 16)`).
   - `disambiguation_note TEXT NOT NULL DEFAULT ''` (observação curta opcional de confirmação operacional, ex.: referência interna autorizada do estudo, limitada a 160 caracteres, sem criar campos clínicos/demográficos).
   - `is_homonym_confirmed BOOLEAN NOT NULL DEFAULT false` (indica se o cadastro foi confirmado explicitamente pelo operador diante de homônimo existente).
   - `active BOOLEAN NOT NULL DEFAULT true` (estado cadastral para inativação lógica sem exclusão destrutiva).
   - `created_at TIMESTAMPTZ NOT NULL`, `updated_at TIMESTAMPTZ NOT NULL`, `created_by_issuer TEXT NOT NULL`, `created_by_subject TEXT NOT NULL`.

2. **Avaliador responsável (`web_evaluators`):**
   - `id UUID PRIMARY KEY` (identificador interno imutável gerado pelo sistema).
   - `evaluator_code TEXT NOT NULL UNIQUE` (código estável gerado automaticamente pelo sistema, ex.: `EVA-000001`, compatível com `^[A-Za-z0-9_-]{2,64}$`).
   - `full_name TEXT NOT NULL` (`CHECK (char_length(btrim(full_name)) BETWEEN 2 AND 120)`).
   - `normalized_name TEXT NOT NULL` (para busca e prevenção de duplicidade).
   - `initials TEXT NOT NULL DEFAULT ''` (`CHECK (char_length(btrim(initials)) <= 16)`).
   - `active BOOLEAN NOT NULL DEFAULT true` (inativação lógica; avaliadores inativos mantêm todo o histórico de avaliações, mas não aparecem como opção ativa em novas sessões).
   - `created_at TIMESTAMPTZ NOT NULL`, `updated_at TIMESTAMPTZ NOT NULL`, `created_by_issuer TEXT NOT NULL`, `created_by_subject TEXT NOT NULL`.

3. **Participação / vínculo com projeto (`web_project_participants`):**
   - Mantém `id UUID PRIMARY KEY`, `project_id UUID NOT NULL`, `participant_id TEXT NOT NULL` (`UNIQUE (project_id, participant_id)`).
   - Acrescenta coluna aditiva `patient_id UUID NULL REFERENCES web_patients(id) ON DELETE RESTRICT`.
   - Para todas as novas preparações a partir de `WEB-045`/`WEB-046`, `patient_id` é preenchido obrigatoriamente e `participant_id` recebe `web_patients.participant_code` (permitindo que o mesmo paciente participe de múltiplos projetos mantendo o mesmo `patient_id` e `participant_code`). Registros históricos anteriores a `CHG-005` conservam `patient_id IS NULL` até associação explícita auditada (`WEB-027`).

4. **Visita (`web_participant_visits`):**
   - Permanece vinculada a `(project_id, participant_uuid, visit_label)`. Um mesmo paciente pode realizar múltiplas visitas no mesmo projeto ou em projetos distintos, e repetir avaliações do mesmo instrumento ou de instrumentos diferentes na mesma visita.

5. **Preparação / convite (`web_invitations`) e sessão experimental (`web_participant_sessions`):**
   - `web_invitations` acrescenta `patient_id UUID NULL REFERENCES web_patients(id) ON DELETE RESTRICT`, `evaluator_uuid UUID NULL REFERENCES web_evaluators(id) ON DELETE RESTRICT` e `participant_initials TEXT NOT NULL DEFAULT ''`.
   - Preserva `issued_by_issuer` e `issued_by_subject` para registrar a **conta técnica autenticada** que operou o sistema, enquanto `evaluator_uuid` e `evaluator_id` (`evaluator_code`) identificam o **avaliador responsável** selecionado na preparação.

6. **Avaliação oficial e resultado (`web_assessments` / `assessments` / `trials` / `web_assessment_metrics`):**
   - `web_assessments` referencia `invitation_id`, `patient_id` (aditivo, `ON DELETE RESTRICT`) e `evaluator_uuid` (aditivo, `ON DELETE RESTRICT`).
   - A tabela científica `assessments` mantém `participant_id` (código estável do participante) e `evaluator` (`evaluator_code` estável do avaliador), preservando a separação física entre a tabela de resultados científicos e os nomes completos armazenados em `web_patients` e `web_evaluators`.
   - Quando uma exportação CSV nominal for explicitamente solicitada e autorizada pela governança do projeto (`DEC-03`), a camada de leitura faz `LEFT JOIN` controlado com `web_patients` e `web_evaluators`; no modo padrão desidentificado, exporta os códigos estáveis (`participant_code` / `evaluator_code`) e preserva `participant_name = NAO_COLETADO` (ou código autorizado), sem expor dados nominais indevidamente.

7. **Histórico de alterações cadastrais e correção de vínculos (`web_registry_audit_events` e `web_legacy_entity_links`):**
   - `web_registry_audit_events`: registra toda criação, edição cadastral, inativação/reativação e correção administrativa de vínculo de paciente ou avaliador (`event_id UUID`, `entity_type IN ('patient', 'evaluator', 'participant_link', 'invitation_link')`, `entity_id UUID`, `action TEXT`, `actor_issuer TEXT`, `actor_subject TEXT`, `reason_code TEXT`, `occurred_at TIMESTAMPTZ`, sem gravar segredos ou payloads livres em logs operacionais).
   - `web_legacy_entity_links`: registra a associação manual, autorizada e verificável entre um `web_project_participants.id` (ou `evaluator` textual histórico) anterior a `CHG-005` e um `web_patients.id` / `web_evaluators.id` central, exigindo confirmação humana explícita e proibindo reconciliação automática por igualdade de string.

### Regras de integridade, verificação de duplicidade, concorrência e exclusão lógica

- **Verificação de duplicidade e homônimos:**
  - Índices de busca: `INDEX ON web_patients (normalized_name)`, `INDEX ON web_patients (participant_code)`, `INDEX ON web_evaluators (normalized_name)`, `INDEX ON web_evaluators (evaluator_code)`.
  - Antes de inserir novo paciente ou avaliador, a API consulta registros com `normalized_name` igual ou prefixo/similaridade, retornando possíveis correspondências com atributos mínimos de confirmação: `participant_code` / `evaluator_code`, `full_name`, `initials`, `disambiguation_note`, projetos vinculados, última visita registrada e `created_at`.
  - Caso já exista registro com o mesmo `normalized_name` e o operador não envie flag explícita de confirmação de homônimo (`confirm_homonym = true`), a API recusa a criação com `409 Conflict` (`duplicate_candidate_found`) e lista os candidatos para seleção ou confirmação consciente.
- **Concorrência na geração de códigos e vínculos:**
  - Os códigos automáticos (`PAT-...` e `EVA-...`) utilizam sequência ou gerador transacional livre de colisão com `UNIQUE` constraint no PostgreSQL.
  - Emissões concorrentes de preparação para o mesmo `(project_id, patient_id, visit_label)` resolvem `web_project_participants` e `web_participant_visits` de forma idempotente (`ON CONFLICT DO NOTHING` / `SELECT FOR UPDATE`), criando convites/sessões distintos sem duplicar o participante ou a visita.
- **Proibição de exclusão destrutiva:**
  - Todas as FKs de resultados, sessões, convites, visitas e participações para `web_patients` e `web_evaluators` usam `ON DELETE RESTRICT`.
  - O papel de runtime (`stroop_app_writer`) não recebe permissão `DELETE` em `web_patients`, `web_evaluators`, `web_project_participants`, `web_participant_visits`, `web_invitations`, `assessments` ou `trials`. A remoção operacional no CRUD é sempre **inativação lógica** (`active = false`).
  - Correções de nome ou iniciais em `web_patients` / `web_evaluators` atualizam o cadastro central e registram evento em `web_registry_audit_events`, preservando intactos todos os UUIDs e vínculos históricos das avaliações já realizadas.
  - Caso uma avaliação tenha sido preparada com paciente ou avaliador incorreto por erro humano, o procedimento autorizado (`WEB-047`) realiza **revinculação administrativa auditada** (ou invalidação da sessão não concluída e emissão de novo convite), nunca exclusão destrutiva do resultado.
