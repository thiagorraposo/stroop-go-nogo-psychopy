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
