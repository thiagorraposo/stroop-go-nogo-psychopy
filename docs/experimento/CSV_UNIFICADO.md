# CSV unificado

Data: 2026-07-06.

## Objetivo

O CSV unificado e a fonte oficial de dados por tentativa do experimento Stroop Go/No-Go. Cada execucao concluida normalmente deve gerar um unico arquivo em `data/`, contendo apenas as tentativas do bloco principal. A pratica permanece no fluxo do experimento para treinamento e feedback, mas nao e exportada no CSV oficial.

O arquivo existe para:

- manter uma linha por tentativa real do bloco principal;
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
| `block` | `main` nas execucoes oficiais atuais; `practice` e aceito apenas para compatibilidade historica |
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

Exemplos integralmente sinteticos, revisados em 2026-10-16 para as 21 colunas
e a versao local `0.2.2`. As quatro linhas ilustram classificacoes; nao
representam uma sessao completa de 16 tentativas.

### Hit

```csv
project,participant_id,participant_name,initials,visit,evaluator,assessment_id,assessment_date,started_at,test_code,test_version,block,trial_number,word,ink_color,condition,correct_response,key_pressed,reaction_time,correct,error_type
PROJETO_SINTETICO,P_SINTETICO,PESSOA SINTETICA,,V_SINTETICA,AV_SINTETICO,00000000-0000-0000-0000-000000000000,2026-10-16,2026-10-16T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.2,main,1,VERDE,green,congruent,space,space,0.512,1,hit
```

### Omission

```csv
PROJETO_SINTETICO,P_SINTETICO,PESSOA SINTETICA,,V_SINTETICA,AV_SINTETICO,00000000-0000-0000-0000-000000000000,2026-10-16,2026-10-16T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.2,main,2,AMARELO,yellow,congruent,space,,,0,omission
```

### Correct rejection

```csv
PROJETO_SINTETICO,P_SINTETICO,PESSOA SINTETICA,,V_SINTETICA,AV_SINTETICO,00000000-0000-0000-0000-000000000000,2026-10-16,2026-10-16T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.2,main,3,AZUL,gray,incongruent,,,,1,correct_rejection
```

### Commission

```csv
PROJETO_SINTETICO,P_SINTETICO,PESSOA SINTETICA,,V_SINTETICA,AV_SINTETICO,00000000-0000-0000-0000-000000000000,2026-10-16,2026-10-16T10:00:00-03:00,stroop_go_nogo_ptbr,0.2.2,main,4,CINZA,green,incongruent,,space,0.681,0,commission
```

## Nome do arquivo

O arquivo oficial deve ser salvo em `data/` com codigo do teste e data/hora local da execucao:

```text
data/stroop_go_nogo_ptbr_YYYY-MM-DD_HHhMMmSSs_trials.csv
```

O nome nao deve conter `participant_id`, `participant_name`, iniciais, visita ou avaliador. Esses metadados e o `assessment_id` permanecem registrados somente no conteudo do CSV para rastrear a execucao especifica. O sufixo `_trials.csv` permite que o launcher local encontre o arquivo oficial mais recente.

## Execucoes abortadas

Nesta fase, execucoes interrompidas antes do encerramento normal nao geram CSV oficial parcial. Essa decisao evita tratar coletas incompletas como dados validos. Se a recuperacao de execucoes parciais for necessaria no futuro, ela deve ser especificada e documentada antes da implementacao.

## Analise tecnica

Execute a partir da raiz do projeto:

```bash
python3 scripts/analisar_stroop.py data/stroop_go_nogo_ptbr_2026-10-16_10h00m00s_trials.csv
```

O script valida o contrato do CSV e calcula metricas descritivas apenas para o bloco `main`.

## Pratica

As tentativas de pratica nao entram no CSV oficial desta versao. Elas continuam sendo classificadas em memoria para feedback imediato e HUD da pratica, mas sao descartadas da lista exportada antes da gravacao do arquivo.

## Variante WEB

O serializador em `stroop/domain/web_export.py` conserva as 21 colunas, usa
`test_version=0.2.2-web.1` na coleta WEB, mascara nome/iniciais e recebe
metadados fixados no servidor. O RT recebido ja esta em segundos; o CSV
preserva sua precisao, sem converter novamente ou arredondar um valor positivo
para zero. Isso permite reproduzir as metricas calculadas antes da exibicao.
O Builder local e sua formatacao existente permanecem preservados.

Horario e data WEB sao UTC; nome do arquivo usa somente codigo do teste e
timestamp. Delimitadores/aspas/quebras de linha sao escapados pelo writer CSV;
campos textuais com prefixo de formula recebem apostrofo para uso em planilhas.
Exportacao exige o [escopo profissional](../seguranca/ACESSO_WEB.md); o resumo
participante nao oferece download. Fixtures e aceite estao no roadmap.
