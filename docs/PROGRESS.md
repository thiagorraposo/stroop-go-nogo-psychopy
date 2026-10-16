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
- W02 e W03 concluidas em `88a48c5` e `ea87120`. W05 permanece em andamento:
  codigo/dependencias em `api/`, README da API e `tests/test_api_base.py`
  preexistentes a esta organizacao, preservados fora do seu commit. A suite
  acima inclui seus 16 testes; aceite e integracao da etapa ainda pendentes.
- Retomada WEB: revisar/integrar W05 e seus arquivos locais antes de W06.
  Nao iniciar novas funcionalidades sob o pedido atual de organizacao.
- Branch `prep-web`. Container exclusivo `stroop-web-roadmap-test` encerrado
  apos os testes; sem volume persistente. Para futuras suites PostgreSQL,
  preparar outro banco descartavel e executar sequencialmente.

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
