# Condicoes

Esta pasta contem os CSVs de condicoes usados pelo PsychoPy Builder.

- `pratica_stroop_go_nogo_ptbr.csv`: tentativas do bloco de pratica.
- `bloco_principal_stroop_go_nogo_ptbr.csv`: tentativas do bloco principal.
- `contagem_regressiva.csv`: textos usados nas telas breves de preparacao antes dos blocos.

Colunas esperadas nos CSVs de tentativas:

- `trial_number`
- `word`
- `ink_color`
- `ink_color_display`
- `condition`
- `correct_response`

`ink_color` e o valor logico usado no CSV unificado. `ink_color_display` usa hexadecimal apenas para renderizacao do estimulo no PsychoPy.

Os CSVs desta pasta sao rastreados pelo Git porque definem a logica experimental. Eles nao sao dados coletados de participantes.
