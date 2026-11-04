# Progresso e retomada

Estado formal/aceite no [roadmap WEB](ROADMAP_WEB.md), evidencias no
[registro](REGISTRO_DE_ALTERACOES.md), arquitetura nos ADRs.

## Atual — GitHub Flow permanente; proxima unidade de desenvolvimento W22

- Retomada Git em2026-11-04: CI de4782ae6 passou suites Python/PostgreSQL,
  frontend, navegadores e HTTPS, mas falhou na auditoria Python. Locks corrigidos:
  Streamlit1.66.1, Authlib1.9.4, certifi2026.10.18, joserfc1.7.6,
  Pillow13.0.0 e pyasn1 0.6.5. Auditoria npm/pip-audit repetida sem achados;
  pip check,12testes do runner e27focados, actionlint e scanner339fontes com
  prova negativa aprovados. Auditoria antecipada antes dos navegadores/HTTPS
  no workflow e runner; reproducao documentada em CI_WEB.
  Publicar correcao, aguardar verify na HEAD final, squash e conferir CI de main.
  Regressao Python/PostgreSQL descartavel:369/369, zero skips, em69,246s.
  Hunk AGENTS preservado; sem deploy ou avancar W22 nesta solicitacao.

- Solicitacao autoriza permanentemente pushes, PRs e squash merges com CI/regras
  satisfeitas; sem force push, bypass, deploy ou operacoes destrutivas.
  Diretriz em AGENTS/CONTRIBUTING e protocolo alinhado, mantendo limites legados.
- Branch de integracao `prep-web` renomeada para `feat/evolucao-web`, preservando os67
  commits WEB ainda nao publicados. Base remota main9a52eda, conferida por fetch.
  Hunk preexistente de AGENTS raiz preservado somente na worktree, fora do index.
- GitHub permite administracao; main antes sem protecao. Agora exige PR, verify
  do app GitHub Actions15368, branch atualizada, historico linear e conversas
  resolvidas, inclusive administradores; force push/exclusao de main negados.
  Nenhum novo aprovador humano exigido; remocao automatica de branch integrada.
- CI existente preservada: Python/PostgreSQL, frontend, navegadores/motor,
  HTTPS real e auditorias. Push limitado a main para evitar duplicar PR; banco
  fixado ao digest Compose e typecheck duplicado removido (build ja o executa).
  Teste Bash/GITHUB_ENV confirma URL de banco valida e quebra de linha correta.
- Verificacao de caminhos dos67commits nao encontrou dados locais/chaves/exports
  novos. Scanner historico apontou somente SHA-256 de imagem documentado, ja
  esclarecido no HEAD, sem credencial real ou excecao de regra adicionada.
  Arquivo temporario original nao esta mais disponivel; classificacao baseada
  na proveniencia documentada e no valor conhecido do hash, sem ler dados privados.
- Validacao local do agente:11/11 testes do runner, actionlint oficial1.7.7,
  YAML/Bash aprovados. Principal confirmou11/11 em0,031s, actionlint,118links,
  scanner339fontes e diff check. A integracao e acompanhada pelo
  [PR1](https://github.com/thiagorraposo/stroop-go-nogo-psychopy/pull/1).
  Resultado vivo dos checks/merge no GitHub: `gh pr view 1 --json state,mergeCommit,statusCheckRollup`.
  Isso evita duplicar no arquivo o estado mutavel de cada execucao do Actions.
- Para encerrar a unidade Git, exigir verify aprovado na HEAD final, squash sem
  bypass, main sincronizada e branch temporaria removida; preservar hunk local.
  A execucao de push em main tambem deve passar. A solicitacao nao inclui deploy.
- Proxima acao de desenvolvimento, apos integrar e conferir Git/CI: retomar M3,
  instalar/testar timer local da replica externa e validar restauracao isolada.
  W22/W23 mantem as pendencias do checkpoint abaixo; nao iniciar publicacao
  de producao por este fluxo Git. Antes de retomar, conferir `git status`,
  `git log -1`, PR1 e execucao de main, sem repetir implementacao ja integrada.

## Checkpoint M3 — transporte restrito fechado em 2026-11-04

- **Escopo encerrado:** menor unidade em andamento de W22: verificar a replica
  externa por SSH restrito, testar e salvar contexto. Esta solicitacao nao avanca
  para agenda, restauracao ou publicacao. M3 identifica este checkpoint, sem criar
  outra etapa ou contabilidade paralela ao roadmap WEB.
- **HEAD de codigo validado:** `39dbf378536c16f033152bffe0f6b1e7e6ae30ee`, branch
  `prep-web`. Implementacao da replica em `bb938e8`; checkpoint documental em
  commit posterior. Para resolver seu hash: `git log -1 --format=%H -- docs/PROGRESS.md`.
  Alteracao preexistente de `AGENTS.md` preservada fora dos commits da tarefa.
- **Entregas:** replicador/exportador e modelos systemd versionados; cliente
  imutavel local e exportador remoto da release39dbf37 instalados anteriormente,
  com configuracao0600 e identidade SSH exclusiva restrita a ciphertext.
  Em28/10 houve primeira copia real; em04/11 o transporte foi revalidado sem
  abrir backup em texto claro nem ler chave AES. Nenhum novo deploy nesta unidade.
- **Resultados atuais:** `.venv/bin/python -m unittest tests.test_web_backup_replication -v`:
  10/10 aprovados em0,089s, zero falhas/erros/skips. CLI real do cliente imutavel:
  primeira execucao `copied`, segunda `already_current`, ambas codigo0/sem alerta;
  69.269bytes e duas geracoes retidas, geracao com cerca de13,34h. Comando `id`
  usando a mesma identidade foi recusado pelo exportador, sem saida de shell.
  `systemctl --user is-enabled stroop-web-backup-pull.timer`: `not-found`.
  Cliente imutavel confere com as fontes versionadas em dois arquivos;51links
  locais validos, scanner338fontes sem achados e `git diff --check` aprovado.
- **Evidencias:** exports/w22/20261104/restricted-transport.json (ignorado), copia
  inicial em exports/w22/20261028/external-copy-first.json. Resultados W21 e
  regressao anterior continuam historicos abaixo, sem serem reexecutados aqui.
- **Pendencias:** instalar/testar timer local, restaurar isoladamente uma replica
  externa usando a chave AES sob custodia separada; atualizar publicacao W22 com
  backup/retorno compativel e smoke publico. W23 aguarda implantacao/aceite e
  revisao operacional. Ultima publicacao documentada26fa9bf, nao revalidada aqui.
  RPO depende da disponibilidade do computador externo/rede; novo login Google
  interativo nao foi realizado nesta unidade. Nao conceder aceite geral.
- **Proxima acao exata:** a partir deste checkpoint, preparar a unidade
  `stroop-web-backup-pull.service` usando o modelo versionado e o cliente imutavel
  `~/.local/share/stroop-web-backup-client/releases/39dbf37`, com config
  `~/.local/share/stroop-web-backup-client/pull.json`; validar a unidade, executar
  uma vez, confirmar resultado e so entao habilitar/testar o timer horario.
  Depois validar restauracao da replica; nao antecipar deploy.

## Historico — W21 validada; preparacao operacional W22 em 2026-10-28

- Branch `prep-web`; AGENTS raiz preexistente preservado fora dos commits.
  Correcao `ad3a469`: administracao usa funcao SQL estreita da migration0010,
  sem DML direto em usuarios. Python357/357 sem skips, focados13/13 e navegador
  administrativo2/2 aprovados. Guia/transicao anteriores em7159b60.
- No alvo, API corrigida `stroop-web-api:w21-admin-20261028` e proxyW21:
  interface32/32 em dois navegadores, recuperacao10migrations/1avaliacao em6,013s,
  carga870consultas com710sucessos/160respostas429 e nenhum5xx/transporte invalido.
  Oito clientes a1GET/s sem rejeicoes, p95 67,11ms. Sem extrapolar para participantes.
- Reboot real comprovado por bootID alterado; publicacao4/64/48 e candidato1/16/12
  preservados, detalhe/CSV autenticados aprovados. Administracao via Docker
  existente resolveu ausencia de sudo, sem alterar credenciais/permissoesSSH.
  Pilhas proprias removidas; cinco servicos preexistentes saudaveis.
- Consulta somente de agregados confirmou sessao administrativa nao sintetica
  emitida nas ultimas24h. Callback de conta cadastrada inalterado frente a release
  publica; evidencia operacional registrada sem expor identidade/cookie. Nao foi
  executado novo login Google interativo; limitesW16 permanecem preservados.
- Harness HTTPS reforcado: API usa writer/reader canonicos, sem DSN proprietaria,
  com assertions negativas de privilegios. Integracao completa36/36 em10,9min,
  sem falhas/retries; proprietario somente nas fixtures/migrations.
- Rollback compativel com schema10 ensaiado na VPS: imagem
  stroop-web-api:rollback-schema10-20261028 preserva base antiga e acrescenta
  somente manifests0009/0010. API/proxy anteriores consultam e exportam, retorno
  ao candidato preserva1/16/12 e administra contas201/200. Sem reverter migrations.
- Publicacao ainda26fa9bf. Backup/restauracao e copia externa criptografada
  conferidos antes do reboot. Destino externo existente escolhido para automatizar:
  computador do responsavel; ferramenta SSH forcada/pull e timer em preparacao.
  Dez testes sinteticos do replicador passaram; falta instalar/testar transporte
  real, agenda e restauracao externa. RPO depende da disponibilidade do destino.
- Evidencias em exports/w21/adminfix-20261028 e 20261028-runtime-fix, ignoradas;
  detalhes no relatorio HOMOLOGACAO_WEB. Roadmap concentra estado/aceite.
- Proxima acao: salvar marcos validados, instalar replica restrita+timer em
  cliente imutavel, testar copia/restauracao real; publicar candidato com backup
  e retorno compativel, executar smoke publico e concluir transicao tecnica.
  W23 exige aceite final do responsavel, apos resultado concreto disponivel.

## Historico — W21 validada localmente; alvo aguardava acesso SSH

- Retomada em 2026-10-21 apos pausa solicitada pelo responsavel. Git em
  `prep-web`; `AGENTS.md` preexistente permanece fora da tarefa.
- `scripts/benchmark_web.py` cria pilha exclusiva HTTPS/API/PostgreSQL, mede
  1 GET/s por sessao nos niveis 1/4/8/16, sem alterar limitadores. Massa de uma
  avaliacao sintetica; OIDC apenas fixture de sessao. Nao extrapolar para VPS.
  Helpers Compose aceitam imagens explicitas; recuperacao consulta a lista
  vigente de migrations em vez de exigir oito.
- Primeiro ensaio falhou antes da carga: Nginx rejeitou regex CSV com `{36}`
  sem aspas. Corrigido `web/deploy/nginx.conf.template`; smoke real agora
  confere corpo maior que 64 KiB aceito ate autenticacao nessa rota e 413
  nas demais. Segundo ensaio corrigiu Content-Type da fixture, sem alterar API.
- Terceiro ensaio concluiu: 870 requisicoes; niveis 1/4/8 clientes ativos a
  1 GET/s sem rejeicoes; em 16 clientes, 320 sucessos e 160 respostas 429.
  Nenhum 5xx ou erro de transporte. Reinicio dos tres containers preservou
  1 avaliacao/16 tentativas/12 metricas. Nao e capacidade medida da VPS.
- Recuperacao com as mesmas imagens: 9 migrations/1 avaliacao restauradas,
  alerta e rollback de candidato invalido aprovados. Regressao Python 352/352,
  zero skips; integracao HTTPS/API/PG Chromium/Firefox 36/36; typecheck/build
  aprovados. Nenhum recurso temporario desses ensaios permaneceu ativo.
- [Relatorio de homologacao local](operacao/HOMOLOGACAO_WEB.md): metodo,
  resultados e limites. Artefatos em `exports/w21/`, incluindo as duas falhas
  iniciais; manifesto com 10 checksums conferidos. Sem logs/exports no Git.
- SSH de leitura ao alvo documentado: autenticacao recusada; chave local
  protegida por passphrase. Solicitado desbloqueio no agente, sem pedir segredo
  na conversa. Dialogo grafico nao carregou a chave; agente temporario removido.
  Smoke publico fez apenas dois GETs (200); nenhuma alteracao remota.
  Homologacao/capacidade/reboot do alvo
  continuam sem evidencia e o aceite reduzido W16 nao se aplica a W21.
- Proxima acao: disponibilizar chave desbloqueada em agente SSH acessivel a
  esta sessao, conferir o alvo em leitura e executar homologacao isolada la.
  Nao publicar o candidato, reiniciar a VPS ou acessar dados reais implicitamente.
  W21 nao concluida; W22/W23 nao foram avancadas. `AGENTS.md` preservado.

## Historico — W16 encerrada com ressalvas por aceite de evidencia parcial

- Em 2026-10-20 o responsavel instruiu produzir evidencia parcial e tratar W16
  como completa. Aceite registrado como encerramento com ressalvas, sem
  afirmar execucao da matriz fisica original. Gates de motor/API inalterados.
- Campanha `cd web && npm run test:w16`: 10 tentativas independentes por
  navegador visivel (Chrome instalado e Firefox Playwright), Escape separado,
  um worker e zero retries. Pratica e principal reais; API double e teclado
  sintetico. Artefatos em `web/test-results/w16/` (ignorados pelo Git).
- Resultado: 20 cenarios aprovados e 2 falhas Firefox; exit 1, zero skips/retries.
  Chrome 10/10 blocos validos; Firefox 8/10, falha de pratica na tentativa 2 e
  `timing_invalid` na 4 (864 ms, 42 transicoes preservadas). Escape passou nos
  dois navegadores. Causas das falhas nao determinadas, sem nova tentativa para
  substituir as falhas. Matriz fisica original dispensada para este aceite.
- Lote imutavel local em `exports/w16/2026-10-20T13-23-27Z/`, 21 trilhas brutas,
  erros, inventario, coletor original e agregado. 92 checksums verificados.
  Medicoes/limites em [VALIDACAO_WEB](VALIDACAO_WEB.md), estado no roadmap.
- Validacao adicional: 273 Vitest, typecheck/build, probe Escape Chrome 1/1 e
  `git diff --check`; 66 links locais conferidos. Corrigido rotulo de duracao das interrupcoes no coletor;
  JSONs originais preservados. Motor/API/paradigma nao alterados. Arquivos:
  `web/pilots/`, config Playwright W16, comando npm/tsconfig, README e documentos
  de metodo/roadmap/validacao/registro. `AGENTS.md` preexistente fora do commit.
- Proxima etapa do roadmap: W21, que ainda exige homologacao no ambiente alvo
  autorizado e capacidade medida. O aceite parcial W16 nao autoriza acesso
  remoto, deploy, coleta real ou homologacao de combinacoes nao testadas.

## Historico — W15E concluida; instrumentacao W16 pronta; pilotos fisicos pendentes

- W15E entrega upload CSV WEB com minimizacao em memoria no navegador,
  validacao server-side, vinculo explicito ao projeto, auditoria e recuperacao
  por UUID. Original fica local; a rota aceita ate 5 MiB/10.000 registros e as
  demais mantem 64 KiB. Transacao grava avaliacao e estado auditado atomicamente.
- Validacao concluida: 347 testes Python sem skips; 271 Vitest; typecheck e
  build; Playwright geral 98/98 e temporal 4/4. Na primeira suite combinada,
  Chromium acionou o gate de tempo uma vez; o teste isolado e a repeticao serial
  completa passaram.
  Integracao HTTPS+PostgreSQL importacao->consulta->detalhe->exportacao em
  Chromium/Firefox (2/2); papeis reais limitados e leitor SELECT; diff limpo.
- O responsavel instruiu “pressuponha todos os aceites”. W09A e W13A foram
  aceitas formalmente por essa instrucao. Isso nao substitui evidencia de piloto
  em equipamento real nem medicao de capacidade/homologacao.
- Commits locais: `e0e2adb` (W15E), `43a7faf` e `5a5d270` (retomada/evidencias).
  Alteracao preexistente em `AGENTS.md` permanece fora dos commits; nesta
  unidade nao houve dado real, acesso VPS, deploy ou push.
- Inventario local parcial registrado: host Linux Mint 22.2, painel eDP
  1920x1080/60 Hz, Chrome 155 e Firefox 158; nao foram identificados teclado
  USB com fio ou Edge, e Windows 11 nao esta disponivel neste host. Nenhum
  piloto fisico foi executado.
- Lacuna de instrumentacao resolvida: captura temporal local, opt-in por flag de
  build e query string, preserva trilhas completas e interrompidas somente em
  memoria e exporta JSON explicitamente. Validacao: Vitest 273/273, browser
  geral 98/98 e temporal 4/4, typecheck/build e `git diff --check` aprovados.
  Isso prepara a coleta, sem homologar W16.
- Proxima acao elegivel: realizar a campanha W16 quando os itens de referencia
  restantes estiverem disponiveis, executando 60 sessoes sinteticas presenciais
  conforme pacote aprovado; W21 requer ambiente de
  homologacao autorizado e capacidade medida. Testes automatizados/headless nao
  suprem essas evidencias, e nao ha outra etapa com dependencias satisfeitas.

## Historico — W15D validada; W15E depende de contrato/minimizacao

- Branch `prep-web`; `AGENTS.md` raiz preexistente permanece fora dos commits.
  W13A esta implementada, mas aguarda aceite operacional. W16 e homologacao/
  coleta real permanecem pendentes. Sem publicacao, push ou acesso remoto.
- W15D adiciona gestao administrativa WEB de contas (`iss` + `sub`), perfil,
  estado e e-mail auxiliar; identidade nao cadastrada recebe apenas seus
  identificadores OIDC verificados para solicitacao institucional. Area Admin
  separada de Resultados; CRUD sem exclusao, confirmacao de mudancas, CSRF,
  auditoria sem claims/e-mail e lock do ultimo administrador. Projetos e
  membros reutilizam operacoes existentes; nenhum acesso a resultados sem
  vinculo explicito. Bloqueio/revogacao revalidam acessos sem excluir coletas.
- Validacao W15D: 341 testes Python sem skips, 268 frontend, build/typecheck,
  browser geral 90/90 e temporal 4/4 Chromium/Firefox, integracao
  HTTPS+PostgreSQL 2/2,
  testes de API/corrida PostgreSQL para ultima conta admin, callback OIDC sem
  cadastro e CSRF. Primeira regressao de browser achou seletor ambiguo causado
  pelo novo botao; seletor corrigido e validado em ambos navegadores.
- W15A–W15C mantem evidencias registradas abaixo/historico. Banco descartavel
  `stroop-w13a-test` na porta 32768/database `stroop_etapa4_test_w13a`; nenhum
  container operacional alterado.
- W15D commit `576e642` (`feat(web): administra contas e vinculos de pesquisa`).
- Proxima acao: definir politica de minimizacao W15E antes do codigo de upload.
  O CSV Stroop canonico exige `participant_name` nao vazio e inclui `initials`;
  o roadmap exige impedir transmissao nominal para a WEB e especificar
  compatibilidade dos validadores. W13A permanece pendente de aceite operacional.

## Historico — relatorio tecnico para leitores externos

- Criada sintese em desenvolvimento/RELATORIO_TECNICO.md, com fluxo local/WEB,
  tempos, classificacao das respostas, formulas/exemplo sintetico, arquitetura,
  persistencia, acesso e limites. Fontes canonicas vinculadas; sem substituir
  contratos nem duplicar o estado/criterios do roadmap.
- Indice docs/README.md aponta para a leitura introdutoria. Relatorio distingue
  APIs existentes de telas pendentes e testes de software de homologacao fisica.
- Validacao:83links locais e diff conferidos; seis valores do exemplo
  sintetico comparados com o nucleo Python. Revisao independente de formulas/
  escopo concluida; diagrama representa acesso ao banco exclusivamente pela API.
- Somente documentacao; nenhum codigo, servico, coleta ou deploy alterado.
  Desenvolvimento permanece no escopo futuro ja definido pelo roadmap.

## Historico — comparacao do dashboard e planejamento documental

- Usuario solicitou comparar dashboard legado/WEB e documentar complementos,
  como no cadastro da sessao. Inspecionados codigo, guias, contratos de dados,
  acesso e mapa legado; revisao independente das areas administrativas/upload.
- Matriz de capacidades observadas incorporada a W15 no [roadmap](ROADMAP_WEB.md),
  com fontes de codigo. W15A–W15E planejam filtros, apresentacao analitica,
  exportacao agregada, administracao e importacao; estado/criterios so no roadmap.
- Diferenciados CSV agregado e CSV oficial individual; API pronta de projetos/
  vinculos versus API ausente de contas/upload; recursos ja presentes versus
  parciais e exclusoes intencionais de nome/iniciais do participante. Nao copiar
  paths, fundir pseudonimos entre projetos ou associar legado por coincidencia.
- Evidencias anteriores preservadas para seus escopos; paridade funcional
  W15/W21/W22 e transicao W23 dependem dos complementos. Streamlit mantido.
- Unidade somente documental, sem codigo, testes funcionais, banco ou VPS.
  Conferidos38links locais, unicidade das fichas/estados e git diff --check;
  revisao independente do planejamento sem achados materiais.
  Proxima acao quando retomado desenvolvimento: W13A, depois complementos W15
  conforme dependencias; definir contrato/minimizacao antes de implementar upload.

## Historico — planejamento documental do cadastro da sessao

- Responsavel identificou ausencia da tela de cadastro e pediu documentar
  primeiro o trabalho no roadmap. Implementacao/deploy suspensos nesta unidade;
  delegacao de testes interrompida antes de qualquer arquivo entregue.
- Escopo, dependencias, fluxo, criterios de aceite e verificacoes previstos
  registrados em W13A do [roadmap](ROADMAP_WEB.md). A API existente nao supre a
  falta do formulario; evidencia anterior de integracao nao concede esse aceite.
- Preservadas as decisoes WEB: projeto/codigo/visita e avaliador autenticado,
  sem nome/iniciais do participante. W16/W21 e coleta real continuam pendentes.
- Proxima acao de desenvolvimento: implementar W13A conforme sua ficha quando
  esse escopo for retomado. Nesta solicitacao, somente documentos e validacao
  de links/diff; nenhuma mudanca funcional ou acesso a VPS.

## Historico — correcao do callback Google apos relato de falha

- Usuario encontrou `invalid_oidc_state` no login pessoal. Reproduzido no
  dominio publico com cookie/state validos e metadados Google sinteticos:
  a allowlist exigia apenas code/state e rejeitava scope/authuser/prompt/iss.
- Commit26fa9bf aceita metadados conhecidos; iss opcional exige o emissor Google
  exato. Duplicados/desconhecidos, code+error, state divergente, expiracao e
  reutilizacao continuam rejeitados. Identidade vem somente do ID token validado.
- Regressao: 322 testes Python aprovados em48,161s, com PostgreSQL sintetico;
  teste novo cobre callback legado com metadados, sessao/me e replay.
- Backup criptografado executado antes da troca. Runtime current agora aponta
  releases/26fa9bf; API stroop-web-api:fix-oidc-20261017, imagem b78bc442321e...
  API anterior e web.env.pre-oidc-fix preservados para retorno. Sem migrations,
  alteracao de dados, proxy ou credenciais. Todos os servicos saudaveis.
- Smoke HTTPS publico apos a troca: metadados aceitos; codigo deliberadamente
  invalido alcanca troca Google e falha fechado; replay rejeitado e nenhuma
  sessao criada. Readiness200, monitor0. Isso nao comprova login pessoal.
- Proxima acao: usuario iniciar novo login em /equipe e confirmar acesso.
  Replica externa automatica e homologacoes W16/W21 continuam pendentes.
  Somente AGENTS raiz preexistente permanece fora dos commits desta correcao.

## Historico — deploy delegado explicitamente pelo usuario

- Usuario autorizou substituir a aplicacao publicada na VPS, preservar dados/
  credenciais, realizar backups e agir autonomamente. Essa instrucao substitui
  nesta implantacao a atribuicao anterior W22 exclusivamente ao usuario.
  W16 continua pendente; somente fluxos sinteticos permitidos.
- SSH raposo@108.174.145.177:22022, chave/hostkey locais existentes. Hostname
  informado nao resolve DNS, mas o IP do dominio foi confirmado pelo hostname
  remoto. Ubuntu22.04.5/x86_64, 2vCPU/~4GBRAM, DockerCompose5.6. UsuarioDocker;
  sudo exige senha. Operacoes administrativas especificas realizadas por Docker,
  com mounts limitados, sem montar raiz do host nem expor credenciais.
- Original /opt/stroop-go-nogo-psychopy e volume stroop-production_postgres_data
  preservados: schema3, 0avaliacoes, 1conta. Backup PostgreSQL restaurado em
  container isolado e conferido; configuracoes/segredos/Certbot criptografados
  e autenticados. Copias externas neste computador em
  /home/raposo/.local/share/stroop-web-vps-backups, chaves em diretorio separado
  /home/raposo/.local/share/stroop-web-vps-keys. Nao imprimir nem versionar.
- Novo runtime /home/raposo/stroop-web; current aponta releases/aa6c844.
  Config web.env externa600; compose.vps.yaml adiciona apenas webroot ACME.
  Secrets /home/raposo/.local/share/stroop-web/secrets, arquivos600 com UIDs
  especificos10001(API)/101(TLS)/999(PG). Originais legados inalterados.
- Novo PG separado, backup legado restaurado e migrations0004–8/grants aplicados.
  Conta original preservada; fixtures administrativas sinteticas desativadas.
  Administrador original vinculado aos projetos sinteticos e projeto proprio
  SYNTHETIC_HOMOLOGATION. Convite manual novo em /tmp/stroop-vps-manual-invite.json
  neste computador, protegido600; nao copiar codigo para docs/logs.
- Imagens: APIdeploy-20261017 ID40c71ee1922d..., proxydeploy-20261017 ID51b05c773ecc...
  Transferidas prontas, contextos de fonte permitidos, sem data/database/secrets.
  Commits d2e765e(callbackoptin), befaf88(ACME), aa6c844(hook). Python317/49,987s,
  callback5/proxy6 aprovados. OIDC/TLS existentes reutilizados; alias legado
  /oauth2callback chama handler original, sem redirect intermediario.
- Cutover aprovado em 2026-10-17T01:11:40Z, operacao6,444s. NovaWEB publica80/443;
  API/PG sem portas. Proxy antigo parado, dashboard/PGlegados privados mantidos
  para rollback. Deployment.json no runtime. HTTPS/publicready aprovados.
- Preflight privado e publico: convite/conclusao/retry/consulta/CSV reais
  aprovados. Navegador Chromium executou pratica+principal60s no dominio real,
  gravou1vez/16tentativas/12metricas, sem erroJS/storage e logoutcookie confirmado.
  Total3coletas sinteticas/48tentativas/36metricas. Artefatos /tmp/stroop-vps-
  browser-{result,timing,fixture}.json; nao inferir W16 fisica desses ensaios.
- Certbot alterado para webroot; timer existente preservado. Backup completo
  /etc/letsencrypt autenticado antes de alterar renewal/hook. DryrunACME0 e
  hookreal0, incluindo recriacao proxy para renovar inode dos binds. Certificado
  publico valido ate2027-01-05. Sem nova dependencia instalada na VPS.
- Cron usuario preservado e ampliado: monitor/minuto, backup02:15 diario,
  restore03:30domingo. Scripts tools/vps-maintenance.sh e vps-rollback.sh;
  rotina backup/restore90984 terminou0, snapshot atualizado com3coletas.
  Overlay de logs limitados aplicado nos3servicos; recriacao preservou dados.
- Perguntas assincronas pendentes: usuario confirmar login Google pessoal e
  destino externo estavel para automatizar replicas. HandoffGoogle real passou
  no browser sem redirect_uri_mismatch/invalid_client; login pessoal nao presumido.
- Validacao final: todos saudaveis,3coletas/48tentativas/36metricas preservadas
  apos recriacao; banco original0avaliacoes/1conta intacto. Roles writersemDDL/
  UPDATEusuarios e readersemPII; logsproxy6registros so camposfechados, APIvazio.
  Seis copias criptografadas externas comSHA256 conferido, incluindo configuracao
  WEB/credenciais autenticada em web-config-20261017T011949Z.tar.enc; chavesseparadas.
- Rollback reforcado: confirma HTTPS do legado e reinicia proxyWEB se falhar;
  dois testes de controle de falha aprovados, sem trocar trafego real novamente.
- Commit operacional d6f49a0 concluido; links90, scanner281 e sintaxe shell
  aprovados. Somente AGENTS raiz preexistente permanece alterado; sem push.
- Proxima acao: receber confirmacao Googlepessoal e destino de replica externa
  automatica; corrigir qualquer falha relatada. Nao afirmar
  validacao pessoal sem resposta. Publicacao tecnica e fluxos sinteticos feitos;
  W16/W21 permanecem pendentes. Preservar previa local34647/4173 e AGENTS raiz
  preexistente. TunelSSH19443 encerrado apos cutover.

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
- Usuario aprovou o pacote W16 integralmente: configuracao canonica em
  VALIDACAO_WEB.md (Windows11/LinuxMint22.2, Chrome/Edge/Firefox, 60sessoes,
  monitor1080p60Hz e tecladoUSB). Nao pedir novamente decisoes desse pacote.
  A aprovacao nao confirma existencia/acesso aos equipamentos nem execucao das
  replicas. Falta disponibilidade/inventario real e evidencias presenciais;
  preservar tolerancias D5 e nao substituir por headless/VM.
- W20 commit37fd066 concluido. Bloqueio revalidado em tres turnos consecutivos:
  nao chegaram equipamento/evidencias W16 nem ambiente autorizado W21. Nao ha
  outra etapa independente com dependencias atendidas. Goal bloqueado aguardando
  informacoes externas, sem conclusao geral nem alteracao do escopo.
- Proxima acao: receber configuracao de referencia e ambiente de homologacao,
  executar/analisar pilotos e seguir W21 apos aceite W16. ContainerCI
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
