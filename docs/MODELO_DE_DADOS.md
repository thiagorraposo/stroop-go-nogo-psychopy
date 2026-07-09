# Modelo de dados

Data: 2026-07-09.

Este documento define o modelo logico para SQLite local. A Fase 7 implementou o schema em `scripts/db_schema.sql` e a importacao em `scripts/importar_csv_sqlite.py`.

## Visao geral

O banco local deve representar tres niveis principais:

- `assessments`: uma linha por execucao completa da tarefa.
- `assessment_metrics`: uma linha por metrica calculada por execucao.
- `trial_results`: uma linha por tentativa individual da pratica ou bloco principal.

Relacionamentos:

- `assessments` 1:N `assessment_metrics`
- `assessments` 1:N `trial_results`

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
