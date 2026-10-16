# Progresso e retomada

Estado formal/aceite no [roadmap WEB](ROADMAP_WEB.md), evidencias no
[registro](REGISTRO_DE_ALTERACOES.md), arquitetura nos ADRs.

## 2026-10-16 — Decisoes aprovadas; implementacao retomada

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
- Proxima acao: concluir contrato W02, depois W03 e base HTTP W05 em paralelo
  quando suas dependencias estiverem concluidas. Nao repetir perguntas ja
  respondidas; implementar as decisoes aprovadas e validar cada etapa.
- Medicoes W16/homologacao alvo, textos/configuracoes especificas da pesquisa
  e retencao definitiva nao foram evidenciados pela aprovacao; permanecem
  entregas futuras, sem bloquear testes locais com dados sinteticos.
- Branch `prep-web`, inicialmente limpa. PostgreSQL sintetico exclusivo vivo:
  container `stroop-web-roadmap-test`, banco `stroop_etapa4_test_web_roadmap`,
  porta local 32772; nenhum volume operacional. Nao executar suites de banco
  em paralelo; testes recriam schema. Encerrar esse container ao final.
