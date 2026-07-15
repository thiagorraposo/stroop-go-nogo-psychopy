# Condicoes

Esta pasta contem os CSVs de condicoes usados pelo PsychoPy Builder.

- `pratica_stroop_go_nogo_ptbr.csv`: tentativas do bloco de pratica.
- `bloco_principal_stroop_go_nogo_ptbr.csv`: tentativas do bloco principal.
- `contagem_regressiva.csv`: textos usados nas telas breves de preparacao antes dos blocos.

Na versao `0.2.2`, a pratica tem 4 tentativas, com 2 Go/congruentes e 2 No-Go/incongruentes. O bloco principal tem 16 tentativas, com 8 Go/congruentes e 8 No-Go/incongruentes.

Colunas esperadas nos CSVs de tentativas:

- `trial_number`
- `word`
- `ink_color`
- `ink_color_display`
- `condition`
- `correct_response`

`ink_color` e o valor logico usado no CSV unificado. `ink_color_display` usa hexadecimal apenas para renderizacao do estimulo no PsychoPy.

Os CSVs desta pasta sao rastreados pelo Git porque definem a logica experimental. Eles nao sao dados coletados de participantes.
