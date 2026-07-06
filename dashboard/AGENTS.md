# AGENTS.md

## Regras para dashboard

- O dashboard deve ser local e baseado em Streamlit, salvo decisao documentada.
- O dashboard so pode ler SQLite e nunca alterar CSV bruto.
- Dados reais nao podem ser versionados.
- Nao exibir diagnostico, normas, percentis clinicos ou interpretacao de saude.
- Filtros devem operar por projeto, participante, visita, avaliador, periodo, teste e versao.
- Qualquer nova metrica precisa ter formula documentada antes da implementacao.
- O dashboard deve diferenciar claramente pratica e bloco principal.
- Nao usar identidade visual ou elementos proprietarios de terceiros.
- Scripts do dashboard devem ter validacao de erros e mensagens claras.
- Qualquer alteracao relevante deve atualizar documentacao e `docs/REGISTRO_DE_ALTERACOES.md`.
