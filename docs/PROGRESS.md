# Progresso e retomada

Memoria concisa da ultima unidade de trabalho; estado formal, dependencias e
aceite ficam no [roadmap WEB](ROADMAP_WEB.md). Fatos historicos ficam no
[registro de alteracoes](REGISTRO_DE_ALTERACOES.md), e decisoes arquiteturais
nos [ADRs](arquitetura/ADR-001-evolucao-web.md).

## 2026-10-16 — Consolidacao das regras de trabalho

- Solicitacao atual: consolidar instrucoes de autonomia, continuidade, subagentes,
  qualidade, contexto e Git. Objetivo de implementacao WEB pausado; esta tarefa
  documental nao o retoma nem concede aceite a etapas.
- Estado observado: branch de desenvolvimento `prep-web`, worktree inicialmente
  limpo; a proxima etapa indicada no roadmap e W01. Nenhuma etapa funcional
  foi iniciada nesta consolidacao.
- Regras consolidadas em `AGENTS.md`, `docs/AGENTS.md` e `tests/AGENTS.md`;
  protocolo, retomada do roadmap e README alinhados. `ROADMAP_WEB.md` e ADRs
  existentes preservados como fontes canonicas, sem criar documentos paralelos
  `ROADMAP.md` ou `ARCHITECTURE.md`.
- Arquivos da unidade: os tres AGENTS acima, `README.md`,
  `docs/WORKFLOW_CODEX_CLI.md`, `docs/ROADMAP_WEB.md`, este arquivo,
  `docs/ESTRUTURA_DO_PROJETO.md` e `docs/REGISTRO_DE_ALTERACOES.md`.
- Validacoes: `git diff --check` aprovado; verificador Python ad hoc conferiu
  50 destinos de links relativos nos nove documentos, sem ausencias. Comparacao
  com o HEAD confirmou preservacao das fichas W00–W23, estado/aceite do roadmap,
  protocolo legado e limites de dominio/seguranca. Revisao independente por
  subagente concluiu sem lacunas materiais nas sete secoes.
  Testes de codigo, lint, tipos, build e integracao nao se aplicam a esta mudanca
  exclusivamente documental; nenhum comportamento executavel foi alterado.
- Unidade documental validada e registrada; commit local com mensagem
  `docs: consolida regras de execucao autonoma web`.
- Proxima acao de desenvolvimento: quando o usuario retomar a implementacao
  pausada, consultar W01 e suas decisoes de produto/metodo antes de implementar,
  sem presumir aceite; se houver bloqueio localizado, avaliar W04 conforme suas
  dependencias, registrando a decisao no roadmap.
