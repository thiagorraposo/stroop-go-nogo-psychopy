# Scripts

Esta pasta contem scripts auxiliares para analise descritiva e manutencao local.

Para executar a analise a partir da raiz do projeto:

```bash
python3 scripts/analisar_stroop.py
```

`analisar_stroop.py` deve consumir apenas dados locais em `data/`. A evolucao esperada e usar o CSV unificado de uma execucao futura, distinguindo `practice` e `main` pela coluna `block`.

Os resultados sao descritivos e exploratorios. Eles nao sao interpretacao clinica, diagnostico ou comparacao normativa.
