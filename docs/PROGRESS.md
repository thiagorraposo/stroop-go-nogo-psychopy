# Progresso e retomada

Memoria concisa; estado formal, dependencias e aceite no
[roadmap WEB](ROADMAP_WEB.md). Evidencias datadas no
[registro de alteracoes](REGISTRO_DE_ALTERACOES.md); arquitetura nos
[ADRs](arquitetura/ADR-001-evolucao-web.md).

## 2026-10-16 — Retomada autonoma e W04

- Objetivo de implementacao WEB retomado pelo usuario; branch `prep-web`,
  inicialmente limpa. Regras de continuidade/subagentes/Git ja consolidadas.
- W04 implementada e validada: casos de uso em `stroop/application/`, drivers,
  SQL e transacoes em `stroop/persistence/`; CLIs apenas delegam/reexportam.
  Schema/migrations, formulas, CSV, comandos, erros e retornos preservados.
- Arquivos: novas camadas; dois importadores; testes de importacao SQLite/PG
  e `test_casos_uso_importacao.py`; AGENTS raiz/stroop; READMEs scripts/tests;
  guias de importacao, mapa estrutural, roadmap, este arquivo e registro.
- Validacao: baseline 168 aprovados; resultado 173 aprovados, sem falhas/erros/
  skips, com PostgreSQL sintetico descartavel. AST confirmou 18 SQLs identicos
  e quatro hashes de schema/migrations preservados. Compileall, Compose, build,
  smoke health/HTTP/imports, importacao SQLite em tmpfs e validacao PostgreSQL
  sem rede na imagem aprovados; revisao independente SQLite aprovada.
- Nenhuma dependencia instalada; lint/tipos autonomos sem configuracao atual.
  Nenhum dado real, secret operacional, coleta, producao ou OCI acessado.
- W01: subagente conferiu `.psyexp`/condicoes e redigiu protocolo factual;
  perguntas enviadas na sessao sobre desktop/teclado, foco/aba, pratica,
  variante web e aceite temporal. Sem resposta, nao conceder aceite nem iniciar
  etapas dependentes. Exemplos antigos do CSV com 20 campos precisam de correcao
  documental para as 21 colunas canonicas.
- Proxima acao: registrar/commitar W04 e concluir a parte factual W01, corrigindo
  exemplos e validando fontes/links; retomar contratos e implementacao seguintes
  somente com as decisoes indispensaveis. W04 e a unica etapa funcional
  independente de W01 neste ponto; W05 depende tambem de W02.
