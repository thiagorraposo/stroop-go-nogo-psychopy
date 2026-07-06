# Validacao estatica de condicoes e tempos

Data da validacao: 2026-07-06.

## Escopo

Esta validacao documenta a Fase 3 do experimento Stroop Go/No-Go: ampliacao para 10 cores oficiais, balanceamento das condicoes e perfil temporal de tentativa.

Arquivos validados:

- `stroop_go_nogo_ptbr.psyexp`
- `condicoes/contagem_regressiva.csv`
- `condicoes/pratica_stroop_go_nogo_ptbr.csv`
- `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv`
- `tests/test_fase3_condicoes_tempos.py`
- `tests/test_csv_unificado.py`

Nenhum arquivo em `data/` foi alterado ou usado como fonte de validacao. Esta configuracao e experimental propria, para fins educacionais e de pesquisa exploratoria, sem norma clinica, diagnostico ou equivalencia com instrumentos de terceiros.

## Cores oficiais

| Palavra | `ink_color` | Cor visual |
|---|---|---|
| `VERDE` | `green` | `#1BAE55` |
| `AMARELO` | `yellow` | `#B8860B` |
| `ROSA` | `pink` | `#D42E88` |
| `PRETO` | `black` | `#1A1A1A` |
| `VERMELHO` | `red` | `#CF2E2E` |
| `LARANJA` | `orange` | `#E56A00` |
| `MARROM` | `brown` | `#6D4027` |
| `ROXO` | `purple` | `#7837B8` |
| `AZUL` | `blue` | `#1976D2` |
| `CINZA` | `gray` | `#626870` |

`ink_color` permanece como valor logico no CSV unificado oficial. O campo `ink_color_display` existe apenas nos CSVs de condicoes para renderizar o texto no PsychoPy com hexadecimal. O exportador unificado continua gravando somente `ink_color`.

## Arquivos de condicoes

| CSV | Codificacao | Delimitador | Linhas de dados | Colunas |
|---|---|---|---:|---|
| `pratica_stroop_go_nogo_ptbr.csv` | UTF-8 | virgula | 10 | `trial_number`, `word`, `ink_color`, `ink_color_display`, `condition`, `correct_response` |
| `bloco_principal_stroop_go_nogo_ptbr.csv` | UTF-8 | virgula | 60 | `trial_number`, `word`, `ink_color`, `ink_color_display`, `condition`, `correct_response` |

Os testes validam UTF-8, separacao por virgula, largura uniforme e presenca das colunas esperadas.

## Balanceamento da pratica

| Propriedade | Valor |
|---|---:|
| Tentativas | 10 |
| Congruentes | 5 |
| Incongruentes | 5 |
| Aparicoes por palavra | 1 |
| Aparicoes por `ink_color` | 1 |

Regras validadas:

- cada uma das 10 palavras aparece exatamente uma vez;
- cada uma das 10 cores aparece exatamente uma vez;
- `correct_response` e `space` somente em tentativas `congruent`;
- `correct_response` fica vazio em tentativas `incongruent`;
- nenhuma tentativa `incongruent` tem palavra e cor equivalentes.

## Balanceamento do bloco principal

| Propriedade | Valor |
|---|---:|
| Tentativas | 60 |
| Congruentes / Go | 40 |
| Incongruentes / No-Go | 20 |
| Aparicoes por palavra | 6 |
| Aparicoes por `ink_color` | 6 |
| Aparicoes congruentes por palavra | 4 |
| Aparicoes incongruentes por palavra | 2 |
| Aparicoes congruentes por `ink_color` | 4 |
| Aparicoes incongruentes por `ink_color` | 2 |

As 20 tentativas incongruentes usam duas rotacoes ciclicas das 10 cores, com deslocamentos +1 e +3. Isso preserva duas ocorrencias incongruentes por palavra e por cor, impede pares incongruentes palavra + cor equivalentes e evita duplicidade de pares incongruentes.

O loop `principal_loop` permanece com selecao `random`, preservando a randomizacao atual do Builder.

## Regras do paradigma

- `congruent` + Espaco = `hit`;
- `congruent` sem resposta = `omission`;
- `incongruent` sem resposta = `correct_rejection`;
- `incongruent` + Espaco = `commission`.

Essas regras nao foram alteradas. O CSV unificado continua recebendo `word`, `ink_color`, `condition` e `correct_response` a partir das condicoes e exportando o contrato canonico de 20 colunas.

## Perfil temporal

Cada tentativa de pratica e do bloco principal usa:

| Segmento | Inicio | Duracao | Fim |
|---|---:|---:|---:|
| Cruz de fixacao | 0.0 s | 0.3 s | 0.3 s |
| Estimulo e janela de resposta | 0.3 s | 1.5 s | 1.8 s |
| Intervalo vazio | 1.8 s | 0.2 s | 2.0 s |

Configuracao validada no `.psyexp`:

- `fix_pratica` e `fix_principal`: `startVal = 0`, `stopVal = 0.3`;
- `stim_pratica`, `stim_principal`, `lembrete_pratica` e `lembrete_principal`: `startVal = 0.3`, `stopVal = 1.5`;
- `resp_pratica` e `resp_principal`: `startVal = 0.3`, `stopVal = 1.5`, `forceEndRoutine = False`;
- `hold_pratica` e `hold_principal`: `startVal = 0`, `stopVal = 2.0`.

Pressionar Espaco nao encerra a tentativa antes do fim da janela de 1500 ms. A resposta e registrada dentro da janela, mas o estimulo permanece ate o fim do segmento. Respostas durante a fixacao e o intervalo vazio nao sao aceitas porque o componente de teclado inicia apenas aos 300 ms e termina apos 1500 ms de janela. O tempo de reacao e medido a partir do inicio do componente de teclado, alinhado ao inicio do estimulo.

O bloco principal tem duracao estimada:

```text
60 tentativas x 2.0 s = 120 s
```

Assim, o bloco principal dura cerca de 2 minutos. O fluxo completo e maior porque inclui formulario, instrucoes, contagens e pratica.

## Validacao automatica

Comandos executados:

```bash
python3 -m unittest tests.test_fase3_condicoes_tempos -v
python3 -m unittest tests.test_csv_unificado -v
python3 -c "import xml.etree.ElementTree as ET; ET.parse('stroop_go_nogo_ptbr.psyexp'); print('psyexp XML ok')"
```

Resultados esperados:

- 6 testes da Fase 3 aprovados;
- 10 testes do CSV unificado aprovados;
- XML do `.psyexp` parseavel.

## Checklist Pilot

1. Preencher formulario normalmente.
2. Confirmar as 10 cores.
3. Confirmar 300 ms de fixacao.
4. Confirmar 1500 ms de estimulo/resposta.
5. Confirmar 200 ms entre tentativas.
6. Confirmar que Espaco nao encerra a tentativa antecipadamente.
7. Confirmar que tentativas `congruent` aceitam Espaco.
8. Confirmar que tentativas `incongruent` exigem ausencia de resposta.
9. Concluir o teste.
10. Confirmar o CSV unificado em `data/`.
11. Executar `python3 scripts/analisar_stroop.py data/ASSESSMENT_ID.csv`.
12. Confirmar 60 tentativas principais.
13. Confirmar duracao aproximada de 2 minutos no bloco principal.
14. Confirmar classificacao coerente.

Nao foi realizado teste grafico real nesta validacao automatica.
