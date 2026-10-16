# Progresso e retomada

Estado formal/aceite no [roadmap WEB](ROADMAP_WEB.md), evidencias no
[registro](REGISTRO_DE_ALTERACOES.md), arquitetura nos ADRs.

## 2026-10-16 — Organizacao documental validada

- Pedido atual: organizar arquivos preservando funcionamento. Documentos
  agrupados por assunto, com [indice](README.md) e
  [mapa atualizado](ESTRUTURA_DO_PROJETO.md). Codigo, entradas publicas,
  condicoes, SQL/migrations e infraestrutura conservam seus caminhos.
- Alterados nesta unidade: 37 documentos movidos, indice novo, referencias
  nos READMEs/AGENTS, roadmap, ADR-001 e registro. Unica alteracao Python:
  caminho de documento em `tests/test_hardening_producao.py`, sem mudar assercoes.
- Validacao: 189 testes aprovados, zero falhas/erros/skips, em 5,651 s;
  PostgreSQL sintetico descartavel, sem dados operacionais. Conferidos
  integridade dos 37 documentos, 240 links locais e `git diff --check`.
  Revisao independente sem achados bloqueantes. Sem build novo: fontes e
  configuracoes executaveis existentes inalteradas nesta reorganizacao.
- W02/W03 concluidas em `88a48c5`/`ea87120`, W05 em `b19d8b6`. W05 cobre
  factory FastAPI sem Streamlit, configuracao fechada,
  health/readiness somente leitura, limite real de 64 KiB, erros sanitizados,
  dependencias fixadas e `RequestModel` estrito.
- W05: 189 testes aprovados, zero falhas/erros/skips, incluindo readiness com
  PostgreSQL real descartavel e preservacao de migrations/contagens;
  `compileall`, `pip check`, `git diff --check` e revisao independente aprovados.
  Smoke Uvicorn em loopback respondeu live 200 e ready 200 com `no-store` e
  request ID; Host divergente foi recusado (422). A factory de teste comprova
  que importar a API nao carrega Streamlit, dashboard ou CLIs.
- W06 iniciada: validar primeiro o fluxo de login Google ja usado no dashboard
  e contratos autorizados. Autenticacao web sera verificada criptograficamente
  no servidor; testes usam chaves/claims sinteticos, sem credencial Google real.
- Container de teste W05 encerrado sem volume persistente. Proxima acao:
  identificar componentes OIDC reaproveitaveis e definir validacao/token e
  sessao do servidor para os criterios W06.

## Decisoes e contexto preservados

- Usuario aprovou explicitamente itens 1–19 da sessao. Finalidade coleta do
  grupo de pesquisa; participantes sem novo filtro demografico; usuario assume
  protocolo, elegibilidade, informacao/consentimento aplicaveis, validacao,
  operacao e incidentes. Desenvolvimento/pilotos com dados sinteticos.
- W01 concluida: D1–D6 e finalidade registradas no protocolo/metodologia;
  39 testes focados, 14 links e diff aprovados. W04 ja concluida em `cd35d78`
  (173 testes integrais sem skips, SQL/hash preservados, build/smoke aprovados).
- VPS adquirida e dominio existente: [ADR-002](arquitetura/ADR-002-hospedagem-vps.md).
  Nao presumir OCI/ARM64. Informacoes reais do host, DNS, OIDC e backup externo
  serao usadas apenas nas etapas autorizadas. Push/merge/producao continuam
  exigindo autorizacao especifica; W22 executada pelo usuario.
- Medicoes W16/homologacao alvo, textos/configuracoes especificas da pesquisa
  e retencao definitiva nao foram evidenciados pela aprovacao; permanecem
  entregas futuras, sem bloquear testes locais com dados sinteticos.
