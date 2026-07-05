# AGENTS.md

## Regras para scripts

- Scripts devem analisar apenas arquivos locais em `data/`.
- Scripts nao devem modificar arquivos brutos de coleta.
- Scripts devem suportar o CSV unificado futuro.
- Scripts devem distinguir `practice` e `main` por meio da coluna `block`.
- Nao incluir interpretacao clinica, diagnosticos ou normas populacionais.
