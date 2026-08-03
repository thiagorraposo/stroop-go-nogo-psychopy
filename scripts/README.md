# Scripts

Esta pasta contem scripts auxiliares para analise descritiva e manutencao local.

Para executar a analise a partir da raiz do projeto:

```bash
python3 scripts/analisar_stroop.py data/PARTICIPANT_ID.csv
```

`analisar_stroop.py` consome apenas um CSV unificado local em `data/`, distinguindo `practice` e `main` pela coluna `block`. O script valida o contrato oficial, calcula metricas descritivas do bloco principal e nao modifica o CSV bruto.

Os resultados sao descritivos e exploratorios. Eles nao sao interpretacao clinica, diagnostico ou comparacao normativa.

`setup_env.py` cria a `.venv` multiplataforma e instala as dependencias do dashboard. `run_dashboard.py` seleciona ou recebe um CSV oficial, chama o importador SQLite sem modificar o CSV e inicia o Streamlit. Consulte `docs/INSTALACAO_MULTIPLATAFORMA.md`.

`doctor.py` faz somente verificacoes de leitura no ambiente. Na raiz do projeto,
use `py scripts\doctor.py` no Windows ou `python3 scripts/doctor.py` no Linux e
macOS. Ele nao instala pacotes, nao modifica CSVs, nao cria o SQLite e nao abre o
dashboard.
