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

## 2026-10-16 — W08 concluida

- `api/results.py` implementa conclusao com autenticacao/CSRF/estado antes do
  schema. `stroop/domain/web_results.py` valida ordem, versoes e todos os gates
  temporais, deriva quatro respostas e reutiliza o calculo canonico. Hash
  decimal normalizado tem quatro vetores compartilhados com o futuro frontend.
- Migration 0006 adiciona `web_assessments`/`web_trial_observations`; preserva
  linhas legadas e sessoes WEB ativas. `stroop/application/web_results.py` e
  persistencia coordenam uma transacao: locks, validacao, avaliacao, 16 tentativas,
  12 metricas, proveniencia, recibo e estado completed. Retry identico retorna
  mesmo recibo; divergente recebe 409. Nenhuma gravacao parcial sobrevive a falha.
- Participantes possuem limites HMAC independentes de leitura/escrita;
  credencial desconhecida recebe 401, revogacao/escopo 404. Resultado concluido
  e preservado apos vencer seu canal participante. RT sem hits permanece 0 no
  nucleo/banco e null no HTTP; conversao que perde positividade e rejeitada.
- Evidencias: 65 testes focados; regressao integral PostgreSQL sintetico,
  240 testes aprovados em 29,019 s, zero falhas/erros/skips. `compileall`,
  `pip check` e `git diff --check` aprovados. Revisao independente sem bloqueantes.
  Integracao inclui falha real em trigger com rollback/retry, concorrencia
  identica/divergente, CSRF, estados, expiracao, schema e upgrades 0004/0005.
- Proxima acao: W09 — ler README web/ADR/protocolo, criar React/TypeScript com
  cliente HTTP, navegacao minima, testes DOM/navegador e build. Node local
  24.15.0/npm 11.16.0; nenhuma dependencia frontend instalada ainda. Alteracao
  preexistente em `AGENTS.md` permanece fora dos commits da etapa.
- W22 e implantacao futura pelo usuario; nao ha evidencia de deploy WEB concluido.

## 2026-10-16 — W09 concluida

- Base em `web/`: React/TypeScript/Vite com navegacao/historico/foco, orientacoes,
  acesso da equipe, loading/erro/retry e logout. Cliente usa endpoints relativos,
  cookies same-origin, no-store, CSRF somente em RAM, timeout/cancelamento e
  schema/erros fechados. `ExperimentHost` conserva DOM imperativo e limpa ao sair;
  jsPsych/pratica/motor ainda serao implementados nas proximas etapas.
- Versoes diretas exatas e lockfile; Node 24.15.0/npm 11.16.0 locais.
  `npm ci`, `npm run typecheck`, `npm test` (36 aprovados), `npm run build` e
  `npm run test:browser` (10 aprovados) passaram. `npm audit` nao apontou
  vulnerabilidades. Build servido por preview foi inspecionado visualmente em
  1440x1000; nenhuma excecao JavaScript observada. Servidores de teste encerrados.
- Navegadores observados: Chromium 156.0.8078.4 e Firefox 157.0 do Playwright
  1.64.1, headless no Linux Mint 22.2, binarios fallback Ubuntu 24.04.
  Rede API interceptada apenas em testes sinteticos; W13 exige integracao real.
  Sem evidencia de Windows, latencia fisica ou homologacao W16/W21 nesta etapa.
- Revisao independente sem bloqueantes; logout verifica Origin e CSRF no
  navegador. UI nao exibe ID/token, nem usa storage JS. Fontes npm/React/Vite/
  Vitest/Playwright conferidas antes da instalacao; README/AGENTS/mapa atualizados.
- Proxima acao exata: W10 — ler protocolo W01/contrato W02 e fontes de pratica;
  implementar preparo, elegibilidade do ambiente, instrucoes/contagens e pratica
  jsPsych com teclado/foco/feedback, sem gravar treino como resultado oficial.

## 2026-10-16 — W10 concluida

- Pratica real jsPsych 8.3.0: preparo desktop/teclado/foco, regra, contagem,
  quatro condicoes-fonte aleatorias sem reposicao, HUD, quatro feedbacks e
  repeticao opcional sem pontuacao minima. Treino nunca integra resultado oficial;
  interrupcao descarta rodada. Nenhum dado pessoal e solicitado; metadados
  pseudonimizados da sessao serao conectados ao bootstrap na integracao W13.
- `condicoes/web_protocol.json` e snapshot unico API/frontend, extraido de W07
  com lembrete aprovado de 1500 ms. CSVs/Builder intactos. Filtro UA conservador
  recusa mobile/Safari/macOS e derivados identificados fora do MVP; nao prova
  hardware ou homologacao. Tecla mantida/repeat e eventos tardios sao ignorados.
- Evidencias: 77 testes Vitest; 18 Playwright Chromium/Firefox em 36,2 s;
  typecheck/build/npm ci e audit (zero vulnerabilidades) aprovados. Preview
  1440x1000 inspecionado, sem excecoes JS. Mesmos navegadores/SO de W09;
  sem validacao Windows/latencia fisica. Backend: 240 testes PostgreSQL 17.6
  em 28,934 s, zero skips; compileall/pip check aprovados. Container sintetico
  removido. Observacao do feedback em e2e usa polling por quadro para nao perder
  sua fase de 500 ms; duracoes do produto nao foram ampliadas para o teste.
- Proxima acao exata: W11 — implementar bloco principal monotono de 16 tentativas,
  duracao nominal de 60 s, sem feedback; ordem/observacoes temporais e filtros
  de resposta devem satisfazer contrato W02 e politica D2/D5/D6. Integracao de
  ordem persistida/HTTP permanece W13. Preservar alteracao raiz AGENTS preexistente.

## 2026-10-16 — W11 concluida

- Motor principal jsPsych em `web/src/experiment/main{,-engine,.test}.ts`:
  ordem explicitamente recebida e conferida contra as 16 fontes, 8 Go/8 No-Go,
  dez cores, contagem, calibracao de 30 intervalos rAF e origem monotona unica.
  Registra inicio/onset/offset/fim/primeira Space; nao usa rede/relogio civil.
  Gates D5/D6 validam todos os registros antes do callback completo; foco,
  ocultacao, Escape, fechamento e falha temporal descartam a serie.
- UI conecta pratica completa sem limiar ao principal, permite repetir treino,
  mantem HUD/cronometro sem feedback principal e bloqueia retomada interrompida.
  Resultado fica em RAM, sem afirmar recebimento no servidor. W13 substituira
  ordem local pela persistida e conectara metadados/credencial da sessao.
- Ensaios iniciais com agendamento sempre apos o alvo abortaram no gate,
  inclusive Firefox isolado. Corrigido para quadro mais proximo do alvo nominal
  (meio periodo antes), sem relaxar gates ou fabricar/quantizar timestamps.
  Teste cobre observacao adiantada, continuidade e rejeicao acima da tolerancia.
- Evidencias finais: npm ci sem vulnerabilidades; 120 testes Vitest,
  typecheck/build e diff aprovados. 20 browser navegacao/pratica passaram;
  apos ajuste, quatro @timing seriais sem trace passaram em 3,5 min, incluindo
  pratica + 60 s reais e Escape em Chromium/Firefox. Mesmos navegadores/SO W09.
  Nao certifica latencia fisica, Windows ou homologacao W16/W21. Backend nao foi
  alterado nesta etapa; regressao PostgreSQL 240 testes consta na W10.
- Proxima acao: W12 — resumo apenas principal, mediana dos hits/ausencia e
  arredondamentos aprovados; serializer Python CSV 21 campos para uso autorizado
  W14, fixtures Python/TypeScript e importacao sintetica real. Nao oferecer
  download participante: W03 reserva exportacao a profissionais vinculados.

## W14 — Trabalho paralelo preservado, sem aceite

- Dependencias W06/W08 atendidas. Subagente atingiu cota e deixou somente
  `stroop/persistence/web_assessments.py`, nao integrado/validado. Principal
  adicionou `APIConfig.read_database_url`/`API_READ_DATABASE_URL` opcional, sem
  fallback para escrita. Nenhuma rota nova esta registrada.
- Revisao encontrou associacao insegura do legado por `a.project=p.code`.
  Principal substituiu por mapa explicito controlado pela operacao, migration
  0007 inicialmente vazia, e ADR-003. Ainda falta validar query/migration,
  colisao de codigo, mapa/desativacao e acesso cruzado com papel PostgreSQL
  realmente somente leitura. Nao acessar coletas reais nem preencher mapa.
- Arquivos W14 ainda fora de commit: `api/config.py`, `api/README.md`,
  `stroop/persistence/web_assessments.py`, migration 0007, ADR-003,
  contrato API e indice docs. Faltam application/router, serializer W12,
  integracao create_app e testes PostgreSQL. Preservar no checkout.
- `AGENTS.md` raiz continua alteracao preexistente e fora dos commits.

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
  exigindo autorizacao especifica; W22 sera executada pelo usuario.
- Medicoes W16/homologacao alvo, textos/configuracoes especificas da pesquisa
  e retencao definitiva nao foram evidenciados pela aprovacao; permanecem
  entregas futuras, sem bloquear testes locais com dados sinteticos.
