# Validacao estatica de condicoes e tempos

Data da validacao: 2026-07-09.

## Escopo

Esta validacao documenta a versao `0.2.2` do experimento Stroop Go/No-Go: protocolo curto, 10 cores oficiais, tema escuro, HUD de precisao, cronometro visual do bloco principal e formulario com `participant_name`.

Arquivos validados:

- `stroop_go_nogo_ptbr.psyexp`
- `condicoes/contagem_regressiva.csv`
- `condicoes/pratica_stroop_go_nogo_ptbr.csv`
- `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv`
- `tests/test_fase3_condicoes_tempos.py`
- `tests/test_interface_pre_pratica.py`
- `tests/test_csv_unificado.py`

Nenhum arquivo em `data/` foi alterado ou usado como fonte de validacao. Esta configuracao e experimental propria, para fins educacionais e de pesquisa exploratoria, sem norma clinica, diagnostico ou equivalencia com instrumentos de terceiros.

## Cores oficiais

| Palavra | `ink_color` | Cor visual |
|---|---|---|
| `VERDE` | `green` | `#16A34A` |
| `AMARELO` | `yellow` | `#B77900` |
| `ROSA` | `pink` | `#DB2777` |
| `PRETO` | `black` | `#111111` |
| `VERMELHO` | `red` | `#DC2626` |
| `LARANJA` | `orange` | `#EA580C` |
| `MARROM` | `brown` | `#92400E` |
| `ROXO` | `purple` | `#7C3AED` |
| `AZUL` | `blue` | `#2563EB` |
| `CINZA` | `gray` | `#64748B` |

`ink_color` permanece como valor logico no CSV unificado oficial. O campo `ink_color_display` existe apenas nos CSVs de condicoes para renderizar o texto no PsychoPy com hexadecimal. O exportador unificado continua gravando somente `ink_color`.

## Arquivos de condicoes

| CSV | Codificacao | Delimitador | Linhas de dados | Colunas |
|---|---|---|---:|---|
| `pratica_stroop_go_nogo_ptbr.csv` | UTF-8 | virgula | 4 | `trial_number`, `word`, `ink_color`, `ink_color_display`, `condition`, `correct_response` |
| `bloco_principal_stroop_go_nogo_ptbr.csv` | UTF-8 | virgula | 16 | `trial_number`, `word`, `ink_color`, `ink_color_display`, `condition`, `correct_response` |

Os testes validam UTF-8, separacao por virgula, largura uniforme e presenca das colunas esperadas.

## Balanceamento da pratica

| Propriedade | Valor |
|---|---:|
| Tentativas | 4 |
| Congruentes / Go | 2 |
| Incongruentes / No-Go | 2 |

Regras validadas:

- `correct_response` e `space` somente em tentativas `congruent`;
- `correct_response` fica vazio em tentativas `incongruent`;
- nenhuma tentativa `incongruent` tem palavra e cor equivalentes.

## Balanceamento do bloco principal

| Propriedade | Valor |
|---|---:|
| Tentativas | 16 |
| Congruentes / Go | 8 |
| Incongruentes / No-Go | 8 |
| Cores oficiais presentes | 10 |

O bloco principal inclui todas as 10 cores oficiais ao menos uma vez. As palavras e cores foram distribuidas da forma mais equilibrada possivel para 16 tentativas e razao 8/8, preservando pares incongruentes validos e sem duplicidade. O loop `principal_loop` permanece com selecao `random`, preservando a randomizacao atual do Builder.

## Regras do paradigma

- `congruent` + Espaco = `hit`;
- `congruent` sem resposta = `omission`;
- `incongruent` sem resposta = `correct_rejection`;
- `incongruent` + Espaco = `commission`.

Essas regras nao foram alteradas. O CSV unificado continua recebendo `word`, `ink_color`, `condition` e `correct_response` a partir das condicoes e exportando o contrato canonico de 21 colunas.

## Perfil temporal

Pratica:

| Segmento | Inicio | Duracao | Fim |
|---|---:|---:|---:|
| Cruz de fixacao | 0.0 s | 0.3 s | 0.3 s |
| Estimulo e janela de resposta | 0.3 s | 2.0 s | 2.3 s |
| Intervalo vazio | 2.3 s | 0.5 s | 2.8 s |
| Feedback automatico | apos a tentativa | 0.5 s | - |

Bloco principal:

| Segmento | Inicio | Duracao | Fim |
|---|---:|---:|---:|
| Cruz de fixacao | 0.0 s | 0.3 s | 0.3 s |
| Estimulo e janela de resposta | 0.3 s | 2.5 s | 2.8 s |
| Intervalo vazio | 2.8 s | 0.95 s | 3.75 s |

Configuracao validada no `.psyexp`:

- `fix_pratica` e `fix_principal`: `startVal = 0`, `stopVal = 0.3`;
- `stim_pratica`, `lembrete_pratica` e `resp_pratica`: `startVal = 0.3`, `stopVal = 2.0`;
- `hold_pratica`: `startVal = 0`, `stopVal = 2.8`;
- `texto_feedback`: `stopVal = 0.5`;
- `stim_principal` e `resp_principal`: `startVal = 0.3`, `stopVal = 2.5`;
- `hold_principal`: `startVal = 0`, `stopVal = 3.75`;
- `resp_pratica` e `resp_principal`: `forceEndRoutine = False`.

Pressionar Espaco nao encerra a tentativa antes do fim da janela de resposta. A resposta e registrada dentro da janela, mas o estimulo permanece ate o fim do segmento. Respostas durante fixacao, intervalo vazio e feedback nao sao aceitas porque o componente de teclado inicia apenas aos 300 ms e termina antes do intervalo.

Durante as tentativas do bloco principal nao ha texto instrucional visivel, como lembrete de pressionar Espaco ou instrucao de navegacao. A tela principal mantem estimulo central, cronometro, precisao e progresso.

O bloco principal tem duracao estimada:

```text
16 tentativas x 3.75 s = 60 s
```

Essa duracao se refere apenas ao bloco principal. O fluxo completo e maior porque inclui formulario, tutorial, contagens, pratica e feedbacks.

## HUD e cronometro

O HUD mostra `Precisão: —` antes da primeira tentativa concluida e `Precisão: XX%` com uma barra horizontal textual apos tentativas concluidas. A pratica calcula apenas tentativas de pratica; o bloco principal calcula apenas tentativas principais.

O cronometro visual mostra `Tempo: MM:SS`, inicia apenas no comeco da primeira tentativa principal e segue continuamente ate o fim do intervalo da ultima tentativa principal. Ele e visual e nao altera CSV, metricas ou classificacao de respostas.

A precisao ao vivo pode influenciar o comportamento do participante e e uma decisao de UX, nao uma configuracao metodologicamente neutra.

## Tema e contraste

A interface usa tema escuro original com fundo `#0B1020`, texto principal `#F8FAFC`, texto auxiliar `#CBD5E1` e destaque proprio de alto contraste. Os estimulos ficam sobre cartao claro aproximado de `#F8FAFC` para preservar contraste, especialmente em PRETO, CINZA e AMARELO. Branco nao foi adicionado como cor de estimulo.

## Validacao automatica

Comandos executados:

```bash
python3 -m unittest discover -s tests -v
python3 -c "import xml.etree.ElementTree as ET; ET.parse('stroop_go_nogo_ptbr.psyexp'); print('psyexp XML ok')"
```

Resultados esperados:

- testes automatizados aprovados;
- XML do `.psyexp` parseavel;
- sintaxe dos Code Components valida.

## Checklist Pilot

1. Abrir o `.psyexp` no Builder.
2. Executar em modo Pilot.
3. Confirmar o tema escuro em todas as telas.
4. Confirmar visibilidade de PRETO, CINZA, AMARELO e demais cores.
5. Confirmar 4 tentativas de pratica.
6. Confirmar que o cronometro fica parado durante tutorial e pratica.
7. Confirmar 16 tentativas principais.
8. Confirmar que o cronometro inicia na primeira tentativa principal.
9. Confirmar precisao atualizando apos cada tentativa concluida.
10. Confirmar duracao do bloco principal proxima de 1 minuto.
11. Confirmar que Espaco nao encerra o estimulo antecipadamente.
12. Confirmar geracao de apenas um CSV unificado.
13. Executar `python3 scripts/analisar_stroop.py data/ARQUIVO_trials.csv`.
14. Confirmar classificacao coerente das tentativas.

Nao foi realizado teste grafico real nesta validacao automatica.
