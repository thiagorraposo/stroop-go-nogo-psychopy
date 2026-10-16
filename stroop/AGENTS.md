# Nucleo Python compartilhado

Herda as instrucoes da raiz. Mapa: [estrutura](../docs/ESTRUTURA_DO_PROJETO.md).
Decisoes: [ADR-001](../docs/arquitetura/ADR-001-evolucao-web.md).

- `domain/`: contratos, excecoes, validacao e metricas; somente biblioteca padrao.
- `ingestion/`: leitura e adaptadores de entrada; depende de `domain/`.
- Nenhuma dessas camadas importa `scripts`, `dashboard`, drivers de banco ou
  frameworks web. Interfaces e persistencia dependem do nucleo.
- Preserve formulas, unidades, tipos de excecao e dados normalizados existentes.
  Fonte metodologica: `docs/DECISOES_DO_EXPERIMENTO.md`.
- CLIs antigas reexportam os nomes extraidos por compatibilidade. Nao duplique
  as implementacoes nessas CLIs; novos consumidores importam `stroop`.
- Valide com `tests/test_nucleo_compartilhado.py` e a suite de regressao.
