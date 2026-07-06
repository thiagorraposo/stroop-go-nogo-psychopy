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
| `test_version` | constante | `0.1.0` |

`test_version` inicial `0.1.0` identifica a primeira versao com formulario estruturado de sessao.

## Regras de validacao

- `project`, `participant_id`, `visit` e `evaluator` nao podem ficar vazios.
- `initials` pode ficar vazio.
- Todos os valores digitados passam por remocao de espacos no inicio e no fim.
- `participant_id` deve obedecer ao padrao:

```text
^[A-Za-z0-9_-]{2,64}$
```

- Se houver erro, o formulario mostra mensagem clara e preserva os valores digitados para correcao.
- O experimento nao inicia enquanto houver erro de validacao.
- O cancelamento encerra o experimento antes de qualquer tentativa.

## Privacidade e minimizacao

- `participant_id` e o identificador principal e deve ser pseudonimizado.
- `initials` e opcional e deve ser tratado como dado potencialmente identificavel.
- Nao coletar nome completo.
- Nao coletar CPF, e-mail, telefone, endereco, idade ou sexo nesta versao.
- Avaliador(a) deve usar codigo ou iniciais profissionais, nao nome completo.
- O CSV oficial usa `assessment_id` como nome-base do arquivo; demais metadados ficam apenas no conteudo do CSV local.
- Dados reais permanecem em `data/`, pasta ignorada pelo Git.
- Nenhum dado clinico, diagnostico ou normativo e coletado pelo formulario.

## Mapeamento para CSV

Os metadados abaixo sao adicionados as linhas de tentativa:

- `project`
- `participant_id`
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
| `initials` | `TR` |
| `visit` | `V1` |
| `evaluator` | `AV01` |

`initials` e opcional. O campo pode ficar vazio quando nao for necessario.

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
9. Conferir se o CSV local tem o nome do `assessment_id` e inclui todos os metadados.
10. Confirmar que nenhum dado foi versionado.

O checklist deve ser aprovado antes de considerar a Fase 1 completamente validada para coleta.
