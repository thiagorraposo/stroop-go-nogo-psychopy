# Dados e dashboard

Data: 2026-07-06.

Este documento define a arquitetura de coleta estruturada, consolidacao e visualizacao local de dados do experimento Stroop Go/No-Go. A Fase 1 foi implementada no PsychoPy com formulario local de sessao e metadados canonicos no `expInfo`; banco de dados, dashboard, script de importacao e CSV unificado ainda nao foram implementados.

## Objetivo

A camada de dados deve permitir:

- registrar metadados de cada sessao;
- preservar dados brutos por tentativa;
- calcular metricas consistentes;
- consultar varias execucoes;
- filtrar resultados;
- acompanhar todas as avaliacoes realizadas;
- manter rastreabilidade entre resultado agregado e arquivo bruto original.

Os resultados devem permanecer descritivos. O projeto nao deve gerar diagnostico, escore clinico, percentil clinico, comparacao normativa, classificacao individual ou recomendacao de avaliacao clinica.

## Arquitetura definida

Fluxo padrao futuro:

1. Participante ou avaliador inicia o experimento.
2. PsychoPy coleta metadados da sessao.
3. O experimento executa pratica e bloco principal.
4. PsychoPy salva um CSV bruto unificado por execucao em `data/`.
5. Um script futuro valida o CSV e calcula metricas.
6. O script importa a execucao para um banco SQLite local.
7. O dashboard Streamlit le apenas o banco SQLite.
8. O dashboard permite filtros, visao geral, tabela de sessoes e detalhe de avaliacao.
9. Dados brutos permanecem em `data/` e nao sao modificados pelo dashboard.

A solucao inicial deve funcionar sem servidor e sem internet:

```text
PsychoPy -> CSV bruto unificado -> script de importacao -> SQLite local -> dashboard Streamlit local
```

PostgreSQL so deve ser considerado futuramente se houver multiplos usuarios, coleta em rede ou necessidade de sincronizacao centralizada. Essa decisao deve ser documentada antes de qualquer implementacao.

## Formulario da sessao

Campos previstos por execucao:

| Campo | Obrigatorio | Origem | Observacao |
|---|---|---|---|
| `project` | sim | formulario PsychoPy | nome ou codigo do projeto |
| `participant_id` | sim | formulario PsychoPy | identificador principal, pseudonimizado |
| `initials` | nao | formulario PsychoPy | opcional; tratar como potencialmente identificavel |
| `assessment_date` | sim | sistema | data local gerada automaticamente no formato ISO `YYYY-MM-DD` |
| `visit` | sim | formulario PsychoPy | visita, sessao ou momento de avaliacao |
| `evaluator` | sim | formulario PsychoPy | preferir codigo ou iniciais profissionais |

`assessment_date` nao deve depender de digitacao manual, salvo futura necessidade justificada e documentada.

Nao coletar nome completo, CPF, e-mail, endereco, telefone, idade ou sexo nesta versao.

Na implementacao da Fase 1, esses campos entram no `expInfo` com nomes canonicos e acompanham as linhas de tentativa exportadas pelo PsychoPy. Os campos legados `participant` e `session` deixaram de ser usados como identificadores oficiais.

## Metricas obrigatorias

As metricas obrigatorias da tarefa Stroop sao:

| Codigo | Formula | Unidade |
|---|---|---|
| `accuracy` | `((hits + correct_rejections) / total_valid_trials) * 100` | porcentagem |
| `accuracy_go_trials` | `(hits / total_go_trials) * 100` | porcentagem |
| `accuracy_no_go_trials` | `(correct_rejections / total_no_go_trials) * 100` | porcentagem |
| `omission_errors` | quantidade absoluta de tentativas Go sem resposta | contagem |
| `omission_errors_percentage` | `(omission_errors / total_go_trials) * 100` | porcentagem |
| `commission_errors` | quantidade absoluta de tentativas No-Go com pressionamento de Espaco | contagem |
| `response_time` | mediana do tempo de reacao, em segundos, calculada apenas a partir de hits validos | segundos |

Campos tecnicos de auditoria a registrar futuramente:

- `assessment_id`
- `test_code`
- `test_version`
- `started_at`
- `ended_at`
- `total_trials`
- `total_go_trials`
- `total_no_go_trials`
- `hits`
- `correct_rejections`
- `source_file`
- `imported_at`
- `import_status`

## Privacidade e minimizacao de dados

- `participant_id` e obrigatorio e deve ser pseudonimizado.
- `initials` sao opcionais e devem ser tratadas como dado potencialmente identificavel.
- Nao coletar nome completo.
- Nao coletar dados demograficos sem justificativa, consentimento e documentacao.
- Nao subir dados reais para GitHub.
- Nao expor dados reais em prints, commits, README ou arquivos de exemplo.
- Manter banco SQLite local e ignorado pelo Git.
- Documentar qualquer futura coleta adicional de dados pessoais antes de implementacao.
- Avaliador(a) deve preferencialmente usar codigo ou iniciais profissionais, nao nome completo.

## Responsabilidades dos componentes

### PsychoPy

- Coletar metadados minimos da sessao.
- Registrar automaticamente data e hora local da avaliacao.
- Executar pratica e bloco principal sem alterar o paradigma.
- Gerar CSV bruto unificado por execucao em `data/`.
- Preservar uma linha por tentativa com `block` distinguindo `practice` e `main`.

### CSV bruto

- Ser a fonte primaria de auditoria da execucao.
- Permanecer local em `data/`.
- Nao ser modificado por scripts de importacao ou dashboard.
- Conter metadados, tentativas, respostas, tempos e classificacao por tentativa.

### Scripts de importacao

- Validar estrutura e conteudo antes de importar.
- Calcular metricas documentadas.
- Impedir importacao duplicada sem confirmacao explicita.
- Registrar erros sem alterar o CSV original.
- Criar ou atualizar SQLite local, conforme regra documentada.
- Nao produzir interpretacoes clinicas.

### SQLite

- Armazenar avaliacoes, metricas calculadas e tentativas.
- Manter relacao entre `assessment_id`, `source_file` e dados por tentativa.
- Permanecer local e ignorado pelo Git.
- Ser a unica fonte lida pelo dashboard.

### Dashboard

- Ler apenas o SQLite local.
- Permitir filtros e visualizacoes descritivas.
- Nao modificar CSV bruto.
- Nao alterar banco sem funcionalidade documentada e confirmacao explicita.
- Exibir aviso de uso descritivo e nao clinico.

### Documentacao

- Definir campos, formulas, restricoes e fluxo de trabalho.
- Registrar decisoes metodologicas e de dados antes da implementacao.
- Atualizar `docs/REGISTRO_DE_ALTERACOES.md` em mudancas relevantes.

### Git

- Versionar somente codigo-fonte, documentacao e arquivos de configuracao seguros.
- Nunca versionar dados reais, bancos locais, exports, logs ou credenciais.
- Manter `data/`, bancos SQLite e exports ignorados.

## Regras de integridade

Uma importacao deve falhar ou ficar marcada como invalida quando:

- o CSV nao contiver as colunas exigidas;
- houver linhas com numero de campos inconsistente;
- `block` nao for `practice` ou `main`;
- `condition` for incompativel com `word` e `ink_color`;
- `correct_response` for incompativel com `condition`;
- `error_type` for incompativel com resposta e condicao;
- `participant_id` estiver vazio;
- `visit` estiver vazia;
- `evaluator` estiver vazio;
- a mesma execucao for importada duas vezes sem confirmacao explicita.

Falhas de validacao devem ser registradas de forma clara, sem modificar o CSV bruto.
