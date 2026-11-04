# Fixtures sinteticas de CSV

Estes arquivos exercitam o contrato atual do CSV oficial sem usar dados reais.
Todos os nomes, identificadores e metadados sao deliberadamente ficticios.

- `csv/valido_minimo.csv`: quatro tentativas principais validas, cobrindo `hit`,
  `omission`, `correct_rejection` e `commission`.
- `csv/invalido_coluna_ausente.csv`: cabecalho sem `error_type`.
- `csv/invalido_tipo.csv`: `trial_number` nao inteiro.
- `csv/invalido_dominio.csv`: `condition` fora do dominio permitido.
- `csv/instrumento_sintetico_demo.csv`: duas métricas de um instrumento
  demonstrativo sem tentativas, usado para validar coexistência e separação.

As fixtures invalidas devem ser rejeitadas por
`scripts/importar_csv_sqlite.py`. Elas nao devem ser colocadas em `data/`.

## Fixtures WEB compartilhadas

- `web_result_canonical.json`: vetores sinteticos de JSON canonico/hash W08.
- `web_results_summary.json`: cinco execucoes sinteticas completas, ordem,
  observacoes temporais, metricas Python, exibicao e CSV esperado W12. Consumida
  por Python/TypeScript; nao e uma coleta nem fonte de protocolo do aplicativo.
  Inclui mediana par/impar, ausencia de hits e RT positivo muito pequeno.
