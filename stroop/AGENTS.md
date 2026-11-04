# Nucleo Python compartilhado

Herda as instrucoes da raiz. Mapa: [estrutura](../docs/ESTRUTURA_DO_PROJETO.md).
Decisoes: [ADR-001](../docs/arquitetura/ADR-001-evolucao-web.md).

- `domain/`: contratos, excecoes, validacao e metricas; somente biblioteca padrao.
- `ingestion/`: leitura e adaptadores de entrada; depende de `domain/`.
- Nenhuma dessas camadas importa `scripts`, `dashboard`, drivers de banco ou
  frameworks web. Interfaces e persistencia dependem do nucleo.
- `application/`: casos de uso concretos, orquestracao de ingestao/persistencia,
  relogio e erros publicos. `persistence/`: SQL, conexoes, transacoes e traducao
  de erros de driver; pode usar `sqlite3` ou `psycopg` conforme o adaptador.
  Essas camadas nao importam CLIs, dashboard ou frameworks web.
- Preserve os caminhos de `scripts/db_schema.sql` e `scripts/migrations/`;
  acesso ao recurso de schema nao autoriza importar codigo de CLI no pacote.
- Preserve formulas, unidades, tipos de excecao e dados normalizados existentes.
  Fonte metodologica: `docs/experimento/DECISOES_DO_EXPERIMENTO.md`.
- CLIs antigas reexportam os nomes extraidos por compatibilidade. Nao duplique
  as implementacoes nessas CLIs; novos consumidores importam `stroop`.
- Valide com `tests/test_nucleo_compartilhado.py`,
  `tests/test_casos_uso_importacao.py` e a suite de regressao sintetica,
  incluindo PostgreSQL descartavel quando houver mudanca de persistencia.
