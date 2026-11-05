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

Modelo de produto aprovado pelo responsável (DEC-01); desenho lógico alvo,
sem DDL executado. O esquema atual ainda conserva pseudônimo/visita como rótulos.

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

A futura alteração é aditiva, com mapeamento auditável das sessões WEB existentes;
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

Sem tabelas ou estados físicos novos definidos por inferência: o contrato de
transporte alvo validado pelo responsável está no [contrato HTTP](../desenvolvimento/CONTRATO_API_WEB.md),
a estratégia no [ADR-005](../arquitetura/ADR-005-persistencia-incremental.md),
e critérios de validade no [protocolo](../experimento/PROTOCOLO_WEB.md).
