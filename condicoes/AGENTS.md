# AGENTS.md

## Regras para condicoes

- CSVs desta pasta sao arquivos-fonte do experimento, nao dados coletados.
- Nao adicionar colunas sem verificar compatibilidade com o `.psyexp`.
- Nao alterar nomes de colunas usadas em rotinas e loops sem atualizar as referencias.
- Toda mudanca nas condicoes deve preservar o paradigma:
  - congruente + Espaco = `hit`;
  - congruente sem resposta = `omission`;
  - incongruente sem resposta = `correct_rejection`;
  - incongruente + Espaco = `commission`.
- Registrar mudancas relevantes em `docs/REGISTRO_DE_ALTERACOES.md`.
