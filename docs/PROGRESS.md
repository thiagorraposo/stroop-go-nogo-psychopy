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

## 2026-10-16 — W12 concluida

- `summary.ts` calcula as 12 metricas apenas do principal, mediana dos hits sem
  quantizacao/ausencia null e exibicao half-even sobre float conforme Python.
  `ResultSummary.tsx` mostra precisao/RT/quatro contagens, texto descritivo,
  foco acessivel e Finalizar limpando RAM. Sem download participante/salvo ficticio.
- `stroop/domain/web_export.py`: CSV 21 colunas, nomes/iniciais mascarados,
  formulas neutralizadas, escaping, RT ja em segundos sem quantizacao e nome
  sem IDs/timestamp UTC. Recalcula classificacoes no nucleo, recusa pratica e
  principal WEB parcial; legado conserva contagem/horario sem inventar fuso.
  O adaptador profissional W14 deve reautorizar e fornecer metadados do servidor.
- Cinco fixtures Python/TypeScript verificam quatro respostas, medianas par/impar,
  sem hits, empate percentual e RT submicrossegundo. Importador real/SQLite
  descartavel receberam todos os CSVs com 16 linhas/12 metricas identicas.
- Evidencias: 133 frontend, typecheck/build; npm run test:browser passou com
  20 gerais e quatro temporais seriais Chromium/Firefox (3,5 min). Finalizar e
  historico nao restauram resultado. Preview do componente real 1440x1080
  inspecionado, sem overflow/excecoes JS. Mesmos ambientes W09; sem aceite W16.
  Regressao PostgreSQL 245 testes/29,376 s passou sem skips; seis focados CSV
  passaram apos acrescentar compatibilidade legado. compileall/pip check/diff
  aprovados. Containers/servidor de inspecao encerrados.
- Proxima acao: W13 — cliente/fluxo convite-bootstrap-start-conclusao, envio
  confirmado/retry em RAM, abortamento e expiracao, integracao real HTTPS/API/DB.
  Finalizacao local e resumo atuais nao comprovam recebimento no servidor.

## 2026-10-16 — W14 concluida

- Consulta/lista/detalhe/exportacao integradas em `api/assessments.py`, com
  application/persistencia dedicadas. Filtros fechados, limite/cursor HMAC
  vinculados a usuario/projeto/filtros, reautorizacao em cada download e
  projecoes sem nomes/iniciais. Admin sem vinculo nao acessa dados.
- `API_READ_DATABASE_URL` separado, sem fallback, papel SELECT nas colunas de
  REQUIRED_COLUMNS (sem acesso a participant_name/initials/source_file) e
  transacao REPEATABLE READ READ ONLY. Auth/rate limits usam conexao propria.
  Ausencia de configuracao/schema produz erro fechado 503.
- Migration 0007 aditiva inicia mapa legado vazio, sem automapeamento por
  codigo; somente operacao autorizada vincula. ADR-003 registra a protecao.
  Desativacao de mapa/projeto/vinculo bloqueia leitura; rotulos historicos longos
  conservados. Legado sem fuso nao recebe UTC ficticio; avaliador nao associado
  recebe ID null/CSV LEGADO_NAO_MAPEADO, sem divulgar seu texto original.
- Stroop recalcula 12 metricas/classificacoes pelo nucleo sobre tentativas,
  sem modificar banco. Instrumentos genericos mantem metricas/proveniencia
  propria e nenhuma tentativa inventada; CSV 21 campos restrito ao seu contrato.
  Parser/serializer W12 compartilham o mesmo caminho da exportacao autorizada.
- Evidencias: regressao integral 257 testes PostgreSQL/42,181 s, zero skips;
  apos ajuste do mapa longo/credencial por coluna, 23 focados de consulta e
  migrations, mais 12 de consulta com grants minimos, aprovados. Teste de cursor
  entre projetos tambem aprovado. compileall/pip check/diff aprovados.
  Testes comprovam UPDATE recusado, colunas pessoais inacessiveis, READ ONLY
  mesmo com DSN privilegiado, reautorizacao, schema ausente, bloqueio/expiracao,
  isolamento de escopo nas consultas, formulas e paridade com recibo.
- Subagente inicial atingiu cota; principal concluiu a frente. Container de teste
  encerrado; nenhuma acao na VPS, push ou deploy. API README/contrato/mapa e
  AGENTS da API alinhados. Alteracao raiz AGENTS preexistente fora do commit.
- Proxima acao exata: iniciar W13, cliente participante e integracao real sob
  HTTPS local sintetico; conectar convite/bootstrap/start/conclusao/abortamento,
  confirmar recibo e reenvio em RAM, sem usar storage JS ou repetir principal.

## W13 — Concluida

- W14 salva em `e8b01eb`, W12 em `07a465a`, W11 em `27b9a82`, W10 em `8d9e0a3`.
  Worktree inicial seguinte somente AGENTS raiz preexistente, preservado.
- Novos `web/src/api/participant.ts` e `.test.ts` usam transporte compartilhado
  de `client.ts`: caminhos fixos, cookies same-origin/HttpOnly, CSRF RAM,
  timeout/cancelamento e erros fechados. Bootstrap verifica snapshot e fontes
  inteiros, preserva ordem API; running nunca oferece retomada; recibo valida
  versoes, IDs e contagens. Payload completo imutavel/whitelist conserva RT e
  corpo identico em retries. Redeem nao usa URL/storage para segredo.
- Controlador RAM e ParticipantFlow integrados: convite, ordem da API, start
  confirmado antes do motor, payload imutavel, recuperacao GET/reenvio manual,
  expiracao e descarte. Native Web Locks impede motores concorrentes entre abas;
  pagehide descarta estado e bfcache exige recarregar, sem retomar principal.
- Logout com Origin/CSRF rotaciona hash da credencial e preserva completed.
  GET completed fornece CSRF/prazo em headers sem alterar recibo JSON.
  Finalizar aguarda confirmacao do logout antes de limpar a interface.
- Evidencias: 157 testes frontend/typecheck/build e 26 testes isolados de
  navegador aprovados; 22 testes backend focados com PostgreSQL real aprovados.
  Quatro smoke tests HTTPS reais Chromium/Firefox aprovados: cookie seguro,
  expiracao e refresh de running sem avaliacao parcial ou retomada.
- Harness web/e2e/integrated usa API/banco reais com TLS local efemero; exige
  TEST_DATABASE_URL com database stroop_etapa4_test_*, nunca .env. Profissional
  sintetico preparado localmente; nao comprova OIDC externo ou TLS de producao.
- Suite HTTPS ampliada aprovada: seis testes em 3 minutos, Chromium/Firefox.
  Principal real de 60 segundos, perda da resposta depois do commit, recuperacao
  de recibo sem duplicacao (1 avaliacao/16 tentativas/12 metricas), consulta
  profissional autorizada e logout preservando resultado e invalidando cookie.
- Mais dois testes HTTPS aprovados: falha antes do commit, reenvio manual
  com corpo identico e duplo clique; uma unica avaliacao nos dois navegadores.
  Harness ajustado para SO_REUSEADDR na verificacao de portas apos encerramento.
- Regressao final backend: 262 testes/39,645 s, sem skips, PostgreSQL real.
  Frontend: 157 testes aprovados novamente. Build/typecheck aprovados no harness.
- Suite final `npm run test:browser`: 26 gerais/40,8 s e quatro temporais/3,5 min
  aprovados nos dois navegadores. Links locais 31/31 e diff check aprovados.
  Timeout coberto no transporte (inclusive leitura do corpo) e controlador;
  cenarios reais de rede confirmam recuperacao e reenvio sem repetir motor.
- Criterios W13 satisfeitos: confirmacao somente apos servidor, sem duplicacao,
  interrupcao sem parcial, expiracao/refresh/limpeza e duplo clique verificados.
  Sem alegacao de medicao fisica W16, OIDC externo ou infraestrutura de producao.
- Proxima acao: salvar commit local W13 preservando AGENTS raiz; iniciar W15,
  cliente profissional de consultas/cards/graficos/detalhe/exportacao W14.

## W15 — Concluida

- W13 salva em def93c5: 262 testes Python, 157 frontend, 30 browser e oito
  HTTPS reais aprovados. AGENTS raiz preexistente permanece fora do commit.
- Implementados cliente profissional fechado (26 testes novos) e painel
  conectado a projetos/consultas/detalhe/CSV W14. Carrega todas as paginas antes
  de agregar, cancela requisicoes obsoletas e rejeita IDs/cursor repetidos.
  Filtros participante/visita no servidor; instrumento/plataforma na selecao
  carregada, sem misturar metricas de instrumentos distintos.
- Cards e graficos descritivos: datas, precisao por visita, distribuicao RT,
  omissoes/comissoes; evolucao por visita ao filtrar participante. Detalhe com
  metricas/tentativas e exportacao reautorizada. Streamlit intacto.
- Tres testes de agregacao aprovados contra valores das fixtures Python;
  ausencia de hits excluida da mediana, datas legadas sem conversao ficticia.
  Typecheck/build aprovados. Suite frontend 187/187; Streamlit 20/20, sem skips.
  Subagente cliente concluiu; navegador encontrou foco Chromium antes do commit
  DOM; corrigido com efeito apos montar detalhe. Dashboard/navegacao 28/28
  aprovados apos correcao; teste redundante de prazo sera removido.
- Area profissional limpa RAM na expiracao/pagehide e revalida BFCache. Teste
  de prazo usa clock controlado somente na area profissional, sem alterar o
  motor experimental. Fixture antiga de perfil agora usa prazo futuro relativo.
- Subagente navegador adicionou testes HTTPS reais com importacao CSVgolden,
  mapa legado explicito e perfis reais sinteticos; revisao identifica que admin
  lista projetos globais mas consulta exige membership, mantendo regra W03.
- Evidencia final: 40/40 gerais Chromium/Firefox em 46,9 s; 6/6 HTTPS reais em
  17,1 s por consulta/importacao/administracao. API/PostgreSQL, importacao pelo
  nucleo, mapa legado explicito, valores, 16 tentativas, CSV mascarado e bloqueio
  apos revogacao comprovados. Sem mocks na integracao real. Browser timing W13
  permanece evidencia dos motores inalterados, sem reexecutar artificialmente.
- Frontend 187/187, typecheck/build e Streamlit20/20 aprovados. Links27/27 e
  diff check aprovados. Screenshots desktop/mobile390px sinteticos em /tmp
  inspecionados, sem overflow de pagina; tabelas possuem scroll proprio.
- README registra limites explicitos do MVP e coexistencia Streamlit; mapa
  estrutural alinhado. Sem dependencias novas, push, deploy ou dados reais.
- Proxima acao: commit local W15 preservando AGENTS raiz; iniciar W16 com matriz
  e protocolo de evidencias. Ausencia de equipamento/manual impede homologacao
  fisica, mas nao bloqueia revisao de seguranca W17 e automacao W18.

## W16 pendente / W17–W20 concluidas / homologacao aguarda ambiente

- Commits: W15 4d539f9, paridade fd212a9, W17 8bdeab2, CI721c86c e fixYAML
  3b20144. AGENTS raiz preexistente preservado fora dos commits.
- W16: VALIDACAO_WEB registra matriz/protocolo sem conceder aceite; faltam
  equipamento de referencia e dez pilotos por ambiente. Pergunta assincrona
  sobre sistema/navegador/monitor/Hz/teclado enviada, ainda sem resposta.
- W17: seguranca API/CSP, cardinalidade de limites, nonce e framing corrigidos;
  urllib3 2.8.0 nos dois locks/diretas; imagem dashboard reconstruida/smokeOK.
- W18: CIall processo70771 terminou com codigo0 no checkout sparse limpo
  /tmp/stroop-web-ci-721c86c. Python284/50,302s sem skips, frontend188,
  typecheck/build, 40browsergerais/49,8s, quatro temporais/3,5min e HTTPS18/6,9min
  aprovados. Audits npm/Python sem achados; scanner248 e falsoPAT confirmados.
  Actionlint1.7.7 e SHAs das actions conferidos. Sem push/GitHub hospedado.
- Worktree isolada sem data/database/.env, venv/node_modules proprios, ainda
  limpa ao final. Container proprio CI stroop-web-ci-721c86c foi encerrado.
  Container anterior stroop-web-test/32781 permanece disponivel para testes
  sinteticos futuros, banco stroop_etapa4_test_w13. Nenhum servico real acessado.
- Previa do usuario: http://127.0.0.1:4173, processo67560, frontend apenas,
  HTTP200 confirmado; preservar. Testes isolados usam4273; HTTPS4373/API4381.
- W18 aceite documental em 8ed8611, scanner ampliado em84a8963.
- W19: Dockerfiles API/proxy e Compose isolado construidos/validados. Secrets
  *_FILE externos, somente proxy publica portas, API/proxy nao-root/RO/nocaps,
  jobs migrate/provision explicitos. Migration0008 oferece lock estreito de
  app_users sem UPDATE para writer; grants canonicos reader e DML minimo writer.
- Python307/50s:306 passaram e fixture de upgrade antigo falhou por usar API
  nova antes0008; corrigida para SQLestado0005/snapshot. Modulo migrations11/11
  reexecutado no CI32783 aprovado. Provision7/runtime11/proxy5 passaram.
- Smoke Compose processo80853 terminou0: HTTPS/headers/Host/isolamento, grants,
  convite/coleta16tentativas, retry, consulta/CSV e persistencia apos reiniciar
  banco aprovados. Temporarios/volumes somente do smoke removidos. Corrigidas
  opcoes tmpfs YAML entre aspas; verificacao de portas via DockerPortBindings,
  pois composeport sem publicacao nao serve como criterio confiavel.
- Scanner269 passou apos trocar placeholder do exemplo Streamlit por marcador
  curto <substituir>; nenhum segredo operacional aberto. Diffcheck aprovado.
- Acesso manual entregue ao usuario: https://127.0.0.1:34647/, pilha exclusiva
  stroopw198e97815396, configuracao /tmp/stroop-web-preview-6ay1rzpw/compose.env.
  Convite exclusivamente sintetico em /tmp/stroop-web-preview-access.json e
  preview.json no diretorio externo; nao copiar codigo para docs/versionamento.
  Preservar essa pilha para usuario e preview antigo4173. Nao consumir seu convite.
  Chromium abriu welcome/orientacoes/pratica viaHTTPS sem erroJS, input presente.
- Scripts smoke_web_compose.py/preview_web.py geram apenas dados sinteticos.
  Certificado autoassinado requer excecao manual local; area equipe Google real
  nao configurada. Isso nao substitui pilotos temporais W16/homologacao W21.
- W19 commit34d2ce1 concluido. W20: monitor_web.py real retornou ready e
  somente contagens, quatro testes de falha/privacidade passaram; backup existente
  reutilizado e hardening21/21 com PostgreSQLCI32783 passou, sem skips. Regressao
  backupweb1/1 comprova servico com hifen, dump criptografado e opcoes invalidas.
- Ensaio recuperacao processo15468 terminou0: backup/restauracao isolada7,083s,
  8migrations/1coleta restauradas; integridade16tentativas/12metricas/estado
  concluido verificada, alerta durante falha de banco, candidatoimagem invalido
  e retorno a imagem aceita com contagens preservadas. Apenas recursos proprios
  do ensaio removidos; previa do usuario mantida saudavel.
- backup_postgres.py aceita --verify-web e servicoCompose comhifen; restore
  sempre recebe envvazio explicito, sem descoberta .env. ContextoDocker do
  candidato e diretorio minimo sem secrets. Runbook WEB_RECUPERACAO registra
  RPO24h/RTO4h aprovados como objetivos, grants aposrestore e rollbackcompativel.
- Scanner274 fontes sem achados; diffcheck e links operacionais aprovados.
  Docs/topologia ajustam --project-name stroop-web explicito para isolar legado.
  Nenhum push/deploy/servicoexterno acionado. AGENTS raiz permanece preexistente.
- Pendencias reais: W16 requer equipamento de referencia/dez replicas fisicas;
  W21 depende disso e ambiente alvo autorizado com capacidade medida. W22 e
  execucao do usuario; W23 depende da implantacao/aceite. Perguntas sobre hardware
  e ambiente de homologacao enviadas; nao presumir autorizacao VPS ou resultados.
- Proxima acao: commitW20 isolado, aguardar informacoes/artefatos necessarios e
  executar proxima validacao viavel sem antecipar aceite. ContainerCI
  stroop-web-ci-721c86c ativo32783/banco stroop_etapa4_test_ci; DBw13/32781 intocado.
  Preservar pilha de acesso manual e preview4173; convite sem consumo peloCodex.

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
