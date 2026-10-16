# Progresso e retomada

Memoria concisa; estado formal, dependencias e aceite no
[roadmap WEB](ROADMAP_WEB.md). Evidencias datadas no
[registro de alteracoes](REGISTRO_DE_ALTERACOES.md); arquitetura nos
[ADRs](arquitetura/ADR-001-evolucao-web.md).

## 2026-10-16 — W04 concluida; W01 aguarda decisoes

- Objetivo de implementacao WEB retomado pelo usuario; branch `prep-web`,
  inicialmente limpa. Regras de continuidade/subagentes/Git ja consolidadas.
- W04 implementada e validada: casos de uso em `stroop/application/`, drivers,
  SQL e transacoes em `stroop/persistence/`; CLIs apenas delegam/reexportam.
  Schema/migrations, formulas, CSV, comandos, erros e retornos preservados.
  Commit local `cd35d78`.
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
  etapas dependentes. Documento: [PROTOCOLO_WEB.md](PROTOCOLO_WEB.md), D1–D6.
  Exemplos canonicos corrigidos em `CSV_UNIFICADO.md` para as 21 colunas,
  inteiramente sinteticos; sem alterar experimento ou formato oficial.
- Validacao factual W01: 39 testes focados aprovados (condicoes/interface/CSV),
  exemplos aceitos por nucleo/analisador, 29 links locais e diff conferidos.
  Nenhum Pilot grafico ou teste de temporizacao fisica executado.
- Containers sinteticos exclusivos de PostgreSQL e smoke W04 encerrados e
  removidos; nenhum processo de teste permanece ativo. Logs em `/tmp` apenas.
- Proxima acao: obter respostas as perguntas pendentes, registrar as decisoes
  pertinentes e validar W01 integralmente; depois W02 (contrato HTTP). Nao
  presumir aprovacao de propostas ou antecipar dependencias. W04 era a unica
  etapa independente de W01; W05 depende de W02. Sem outra etapa elegivel agora.
