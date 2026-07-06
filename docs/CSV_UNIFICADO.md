# CSV unificado

Data: 2026-07-06.

## Objetivo

O CSV unificado e a fonte oficial de dados por tentativa do experimento Stroop Go/No-Go. Cada execucao concluida normalmente deve gerar um unico arquivo em `data/`, contendo pratica e bloco principal diferenciados pela coluna `block`.

O arquivo existe para:

- manter uma linha por tentativa real;
- preservar metadados da sessao;
- evitar CSVs separados por loop;
- reduzir divergencia entre estimulo exibido e dados exportados;
- servir como fonte futura para validacao, importacao SQLite e dashboard local.

Resultados calculados a partir desse arquivo sao descritivos. O projeto nao gera diagnostico, norma, percentil clinico ou classificacao individual.

## Colunas oficiais

O CSV deve conter exatamente estas 21 colunas, nesta ordem:

```text
project
participant_id
participant_name
initials
visit
evaluator
assessment_id
assessment_date
started_at
test_code
test_version
block
trial_number
word
ink_color
condition
correct_response
key_pressed
reaction_time
correct
error_type
```

## Tipos e valores permitidos

| Coluna | Regra |
|---|---|
| `project` | texto curto do projeto ou protocolo |
| `participant_id` | identificador pseudonimizado |
| `participant_name` | dado pessoal local; usado apenas no formulario |
| `initials` | opcional; pode ficar vazio |
| `visit` | codigo da visita |
| `evaluator` | codigo ou iniciais profissionais |
| `assessment_id` | UUID da execucao |
| `assessment_date` | data local `YYYY-MM-DD` |
| `started_at` | data e hora local ISO 8601 com fuso |
| `test_code` | `stroop_go_nogo_ptbr` |
| `test_version` | versao do experimento |
| `block` | `practice` ou `main` |
| `trial_number` | inteiro positivo, sequencial dentro do bloco, iniciado em 1 |
| `word` | palavra exibida na tentativa |
| `ink_color` | cor exibida pelo PsychoPy, como `green`, `yellow`, `pink`, `black`, `red`, `orange`, `brown`, `purple`, `blue` ou `gray` |
| `condition` | `congruent` ou `incongruent` |
| `correct_response` | `space` em Go; vazio em No-Go |
| `key_pressed` | `space` quando houver resposta; vazio sem resposta |
| `reaction_time` | segundos com ponto decimal apenas quando houver resposta; vazio sem resposta |
| `correct` | `1` ou `0` |
| `error_type` | `hit`, `omission`, `correct_rejection` ou `commission` |

Campos `_raw` nao fazem parte do contrato oficial e nao devem ser usados como fonte de analise.

## Exemplos ficticios

### Hit

```csv
project,participant_id,initials,visit,evaluator,assessment_id,assessment_date,started_at,test_code,test_version,block,trial_number,word,ink_color,condition,correct_response,key_pressed,reaction_time,correct,error_type
PILOTO_STROOP,P_EXEMPLO,NOME_REDIGIDO,V1,AV01,00000000-0000-0000-0000-000000000000,2026-07-06,2026-07-06T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.1,main,1,VERMELHO,red,congruent,space,space,0.512,1,hit
```

### Omission

```csv
PILOTO_STROOP,P_EXEMPLO,NOME_REDIGIDO,V1,AV01,00000000-0000-0000-0000-000000000000,2026-07-06,2026-07-06T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.1,main,2,AZUL,blue,congruent,space,,,0,omission
```

### Correct rejection

```csv
PILOTO_STROOP,P_EXEMPLO,NOME_REDIGIDO,V1,AV01,00000000-0000-0000-0000-000000000000,2026-07-06,2026-07-06T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.1,main,3,VERDE,yellow,incongruent,,,,1,correct_rejection
```

### Commission

```csv
PILOTO_STROOP,P_EXEMPLO,NOME_REDIGIDO,V1,AV01,00000000-0000-0000-0000-000000000000,2026-07-06,2026-07-06T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.1,main,4,AMARELO,blue,incongruent,,space,0.681,0,commission
```

## Nome do arquivo

O arquivo oficial deve ser salvo em `data/` usando o `participant_id` como nome-base. O `participant_name` nao entra no nome do arquivo:

```text
data/<participant_id>.csv
```

O nome nao deve conter iniciais, visita ou avaliador. O `assessment_id` permanece registrado no conteudo do CSV para rastrear a execucao especifica.

## Execucoes abortadas

Nesta fase, execucoes interrompidas antes do encerramento normal nao geram CSV oficial parcial. Essa decisao evita tratar coletas incompletas como dados validos. Se a recuperacao de execucoes parciais for necessaria no futuro, ela deve ser especificada e documentada antes da implementacao.

## Analise tecnica

Execute a partir da raiz do projeto:

```bash
python3 scripts/analisar_stroop.py data/PARTICIPANT_ID.csv
```

O script valida o contrato do CSV e calcula metricas descritivas apenas para o bloco `main`.
