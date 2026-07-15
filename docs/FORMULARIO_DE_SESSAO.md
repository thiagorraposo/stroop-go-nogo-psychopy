# Formulario de sessao

Data: 2026-07-06.

## Objetivo

O formulario de sessao coleta metadados minimos antes do inicio da tarefa Stroop Go/No-Go. Ele substitui o dialogo padrao `participant/session` do Builder por um formulario local, estruturado e validado.

O objetivo e identificar a execucao de forma pseudonimizada, preservar privacidade e permitir rastreabilidade futura entre CSV bruto, avaliacao e metricas agregadas.

## Campos exibidos

| Label no formulario | Campo no CSV | Obrigatorio | Regra |
|---|---|---:|---|
| Projeto | `project` | sim | texto curto identificando projeto ou protocolo |
| ID do participante | `participant_id` | sim | 2 a 64 caracteres; letras, numeros, hifen e sublinhado |
| Nome do participante | `participant_name` | sim | 2 a 120 caracteres; dado pessoal local, trim dos espacos |
| Iniciais (opcional) | `initials` | nao | opcional; nao usar nome completo |
| Visita | `visit` | sim | codigo ou numero da visita |
| Avaliador(a) | `evaluator` | sim | codigo ou iniciais profissionais |

Mensagem fixa exibida:

```text
A data e a hora da avaliação são registradas automaticamente.
```

Botao de confirmacao:

```text
Iniciar tarefa
```

Tambem ha opcao de cancelamento seguro. Se o formulario for cancelado, o experimento e encerrado antes do inicio da tarefa.

## Campos automaticos

| Campo | Origem | Regra |
|---|---|---|
| `assessment_id` | sistema | UUID unico gerado no inicio da execucao |
| `assessment_date` | sistema | data local em formato ISO `YYYY-MM-DD` |
| `started_at` | sistema | data e hora local em ISO 8601 com fuso, ate segundos |
| `test_code` | constante | `stroop_go_nogo_ptbr` |
| `test_version` | constante | `0.2.2` |

`test_version` atual `0.2.2` identifica a versao com protocolo curto, bloco principal balanceado 8/8, HUD, tema escuro, centralizacao do estimulo e formulario com `participant_name`. Os campos centrais do formulario permanecem pseudonimizados, com `participant_id` como identificador tecnico principal.

## Regras de validacao

- `project`, `participant_id`, `participant_name`, `visit` e `evaluator` nao podem ficar vazios.
- `participant_name` e obrigatório, com 2 a 120 caracteres apos trim.
- `initials` pode ficar vazio.
- Todos os valores digitados passam por remocao de espacos no inicio e no fim.
- `participant_id` deve obedecer ao padrao:

```text
^[A-Za-z0-9_-]{2,64}$
```
- `participant_name` e removido dos espacos no inicio e no fim e deve ter entre 2 e 120 caracteres.

- Se houver erro, o formulario mostra mensagem clara e preserva os valores digitados para correcao.
- O experimento nao inicia enquanto houver erro de validacao.
- O cancelamento encerra o experimento antes de qualquer tentativa.

## Privacidade e minimizacao

- `participant_id` e o identificador principal e deve ser pseudonimizado.
- `participant_name` e dado pessoal local, nao deve aparecer em nome de arquivo, exemplos publicos, logs ou commits.
- `initials` e opcional e deve ser tratado como dado potencialmente identificavel.
- Nao coletar nome completo.
- Nao coletar CPF, e-mail, telefone, endereco, idade ou sexo nesta versao.
- Avaliador(a) deve usar codigo ou iniciais profissionais, nao nome completo.
- O CSV oficial usa `participant_id` como nome-base do arquivo; `participant_name` nao entra no nome do arquivo e os demais metadados ficam no conteudo do CSV local.
- Dados reais permanecem em `data/`, pasta ignorada pelo Git.
- Nenhum dado clinico, diagnostico ou normativo e coletado pelo formulario.

## Mapeamento para CSV

Os metadados abaixo sao adicionados as linhas de tentativa:

- `project`
- `participant_id`
- `participant_name`
- `initials`
- `visit`
- `evaluator`
- `assessment_id`
- `assessment_date`
- `started_at`
- `test_code`
- `test_version`

Eles acompanham as colunas de tentativa existentes:

- `block`
- `trial_number`
- `word`
- `ink_color`
- `condition`
- `correct_response`
- `key_pressed`
- `reaction_time`
- `correct`
- `error_type`

Na Fase 2, esses campos passaram a compor o CSV unificado oficial por execucao.

## Exemplos ficticios

| Campo | Exemplo |
|---|---|
| `project` | `PILOTO_STROOP` |
| `participant_id` | `P001` |
| `participant_name` | `NOME_REDIGIDO` |
| `initials` | `TR` |
| `visit` | `V1` |
| `evaluator` | `AV01` |

`initials` e opcional. O campo pode ficar vazio quando nao for necessario. `participant_name` e local e nao deve ser compartilhado em nomes de arquivo, screenshots ou exemplos publicos.

## Checklist de teste manual

1. Abrir `stroop_go_nogo_ptbr.psyexp` no PsychoPy Builder.
2. Rodar em modo Pilot.
3. Confirmar que o formulario aparece antes da abertura.
4. Tentar avancar com `participant_id` vazio.
5. Tentar `participant_id` invalido, como `P 001`.
6. Preencher:
   - Projeto: `PILOTO_STROOP`
   - ID do participante: `P001`
   - Iniciais: `TR`
   - Visita: `V1`
   - Avaliador(a): `AV01`
7. Iniciar e executar uma tentativa curta.
8. Encerrar normalmente.
9. Conferir se o CSV local tem o nome do `participant_id` e inclui todos os metadados.
10. Confirmar que nenhum dado foi versionado.

O checklist deve ser aprovado antes de considerar a Fase 1 completamente validada para coleta.
