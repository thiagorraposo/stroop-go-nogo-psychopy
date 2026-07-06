# AGENTS.md

## Regras para scripts

- Scripts devem analisar apenas arquivos locais em `data/`.
- Scripts nao devem modificar arquivos brutos de coleta.
- Scripts devem suportar o CSV unificado futuro.
- Scripts devem distinguir `practice` e `main` por meio da coluna `block`.
- Nao incluir interpretacao clinica, diagnosticos ou normas populacionais.
- Scripts futuros devem validar CSVs antes de importar.
- Scripts nao devem sobrescrever banco local sem backup ou confirmacao explicita.
- Scripts devem impedir importacao duplicada sem confirmacao explicita.
- Scripts devem separar erros de validacao de dados validos.
- Scripts de importacao devem manter rastreabilidade entre `assessment_id`, `source_file` e tentativas.
