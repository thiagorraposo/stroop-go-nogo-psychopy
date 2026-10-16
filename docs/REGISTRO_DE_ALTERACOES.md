# Registro de alteracoes

Este arquivo preserva fatos datados; nao define estado ou aceite vigente.
Consulte o [backlog canonico](legado/Projeto%20Stroop%20Test.md).

O estado da nova versao web e mantido separadamente no
[roadmap WEB](ROADMAP_WEB.md); os registros abaixo sao evidencias datadas.

## 2026-10-16 — W18: pipeline reproduzivel e falhas bloqueantes

- `ci`: workflow sem deploy, actions fixadas por SHA, PostgreSQL17.6/tmpfs e
  runner com secrets/dependencias, Python sem skips, frontend e navegador real.
  Checkout sparse antecede materializacao; sem copiar dados historicos/.env.
- `test`: CIall aprovado em checkout limpo: 284 Python, 188 frontend, 40 browser
  gerais, quatro temporais e 18 HTTPS reais. Build/typecheck, Gitleaks248,
  falsoPAT controlado e audits npm/Python aprovados; nenhum secret impresso.
- `fix`: discovery compativel com tests sem __init__, selftest exige finding
  estruturado e erroinfra falha; porta do job em contexto GitHub valido.
  Actionlint e revisoes oficiais das actions confirmados. Sem execucao remota.
- `docs`: comandos/isolamento/limites em desenvolvimento/CI_WEB.md. Previa4173
  preservada; container CI encerrado, sem push/deploy ou dados reais.

## 2026-10-16 — W17: seguranca integrada e preparacao do piloto W16

- `fix`: headers seguros inclusive erros/CSV, framing ambiguo recusado, nonce
  OIDCUnicode fechado e cookies inventados sem criar contadores no banco.
- `security`: CSP de pagina estrita, sem inline/eval, em baseline compartilhada
  com proxy sintetico; script inline/conexao alheia bloqueados, pratica e
  principal preservados em Chromium/Firefox. Proxy de producao continua W19.
- `security`: urllib3 2.8.0 nas diretas/locks API e dashboard corrige tres
  advisories detectados pela auditoria. Fonte: [release oficial](https://github.com/urllib3/urllib3/releases/tag/2.8.0).
- `test`: 284 Python sem skips, 188 frontend, HTTPS14 apos hardening, CSP4 e
  painel6 aprovados; npm/Python audits sem achados, Gitleaks244fontes e falha
  controlada sem imprimir credenciais. Imagem dashboard reconstruida/smokeOK.
- `docs`: threat model atualizado; VALIDACAO_WEB registra matriz/procedimento,
  mantendo W16 pendente dos pilotos no equipamento de referencia, sem inventar
  medicoes. Previa local4173 preservada; nenhum deploy ou dado real.

## 2026-10-16 — Correcao de arredondamento do painel WEB

- `fix`: exibicao profissional reutiliza half-even Python do resumo W12,
  incluindo valores negativos de outros instrumentos. 56,25% com uma casa
  aparece 56,2%, como no Streamlit, sem alterar numeros crus ou formulas.
- `test`: 188 frontend e seis HTTPS reais de painel sob CSP estrita aprovados,
  incluindo empate56.25 e CSV/detalhe/revogacao por perfil.

## 2026-10-16 — W15: painel profissional integrado

- `feat`: filtros/projetos autorizados, conjunto paginado completo, cards e
  graficos descritivos por instrumento/plataforma, detalhe e CSV reautorizado.
  Sem hits permanece ausente; instrumentos adicionais nao recebem formulas
  Stroop. Limpeza na expiracao/pagehide e revalidacao de BFCache.
- `fix`: foco do detalhe aplicado apos commit DOM para navegacao por teclado;
  paginas repetidas falham sem totais inflados ou parciais.
- `test`: 187 frontend, 40 browser gerais, seis HTTPS/API/PostgreSQL reais por
  perfil e 20 regressao Streamlit aprovados; paridade Python, CSV mascarado,
  revogacao, teclado e viewport390px verificados. Build/typecheck/links/diff OK.
- `docs`: limites do MVP explicitos no README; operacao Streamlit preservada,
  sem alteracao do legado, dependencia adicional ou deploy.

## 2026-10-16 — W13: sessao participante integrada

- `feat`: convite e bootstrap real, ordem do servidor, start confirmado antes
  do motor, payload imutavel em RAM, recuperacao de recibo e reenvio manual.
  Mensagem de recebido depende da confirmacao real; nenhuma retomada de running.
- `security`: Web Locks entre abas, descarte em pagehide, expiracao e logout
  HttpOnly com invalidacao no banco, sem apagar resultados. Nenhum storage JS.
- `test`: oito testes HTTPS reais Chromium/Firefox com PostgreSQL, incluindo
  principal completo, perda de resposta apos commit e falha antes da gravacao,
  reenvio identico, duplo clique, expiracao, refresh e limpeza de cookie.
  Regressao Python 262 testes sem skips e frontend 157 aprovados. Validacao
  temporal fisica/homologacao permanece em W16, sem inferencia de equivalencia.

## 2026-10-16 — W14: consulta profissional e exportacao autorizada

- `feat`: lista/detalhe/CSV sob projeto e sessao profissional, filtros fechados,
  cursor HMAC, reautorizacao e recalculo Stroop pelo nucleo. Outros instrumentos
  mantem metricas/identidade propria; nao recebem tentativas ou CSV ficticios.
- `security`: credencial SELECT por coluna e transacao READ ONLY, sem fallback;
  nomes/iniciais inacessiveis a essa credencial e ausentes do JSON. Migration
  0007/ADR-003 exigem mapa operacional explicito para legado, sem heranca por nome.
- `test`: 257 testes integrais e validacoes focadas finais de consulta/migrations
  aprovados no PostgreSQL sintetico; grants minimos, acesso cruzado, colisoes,
  revogacoes, schema, paginacao e exportacao verificados. Sem alteracao de coletas
  existentes ou aplicacao de grants/migrations na VPS.

## 2026-10-16 — W12: resumo e CSV compativel

- `feat`: resumo principal com precisao, mediana dos hits e quatro respostas;
  ausencia de hits permanece `—`, exibicao segue Python e Finalizar descarta RAM.
- `feat`: serializer Python de 21 colunas para uso profissional autorizado,
  mascaramento nome/iniciais, escaping/formulas, RT em segundos sem quantizacao
  e nome seguro. Sem exportacao participante; rota profissional pertence a W14.
- `test`: cinco fixtures compartilhadas Python/TypeScript e importacao SQLite
  real com paridade das 12 metricas. 133 frontend, 24 browser, tipos/build e
  preview visual aprovados. Regressao PostgreSQL 245 testes sem skips e seis
  focados CSV aprovados; nao substitui homologacao ou envio real W13.

## 2026-10-16 — W11: bloco principal WEB

- `feat`: motor jsPsych com 16 condicoes sem reposicao, ordem explicita,
  calibracao rAF, origem monotona, HUD e registro observado das transicoes e
  primeira resposta valida. Nenhuma resposta abrevia estimulo; interrupcoes
  invalidam a serie inteira. UI conecta pratica e principal local em RAM.
- `fix`: agendamento pelo quadro mais proximo usa tolerancia simetrica aprovada,
  mantendo gates absolutos/duracao, timestamps reais e RT exclusivo. Ensaios
  temporais rodam em serie sem trace para reduzir interferencia do proprio teste.
- `test`: 120 testes logica/DOM; 20 browser gerais e quatro temporais reais
  Chromium/Firefox aprovados. Typecheck/build/npm ci/diff aprovados; sem alegar
  homologacao fisica ou envio confirmado pela API, reservado a outras etapas.

## 2026-10-16 — W10: preparacao e pratica jsPsych

- `feat`: ambiente Windows/Linux e familias aprovadas, confirmacao/teste de
  teclado, contagem e quatro tentativas sem reposicao com feedback, HUD e
  repeticao opcional. Pressao de navegacao/tecla mantida nao responde; foco,
  visibilidade, Escape e fechamento descartam treino. Sem limiar de desempenho.
- `refactor`: snapshot aprovado extraido para `condicoes/web_protocol.json`,
  consumido pela API/frontend; CSV e Builder preservados. Lembrete de 1500 ms
  ja aprovado explicitado no snapshot, sem alterar os demais parametros.
- `test`: 77 testes frontend e 18 Chromium/Firefox; typecheck, build, npm ci,
  auditoria sem vulnerabilidades e preview visual sem excecoes aprovados.
  Regressao Python real PostgreSQL: 240 testes, zero skips; compileall/pip check
  aprovados. Evidencia nao certifica latencia fisica, Windows ou coleta real.

## 2026-10-16 — W09: base React e cliente HTTP

- `feat`: interface React/TypeScript com navegacao acessivel, historico, orientacoes,
  acesso da equipe, estados de rede e cliente HTTP seguro. Host experimental
  separa DOM imperativo do ciclo React; ainda sem execucao do experimento.
- `build`: Vite, TypeScript, Vitest e Playwright com versoes exatas/lockfile;
  comandos e fronteiras documentados. Artefatos npm/build/traces ignorados.
- `test`: 36 testes de logica/DOM e 10 em Chromium/Firefox aprovados; typecheck,
  build, instalacao limpa e auditoria aprovados. Preview visual sem excecoes.
  Rede API sintetica nos testes nao substitui integracao real ou validacao temporal.

## 2026-10-16 — W08: conclusao transacional e resultados WEB

- `feat`: conclusao valida protocolo, ordem persistida, temporalidade e RT;
  deriva respostas e recalcula metricas no nucleo, sem aceitar metricas do cliente.
  Migration aditiva 0006 vincula sessao/avaliacao e conserva proveniencia WEB,
  observacoes temporais, hash canonico e recibo, preservando o schema legado.
- `fix`: limites de participantes por HMAC sao independentes; cookie desconhecido
  recebe 401. Acesso/estado precedem schema na conclusao; expiracao do canal nao
  muda resultado completed. RT nao representavel em segundos positivos e rejeitado.
- `test`: 19 testes puros e integracao real cobrem quatro respostas, gates,
  equivalencia numerica de replay, conflito, concorrencia, rollback tardio por
  trigger e upgrades com dados/sessao em andamento. Regressao integral: 240
  testes aprovados, sem skips; compilacao, dependencias e diff aprovados.

## 2026-10-16 — W07: ciclo de sessao participante

- `feat`: migration aditiva 0005 cria projetos sinteticos, vinculos,
  convites, sessoes participantes, ordem principal persistida e limite de
  resgate. Sem migrar ou reescrever `assessments`, metricas ou tentativas.
- `feat`: API implementa gestao de projetos/vinculos, convite com segredo
  aleatorio exibido uma vez e hash no banco, resgate atomicamente one-use,
  cookie participante separado, bootstrap, start idempotente, abortamento e
  revogacao. Valida origem/CSRF, escopo, perfil, estado, prazos absolutos e
  limites configuraveis; ordem de 16 condicoes usa as fontes/paleta oficiais.
  Projetos estao restritos a `synthetic`; coleta real continua desabilitada.
- `security`: limites configuraveis de leitura/escrita por credencial profissional
  armazenam somente HMAC; `user_id` opaco preserva a identidade composta `iss` +
  `sub`; convite desconhecido ou fora do projeto retorna 404 antes da permissao.
- `test`: PostgreSQL descartavel valida migration vazia e upgrade com dados
  legados preservados, concorrencia de resgate, autorizacao negativa,
  identificadores, ordem fixa, start/retry/conflito, abortamento, expiracao,
  revogacao e rate limit. Resultados detalhados em `PROGRESS.md`.

## 2026-10-16 — Documentacao organizada por assunto

- `docs`: 37 documentos agrupados em `experimento/`, `dados/`, `seguranca/`,
  `operacao/`, `desenvolvimento/` (incluindo prompts) e `legado/`.
  ADRs continuam em `arquitetura/`; roadmap, progresso, registro e mapa
  continuam na raiz. Criado [indice](README.md), atualizado mapa e simplificada
  a listagem da raiz. Backlog legado continua vigente para seu fluxo.
- `compat`: referencias atuais de Markdown/AGENTS atualizadas. Integridade
  dos 37 documentos conferida contra snapshot anterior: apenas referencias
  alteradas. Caminhos textuais historicos preservados em registros datados.
  Nenhuma fonte executavel existente, condicao, launcher, schema, migration,
  dependencia ou configuracao de infraestrutura alterada por esta unidade.
- `test`: caminho documental corrigido em `test_hardening_producao.py`,
  mantendo assercoes. Suite integral: 189 testes aprovados em 5,651 s,
  zero falhas/erros/skips, com PostgreSQL sintetico descartavel; 240 links
  locais validos, revisao independente e `git diff --check` aprovados.
  Container exclusivo de testes encerrado sem volume persistente.
- `scope`: implementacao W05 ja em andamento preservada fora do commit de
  organizacao. Nenhuma nova etapa iniciada; W05 nao recebeu aceite antecipado.

## 2026-10-16 — W05: base HTTP validada

- `feat`: criada factory `api.main:create_app`, configuracao obrigatoria
  (PostgreSQL, origem HTTPS e ambiente), schemas estritos, health/readiness
  e fronteira ASGI com limite real de 64 KiB, rejeicao de JSON inseguro,
  erros de formato fixo e logs sem payload/traceback. Readiness e somente
  leitura, exige conjunto exato de migrations e timeout limitado. Sem rotas
  de coleta ou autenticacao; dependencias API fixadas em arquivos proprios.
- `test`: suite integral com PostgreSQL descartavel: 189 testes aprovados,
  zero falhas/erros/skips. Integracao real aplicou migrations na fixture e
  confirmou que readiness nao alterou migrations nem contagens de tabelas.
  `compileall`, `pip check` e `git diff --check` aprovados.
- `test`: processo real Uvicorn iniciado em loopback, sem access log;
  `/health/live` e `/health/ready` retornaram 200, `Cache-Control: no-store`
  e request IDs; Host divergente retornou 422. A configuracao apontou apenas
  ao banco sintetico temporario. Revisao independente sem defeitos criticos.
- `scope`: W05 concluida; segue W06 para OIDC e autorizacao. Sem credenciais,
  migrations, rotas de pesquisa, servico de producao ou coleta real.

## 2026-10-16 — W06: autenticacao e autorizacao HTTP

- `feat`: adicionados login/callback OIDC Google com state, nonce, PKCE S256,
  endpoints de provedor restritos, verificacao de assinatura RS256, emissor,
  audiencia, nonce, `azp` e expiracao; callback usa destino local fixo e nao
  expõe tokens ou valores da query.
- `feat`: adicionada sessao profissional opaca, cookie `__Host-` seguro,
  persistencia somente do hash, limite absoluto de oito horas limitado ao ID
  token, `/auth/me`, logout com Origin/CSRF, revalidacao de cadastro/perfil e
  rate limit de login configuravel por IP sem guardar endereco bruto. Fachada
  `dashboard/auth.py` preserva imports existentes; migration 0004 e lock API.
- `test`: certificados RSA sintéticos exercitam o verificador real do
  `google-auth`, inclusive assinatura inválida, issuer, audience, token vencido,
  nonce e `azp`. Integração PostgreSQL descartável valida transação one-use,
  hash de sessão, bloqueio, perfil insuficiente, limite e logout. Suite integral
  com banco temporário: 201 testes aprovados, sem falhas, erros ou skips;
  `pip check` aprovado.
- `scope`: W06 concluída. Acesso entre projetos é validado em W14, quando as
  rotas de consulta estiverem implementadas; não existe endpoint equivalente
  nesta etapa. Nenhuma credencial real, dado de pesquisa, push ou deploy foi usado.

## 2026-10-16 — W03: acesso e dados WEB especificados

- `docs`: criado `ACESSO_WEB.md` com matriz de perfis/projeto, dados permitidos
  e finalidade de cada campo. Administracao global de vinculos nao concede
  acesso automatico a pesquisa; criacao de convites, consulta e exportacao
  exigem vinculo inclusive para administrador. Revogacao/bloqueio revalidam
  tambem a autorizacao de convites/sessoes participantes ainda ativos.
- `docs`: threat model e tratamento de dados recebem extensoes WEB, preservando
  integralmente o historico anterior. Documentados codigo vazado, replay,
  concorrencia, expiracao, interrupcao, reenvio em RAM e exportacao minimizada.
  Coleta real por projeto exige configuracao especifica pelo responsavel;
  desenvolvimento sintetico segue liberado, sem filtro etario novo.
- `test`: revisao dos cenarios da ficha, 16 links relativos e
  `git diff --check` aprovados. Documentos descrevem controles a implementar,
  sem atribuir aceite de autenticacao/coleta ou medicao fisica.
- `scope`: W03 concluida; W05 permanece em implementacao. Direcionamento
  posterior do usuario prioriza organizar arquivos preservando funcionamento.

## 2026-10-16 — W02: contrato HTTP e ciclo de sessao

- `docs`: especificado `CONTRATO_API_WEB.md`, com catalogo de operacoes,
  cookies/CSRF, estados, expiracao, limites, erros seguros e idempotencia por
  sessao/hash canonico. Criacao, resgate, inicio, abortamento, conclusao,
  consulta e exportacao possuem escopos e resultados definidos.
- `decision`: administrador gerencia projetos/vinculos globalmente, mas acesso
  a pesquisa/convites exige vinculo inclusive para administradores. Identidade
  do avaliador vem do servidor; cliente nao envia nome/iniciais ou metricas.
  Snapshot preserva paleta efetiva do Builder, nao hexadecimais historicos dos
  CSVs de condicoes. RT HTTP em ms e normalizado uma vez para segundos.
- `test`: seis exemplos JSON parseaveis; corpo completo com 16 tentativas,
  permutacao sem reposicao, sequencia e tempos coerentes. Sete links locais
  validos; matriz revisada de reenvio/conflito/expiracao/interrupcao/acesso
  cruzado/resultado invalido. `git diff --check` aprovado.
- `scope`: contrato nao representa rotas implementadas; W02 concluida e W03/W05
  iniciadas conforme dependencias. Start HTTP nao prova apresentacao fisica;
  nao retomar motor apos reload. Medicao W16 preservada.

## 2026-10-16 — W01 aprovada e retomada da implementacao WEB

- `decision`: usuario aprovou explicitamente os itens 1–19 da proposta da
  sessao, incluindo D1–D6 do protocolo, acesso Google/projetos, convites de uso
  unico (24 h), sessoes de 30 min, dados pseudonimizados sem nome/iniciais,
  exportacao profissional, reenvio apenas em memoria, coexistencia e autonomia
  com commits locais. Finalidade: coleta por seu grupo de pesquisa; publico
  participantes da pesquisa sem novo filtro demografico; usuario responsavel.
- `docs`: consolidadas decisoes em protocolo/metodologia. ADR-002 registra VPS
  ja adquirida e dominio existente, substituindo OCI como alvo WEB; sem acesso
  ao host, custos novos, credenciais ou deploy. Backup diario/30 geracoes e
  objetivos de perda maxima 24 h/recuperacao 4 h serao validados nas suas etapas.
- `test`: 39 testes focados aprovados (13 condicoes, 15 interface, 11 CSV),
  sem falhas/erros/skips. Revisao dos dois documentos e 14 links relativos
  aprovados; `git diff --check` aprovado. Criterio temporal aprovado e distinto
  de medicao: W16 permanece obrigatoria, sem equivalencia fisica presumida.
- `scope`: W01 concluida; W02 iniciada em seguida. Nenhuma alteracao do Builder,
  condicoes, CSV legado, formulas, dados reais ou aceitacao antecipada de W16.

## 2026-10-16 — W01: protocolo factual e decisoes pendentes

- `docs`: criado `PROTOCOLO_WEB.md` com fluxo realmente configurado no Builder,
  contagens, balanceamento, tempos/HUD, quatro respostas, casos de fronteira,
  tecla mantida, abortamento, ausencia de hits e distincao da proposta historica.
  Matriz D1–D6 apresenta recomendacoes concretas sem presumir aceite.
- `fix/docs`: exemplos de `CSV_UNIFICADO.md` tinham 20 campos e cabecalho sem
  `participant_name`; corrigidos para 21 colunas e versao local `0.2.2`, com
  dados inequivocamente sinteticos. O comando de analise agora usa o padrao
  seguro de nome com teste/timestamp. Sem alteracao do contrato ou exportador.
- `test`: 39 testes focados aprovados, zero falhas/erros/skips: 13 de condicoes
  e tempos, 15 da interface pre-pratica, 11 de CSV. Comandos de descoberta
  `test_fase3_condicoes_tempos.py`, `test_interface_pre_pratica.py` e
  `test_csv_unificado.py`; XML/loops/colunas conferidos estaticamente.
  Quatro exemplos atuais reunidos em CSV temporario foram aceitos pelo nucleo
  e `scripts/analisar_stroop.py`: quatro classificacoes, precisao 50%, mediana
  dos hits 0,512 s. Conferidos 29 links relativos nos cinco documentos desta
  unidade, sem ausencias; `git diff --check` aprovado.
- `blocker`: W01 exige decisoes explicitas do usuario sobre MVP, foco/aba,
  pratica e variante. Solicitadas tambem tolerancias temporais e fronteiras
  de teclado propostas, pois afetam aceite do protocolo. Sem resposta ate este
  registro; W01 nao concluida. W04 independente foi concluida no commit
  `cd35d78`; nenhuma outra etapa e elegivel com as dependencias atuais.
- `scope`: nenhum `.psyexp`, condicao, CSV coletado, formula, schema, versao
  experimental vigente ou dependencia alterado. Nao houve Pilot grafico,
  medicao fisica, validacao psicometrica, infraestrutura externa ou coleta real.
  As propostas WEB continuam pendentes de decisao, sem equivalencia presumida.
  Auditoria das 24 fichas confirmou ausencia de outra etapa elegivel. Containers
  sinteticos exclusivos de teste e smoke da W04 encerrados/removidos ao concluir.

## 2026-10-16 — W04: casos de uso e persistencia reutilizaveis

- `refactor`: importacao SQLite/PostgreSQL extraida para `stroop/application/`
  e SQL/conexoes/transacoes para `stroop/persistence/`. Relogio UTC compartilhado
  e erros publicos separados; CLIs delegam e reexportam nomes/assinaturas.
  Nenhuma camada nova importa scripts, dashboard ou frameworks web.
- `compat`: preservados retornos, excecoes, duplicidade, `--force`,
  `--validate-only`, lock PostgreSQL, rastreabilidade e codigos de CLI. Validadores
  distintos e caminhos do schema/migrations mantidos; sem repositorio generico.
  Comparacao AST: 12 literais SQL SQLite e seis PostgreSQL identicos ao HEAD
  anterior; hashes SHA-256 do schema e das tres migrations inalterados.
- `test`: baseline integral de 168 testes em 5,554 s; apos extracao, **173
  aprovados, zero falhas, erros ou skips**, em 5,778 s. Comando:
  `TEST_DATABASE_URL=URL_SINTETICA .venv/bin/python -m unittest discover -s tests -v`.
  Banco exclusivo `stroop_etapa4_test_web_w04`, PostgreSQL 17.6 em tmpfs,
  sem volume operacional. Logs sinteticos temporarios fora do repositorio.
- `test`: novas regressoes de reexportacao, casos de uso sem interfaces,
  SQLite sem site-packages/psycopg, CLI por modulo e rollback integral de
  `--force`. Teste anterior de rollback atualizado para falha real do SQLite;
  teste de paridade controla o relogio compartilhado em seu novo modulo.
  Suite existente cobre concorrencia, paridade integral SQLite/PostgreSQL,
  rollback, CSV imutavel, multiplos instrumentos e erros sanitizados.
- `test`: `compileall`, configuracao Compose com `.env.example`,
  `docker build --tag stroop-web-w04-dashboard --file Dockerfile.dashboard .`
  e smoke isolado aprovados. Imagem em filesystem somente leitura retornou
  health `ok`/HTTP 200 e imports validos; sem rede, validou fixture PostgreSQL
  e importou quatro tentativas/12 metricas em SQLite tmpfs. Revisao independente
  confirmou equivalencia SQLite; links locais e `git diff --check` aprovados.
  Lint/tipos autonomos nao possuem configuracao no projeto Python atual.
- `scope`: W04 depende apenas de W00 e foi executada enquanto W01 aguarda
  decisoes de produto/metodo. Nenhuma rota, frontend, dependencia, schema,
  migration, formula, coleta, dado operacional ou recurso OCI alterado.
  Arquitetura ja prevista no ADR-001, sem nova decisao de stack.

## 2026-10-16 — Regras de execucao autonoma e memoria de retomada

- `docs`: consolidadas as sete secoes solicitadas em `AGENTS.md`,
  `docs/AGENTS.md` e `tests/AGENTS.md`: inicializacao, continuidade WEB,
  coordenacao de subagentes, qualidade, contexto, Git e encerramento.
- `docs`: protocolo, comandos no roadmap e README alinhados com execucao
  continua e commits locais validados em branch de desenvolvimento. Ritmo e
  versionamento manual do legado preservados; producao e OCI dependem do usuario.
- `docs`: criado `PROGRESS.md` para retomada concisa e adicionado ao mapa.
  Mantidos `ROADMAP_WEB.md` e ADRs existentes nos papeis dos nomes genericos
  `ROADMAP.md` e `ARCHITECTURE.md`, sem duplicar estado ou decisoes.
- `test`: verificador Python ad hoc conferiu 50 destinos de links relativos
  nos nove documentos da unidade, sem ausencias. Comparacao com o HEAD comprovou
  preservacao das fichas W00–W23, estado/aceite do roadmap, protocolo legado e
  limites de dominio/seguranca. Revisao independente por subagente nao encontrou
  lacunas materiais nas sete secoes; `git diff --check` aprovado.
- `scope`: mudanca exclusivamente documental, sem alterar codigo ou ADR.
  Testes de codigo, lint, tipos, build e integracao nao se aplicam a este escopo.
  Objetivo de implementacao permanece pausado; nenhuma etapa funcional iniciada
  ou concluida por presuncao. Branch `prep-web` ja existente, inicialmente limpa.

## 2026-10-16 — Preparacao estrutural da evolucao web

- `refactor`: extraidos contratos, excecoes, validacao e metricas para
  `stroop/domain/`; leitura CSV e adaptadores para `stroop/ingestion/`.
  Removida a dependencia do registro de instrumentos no importador SQLite.
  Os modulos anteriores reexportam os nomes por compatibilidade; persistencia
  e CLIs conservam comportamento, caminhos, argumentos e codigos de saida.
- `build`: `Dockerfile.dashboard` copia o novo pacote. Nenhuma dependencia,
  imagem base, schema ou migration foi alterada.
- `docs`: criado ADR-001 de monolito modular, atualizado o mapa estrutural e
  reservado `api/` e `web/` somente com READMEs. Criado roadmap com 24 fichas
  W00–W23, objetivos, entregaveis, dependencias, aceite, validacoes e leituras.
  Instrucoes distinguem o workflow web do backlog legado e permitem uma etapa
  por sessao, sem repetir a inspecao global.
- `test`: baseline anterior de 164 testes aprovada; apos a extracao e quatro
  regressoes novas, **168 aprovados, zero falhas, erros ou skips** em 5,584 s.
  Comando: `.venv/bin/python -m unittest discover -s tests -v`, com
  `TEST_DATABASE_URL` exclusivamente em PostgreSQL 17.6 descartavel em tmpfs,
  nome `stroop_etapa4_test_web_structure` e dados sinteticos. Procedimento
  reproduzivel no roadmap; nenhum banco operacional foi consultado.
- `test`: 34 definicoes movidas/preservadas comparadas por AST com o HEAD;
  regras e constantes identicas. Testes novos protegem os imports/excecoes
  anteriores, o nucleo sem site-packages/banco/UI e as CLIs por caminho externo
  e por modulo, incluindo duplicidade e `--force` no SQLite temporario.
- `test`: configuracoes Compose de desenvolvimento, producao e restauracao
  aprovadas com exemplos ficticios; avisos existentes sobre `secrets.mode`
  ignorado fora do Swarm permanecem, sem alterar permissoes de arquivos reais.
  `docker build --tag stroop-web-structure-dashboard --file Dockerfile.dashboard .`
  aprovado; smoke com filesystem somente leitura retornou health `ok`, HTTP 200
  e imports da aplicacao validos. CLI `--validate-only` validou fixture na imagem
  sem rede. Links locais e `git diff --check` aprovados.
- `scope`: nenhuma funcionalidade web, coleta, alteracao experimental, acesso
  OCI ou deploy. Dados, secrets, PsychoPy, condicoes, dashboard, SQL e launchers
  existentes preservados. As etapas legadas 11/12 nao foram iniciadas.
  W01–W23 nao iniciadas; decisoes de protocolo/acesso/dados ficam nas fichas
  W01–W03. Containers sinteticos de verificacao removidos ao concluir.

## 2026-10-07 — Execucao do gerenciador de usuarios como modulo

- `docs`: corrigidos os comandos `bootstrap` e `recover-admin` em
  [autenticacao e permissoes](seguranca/AUTENTICACAO_E_PERMISSOES.md) para usar
  `python -m scripts.gerenciar_usuarios`; nenhuma outra ocorrencia equivalente
  foi encontrada nos arquivos pesquisados, excluindo secrets e dados locais.
- `test`: nove testes de autenticacao aprovados; ajuda dos dois subcomandos
  executada como modulo, sem conexao com banco; `git diff --check` aprovado.
- `scope`: nenhum codigo Python, banco, servico, segredo ou estado de etapa
  foi alterado.

## 2026-10-07 — Revisao do OpenSSL no proxy

- `fix`: atualizada somente a revisao fixada do pacote OpenSSL em
  `Dockerfile.proxy`, de `3.3.7-r0` para `3.3.7-r2`.
- `docs`: sincronizada a versao descrita em [hardening](operacao/HARDENING_PRODUCAO.md).
- `test`: 12 testes estaticos de producao e seis de infraestrutura aprovados;
  `git diff --check` aprovado.
- `scope`: sem build, deploy, alteracao de banco, acesso a secrets ou mudanca
  do estado das etapas.

## 2026-09-30 — Responsabilidade pelas Etapas 11 e 12

- `docs`: por decisao do usuario, o planejamento, a execucao e a validacao das
  Etapas 11 e 12 serao feitos diretamente por ele. O Codex nao as inicia com
  `continue o projeto`; podera revisar evidencias e atualizar a documentacao
  quando solicitado, sem presumir aceite.
- `docs`: alinhados AGENTS, protocolo e README; corrigida a tabela do backlog
  para refletir as conclusoes ja registradas das Etapas 9 e 10 e distinguida a
  autorizacao de leitura da tenancy da autorizacao pendente para deploy.
- `scope`: nenhum deploy, consulta autenticada OCI, validacao operacional ou
  mudanca de progresso foi executado nesta atualizacao documental.

## 2026-09-13 — Consulta pública para a Etapa 11

- `docs`: registrada em [OCI_ETAPA11.md](legado/OCI_ETAPA11.md) a consulta de
  documentação pública da Oracle sobre Always Free, `VM.Standard.A1.Flex`
  ARM64, cotas, disponibilidade, volumes e isolamento de rede.
- `docs`: a proposta mantém limites do Compose configuráveis, reserva de
  capacidade para o sistema operacional e exposição pública restrita a
  HTTP/HTTPS; PostgreSQL e dashboard continuam internos.
- `scope`: nenhuma tenancy, região, cota autenticada, domínio, certificado,
  destino externo, credencial ou recurso OCI foi acessado ou criado. A Etapa 11
  permanece não iniciada e sem crédito parcial.

## 2026-09-13 — Bloqueio de consulta autenticada OCI

- `blocker`: a autorização para leitura autenticada foi recebida, mas o
  workspace não contém OCI CLI, SDK Python ou configuração de tenancy. Nenhuma
  credencial foi solicitada, impressa ou versionada; a retomada depende de uma
  configuração local segura do OCI CLI.

## 2026-09-13 — Dashboard PostgreSQL

- `feat`: concluída a Etapa 10 com leitura operacional PostgreSQL em
  `dashboard/data_access.py`, cursor paginado, validação de schema, mensagens
  sanitizadas e transações forçadas como somente leitura.
- `feat`: adicionada `DASHBOARD_DATABASE_URL` para a credencial `dashboard_ro`,
  separada da `DATABASE_URL` de importação e da `AUTH_DATABASE_URL` de OIDC;
  SQLite permanece apenas como fallback local.
- `docs`: documentados criação da role sem escrita, grants mínimos, tamanho de
  página, migração controlada e ausência de arquivo SQLite no container.
- `test`: cinco testes de integração PostgreSQL, prova manual da role sintética
  com `GRANT SELECT`, fluxo CSV sintético → PostgreSQL → dashboard, rebuild e
  smoke Docker saudável. Suíte integral: 164 testes aprovados, zero falhas,
  erros ou skips; reinicialização preservou uma avaliação sintética; nenhuma
  coleta ou credencial real foi usada.
- `docs`: Etapa 10 marcada como concluída (87%); Etapa 11 permanece não
  iniciada. OCI, domínio, HTTPS real, destino externo e custos continuam fora
  do escopo.

## 2026-09-13 — Hardening de produção

- `feat`: concluída a Etapa 9 com perfil Compose de produção separado, imagens
  fixadas (PostgreSQL/Nginx/Python com manifestos ARM64 verificados), Nginx
  TLS-only na borda, dashboard/PostgreSQL internos, menor privilégio, limites
  configuráveis e reserva de CPU para o host Ampere A1.
- `feat`: adicionados TLS externo obrigatório sem certificado sintético em
  produção, limites de requisição/upload, headers, logs operacionais
  sanitizados, healthchecks e dependências Python travadas.
- `feat`: temporários CSV são removidos sempre; rejeições registram somente
  hash, status e código fechado. Retenção configurável remove apenas auditorias
  vencidas; dados de pesquisa não são eliminados automaticamente.
- `feat`: backup diário automatizável com AES-256-GCM, chave separada,
  checksum, rotação de 30 gerações e restauração transacional isolada para
  teste mensal.
- `docs`: registradas políticas provisórias de 30 dias para logs, 180 para
  auditoria OIDC, cinco anos para incidentes e mínimo de cinco anos após a
  pesquisa para dados pseudonimizados, condicionadas ao protocolo, pesquisador
  responsável, CEP e confirmação institucional. Documentado prazo de três
  dias úteis para comunicação de incidente relevante à ANPD e titulares,
  quando aplicável.
- `test`: 158 testes passaram anteriormente com PostgreSQL descartável e dados
  sintéticos, sem falhas, erros ou skips; nesta conclusão, 16 testes estáticos
  de hardening/criptografia e a suíte sem banco passaram (29 testes de banco
  foram corretamente pulados por ausência de conexão no sandbox). Smoke Docker
  comprovou migrações, isolamento, headers, healthcheck e recusa de certificado
  sintético em produção. Nenhum dado real ou OCI foi acessado.
- `docs`: Etapa 9 marcada como concluída (80%); Etapa 10 permanece não
  iniciada. Destino externo, domínio, certificado real e dimensionamento final
  continuam pendentes da Etapa 11.

## 2026-09-13 — Autenticacao e permissoes

- `feat`: implementado Google OIDC nativo do Streamlit com acesso somente para
  `iss` + `sub` previamente cadastrados; e-mail permanece auxiliar e nao existe
  autocadastro ou armazenamento local de senhas.
- `feat`: adicionada migration de usuarios e auditoria minima, com perfis
  `consulta`, `importacao` e `administracao`, bloqueio, revalidacao explicita de
  `exp`, cinco recusas locais por 15 minutos e preservacao da ultima conta
  administrativa ativa.
- `feat`: visualizacao, detalhe, exportacao sob demanda, importacao e gestao de
  usuarios revalidam autorizacao; areas sem permissao nao aparecem. O comando de
  upload foi preservado, mas a antiga rota HTTP sem OIDC foi removida e agora
  abre a area autenticada em `127.0.0.1`.
- `feat`: criado bootstrap unico do primeiro administrador e recuperacao
  break-glass somente para identidade existente, ambos auditados e sem imprimir
  credenciais. Secrets reais permanecem fora do Git e montados somente leitura
  no container.
- `test`: 17 testes especificos e suite integral com 138 aprovados, zero falhas,
  erros ou skips, em PostgreSQL 17.6 descartavel em tmpfs. Configuracao Docker,
  `pip check`, compilacao, 61 links relativos/externos e `git diff --check`
  aprovados. Build final e smoke confirmaram Authlib, healthcheck `ok` e HTTP
  200; nenhum login ou segredo Google real foi usado.
- `docs`: documentadas configuracao, perfis, bootstrap, bloqueio, recuperacao,
  auditoria e limites. Etapa 8 concluida em 72%; Etapa 9 nao iniciada.

## 2026-09-13 — Preparacao da Etapa 8

- `docs`: corrigida a divergencia da tabela consolidada que ainda marcava a
  Etapa 7 como pendente, apesar do estado e das evidencias canonicas de
  conclusao; Etapa 8 registrada como bloqueada por decisao, sem credito parcial.
- `test`: baseline reexecutada com PostgreSQL 17.6 descartavel em tmpfs e dados
  sinteticos: 124 aprovados, zero falhas, erros ou skips; configuracao Docker e
  `git diff --check` aprovados. Uma primeira execucao sem acesso de rede local
  teve 17 erros de conexao e foi descartada; a reexecucao autorizada passou.
- `docs`: proposta autenticacao OIDC nativa do Streamlit, autorizacao local por
  `iss` + `sub`, tres perfis no PostgreSQL, auditoria minima e upload remoto
  autenticado. Escolha do provedor/tenant, ciclo de contas, MFA e limitacao de
  login aguardam autorizacao explicita do usuario. Nenhuma migration,
  dependencia ou funcionalidade da Etapa 8 foi iniciada.

## 2026-09-13 — Múltiplos instrumentos

- `feat`: criado contrato normalizado e registro de adaptadores por
  `test_code`/`test_version`, preservando integralmente o Stroop e permitindo
  métricas sem tentativas para formatos heterogêneos.
- `feat`: adicionada a fixture e o adaptador `instrumento_sintetico_demo`,
  estritamente demonstrativo, com coexistência em SQLite e PostgreSQL sem
  mistura de métricas ou criação de `trial_results` incompatíveis.
- `feat`: dashboard passou a selecionar um instrumento por vez e adaptar cards,
  gráficos, tabela, detalhe e exportação conforme o registro visual.
- `test`: suíte integral com 124 testes aprovados, zero falhas, erros ou skips,
  usando PostgreSQL 17.6 descartável e dados sintéticos; configuração Docker,
  compilação Python e `git diff --check` aprovados.
- `docs`: documentado o contrato em `docs/MULTIPLOS_INSTRUMENTOS.md` e
  registrada a Etapa 7 como concluída, com a Etapa 8 ainda não iniciada.
- `docs`: decisão operacional desta sessão: instrumentos reais permanecem
  pendentes até confirmação de campos, unidades, fórmulas, interpretação e
  dados permitidos; nenhuma regra clínica foi inventada.

## 2026-09-13 — Upload local autorizado

- `feat`: implementada decisao autorizada pelo usuario: upload separado em
  `127.0.0.1`, um CSV UTF-8 de ate 5 MiB por envio, sem sobrescrever duplicatas,
  temporarios isolados e removidos apos processamento e eventos minimos no terminal.
- `feat`: adicionados controles de Host/Origin/token, formato e tamanho antes da
  leitura, limite de conexoes e recusa de producao. Conteudo nunca e executado
  ou servido; arquivos e erros nao revelam caminhos ou metadados nas respostas.
- `test`: 14 novos testes de upload; suite integral com 118 aprovados, zero
  falhas, erros ou skips, usando PostgreSQL 17.6 descartavel em tmpfs. Smoke HTTP
  comprovou upload, duplicidade, rejeicao e limpeza; JavaScript e Docker validados.
  Testes isolados: 14 aprovados; 35 links e `git diff --check` aprovados.
  Build e smoke do dashboard nao repetidos: imagem e dashboard preservados.
- `docs`: documentados operacao, retencao, limite de limpeza em encerramento
  forcado e UX. Etapa 6 concluida, progresso de 52%; Etapa 7 nao iniciada.
  Nenhuma mudanca em SQLite, dashboard, migrations, formulas ou dependencias;
  nenhum dado real ou OCI acessado, nenhum versionamento executado.

## 2026-09-13 — Preparacao da Etapa 6

- `docs`: inspecionados protocolo, backlog, instrucoes locais, fluxo SQLite e
  importador PostgreSQL; Git inicialmente limpo, Etapa 5 no commit `0d34ce9`.
- `test`: suite completa reexecutada com `TEST_DATABASE_URL` no PostgreSQL 17.6
  descartavel: 104 aprovados, zero falhas, erros ou skips; configuracao Docker
  com `.env.example` aprovada. Nenhum dado real acessado.
- `docs`: registrada no backlog a proposta de arquitetura local e retencao do
  upload, perguntada ao usuario na sessao e ainda sem resposta. Implementacao
  bloqueada ate aprovacao ou ajuste, conforme as regras do AGENTS.md.
  Progresso mantido em 44%; Etapas 6 e 7 sem implementacao nesta execucao.

## 2026-09-13 — Importacao CSV PostgreSQL

- `feat`: adicionada CLI separada para CSV -> PostgreSQL por `DATABASE_URL`,
  reutilizando integralmente validacao, conversoes e metricas do SQLite.
  Transacao unica, duplicidade por `assessment_id`, substituicao explicita por
  `--force`, origem/status/timestamps no schema existente e saidas sanitizadas.
- `docs`: conforme decisao anunciada no plano antes da implementacao, incluido
  `--validate-only` para conferir CSV sem conectar ou persistir. Documentados
  codigos de saida, idempotencia de efeito, bloqueio entre escritores, limites
  da validacao e possivel incerteza de confirmacao em perda de conexao no commit.
- `test`: 12 novos testes cobrem entradas validas/invalidas, paridade integral com
  SQLite, imutabilidade do CSV, duplicidade concorrente, rollback de importacao e
  de substituicao, indisponibilidade e ausencia de conteudo sensivel nas saidas.
  Suite completa: 104 aprovados, zero falhas, erros ou skips, usando PostgreSQL
  17.6 descartavel em tmpfs e dados exclusivamente sinteticos.
- `test`: comando isolado da Etapa 5 com 12 aprovados; 34 links relativos e
  `git diff --check` aprovados, com whitespace dos arquivos novos verificado.
  Configuracao Docker com `.env.example` e smoke da CLI `--validate-only`
  aprovados. Build/smoke do dashboard e persistencia de volume
  nao repetidos: infraestrutura e dashboard nao foram alterados.
- `docs`: Etapa 5 concluida; progresso de 44%. Etapa 6 nao iniciada.
  Sem alteracao no legado, schema, formulas, experimento ou dependencias; sem
  dados reais, OCI ou versionamento automatico.

## 2026-09-13 — Centralizacao documental no Codex CLI

- `docs`: identificada concorrencia entre o antigo WORKFLOW_EVOLUCAO e o backlog
  fornecido, ainda nao rastreado no Git. Os pesos e as conclusoes das etapas 1–4
  coincidiam; as entregas 6, 8, 9, 11 e 12 divergiam (API/upload/autenticacao,
  hardening e hospedagem). Por instrucao explicita do usuario, prevalece
  `Projeto Stroop Test.md`, incluindo OCI Always Free na Etapa 11.
- `docs`: identificadas exigencias antigas de prompt por etapa, VPS somente apos
  a Etapa 11 e validacao com dados reais nas fases historicas. Foram substituidas
  ou marcadas como historicas, sem autorizar dados reais ou infraestrutura futura.
- `test`: a primeira descoberta executou 92 testes com sete skips por ausencia de
  `TEST_DATABASE_URL`; isso nao foi considerado aprovacao integral. A tentativa
  seguinte encontrou bloqueio de conexao pelo sandbox; validacao retomada com
  permissao de acesso a PostgreSQL descartavel e fixtures sinteticas.


Formato: entradas incrementais com data, tipo de mudanca e resumo.

- `docs`: criado protocolo dos tres comandos e referencia obrigatoria na raiz;
  preservadas as regras anteriores dos AGENTS, com redirecionamento da fonte de
  estado. Compatibilizados READMEs, guias, template e documentos historicos.
- `test`: suite completa com `TEST_DATABASE_URL` no PostgreSQL 17.6 descartavel
  em tmpfs: 92 aprovados, zero falhas, erros ou skips. Configuracao Docker com
  `.env.example`, links relativos afetados e `git diff --check` aprovados.
  Build/smoke/persistencia nao repetidos: escopo exclusivamente Markdown.
- `docs`: etapas 1–4 preservadas como concluidas, progresso mantido em 31%,
  Etapa 5 nao iniciada e proxima acao `continue o projeto`. Nenhuma alteracao
  funcional, acesso a dados reais, OCI ou operacao de versionamento executada.

## 2026-09-01

- `feat`: concluida a Etapa 4 vigente com schema PostgreSQL versionado para avaliacoes, metricas e tentativas, executor transacional com controle de versao e migracao legada SQLite -> PostgreSQL explicita e segura.
- `test`: adicionados nove testes de schema, indices, FKs, idempotencia, rollback, validacao de origem, recusa de destino preenchido, paridade sintetica e ajuste de identities; suite total com 92 testes aprovados.
- `docs`: documentados schema, operacao das migrations e distribuicao canonica das pendencias, mantendo importacao PostgreSQL na Etapa 5 e integracao Streamlit na Etapa 10.
- `chore`: concluida a Etapa 3 vigente com containers separados para Streamlit e PostgreSQL 17.6, volume persistente, healthchecks, dependencia por saude, configuracao ficticia por ambiente e contexto de imagem sem coletas ou secrets.
- `test`: adicionadas seis regressoes da infraestrutura; build, smoke do Streamlit, saude dos servicos e persistencia de marcador sintetico apos reinicializacao foram comprovados, totalizando 83 testes aprovados.
- `docs`: documentada a operacao Docker local e preservado explicitamente o fluxo funcional SQLite ate as etapas futuras de schema, importacao e integracao PostgreSQL.
- `refactor`: concluida a Etapa 2 com separacao do dashboard em composicao Streamlit, acesso SQLite somente leitura, transformacoes puras e componentes visuais, preservando o ponto de entrada e o comportamento publico.
- `test`: adicionadas quatro verificacoes de fronteira para API compativel, direcao de dependencias sem ciclos, importacao sem iniciar Streamlit e preservacao do launcher; suite total com 77 testes aprovados.
- `docs`: otimizada a hierarquia de `AGENTS.md`, com regras duraveis na raiz e especializacoes concisas para condicoes, dashboard, documentacao, scripts e testes.
- `docs`: criado o workflow canonico de 12 etapas, sua auditoria de instrucoes, o template de prompts e o prompt da Etapa 2, sem executar a modularizacao.
- `docs`: registrada a baseline reproduzivel da Etapa 1 para o fluxo PsychoPy -> CSV -> SQLite -> Streamlit, incluindo componentes, esquema, limitacoes, integridade, contagens agregadas e procedimento validado de backup.
- `test`: confirmada a suite atual com 73 testes aprovados e adicionadas fixtures CSV inteiramente sinteticas para caso valido, coluna ausente, tipo invalido e valor fora do dominio.
- `chore`: reforcadas exclusoes de credenciais, secrets e chaves no `.gitignore`, mantendo uma excecao estreita para fixtures CSV sinteticas em `tests/fixtures/`.

## 2026-08-04

- `fix`: atualizado `setup.bat` para tentar o launcher `py -3` antes de `python` e orientar a instalacao oficial quando nenhum deles funcionar; `abrir_dashboard.bat` passa a usar diretamente o Python da `.venv`.
- `fix`: substituido o dialogo nativo de metadados por uma rotina visual responsiva em fullscreen, com campos editaveis, validacao e erro dentro da janela do PsychoPy.
- `ux`: padronizado o cursor visivel no formulario e nas telas com botao, ocultando-o somente durante tentativas Stroop.
- `test`: adicionadas regressoes para Flow, ausencia de dialogos externos, unidades `height`, validacoes, fullscreen, cursor e preservacao do CSV canonico.
- `fix`: impedido o encerramento automatico da rotina visual de formulario no primeiro frame, garantindo o preenchimento de `expInfo` antes da pratica e preservando o caminho global do CSV oficial.
- `fix`: ampliados os cartoes claros dos estimulos e ajustada a fonte das palavras na pratica e no bloco principal para evitar overflow de `AMARELO` e `VERMELHO`.
- `test`: adicionadas regressoes para geometria identica, centralizada e responsiva dos cartoes e palavras nas duas rotinas.

## 2026-08-03

- `feat`: adicionado `scripts/doctor.py` para diagnostico somente leitura do ambiente no Windows, Linux e macOS, com resultados `OK`, `ERRO` e `AVISO` e orientacoes de correcao por plataforma.
- `docs`: documentados no README os comandos para executar o diagnostico multiplataforma.

## 2026-07-15

- `fix`: corrigido o nome do CSV oficial para `stroop_go_nogo_ptbr_YYYY-MM-DD_HHhMMmSSs_trials.csv`, sem campos identificadores e compativel com a busca `data/*_trials.csv` do launcher.
- `test`: adicionada validacao do timestamp, sufixo `_trials.csv`, ausencia de metadados pessoais no filename e compatibilidade com o fluxo do dashboard.
- `fix`: fixadas unidades `height` antes da criacao do mouse nas telas de navegacao, evitando falha de `contains()` em monitores sem distancia calibrada quando o PsychoPy interpreta coordenadas como `degFlatPos`.
- `test`: adicionada regressao estatica para garantir que as unidades relativas sejam definidas antes de `event.Mouse` nas telas clicaveis.
- `ux`: atualizada somente a renderizacao das dez cores dos estimulos para uma paleta mais viva sobre o cartao claro, preservando as chaves logicas, condicoes e CSV oficial.
- `fix`: explicitadas ancoras e alinhamento central das palavras na pratica e no bloco principal.
- `test`: adicionadas validacoes da nova paleta visual, das dez chaves logicas, da centralizacao e da ausencia de cores de exibicao ou campos `_raw` no contrato exportado.
- `docs`: implementada a Etapa 10 com guias para Download ZIP do GitHub, primeira instalacao, uso cotidiano, privacidade, solucao de problemas e checklist do usuario.
- `docs`: atualizados README e estrutura do projeto para orientar usuarios sem Git aos atalhos multiplataforma e ao fluxo PsychoPy -> CSV -> SQLite -> dashboard.
- `feat`: criado fluxo multiplataforma para configurar `.venv`, instalar dependencias, importar o CSV oficial mais recente e iniciar o dashboard local em Windows, Linux e macOS.
- `feat`: adicionados atalhos `setup.bat`, `setup.sh`, `abrir_dashboard.bat` e `abrir_dashboard.sh`, sem dependencia de `.desktop` ou shell especifico na logica Python.
- `test`: adicionadas validacoes estaticas para deteccao do sistema, Python da venv, selecao do CSV mais recente, ausencias de CSV e venv, comando Streamlit e preservacao de `data/`.
- `docs`: documentada instalacao multiplataforma, uso manual, armazenamento local e limite descritivo nao clinico dos resultados.
- `feat`: implementada Fase 8 com dashboard Streamlit local em `dashboard/app.py`, lendo apenas o SQLite padrao `database/stroop_results.sqlite3` em modo somente leitura.
- `feat`: adicionados filtros por periodo, projeto, `participant_id`, `participant_name`, visita, avaliador, teste e versao, com cards, graficos, tabela agregada, detalhe por avaliacao e download manual da visao filtrada.
- `test`: adicionados testes do dashboard com SQLite temporario para conexao, banco ausente, schema, leitura das tres tabelas, tabela agregada, filtros, cards, detalhe, linguagem proibida e ausencia de escrita no banco.
- `docs`: atualizada documentacao do dashboard, plano e camada de dados para marcar a Fase 8 como implementada tecnicamente e pendente de validacao manual com banco real.

## 2026-07-09

- `feat`: adicionada rotina `resultados` apos `principal_loop`, com resumo descritivo do bloco principal em painel central claro, indicador circular de precisao, mediana de RT dos hits e contagens por tipo de resposta.
- `fix`: ajustado o fluxo para que `resultados` seja a tela final e grave o CSV oficial ao finalizar, evitando depender da rotina antiga `fim`.
- `fix`: removida importacao local de `visual` e `event` no Code Component de `resultados`, evitando `UnboundLocalError` no script gerado pelo Builder.
- `fix`: alterado o CSV oficial para exportar apenas tentativas do bloco principal, mantendo a pratica somente para feedback e HUD local.
- `test`: adicionadas validacoes estaticas para Flow, formulas, textos obrigatorios, navegacao por clique/Espaco/Enter, sintaxe dos Code Components, escrita no encerramento e ausencia de linhas extras no CSV pela tela de resultados.
- `docs`: documentadas formulas, limites de interpretacao e decisao de UX da tela final de resultados.
- `feat`: implementada Fase 7 com importacao do CSV unificado para SQLite local em `scripts/importar_csv_sqlite.py` e schema em `scripts/db_schema.sql`.
- `test`: adicionados testes com CSVs temporarios para importacao valida, cabecalho invalido, duplicidade, `--force`, metricas, rollback, validacao de RT e coerencia de resposta.
- `docs`: criada documentacao `docs/IMPORTACAO_SQLITE.md` e atualizados README, modelo de dados e arquitetura para marcar SQLite local como implementado e pendente de validacao manual com CSV real em Pilot.
- `feat`: atualizada versao para `0.2.2`, com bloco principal balanceado em 8 tentativas congruentes e 8 incongruentes, preservando pratica 2/2 e protocolo curto 4 + 16.
- `fix`: removido texto instrucional visivel do `trial_principal`, mantendo apenas estimulo central, cronometro, precisao e progresso durante o bloco principal.
- `test`: atualizadas validacoes de condicoes, versao, cores oficiais, pares incongruentes e ausencia de texto instrucional no bloco principal.
- `docs`: sincronizadas decisoes e validacao de condicoes com a distribuicao 8/8 e a limpeza da tela principal.

## 2026-07-06

- `feat`: atualizada versao para `0.2.1`, com formulario incluindo `participant_name` local, fullscreen padrao, fundo escuro mantido e centralizacao dos componentes de estimulo.
- `fix`: ajustado o contrato do CSV unificado para 21 colunas, inserindo `participant_name` apos `participant_id` e mantendo `participant_id` como nome-base do arquivo.
- `test`: atualizadas validacoes automatizadas para `participant_name`, tela cheia, ausencia de tamanho fixo e alinhamento central do cartao e do estimulo.
- `docs`: sincronizada a documentacao de formulario, CSV unificado, dados e decisoes com `participant_name` e a versao `0.2.1`.

- `fix`: substituido o uso de variaveis globais diretas do HUD por `hud_state`, evitando `SyntaxError` por declaracao `global` tardia no script gerado pelo Builder.
- `fix`: declarados contadores do HUD como globais nos Code Components de pratica e bloco principal, evitando `UnboundLocalError` ao atualizar precisao e cronometro no `run()`.
- `fix`: corrigidas cores dos cartoes de estimulo para literal constante, evitando geracao de `setColor(#F8FAFC, ...)` invalido no `lastrun.py`.
- `fix`: corrigida a cor de fundo do tema escuro no `.psyexp` para lista RGB numerica, evitando geracao de `color=[#0B1020]` invalido no `lastrun.py`.
- `feat`: atualizada versao para `0.2.0`, com protocolo curto de 4 tentativas de pratica e 16 tentativas principais, bloco principal de cerca de 1 minuto, HUD de precisao, cronometro principal e tema escuro com cartao claro para estimulos.
- `test`: atualizadas validacoes automatizadas para condicoes 4/16, tempos 300/2000/500 ms na pratica, 300/2500/950 ms no principal, HUD, cronometro, tema escuro e preservacao do CSV canonico.
- `docs`: documentados protocolo curto, duracao exclusiva do bloco principal, precisao ao vivo como decisao de UX e tema escuro.
- `fix`: alterado o nome do CSV oficial para usar `participant_id` como nome-base do arquivo gerado em `data/`.
- `feat`: adicionada primeira fase da interface visual pre-pratica com abertura, tutorial unico, introducao a pratica e lembrete rapido automatico.
- `test`: adicionada validacao automatica do Flow pre-pratica, remocao de telas antigas duplicadas, navegacao por clique/teclado e preservacao do formulario.
- `docs`: registradas decisoes de UX da interface pre-pratica e checklist Pilot correspondente.
- `feat`: implementada Fase 3 com 10 cores oficiais, pratica de 10 tentativas, bloco principal de 60 tentativas e perfil temporal de 2,0 segundos por tentativa.
- `test`: adicionada validacao automatica de balanceamento das condicoes, renderizacao por `ink_color_display`, preservacao do CSV unificado e tempos do `.psyexp`.
- `docs`: atualizada validacao de condicoes para documentar balanceamento, duracao aproximada de 2 minutos do bloco principal e checklist Pilot da Fase 3.
- `fix`: corrigido `.gitignore` para manter `data/` local e versionar somente `data/README.md`.
- `fix`: alterado o nome do CSV oficial para usar o `assessment_id` como nome-base do arquivo gerado em `data/`.
- `fix`: removida importacao local redundante de `os` no componente `formulario_sessao`, evitando `UnboundLocalError` no inicio da execucao gerada pelo PsychoPy.
- `feat`: implementada exportacao unificada em CSV oficial `_trials.csv`, com uma linha por tentativa real, metadados de sessao, pratica e bloco principal no mesmo arquivo.
- `test`: atualizado `scripts/analisar_stroop.py` para validar o contrato do CSV unificado e calcular metricas descritivas do bloco principal; criados testes automatizados em memoria para os quatro tipos de resposta e casos invalidos.
- `docs`: criado `docs/CSV_UNIFICADO.md` e atualizada a documentacao da camada de dados para registrar o CSV unificado como fonte oficial futura.
- `fix`: movida a execucao do formulario de sessao para `Begin Experiment`, evitando acesso a `expInfo` antes de sua criacao pelo PsychoPy.
- `fix`: corrigida leitura dos campos do formulario de sessao para aceitar retorno em lista ou dicionario do `psychopy.gui.Dlg`, evitando falso erro em `participant_id` valido.
- `feat`: implementado formulario local de sessao no PsychoPy com metadados canonicos, validacao de `participant_id` e nome de arquivo sem identificadores digitados.
- `docs`: criado `docs/FORMULARIO_DE_SESSAO.md` com regras, mapeamento para CSV e checklist manual de Pilot.
- `docs`: definida arquitetura futura de dados e dashboard local em `docs/DADOS_E_DASHBOARD.md`, `docs/MODELO_DE_DADOS.md` e `docs/PLANO_DE_IMPLEMENTACAO_DASHBOARD.md`.
- `docs`: criada estrutura documental de `dashboard/` com regras persistentes e README, sem implementar Streamlit ou banco.
- `chore`: atualizadas regras de Git e agentes para proteger SQLite, bancos locais, exports e dados reais.
- `docs`: criada especificacao visual e funcional futura em `docs/ESPECIFICACAO_VISUAL_E_FLUXO.md`.
- `docs`: criado copy sugerido das telas em `docs/COPY_DAS_TELAS.md`.
- `docs`: atualizadas decisoes de UX e decisoes metodologicas sem alterar `.psyexp`, condicoes, scripts, dados ou exportacao.

## 2026-07-05

- `test`: documentada validacao estatica de loops, variaveis e CSVs de condicoes em `docs/VALIDACAO_CONDICOES.md`, sem alterar o paradigma ou arquivos de coleta.
- `refactor`: organizada a estrutura do projeto com separacao entre experimento, condicoes, scripts, documentacao, testes, assets e dados locais.
- `docs`: criados READMEs locais, `AGENTS.md` por diretorio e `docs/ESTRUTURA_DO_PROJETO.md`.
- `chore`: movido `analisar_stroop.py` para `scripts/analisar_stroop.py` sem alterar a logica de analise.
- `chore`: preservados os nomes dos CSVs em `condicoes/` porque sao referenciados diretamente pelo `.psyexp`.
- `chore`: criada estrutura inicial de versionamento profissional com `.gitignore`, `AGENTS.md`, documentos de governanca e pastas auxiliares.
- `docs`: documentadas regras de privacidade, padrao de commits e decisoes iniciais do experimento.
- `chore`: preservada a pasta `condicoes/` como pasta local de CSVs de condicoes, em vez de duplicar conteudo em `conditions/`.
