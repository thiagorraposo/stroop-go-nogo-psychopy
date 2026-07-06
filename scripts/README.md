# Scripts

Esta pasta contem scripts auxiliares para analise descritiva e manutencao local.

Para executar a analise a partir da raiz do projeto:

```bash
python3 scripts/analisar_stroop.py data/ASSESSMENT_ID.csv
```

`analisar_stroop.py` consome apenas um CSV unificado local em `data/`, distinguindo `practice` e `main` pela coluna `block`. O script valida o contrato oficial, calcula metricas descritivas do bloco principal e nao modifica o CSV bruto.

Os resultados sao descritivos e exploratorios. Eles nao sao interpretacao clinica, diagnostico ou comparacao normativa.
