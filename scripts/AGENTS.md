# Scripts e camada de dados

Escopo: `scripts/`. Herda todas as regras da raiz.

- Nunca modifique CSV bruto. Valide completamente antes de persistir e mantenha
  erros de validacao separados de dados aceitos.
- Preserve rastreabilidade por `assessment_id` e `source_file`, transacoes,
  bloqueio de duplicidade e exigencia explicita de `--force` para reimportacao.
- Nao sobrescreva banco preenchido fora do fluxo documentado e sem backup ou
  confirmacao. Migre schema apenas na etapa que autorizar migracoes.
- Calcule somente metricas com formula e unidade documentadas; nao produza
  interpretacao clinica ou normativa.
- Teste scripts de dados apenas com CSVs e bancos temporarios sinteticos. Nao use
  `data/` ou `database/` como fixtures.
- Preserve as CLIs publicas documentadas, salvo requisito explicito.
