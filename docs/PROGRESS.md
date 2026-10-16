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
- Container PostgreSQL temporario da validacao W06 foi encerrado sem volume
  persistente. O registro especifico e os testes aprovados estao em W06 abaixo.

## 2026-10-16 — W06 autenticacao HTTP concluida

- Login Google OIDC em `api/auth.py` usa state, nonce, PKCE S256 e cookie
  temporario de uso unico; callback valida cookie/transacao e nao aceita destino
  externo. `api/google_oidc.py` valida assinatura RS256, emissor, audiencia,
  nonce, expiracao e `azp` com `google-auth`; rede externa tem timeout de cinco
  segundos, endpoints fixados e respostas limitadas.
- Sessao profissional opaca de 256 bits, cookie `__Host-` Secure/HttpOnly/Lax,
  hash no PostgreSQL e duracao limitada a oito horas e ao ID token. `/auth/me`
  revalida cadastro, bloqueio e perfil; logout exige Origin/CSRF e revoga sessao.
  Login limita chamadas por IP em janela configuravel, guardando apenas HMAC.
- `dashboard/auth.py` preserva a fachada do Streamlit; regras de identidade e
  autorizacao ficam em `stroop/`, SQL em persistencia. Migration 0004 e locks
  API atualizados sem modificar as migrations anteriores.
- Evidencia: teste Google OIDC usa RSA/certificado sintetico e exercita o
  verificador real (assinatura, issuer, audience, nonce, exp e azp); integracao
  real cobre state one-use, cookies/hash, 8h, bloqueio, perfil insuficiente,
  CSRF/logout, limite de login e migration. Suite integral PostgreSQL: 201
  testes aprovados, zero falhas/erros/skips; focused W06/API 37 aprovados;
  `pip check` sem dependencias quebradas.
- Delimitacao por dependencia: acesso cruzado de projetos fica para W14, quando
  a API expuser consultas de objetos; W06 nao possui essa superficie HTTP.
- Proxima acao registrada a conclusao de W06: iniciar W07 — criacao e ciclo
  de vida de sessao participante; ler contrato W02/W03 antes de persistir.

## 2026-10-16 — W07 concluida

- Implementados em `api/sessions.py`, `stroop/application/web_sessions.py` e
  `stroop/persistence/web_sessions.py`: projetos/vinculos administrativos,
  convites unicos de 24h, resgate atomico, sessao participante de 30min,
  bootstrap com condicoes/paleta/protocolo, ordem principal persistida, inicio
  idempotente, abortamento fechado e revogacao. API guarda hashes de convite e
  sessao; rate limit de resgate guarda HMAC do endereco.
- Migration aditiva 0005 cria tabelas WEB sem alterar tabelas de avaliacao; modo
  de projeto e restrito a `synthetic`. Revalidacao verifica projeto, membro,
  perfil e emissor em cada operacao participante. Gestao e convites exigem
  autenticacao profissional, escopo e CSRF nas escritas.
- Revisao independente identificou e levou a correcoes: rate limits configuraveis
  para rotas profissionais (120 leituras/60 escritas por minuto, armazenando HMAC
  da credencial), `user_id` opaco derivado de `iss` + `sub`, e 404 para projeto
  fora do escopo antes de revelar permissao. A consulta com vinculo sem papel
  suficiente recebe 403. Contrato W02 e testes estao alinhados.
- Evidencias finais: suite focada 43 testes e suite integral 210 testes aprovados
  no PostgreSQL sintetico descartavel, sem skips; `compileall`, `pip check` e
  `git diff --check` aprovados. Abrange migration vazia/upgrade, concorrencia,
  expiracao, revogacao, rate limits, identidade e autorizacao. Container de teste
  encerrado apos validacao. W07 foi registrada e commitada localmente.
- Proxima acao exata: iniciar W08 — conclusao e recebimento de resultados;
  ler ficha W08, contrato HTTP, modelo de dados e caminhos de calculo canonicos.

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
