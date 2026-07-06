# Validacao estatica de condicoes e variaveis

Data da validacao: 2026-07-05.

## Arquivos analisados

- `stroop_go_nogo_ptbr.psyexp`
- `condicoes/contagem_regressiva.csv`
- `condicoes/pratica_stroop_go_nogo_ptbr.csv`
- `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv`
- `scripts/analisar_stroop.py`

Nenhum arquivo em `data/` foi alterado ou usado como fonte de validacao.

## Loops encontrados

| Loop | Rotinas envolvidas | CSV de condicoes | Caminho relativo | Selecao | Repeticoes |
|---|---|---|---|---|---|
| `contagem_pratica_loop` | `contagem` | `contagem_regressiva.csv` | `condicoes/contagem_regressiva.csv` | `sequential` | `1` |
| `pratica_loop` | `trial_pratica`, `feedback_pratica` | `pratica_stroop_go_nogo_ptbr.csv` | `condicoes/pratica_stroop_go_nogo_ptbr.csv` | `random` | `1` |
| `contagem_principal_loop` | `contagem` | `contagem_regressiva.csv` | `condicoes/contagem_regressiva.csv` | `sequential` | `1` |
| `principal_loop` | `trial_principal` | `bloco_principal_stroop_go_nogo_ptbr.csv` | `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv` | `random` | `1` |

Todos os caminhos relativos referenciados pelo `.psyexp` apontam para arquivos existentes.

## Variaveis esperadas e encontradas

| Variavel | Onde e usada | Rotina | Componente | Origem esperada | Encontrada | Risco |
|---|---|---|---|---|---|---|
| `countdown_text` | texto da contagem | `contagem` | `contagem_texto` | `condicoes/contagem_regressiva.csv` | sim | nenhum |
| `word` | texto do estimulo e exportacao | `trial_pratica`, `trial_principal` | `stim_pratica`, `stim_principal`, codigo | CSVs de pratica e principal | sim | nenhum |
| `ink_color` | cor do estimulo e exportacao | `trial_pratica`, `trial_principal` | `stim_pratica`, `stim_principal`, codigo | CSVs de pratica e principal | sim | nenhum |
| `condition` | classificacao e exportacao | `trial_pratica`, `trial_principal` | codigo | CSVs de pratica e principal | sim | nenhum |
| `correct_response` | resposta correta e regra Go/No-Go | `trial_pratica`, `trial_principal` | `resp_pratica`, `resp_principal`, codigo | CSVs de pratica e principal | sim | nenhum |
| `trial_number` | exportacao | `trial_pratica`, `trial_principal` | codigo | CSVs de pratica e principal | sim | nenhum |
| `block` | exportacao | `trial_pratica`, `trial_principal` | codigo | `practice` ou `main` definido no codigo | sim | nenhum |
| `key_pressed` | exportacao e classificacao | `trial_pratica`, `trial_principal` | codigo | `resp_pratica.keys` ou `resp_principal.keys` | sim | nenhum |
| `reaction_time` | exportacao | `trial_pratica`, `trial_principal` | codigo | `resp_pratica.rt` ou `resp_principal.rt` | sim | nenhum |
| `correct` | exportacao | `trial_pratica`, `trial_principal` | codigo | classificacao no fim da rotina | sim | nenhum |
| `error_type` | exportacao | `trial_pratica`, `trial_principal` | codigo | classificacao no fim da rotina | sim | nenhum |
| `feedback_text` | feedback da pratica | `trial_pratica`, `feedback_pratica` | codigo, `texto_feedback` | codigo de classificacao da pratica | sim | nenhum |
| `progress_text` | progresso do bloco principal | `trial_principal` | codigo, `progresso_principal` | codigo no inicio da rotina principal | sim | nenhum |
| `corrAns` | nao usado | nenhum | nenhum | nao aplicavel | ausente | nenhum; a variavel usada e `correct_response` |

## Validacao dos CSVs

| CSV | Codificacao | Delimitador | Linhas de dados | Cabecalho | Largura uniforme | Colunas obrigatorias ausentes | Colunas nao utilizadas | Vazios indevidos | Duplicidades acidentais |
|---|---|---|---:|---|---|---|---|---|---|
| `contagem_regressiva.csv` | UTF-8 | virgula | 5 | `countdown_text` | sim | nenhuma | nenhuma | nenhum | nenhuma |
| `pratica_stroop_go_nogo_ptbr.csv` | UTF-8 | virgula | 8 | `trial_number`, `word`, `ink_color`, `condition`, `correct_response` | sim | nenhuma | nenhuma | nenhum | nenhuma |
| `bloco_principal_stroop_go_nogo_ptbr.csv` | UTF-8 | virgula | 32 | `trial_number`, `word`, `ink_color`, `condition`, `correct_response` | sim | nenhuma | nenhuma | nenhum | nenhuma |

Campos vazios em `correct_response` foram considerados esperados quando `condition` e `incongruente`, pois a resposta correta e nao pressionar tecla.

## Validacao do paradigma

Resultado: nenhuma inconsistencia encontrada nos CSVs de pratica e principal.

- Todas as linhas `congruente` combinam palavra e cor.
- Todas as linhas `congruente` usam `correct_response` igual a `space`.
- Todas as linhas `incongruente` apresentam palavra e cor diferentes.
- Todas as linhas `incongruente` deixam `correct_response` vazio.
- Nao foi encontrada condicao ambigua.
- Nao foi encontrada combinacao que induza classificacao incorreta de `hit`, `omission`, `correct_rejection` ou `commission`.

Mapeamento atual entre palavras e valores usados pelo PsychoPy:

| Palavra | Valor em `ink_color` |
|---|---|
| `VERMELHO` | `red` |
| `AZUL` | `blue` |
| `VERDE` | `green` |
| `AMARELO` | `yellow` |

Os valores de `ink_color` sao legiveis para PsychoPy e seguros para CSV, pois usam nomes simples sem virgulas internas.

## Cores

Cores atualmente presentes:

- vermelho;
- azul;
- verde;
- amarelo.

Cores previstas, mas ainda ausentes:

- rosa;
- preto;
- laranja;
- marrom;
- roxo;
- cinza.

Nao foram adicionadas cores nesta etapa para evitar alterar quantidade de tentativas, distribuicao experimental ou desenho do bloco.

## CSV unificado futuro

| Coluna final | Origem atual | Disponivel | Depende de loop | Depende de codigo | Risco de divergencia | Ajuste futuro |
|---|---|---|---|---|---|---|
| `participant` | `expInfo['participant']` | sim | nao | sim | baixo | manter no CSV unificado |
| `session` | `expInfo['session']` | sim | nao | sim | baixo | manter no CSV unificado |
| `block` | codigo em `trial_pratica` e `trial_principal` | sim | nao | sim | baixo | garantir `practice` e `main` no CSV unificado |
| `trial_number` | CSV de condicoes | sim | sim | nao | baixo | manter uma linha por tentativa |
| `word` | CSV de condicoes | sim | sim | nao | baixo | manter valores padronizados |
| `ink_color` | CSV de condicoes | sim | sim | nao | baixo | manter nomes simples de cor |
| `condition` | CSV de condicoes | sim | sim | nao | baixo | validar contra `word` e `ink_color` |
| `correct_response` | CSV de condicoes | sim | sim | nao | baixo | manter vazio para No-Go |
| `key_pressed` | componente de teclado | sim | nao | sim | baixo | consolidar no CSV unificado |
| `reaction_time` | componente de teclado | sim | nao | sim | baixo | consolidar no CSV unificado |
| `correct` | codigo de classificacao | sim | nao | sim | baixo | consolidar no CSV unificado |
| `error_type` | codigo de classificacao | sim | nao | sim | baixo | consolidar no CSV unificado |

A estrutura atual possui base suficiente para produzir um CSV unificado por execucao. A unificacao ainda deve ser tratada em etapa futura, porque a execucao atual tambem pode gerar arquivos separados por loop.

## Inconsistencias identificadas

Nenhuma inconsistencia bloqueante foi identificada entre `.psyexp`, loops, rotinas e CSVs de condicoes.

Pendencia nao bloqueante:

- a documentacao e o script ja apontam para um CSV unificado futuro, mas a exportacao atual ainda pode produzir arquivos separados por loop; isso deve ser resolvido em uma etapa propria, sem alterar o paradigma.

## Correcoes realizadas

Nenhuma correcao foi realizada em `.psyexp` ou CSVs de condicoes.

Esta validacao adicionou somente documentacao.

## Conclusao

O experimento esta estruturalmente pronto para avancar para a especificacao visual das novas telas. Antes de coleta real, ainda sera necessario testar em modo Pilot depois de qualquer mudanca visual e implementar a unificacao definitiva da exportacao em etapa separada.
