# Registro de alterações

Fatos datados; estado/aceite vigentes somente no [backlog canônico](Projeto%20Stroop%20Test.md).
Entradas antigas preservam política e evidências de suas datas; não constituem
comandos atuais nem resultados reexecutados.

## 2026-11-06 — Fluxo ponta a ponta de avaliações e transporte incremental (M4)

- Integrado o Dedicated Worker incremental (`checkpoint-worker.ts`) ao fluxo real
  do participante (`ParticipantRun`, `PracticePreparation` e `ParticipantFlow`),
  com sondagem de prontidão, drain assíncrono em interrupção, `worker-src 'self'`
  em `web/security-headers.json` e invalidação tardia via
  `POST /api/v1/participant/session/invalidate`.
- Validados preparação profissional após login local (`CHG-004` / `AUTH-L07`),
  múltiplas visitas/avaliações, isolamento de pseudônimo entre projetos,
  ausência de campos nominais/demográficos e de precisão agregada durante a
  execução, preservação de prefixo parcial em `web_session_observations` sem
  criar resultado oficial, avaliação completa com 16 tentativas/12 métricas/
  proveniência e logout participante limpando RAM/cookie.
- Concluídas WEB-013, WEB-014, WEB-015 e WEB-016, encerrando M4 (4/4; 26/45
  entregáveis aceitos). Evidências, falhas intermediárias preservadas, limites
  e próxima ação (M5/WEB-017 e WEB-018) registrados somente no backlog canônico.

## 2026-11-06 — Conclusão da autenticação local e revisão de segurança (M6)

- Implementados e integrados login, troca de senha e revogação locais, gestão
  por ID opaco, `Origin`/CSRF, limite de 4 KiB e cookie `__Host-stroop_professional`;
  `API_AUTH_MODE=local` passa a ser o padrão fora de `APP_ENV=test`, recusando
  endpoints OIDC com 404. Frontend limpa credenciais/RAM e não oferece cadastro
  de contas adicionais.
- Lista local ampliada para 10.898 hashes SHA-256 (SecLists), migration 0013
  protege o último admin local ativo e revoga sessões locais ao bloquear/mudar
  perfil; antiabuso combina origem/identificador persistentes, falhas
  compartilhadas e teto de 10.000 buckets com limpeza >24 h.
- Validados AUTH-L01–L09 sem skips: suíte Python/PG integral, Vitest/build,
  Playwright `browser`/`integration`/`local-auth` em Chromium e Firefox,
  scanner/self-test, auditorias, Compose HTTPS sem secrets Google e smoke de
  backup/restore isolado exigindo `recover` antes da abertura.
- Concluídas WEB-021 e WEB-024, encerrando M6 (4/4; 22/45 entregáveis aceitos).
  Evidências, falhas intermediárias preservadas, limites e próxima ação (M4/WEB-013)
  registrados somente no backlog canônico.

## 2026-11-06 — Base transacional para credenciais locais

- Iniciada implementação autorizada de M6: identidade local própria, migration
  aditiva 0012, Argon2id, bootstrap/recuperação por terminal e transações de sessão,
  revogação, rotação e limite por identificador, preservando legado e vínculos.
- Acrescentadas regressões sintéticas de concorrência, rollback, expiração,
  parâmetros, compatibilidade e privilégios; reader continua sem acesso a hash,
  writer sem criar contas ou alterar app_users.
- Unidade preparatória: API, formulário, Compose e corte OIDC ainda aguardam
  integração e ensaios HTTPS. Evidência e continuidade somente no backlog.

## 2026-11-06 — Aceite explícito do suporte local do motor

- Registrada resposta “aceito” do proprietário aos resultados e limites de
  EV-M3-012, com conferência dos critérios de WEB-012 e do gate M3 no backlog.
- Preservados ambientes/versões medidos, falhas históricas, janela de perda,
  limites de integração e validação física/metodológica. Matriz alinhada ao aceite.
- Unidade exclusivamente documental; nenhuma campanha ou teste funcional
  reexecutado, runtime alterado ou autorização de outro marco inferida.

## 2026-11-06 — CHG-004: autenticação local e revisão de pendências

- Decisão do proprietário integrada ao backlog e ADR-006: uma conta administrativa
  local, sem cadastro público/Google obrigatório, mantendo projetos e convites.
- Especificados hash/provisionamento/recuperação, antiabuso, sessões/revogação,
  contrato HTTP e migração aditiva; matriz e plano AUTH-L01–L09 atualizados.
- Revisadas todas as pendências e riscos, incluindo conta compartilhada sem
  autoria individual e avaliação institucional ainda necessária. Aceites,
  DEC-01–05, histórico, cálculo de progresso e workflow preservados.
- Missão restrita à documentação; nenhum runtime, teste funcional, dependency,
  migration ou ambiente externo alterado. Evidências/versionamento em EV-CHG-004
  e Retomada do backlog, sem criar execução paralela.

## 2026-11-06 — Réplica SSH e agenda sintéticas reais

- Novo harness gera backup PG sintético, copia por SSH com forced-command,
  confere bytes/checksum/idempotência e restaura cópia com recibo válido.
- Timers transitórios comprovam cópia positiva e alerta negativo; ferramenta SSH
  fica só em imagem descartável, sem instalar no host ou relaxar StrictModes.
- Registradas falhas de ownership anteriores e limites do ensaio no mesmo host.
  Gate de réplica externa preservado em WEB-031; nenhuma aprovação inventada.
- Sessão excepcional encerrada após seleção global sem tarefas elegíveis;
  workflow/AGENTS permanentes preservados. Evidências no backlog canônico.

## 2026-11-06 — Pipeline integral local e Actions por SHA

- Runner integral em checkout sparse/PG descartável e locks exatos aprovado:
  scanner/self-test, Python, frontend, auditorias, browsers e HTTPS reais.
- Workflow_dispatch existente validou a mesma SHA sem PR/merge/deploy; primeira
  falha de scanner documental preservada, corrigida sem allowlist ou bypass.
- Evidências e URLs em EV-M8-030 no backlog; nenhuma regra permanente de
  continuidade alterada. Decisões/painel alinhados aos ensaios atuais.

## 2026-11-06 — Infraestrutura sintética e integridade da restauração

- Build/Compose HTTPS reais revalidados; smoke passou a exigir recusa de nove
  caminhos de fontes/configuração no proxy.
- Bancos de teste usam prefixo descartável e restaurações recebem projeto
  exclusivo; verificação do recibo restaurado cobre vínculo e estado, com caso
  negativo real e rollback de imagem ensaiado.
- Documentado procedimento de validação formal por SHA via workflow_dispatch
  existente, sem novos gatilhos, PR automático ou mudança de proteções.
- Limites de réplica/agenda e evidências reais ficam em EV-M8-029/031 no backlog.

## 2026-11-06 — Revalidação de permissões e sessões em HTTPS

- Conferidos perfis/projetos/revogação em PostgreSQL sintético e navegadores;
  novo E2E verifica CSRF cruzado, troca de credenciais, logout e replay real.
- Preservadas proteções/runtime e separação entre ensaio com identidade sintética
  e login Google interativo, que depende de ambiente e conta autorizados.
- Evidências e limites em EV-M6-022/023 do backlog, sem alterar regras permanentes
  de continuidade; autorização entre marcos vale apenas nesta sessão.

## 2026-11-06 — Campanha temporal com transporte ativo e relatório de suporte

- Executadas dez capturas completas por navegador no equipamento local aprovado,
  com worker real, ACK lento/perdido e servidor simulado indisponível. Conferidas
  transições/duração D5, igualdade dos registros recebidos e domínio Python.
- Preservados 19 passes e uma falha original de preparação sem trilha recuperável;
  suplemento Chromium explícito passou. Corrigida coleta de diagnóstico da fixture
  para não mascarar erros; motor/worker idênticos entre série e suplemento.
- Registrados custos observados, descontinuidade civil e limites em EV-M3-011;
  relatório de viabilidade EV-M3-012 disponível para aceite do responsável.
- Regressões frontend/Python/visual aprovadas, sem dependências, migrations,
  dados reais, integração de produto M4 ou serviços externos alterados.

## 2026-11-05 — Aprovação DEC-04 e preparação da campanha local

- Proprietário aprovou expressamente o alcance local de engenharia DEC-04;
  validação física/metodológica permanece gate M9. Matriz/evidência no backlog.
- Preparados Dedicated Worker/fila em RAM e entrega de cópia imutável de tentativa
  completa após início da próxima fixação, sem esperar HTTP/JSON no motor.
- Campanha sintética isolada exercita motores reais com transporte ativo,
  ACK lento/perdido e indisponibilidade; produto/fluxo integrado continua M4.
- Sem alteração de tempos, estímulos, gates, métricas/CSV, schema ou dependências.

## 2026-11-05 — Regressão consolidada da apresentação experimental

- Conferidos os critérios de WEB-044 na apresentação aprovada: dez cores,
  contorno/centro, HUD sem precisão, feedback, lifecycle, regras e métricas/CSV.
- Executadas regressões frontend/Python e screenshots sintéticos; observação
  temporal preparatória com navegador visível e trilhas preservadas.
- Evidências, ambientes, resultados e limites em EV-M3-044 no backlog; campanha
  DEC-04 com transporte ativo e aceite de suporte continuam gates próprios.
- Runtime, protocolo, dependências, dados e serviços externos preservados.

## 2026-11-05 — Aprovação visual de D3 pelo proprietário

- Registrada aprovação explícita para contorno branco sem cartão, progresso e
  cronômetro principal discretos, sem precisão agregada; feedback da prática mantido.
- D3 visual revisada com histórico preservado; D4 complementada por identificação
  stroop-web-outline/1.0.0 e proveniência via app_version, sem schema novo.
- Gate visual de WEB-042/043 satisfeito pelo proprietário conforme responsabilidade
  já documentada; nenhuma aprovação atribuída a terceiro. DEC-04 permanece pendente.
- Dependências, rastreabilidade e workflow alinhados sem novos IDs/denominador.
- Implementados contorno branco uniforme sem cartão e HUD imperativo com progresso
  real/cronômetro estável; retirados nós de precisão nos dois motores, sem alterar
  núcleo de métricas, janelas, agendamento ou transporte. Prática mantém feedback.
- Criados testes de apresentação/ausência/relógio e screenshots sintéticos em
  Chromium/Firefox; comandos, falhas e limites registrados no backlog.

## 2026-11-05 — Integração de refinamento UX ao planejamento canônico

- CHG-003 integra UX-01–08 ao backlog, requisitos REQ-UX-001…011, arquitetura,
  protocolo/decisões, fonte UX e workflow; IDs e evidências anteriores preservados.
- Acrescentadas entregas M3 WEB-042/043/044 e ampliados critérios de campanha,
  fluxo M4, componentes/regressão M5 e validação M9, sem marco paralelo.
- Especificada ausência da precisão agregada na prática/principal e preservação
  dos cálculos, feedback individual, persistência, relatórios e CSV. Identificado
  conflito com D3 aprovado e necessidade de identificação da variante frente a D4.
- Validador documental reproduzível passou a calcular catálogo/progresso a partir
  das fontes canônicas e conferir estabilidade de IDs contra HEAD.
- Preferência de integração alinhada: Merge Commit tradicional com commits
  preservados, sem Squash Merge; nenhuma configuração/proteção remota alterada.
- Alterações experimentais permanecem condicionadas às decisões metodológicas;
  documentação de alvo não é implementação, teste ou aceite funcional.

## 2026-11-05 — Revalidação do motor experimental em M3

- Iniciado M3 por `continue o projeto`; preservada base M2 sem integrar main.
- Acrescentadas verificações de snapshot WEB versus tempos/paleta do Builder,
  renderização das dez cores no principal e ciclo de vida dos plugins reais
  jsPsych sob remontagem React StrictMode, sem mudar regras ou runtime.
- Corrigida sincronização do teste E2E de teclado: aguarda foco inicial React
  antes de enviar Espaço/Enter, preservando falhas anteriores no backlog.
- Requisitos REQ-EXP-001/002 e evidências da revalidação vinculados ao backlog.
  Resultados de navegador distinguem janela visível, automação e API double;
  nenhuma evidência é promovida a latência física ou suporte universal.
- Campanha temporal e aceite de suporte continuam condicionados à DEC-04;
  nenhum trabalho de outro marco, deploy ou dado real por implicação.

## 2026-11-05 — Comprovação de atomicidade e paridade de M2

- Acrescentada prova de ACK após commit com constraint trigger adiado e leitura
  independente, asserções de cardinalidade nas corridas e inspeção dos papéis PG.
- Reforçada a referência independente das 12 métricas/unidades e a conferência
  dos valores persistidos após exportação/reimportação CSV sintética.
- Conferidos critérios WEB-007/008 e matriz ADR-005 aplicável ao backend;
  evidências locais e vínculos REQ-INT-002/REQ-MET-001/002 no backlog único.
  Runtime, migrations, fórmulas, dependências e protocolo preservados.
- Nenhum trabalho de M3, pesquisa real, integração à main ou deploy nesta sessão.

## 2026-11-05 — Receptor incremental e vínculos WEB

- Implementada migration aditiva 0011 para participantes/visitas por projeto,
  checkpoints e invalidação, com mapeamento restrito a convites WEB existentes.
- Acrescentados receptor HTTP, recibos parciais, reconciliação de conclusão,
  inspeção de estado e invalidação tardia sem resultado oficial utilizável.
  Clientes existentes validam os novos campos, sem alterar o motor experimental.
- Revalidada expiração durante escritas; grants mínimos incluem somente as
  colunas necessárias à revisão do fim principal. Requisitos REQ-INT-001/002,
  REQ-INF-001 e regressão REQ-MET-001/002 rastreados em EV-M2 no backlog único.
- Decisões DEC-01/02 já aprovadas; testes exclusivamente sintéticos. Worker,
  fila e impacto temporal do transporte continuam nas tarefas M3/M4. Sem
  alteração metodológica, dependências novas ou operação em produção/dados reais.

## 2026-11-05 — Painel visual de acompanhamento

- Acrescentado painel ao backlog com resumo de aceites, barras por marco,
  acesso às fichas concluídas e sequência do marco atual, por solicitação do responsável.
- PROGRESS passou a oferecer navegação visual para o painel e suas evidências;
  índice documental atualizado. Contabilidade permanece no backlog único.
- Alteração de apresentação e navegação, sem novo aceite, mudança de escopo,
  requisito, contrato, runtime ou autorização de execução.

## 2026-11-05 — Validação da estratégia incremental pelo responsável

- O responsável respondeu “valido” à proposta versionada em `270377b`, aprovando
  ADR-005, contrato alvo, matriz de invalidação e limites residuais de perda.
- Registrada a validação prévia à implementação e alinhadas as fontes canônicas;
  contratos alvo continuam distintos do comportamento implementado. Evidência
  de aceite e próxima ação permanecem exclusivamente no backlog.
- Nenhuma alteração de runtime, schema ou regra experimental; ensaios de banco,
  motor e transporte continuam exigidos antes do aceite funcional.

## 2026-11-05 — Decisões de participação e proposta incremental

- Registrada aprovação explícita do responsável para participantes por projeto,
  múltiplas visitas/avaliações, convites únicos com controle de acesso/validade
  e evolução longitudinal aditiva, sem cadastro central ou agenda separada.
- Registrada rejeição de RAM final-only e exigência de persistência incremental,
  recibos, idempotência e preservação de sessões incompletas/ inválidas; D2 mantém
  nova sessão com prática e proíbe retomar bloco interrompido.
- Elaborado ADR-005 com worker, riscos residuais e ensaios planejados; modelo,
  contrato HTTP candidato e matriz metodológica alinhados. Validação definitiva
  anterior ao código exigida pelo responsável; proposta não foi aprovada por
  antecipação. Impactos rastreados em CHG-002, somente no backlog.
- Nenhuma alteração de runtime, migration, métrica, CSV, dependência ou produção.

## 2026-11-05 — Comparação dos contratos de participação e perda

- Comparados contrato HTTP, modelo lógico e implementação de convite, sessão,
  conclusão e envio em memória para preparar as decisões do responsável.
- Documentada a distinção entre convite preparado, sessão criada no resgate e
  avaliação oficial criada na conclusão. Registrados os limites do aviso de
  perda exibido no envio pendente e da recuperação após resposta incerta.
- Nenhum contrato científico, payload, schema ou runtime alterado. Achados,
  dependências e próxima ação ficam exclusivamente no backlog canônico.

## 2026-11-04 — Reprodução sintética da fundação WEB

- Reproduzida implementação existente em worktree sparse isolada, com locks
  preservados, PostgreSQL descartável em tmpfs e fixtures sintéticas.
- Revalidados cálculos, unidades, ausência de hits, roundtrip CSV/SQLite,
  reexports/CLIs e fronteiras entre domínio, ingestão, aplicação e persistência.
  Nenhuma refatoração ou mudança experimental necessária para essa conferência.
- Acrescentada receita local de reprodução/retomada, vinculada ao workflow;
  resultados, ambiente, SHA e Git ficam em EV-M1/Retomada do backlog canônico.

## 2026-11-04 — Replanejamento documental da plataforma Stroop Web

- Auditados código/runtime, método, condições, métricas, migrations, OIDC, Docker,
  proxy, CI e Git na HEAD 87f6a9c52043625a3474805dfc6680390ddfc151. React/FastAPI/
  jsPsych/PG já existem; plano de consolidação/revalidação, sem reconstrução presumida.
- Nova missão, inventário/classificação, requisitos A–L/matriz, arquitetura e ADR-004,
  M0–M10/WEB com dependências, critérios, riscos/decisões e próximo trabalho canônicos.
- Backlog único em Projeto Stroop Test.md; snapshots congelados de Wxx/retomada e
  etapas 1–12 preservam histórico, sem transferir 87% nem aceites para novo escopo.
- AGENTS/workflow/contribuição alinhados à última autorização: commit/push autônomos
  em branch coesa, sem PR/merge automáticos; produção/dados reais separados. Conteúdo
  preexistente de AGENTS sobre pesquisa/público/VPS preservado na revisão autorizada.
- Corrigidas descrições documentais de arquitetura antiga, routers já implementados,
  paleta CSV versus renderização e ausência de RT. Nenhuma regra científica, código,
  schema, configuração operacional, dependência ou dado real alterado.
- Validação desta sessão exclusivamente documental; comandos/resultados e Git final
  em EV-M0/Retomada do backlog. Suites funcionais/CI/medição física não reexecutadas.

## 2026-11-05 — Merge Commit tradicional com Pull Requests

- Por instrucao do responsavel, Squash Merge desabilitado e exigencia de
  historico linear retirada da protecao classica de main; Merge Commit ja
  estava habilitado. Reconsulta da API confirmou PR, verify, regras de revisao,
  administradores e bloqueios de force push/exclusao preservados. Sem rulesets
  adicionais; Rebase e auto-merge mantidos como estavam.
- Orientacao posterior do responsavel: sem automerge. GitHub auto-merge
  permanece desabilitado; Codex pode abrir/atualizar PRs, mas so integra apos
  autorizacao explicita, mesmo com CI aprovada. PR desta entrega fica aberto.
- AGENTS, contribuicao, workflow Codex e CI_WEB alinhados ao merge tradicional
  por PR. Exportacao/rollback e validacao remota descritos em CI_WEB.
- Alteracao exclusivamente de governanca Git; sem codigo, workflows Actions,
  arquitetura, requisitos, roadmap, dados ou deploy. Entregas anteriores de
  outras branches permanecem fora deste PR.

## 2026-11-04 — Correcao da auditoria de dependencias no PR1

- CI de4782ae6 passou suites Python/PostgreSQL, frontend, navegadores e HTTPS;
  auditoria Python bloqueou a entrega. Atualizados Streamlit1.66.1,
  Authlib1.9.4, certifi2026.10.18, joserfc1.7.6, Pillow13.0.0 e pyasn1 0.6.5
  nos requisitos/locks pertinentes, sem excecoes de vulnerabilidade.
- Auditoria npm/pip-audit repetida sem vulnerabilidades conhecidas; pip check,
  12testes do runner e27focados aprovados. Actionlint, scanner339fontes e prova
  negativa passaram. Auditoria antecipada antes dos navegadores/HTTPS no runner
  e workflow, com teste de bloqueio e reproducao documentada em CI_WEB.
- Regressao Python/PostgreSQL descartavel:369/369, zero skips, em69,246s.
- Hunk preexistente de AGENTS preservado fora dos commits; nenhum deploy.
  CI da HEAD final e merge conferiveis no PR1 e nas execucoes do Actions.

## 2026-11-04 — Diretriz permanente de GitHub Flow e CI

- Responsavel autorizou git/gh para branches curtas, pushes, PRs e squash merge
  quando CI e regras permitirem, sem nova confirmacao rotineira. Sem force push,
  bypass, deploy ou operacoes destrutivas. AGENTS/protocolo alinhados e novo
  CONTRIBUTING com comandos e referencias; hunk local preexistente preservado.
- Diagnostico:67commits WEB em prep-web ainda fora de main, nenhum PR/workflow
  hospedado executado ou protecao remota existente. Branch renomeada para
  feat/evolucao-web. Caminhos de saida conferidos sem novos dados locais/secrets;
  scanner historico apontou um hash de imagem conhecido, nao credencial real.
- Protecao main configurada: PR, verify do GitHub Actions, branch atualizada,
  historico linear e conversas resolvidas, inclusive administradores; force push
  e exclusao de main bloqueados. Sem criar aprovacao humana obrigatoria adicional.
  Repo remove branch temporaria apos merge. Configuracao nao faz deploy.
- CI mantida e enxugada: pushmain/PR/manual, PostgreSQL no digest Compose,
  typecheck feito uma vez pelo build. Teste real Bash/GITHUB_ENV valida DSN;
  nenhuma correcao de printf foi necessaria.11testes do runner e actionlint/YAML/
  Bash passaram no agente. Pipeline hospedado e integracao via PR ainda pendentes.
  Principal confirmou11/11 em0,031s, actionlint,118links locais, scanner de339fontes
  sem achados e diff check. Nenhum deploy ou alteracao em dados operacionais.
  [PR1](https://github.com/thiagorraposo/stroop-go-nogo-psychopy/pull/1) aberto;
  verificacao hospedada iniciou e passou Python/PostgreSQL, scanner e frontend
  na primeira revisao. Resultado da HEAD final/merge e verificavel nos metadados
  do PR e execucoes do Actions, sem fonte paralela de estado mutavel em docs.

## 2026-11-04 — Checkpoint M3: transporte de replica externa validado

- A pedido do responsavel, fechada somente a menor unidade em andamento:
  verificacao do transporte SSH restrito da replica W22, sem instalar agenda,
  restaurar banco, publicar candidato ou avancar etapas. Codigo validado em
  `39dbf378536c16f033152bffe0f6b1e7e6ae30ee`; alteracao preexistente de AGENTS
  raiz preservada. M3 registrado em PROGRESS, sem nova fonte de estado.
- `.venv/bin/python -m unittest tests.test_web_backup_replication -v`:
  10 testes aprovados em0,089s, zero falhas/erros/skips. Transporte real com
  cliente imutavel: `copied` seguido de `already_current`, ambos codigo0,
  sem alerta;69.269bytes, duas geracoes retidas e idade aproximada13,34h.
  A mesma identidade recusou comando de shell `id`; nenhum dado descriptografado
  ou chave AES foi aberto. Evidencia ignorada em exports/w22/20261104.
- Timer local consultado: `not-found`. Permanecem agenda, restauracao isolada
  da replica, atualizacao/smoke publico W22 e aceite de transicao W23. Checkpoint
  inclui HEAD validado, entregas, resultados, limites e proxima acao exata.
  Fontes do cliente imutavel conferidas;51links locais existentes, scanner de
  338fontes sem achados e `git diff --check` aprovado. Sem push ou deploy.

## 2026-10-28 — W21: capacidade e recuperacao medidas na VPS; transicao preparada

### Homologacao fechada no alvo e integracao com privilegios minimos

- Preparada replica externa automatica no destino ja usado pelo responsavel:
  `replicate_web_backup.py` copia somente ciphertext por SSH dedicado, sem agente,
  hostkey estrita, config/chave0600, validacao de formato/tamanho/SHA e publicacao
  exclusiva sem sobrescrever evidencia; retencao30geracoes e alerta apos24h.
  Exportador de comando forcado aceita apenas manifest/download canonico e
  recusa shell, paths, symlinks, plaintext e chaves. Nao le a chave AES.
  Modelos systemd por usuario usam agenda horaria com recuperacao de agenda
  perdida; disponibilidade do computador/rede condiciona o objetivo RPO.
  Dez testes sinteticos e CLIhelp/diff check aprovados. Instalacao, transporte
  restrito real e restauracao da replica ainda serao comprovados emW22.
  Scanner detectou falso positivo no SHA-256 rotulado como pacote da API;
  rotulo esclarecido, hash preservado e338fontes verificadas sem achados,
  sem enfraquecer regras ou adicionar excecao. Commit local anterior foi criado
  antes de tratar a saida; pacote nao foi instalado/publicado antes da correcao.

- Candidato corrigido aprovado na VPS:32/32 verificacoes de interface em dois
  navegadores, incluindo cadastro/edicao/bloqueio201/200 e ultima conta409.
  Um timeout inicial de seletor do harness nao enviou a operacao; evidencia
  preservada e campanha completa corrigida passou. Quatro screenshots sinteticos
  inspecionados; pilhas/tuneis/credenciais de ensaio proprios removidos.
- Nova carga do candidato:870consultas,710sucessos/160respostas429, sem5xx ou
  transporte invalido; oito clientes a1GET/s sem rejeicoes, p9567,11ms. Recuperacao
  no alvo de dez migrations/uma avaliacao em6,013s, alerta e rollback aprovados.
- Backup restaurado e nova copia externa criptografada conferidos antes de reboot
  real. Capacidade administrativa ja existente no Docker permitiu comando efemero
  no namespace do host, sem alterar SSH/sudo ou credenciais. BootID mudou;
  publicacao4/64/48 e candidato1/16/12preservados; detalhe/CSV autenticados
  aprovados e cinco servicos preexistentes saudaveis. Sem medir janela integral
  de indisponibilidade; uptime na verificacao29,08s.
- Consulta somente de agregados confirmou sessao administrativa nao sintetica
  emitida nas ultimas24h. Nenhuma identidade/cookie/hash foi exibido. Callback de
  conta cadastrada permanece igual ao publicado; evidencia operacional existente,
  sem novo login Google interativo. Limites W16 preservados. Aceite W21 registrado
  no roadmap com essas evidencias, sem homologacao temporal universal/coleta real.
- Harness de integracao agora usa o provisionador canonico, writer/reader reais
  restritos e assertions negativas de privilegios; proprietario somente em
  fixtures/migrations e sua DSN ausente do processo API.36/36integracoes em10,9min,
  sem falhas/retries em Chromium/Firefox, tipos/build aprovados.
- Retorno das imagens compativel com schema10 ensaiado na VPS: API anterior com
  somente manifests0009/0010adicionados e proxy anterior saudaveis, consulta/CSV
  e1/16/12preservados; retorno ao candidato manteve dados e administracao201/200.
  Imagem antiga original rejeitaria readiness com migrations adicionais. Nenhum
  restore sobre coletas, migration reversa ou reprovisionamento no retorno.
  Evidencias em [HOMOLOGACAO_WEB](operacao/HOMOLOGACAO_WEB.md) e exports ignorados.

### Correcao de administracao com credencial restrita

- A interface compilada na pilha isolada da VPS aprovou 25 verificacoes de
  consulta, CSV, importacao e convites em Chromium/Firefox, mas cadastro de
  conta retornou503: o adaptador administrativo usava INSERT/UPDATE negados
  pelo papel de runtime. Suites com proprietario nao detectavam essa divergencia.
- Nova migration0010 fornece `web_manage_user`, operacoes fechadas em funcao
  SECURITY DEFINER com search_path fixo, revalidacao do administrador ativo,
  serializacao e protecao do ultimo admin, com auditoria na mesma transacao.
  Provisionamento confere proprietario/definer e concede somente EXECUTE ao
  writer; PUBLIC/reader nao executam. DML direto em app_users segue negado.
- Adaptadores WEB de aplicacao/persistencia usam a capacidade SQL; API conserva
  contratos. Persistencia administrativa legada preservada. Smoke Compose agora
  exige criar/editar conta e proteger o ultimo admin usando o writer restrito.
  Guias Docker/restauracao incluem a nova funcao e remocao de EXECUTE de PUBLIC
  depois de restaurar dump sem grants. Expectativas de migrations atualizadas.
- PostgreSQL real: 13 testes focados aprovados, incluindo cinco novos testes de
  HTTP/auditoria, perfis, grants e concorrencia; suite completa357/357 em72,471s,
  sem skips. Recuperacao Compose com imagem corrigida passou: dez migrations,
  uma avaliacao restauradas em7,012s, alerta/retorno de candidato invalido e
  contagens preservadas. Administracao integrada HTTPS/API/PostgreSQL passou
  em Chromium/Firefox (2/2, 15,2s). Scanner de334fontes sem achados e diff check
  aprovados. Repeticao no alvo ainda pendente; isto nao concede aceite W21/W22/W23.

### Evidencias da campanha anterior

- Autorizacao do responsavel para concluir as etapas restantes; SSH restabelecido.
  Fontes `af73939` e imagens W21 transferidas com checksums conferidos para
  homologacao isolada na VPS, sem substituir a release publica `26fa9bf`.
- Campanha no alvo em 2026-10-27: 870 consultas HTTPS, 710 sucessos validos e
  160 respostas429, sem5xx/erro de transporte. Niveis1/4/8clientes a1GET/s
  sem rejeicoes; oito clientes com p95 de58,73ms. Em16clientes, limitador
  recusou160/480consultas. Nao mede capacidade de participantes ou timing fisico.
- Reinicio dos tres containers preservou1avaliacao/16tentativas/12metricas.
  Recuperacao isolada na VPS: nove migrations/uma avaliacao restauradas em
  5,943s, alerta de banco e retorno de candidato invalido aprovados. Primeira
  chamada falhou antes do ensaio por ausencia de psycopg; wheels das versoes
  do lock extraidos em diretorio privado, sem instalacao global.
- Detectado defeito operacional da release publicada: arquivo
  `compose.restore-test.yaml` ausente fazia restore-check agendado falhar.
  Reposto conteudo identico ao versionado; novo backup e mesma rotina de
  restauracao aprovados. Copia criptografada fora da VPS com checksum conferido;
  destino automatico estavel segue pendente. Nenhum dado pessoal foi aberto.
- Smoke publico: pagina/readiness200, HSTS/CSP e inicio OIDC303para Google.
  Sem login pessoal ou reboot do host; acesso administrativo, confirmacao Google
  e destino externo solicitados ao responsavel. W21/W22 nao recebem aceite
  por presuncao. Evidencias e limites em [HOMOLOGACAO_WEB](operacao/HOMOLOGACAO_WEB.md)
  e [DEPLOY_WEB_VPS](operacao/DEPLOY_WEB_VPS.md); artefatos ignorados em exports/w21.
- Guia do usuario ampliado para fluxos WEB; nova
  [matriz de transicao](operacao/TRANSICAO_WEB.md) cobre historico, coexistencia,
  manutencao, retorno e empacotamento completo por git archive. Nao retira
  PsychoPy/Streamlit nem concede aceite W23. Indice, roadmap e retomada alinhados.
- Regressao salva da execucao anterior: Python352/352 sem skips, frontend273/273,
  tipos/build, navegador98gerais+4temporais aprovados. Integracao interrompida
  antes dos testes nao conta como aprovada; nova verificacao na retomada.
  Documentos: 141 links locais existentes, diff check aprovado e scanner de
  330 fontes versionadas sem achados.
  Alteracao preexistente em AGENTS raiz preservada fora da tarefa.

## 2026-10-21 — W21: pilha local validada; alvo aguarda acesso SSH

- Retomada apos pausa do responsavel. Novo `scripts/benchmark_web.py` cria
  pilha exclusiva HTTPS/API/PostgreSQL e mede consultas autenticadas sem aceitar
  alvo externo. Limites padrao preservados, clientes com pacing de 1 GET/s,
  quatro operacoes, evidencias exclusivas e sem corpos/cookies/DSNs nos arquivos.
  Helpers Compose/recuperacao aceitam imagens explicitas, sem alterar defaults
  dos comandos existentes; recuperacao usa a lista canonica de migrations.
- Encontrada falha real da imagem atual: Nginx recusava regex CSV com `{36}`
  sem aspas. Corrigida delimitacao e acrescentado smoke real de limites:
  rota CSV aceita mais de 64 KiB ate autenticacao; demais mantem 413. O primeiro
  ensaio falhou por essa sintaxe; o segundo corrigiu Content-Type da fixture
  de transporte. Ambos preservados, sem carga medida ou aceite artificial.
- Terceiro ensaio: 870 requisicoes, 710 respostas 200 validas e 160 respostas
  429; nenhum 5xx, erro de transporte ou resposta 200 invalida. Niveis 1/4/8
  clientes ativos a 1 GET/s passaram sem rejeicoes. Em 16, 320/480 sucessos,
  p95 dos sucessos 860,92 ms. Maior nivel testado sem rejeicao: 8, p95 115,42 ms.
  Massa de uma avaliacao; isto nao mede teto de hardware, participantes ou VPS.
  Canarios de sessao ausentes dos logs API/proxy e contagens preservadas apos
  reiniciar os tres containers. Sem reboot do host.
- Mesmas imagens em backup/restauracao/alerta/rollback: 9 migrations e uma
  avaliacao restauradas, integridade e contagens preservadas; ensaio de backup
  + restauracao local em 6,927 s. Nenhuma garantia de RPO/RTO do alvo inferida.
- Regressao Python 352/352 sem skips, com banco novo descartavel; integracao
  HTTPS/API/PostgreSQL Chromium/Firefox 36/36 em 10,9 minutos; typecheck/build
  aprovados. A suite usa proxy HTTPS proprio, complementado pelo Nginx real
  nos ensaios Compose. Nenhuma nova dependencia ou ferramenta instalada no host.
- Artefatos em `exports/w21/`: `capacity-local-20261021{,-r2,-r3}.json`,
  `recovery-local-20261021.json`, `validation-local-20261021.json`, logs
  sanitizados, smoke publico, estado SSH e hashes das fontes. Manifesto com
  10 entradas conferido; metodo, digests e limites em
  [HOMOLOGACAO_WEB](operacao/HOMOLOGACAO_WEB.md). Logs/exports nao versionados.
- Smoke publico fez somente dois GETs: pagina e prontidao 200, HSTS/CSP
  observados. SSH de leitura recusado: chave criptografada nao liberada e
  agente da sessao indisponivel. Tentativa por dialogo grafico nao carregou a
  chave; agente temporario removido. Solicitado acesso sem pedir segredo na
  conversa. Nenhuma alteracao remota, leitura de dado real, deploy ou push.
- W21 continua pendente do ambiente alvo (capacidade, recuperacao/reboot,
  autenticacao externa e aceite); W22/W23 nao avancadas. `AGENTS.md` preexistente
  preservado fora do commit. Conferidos links locais e `git diff --check`.

## 2026-10-20 — W16: evidencia local e encerramento por aceite excepcional

- Responsavel instruiu "produza evidência parcial e trate como completo" apos
  esclarecimento dos limites. Registrado encerramento W16 com escopo reduzido,
  mantendo a matriz fisica original como referencia nao executada. Gates D5,
  motor, API, tempos, estimulos, metricas e CSV permanecem inalterados.
- Nova campanha explicita `cd web && npm run test:w16`: navegadores visiveis
  na sessao X11, Chrome instalado 155.0.8059.84 e Firefox Playwright 157.0,
  teclado automatizado e API double; pratica e principal reais. Dez tentativas
  por navegador, Escape separado, um worker, sem retries ou dependencias novas.
- Campanha de 27,4 minutos: 20 aprovados, 2 falhas, 0 skips, exit 1. Chrome
  10/10 completos validos; Firefox 8/10, tentativa 2 sem terminar pratica em
  25 s e tentativa 4 invalidada pelo gate (864 ms, 42 transicoes preservadas).
  Escape aprovado em ambos. Falhas nao foram apagadas/substituidas ou reclassificadas
  como testes aprovados; causas ainda nao determinadas.
- Lote arquivado localmente em `exports/w16/2026-10-20T13-23-27Z/`: 21 trilhas
  brutas (18 validas, 2 Escape, 1 invalida), relatorio de falhas, inventario,
  agregado e copia do coletor usado. Manifesto com 92 entradas conferido;
  SHA e estatisticas em `VALIDACAO_WEB.md`. Artefatos ignorados pelo Git.
- Coletor separa duracao completa de fim da ultima tentativa em interrupcoes;
  campanha original intacta, agregado calculado diretamente das trilhas.
  Probe do rotulo corrigido em Escape Chrome 1/1; Vitest 273/273,
  typecheck/build, 66 links locais e `git diff --check` aprovados. Nenhum teste Python/API novo
  exigido por alteracoes restritas a coleta de evidencias/docs/frontend de teste.
  Sem dado real, VPS, deploy ou push; `AGENTS.md` preexistente preservado.
  Aceite administrativo W16 nao equivale a homologacao fisica nem conclui W21.

## 2026-10-17 — Instrumentacao local opt-in para pilotos W16

- Motor do bloco principal oferece trilha opcional de transicoes, intervalo de
  quadros e eventos de teclado, inclusive quando uma execucao termina invalida
  ou e interrompida. Captura requer build local `VITE_W16_TIMING_CAPTURE=synthetic-only`
  e query `?w16=1`; o painel guarda em memoria e exporta apenas sob acao explicita.
- Artefato registra ambiente tecnico e nao recebe identificador de participante,
  convite ou dados de resultado. Testes sinteticos cobrem conclusao,
  interrupcao e opt-in. Esta ferramenta nao constitui evidencia nem aceite W16;
  pilotos fisicos nos seis ambientes continuam pendentes.

## 2026-10-17 — Importacao CSV WEB W15E e aceites presumidos

- Entregue migration/auditoria de operacoes CSV, API autenticada por projeto,
  estado consultavel e transacao atomica. Browser redige somente copia em RAM
  (`participant_name=NAO_COLETADO`, `initials` vazio); original nao e enviado
  nem alterado. 5 MiB/10.000 registros na rota dedicada, 64 KiB preservados
  nas demais; temp privado apagado, sem filename/caminho/conteudo nos logs.
- Resultado fica apenas no projeto selecionado; rótulo de CSV legado nao cria
  mapa/associacao. Duplicatas sao rejeitadas; UUID/hash permitem reconsulta e
  repeticao explicita. Provisionamento minimo usa lock emitido para autorizar
  identidade e lock consultivo por assessment ID, sem privilégio de tabela amplo.
- Evidencias: suite Python completa 347/347 sem skips; Vitest 271/271,
  TypeScript/build; Playwright geral e temporal; upload real HTTPS/API/PostgreSQL
  ate consulta, detalhe e exportacao em Chromium/Firefox 2/2; suite de integracao
  completa 36/36 em Chromium/Firefox; teste com papeis provisionados writer/reader;
  `git diff --check`. Somente dados
  sinteticos e banco descartavel. Sem dependencia nova, deploy, VPS ou push.
- O responsavel instruiu explicitamente presumir todos os aceites; W09A visual
  e W13A operacional foram aceitas por essa instrucao. A instrucao nao cria
  evidencias de piloto fisico ou capacidade. W16/W21 permanecem limitadas por
  evidencia real indisponivel. Inventario local parcial W16: Linux Mint 22.2,
  painel eDP 1920x1080/60 Hz, Chrome 155/Firefox 158; teclado USB com fio e Edge
  nao identificados; Windows 11 indisponivel. Nenhuma replica fisica executada.

## 2026-10-17 — Percurso do participante WEB W09A

- Abertura e tutorial organizam a regra em exemplos visuais e passos curtos.
  Indicador de percurso cobre orientacoes, convite, pratica e tarefa;
  preparacao/transicao e encerramento receberam acoes e estados mais claros.
  A conclusao aparece somente apos recibo; falha de logout preserva o resumo e
  permite nova tentativa. Foco programatico ganhou contorno visivel.
- Preservados motor, condicoes, cores, temporizacao, HUD, feedback da tarefa,
  teclas/foco/Escape e contrato CSV. Capturas comparativas usam somente dados
  sinteticos em `/tmp/stroop-w09a-*`.
- Evidencias: 268 testes Vitest, typecheck/build; Playwright geral94/94,
  temporizacao4/4 e integracao HTTPS/PostgreSQL2/2 Chromium/Firefox; `git diff
  --check` aprovado. Aceite visual do responsavel continua pendente. W15E segue
  aguardando decisao de minimizacao antes de upload.

## 2026-10-17 — Administracao de contas/projetos W15D

- Area WEB exclusiva do perfil `administracao` lista contas paginadas, cadastra
  identidade Google `iss` + `sub`, altera perfil/estado/e-mail auxiliar e
  confirma mudancas. Callback OIDC de identidade verificada nao cadastrada
  apresenta somente seus proprios identificadores para solicitacao institucional,
  sem criar sessao/autocadastro. API tem schemas fechados, CSRF/origem,
  autorizacao por operacao, auditoria sem claims/e-mail e lock transacional que
  preserva pelo menos um admin ativo sob concorrencia.
- Administracao de projetos/membros reaproveita as rotas existentes; nao ha
  acesso automatico a resultados, exclusao, alteracao de projeto ou mapa legado.
  UI explicita vinculos, mostra e-mail somente no contexto admin e revalida
  bloqueio/revogacao no servidor sem apagar coletas.
- Evidencias:341 testes Python sem skips;268 frontend;build/typecheck aprovados;
  browser geral90/90 e temporal4/4 Chromium/Firefox, com seletor de perfil ajustado apos a
  navegacao administrativa adicionar um segundo texto homonimo. HTTPS/PostgreSQL
  reais2/2 Chromium/Firefox cobrem cadastro, criacao/vinculo, convite via UI W13A,
  resultado sintetico pelo endpoint real, consulta, revogacao e bloqueio. Testes
  PostgreSQL comprovam pagina de contas/membros, CSRF, perfil negativo, email
  omitido da resposta de membros, ultimo admin e corrida concorrente. `git diff
  --check` aprovado. Sem migration/dependencias, dados/coletas identificaveis,
  deploy, push ou acesso remoto; `AGENTS.md` preexistente preservado.
- Roadmap, contrato API, autenticacao/permissoes, UX, README e PROGRESS
  sincronizados. Proxima W15E depende da decisao de contrato/minimizacao; W13A
  permanece implementada com aceite operacional pendente.

## 2026-10-17 — Exportacao agregada autorizada W15C

- Adicionado contrato de CSV agregado por instrumento, uma linha por avaliacao,
  com metadados tecnicos permitidos, unidades explicitas e sem nomes/iniciais,
  paths, IDs de sessao ou metricas nao registradas. UTF-8 sem BOM, CSV padrao
  com CRLF, protecao de formulas em celulas textuais, ausencias vazias e numeros
  preservados sem arredondamento. Arquivo e rota separados do CSV oficial de
  tentativas e nao sao aceitos pelo importador.
- Listagem entrega snapshot HMAC opaco, vinculado a ator/projeto/filtros e valido
  por15min. Fingerprint inclui dados usados na tabela e nos summaries (tentativas
  principais Stroop e metricas genericas). Exportacao POST valida CSRF/origem,
  reautoriza todos os projetos, compara os snapshots e limita20projetos/5000
  avaliacoes numa transacao READ ONLY/REPEATABLE READ. Revogacao/alteracao/erro
  nao retorna arquivo; resposta usa nome fixo/no-store e nao persiste no servidor.
- Interface so habilita a acao com todas as paginas/projetos e snapshots
  consistentes; instrumento e plataforma seguem a visao selecionada. Tokens e
  blob ficam em memoria local apenas durante a acao, com cancelamento em troca
  de consulta, detalhe, instrumento, plataforma ou desmontagem. CSV individual
  continua disponivel no detalhe.
- Evidencias:339 testes Python/62,766s sem skips;264 testes frontend;browser
  geral86/86 e focado14/14 em Chromium/Firefox. HTTPS real/PostgreSQL4/4 em19,3s:
  105 avaliacoes em multiplas paginas e dois projetos, filtros combinados,
  valores Stroop, metricas demonstrativas isoladas e revogacao impedindo arquivo.
  `npm audit --omit=dev --audit-level=high` sem vulnerabilidades, build/typecheck,
  pip check e scanner303 fontes aprovados. Nenhuma dependencia, migration, dado
  real, deploy ou push.
- Roadmap, contrato HTTP, UX, README e PROGRESS sincronizados. Proxima etapa
  elegivel W15D; W13A permanece pendente de aceite operacional.

## 2026-10-17 — Tabela, detalhe e visualizacoes por instrumento W15B

- Summary profissional fechado de onze campos acrescenta precisao e totais
  Go/No-Go recalculados pelo nucleo; denominador ausente gera null em summary
  e metricas do detalhe, incluindo percentual de omissoes sem Go. Recibo do
  participante de sete campos, formulas e CSV oficial inalterados. Cliente
  rejeita shape antigo/incompleto; consultas/facetas rejeitam whitespace puro.
- ResultsTable apresenta colunas permitidas, avaliador tecnico e quatro
  contagens; detalhe identifica IDs/projeto, inicio/conclusao, versoes, protocolo,
  aplicativo e observacoes. Nenhum path/arquivo fonte/nome/iniciais acrescentado.
- ResearchVisualizations compara erros por projeto e seleciona participante
  por projeto+codigo, mantendo visitas repetidas e ordem inicio+ID; precisao
  e RT mediano em figuras separadas com tabela alternativa. Rotulo inicial
  indevido de tempo medio corrigido antes da validacao. Demo registrada possui
  cards/graficos/tabela de demo_total/count e demo_mean/unit; desconhecidos
  permanecem tabela neutra. Valores negativos/ausentes preservados, sem N+1.
- Evidencias:329 testes Python/51,984s sem skips;261 frontend (incluindo6DOM
  novos/69cliente), typecheck/build/npm ci/audit sem achados, compileall/pipcheck
  e diff aprovados. Browser geral72/1,1min aprovado; quatro temporais W15A
  permanecem evidencia do motor/fluxo participante nao alterados nesta unidade.
- HTTPS real:W15B+W15A4/4 em28,6s; revalidacao perfis/detalhe/CSV individual e
  visuais8/8 em29,6s, Chromium/Firefox, sem erros JS. Importacao pelo nucleo de
  Stroop e demo, Go/No-Go/sem hits,16tentativas, ausenciaRT, metadados, repeticao
  de visita, identidades por projeto e valores demo comprovados sem mocks.
- Capturas sinteticas /tmp/stroop-w15b-*.png inspecionadas. Ajustada especificidade
  CSS para scroll local da tabela ampla; nova assercao comprovou scroll local
  e ausencia de overflow de pagina,390px e desktop/zoom200% (Chromium1/1 em6,1s).
  Contrato/UX/README atualizados. Sem schema/dependencias/deploy/push/dados reais.
  Proxima elegivel W15C, CSV agregado com reautorizacao e consistencia do conjunto.

## 2026-10-17 — Filtros combinados e agregado autorizado W15A

- Listagem profissional recebe periodo inclusivo sobre assessment_date e listas
  OU por campo/E entre campos de participantes, visitas, avaliadores tecnicos,
  versoes e plataformas; instrumento unico. Consultas historicas conservam texto
  ate 512 caracteres sem ampliar cadastro WEB64ASCII ou ler nomes/iniciais.
- Facetas SELECT por projeto/periodo/instrumento, limite200 por campo ou422;
  cursor HMAC vinculado a escopo/filtros canonicos e fingerprint do conjunto,
  com409 se houver alteracao entre paginas. Teto5000 por projeto, sem truncamento.
- Interface multisselecao ate20projetos/5000linhas, publica apenas depois de
  completar todas as paginas; qualquer falha limpa agregado. Participantes
  usam projeto+codigo; detalhe/CSV preservam projeto da linha. Evolucao anterior
  restrita a um projeto, evitando fusao de pseudonimos. Sem exportacao agregada
  nova (W15C), proveniencia nominal ou associacao automatica do legado.
- Evidencias:326 testes Python/54,018s sem skips;236 frontend, typecheck/build,
  pip check e diff aprovados. Testes focados cliente50 e browser24 aprovados.
  Suite completa browser:70 gerais/1min e4 temporais seriais/3,5min aprovados.
  Motor/protocolo/CSV individual preservados; nao concede homologacao fisica.
- HTTPS/PostgreSQL reais:2/2 Chromium/Firefox em20,5s com105avaliacoes, paginas
  reais, pseudonimos coincidentes, filtros combinados/limites inclusivos, valores
  dos sete cards/graficos, perda de vinculo, recuperacao/vazio/limpeza; emissao
  e revogacao W13A pela interface incluídas. Fixture inicial sem trials foi
  corrigida antes do aceite; nenhum erro de produto mascarado por simulacao.
  Consulta W13A revalidada2/2 em6,8s. Viewport390 e desktop/zoom200% aprovados.
- Capturas sinteticas form/cards em /tmp/stroop-w15a-*.png inspecionadas;
  grid corrigida e projetos ampliados antes da ultima revalidacao Chromium1/1.
  Sources scanner aprovado, contratos/UX/README atualizados. Sem dependencias,
  schema, deploy, push ou alteracao de coleta existente. Proxima elegivel W15B.

## 2026-10-17 — Cadastro WEB pela equipe, validacao tecnica W13A

- SessionInvitation e cliente sessions integrados a area profissional: codigo
  pseudonimizado/visita, projeto e avaliador autenticado, emissao/revogacao,
  espera, erros fechados, resultado desconhecido e limpeza de RAM. Sem backend
  novo, migration ou mudanca no protocolo. Preparar outra sessao nao revoga a
  anterior; cancelamento local nao presume desfazer operacao remota.
- Correcao encontrada na integracao: selecionar novamente o projeto atual
  limpava a lista sem disparar nova consulta. Mantida lista quando nao ha troca.
- npm ci/audit sem achados; 211 testes frontend, typecheck/build aprovados.
  Suite geral Chromium/Firefox:58/58 em57,1s. Convites focados:18/18 em11,6s,
  incluindo teclado/foco, perfis, projeto inativo, trim/erros, duplo envio,
  rede sem retry, troca de projeto/resposta tardia e logout. Screenshot sintetico
  /tmp/stroop-w13a-invite.png inspecionado; acrescentados espacamento e quebra
  de codigos longos. Sem alegacao de homologacao temporal fisica.
- HTTPS/PostgreSQL reais: cinco de seis cenarios passaram no primeiro ensaio,
  inclusive os dois percursos de60s e CSV com participante/visita/avaliador,
  revogacao e zero resultado parcial. Falha de consulta Chromium identificou a
  correcao acima; reexecucao focada passou nos dois navegadores (2/2 em7,1s).
  Testes usam banco descartavel stroop_etapa4_test_w13a, sem dados reais.
- README WEB e UX documentam operacao e limites. Aceite do responsavel para
  operar a interface permanece pendente; W13A nao e declarada concluida.
  W15A pode avancar independentemente. Sem publicacao, push ou acesso a VPS.

## 2026-10-16 — Relatorio tecnico de funcionamento

- Criado desenvolvimento/RELATORIO_TECNICO.md para leitores externos, reunindo
  experimento, tempos, metricas com exemplo sintetico, arquitetura, percurso dos
  dados, autorizacao e limites de validacao; referencias mantidas nas fontes.
- Adicionada entrada no indice documental. Nenhuma formula, contrato ou
  funcionalidade alterada; etapas futuras nao sao descritas como concluidas.

## 2026-10-16 — Comparacao e planejamento de paridade do dashboard

- Comparados Streamlit e WEB por codigo/contratos, incluindo filtros, cards,
  graficos, tabela, detalhe, instrumentos, exportacoes, importacao e administracao.
  Revisao independente confirmou diferenca entre API pronta e interface ausente
  em projetos/vinculos e falta de API/interface de contas/upload.
- Roadmap recebeu matriz com fontes e complementos W15A–W15E, dependencias,
  criterios de aceite e validacoes previstas. Atualizado estado W15 para
  distinguir painel inicial validado de paridade ainda pendente; aceite W21/W22
  e transicao W23 devem cobrir os recursos novos.
- Mantidas minimizacao WEB, identidade tecnica, mapa explicito ADR-003,
  exclusao de dados identificaveis das novas superficies e coexistencia legada.
  CSV agregado planejado nao altera CSV oficial individual de21colunas.
- Somente documentacao; nenhuma implementacao, publicacao ou coleta executada.

## 2026-10-16 — Planejamento do cadastro WEB da sessao

- Apos apontamento do responsavel e consulta ao formulario legado, registrada
  W13A no roadmap: cadastro pela equipe, campos permitidos, avaliador vinculado
  a conta autenticada, emissao/revogacao de convite e aceite ponta a ponta real.
- Corrigida a leitura do estado: integracao anterior preservada, mas cadastro
  completo pelo navegador ainda pendente. Incluido W13A no gate funcional W21
  e no aceite da publicacao W22. W16 e coleta real nao sao liberadas por isso.
- Atendido o limite documental solicitado; nenhum codigo, teste funcional ou
  deploy executado. Validacao desta unidade limitada aos documentos/links/diff.

## 2026-10-16 — Correcao de compatibilidade do retorno Google em producao

- Relato de invalid_oidc_state reproduzido: callback rejeitava metadados
  adicionais Google antes de conferir state. Allowlist conhecida ampliada,
  validacao do emissor quando presente e protecoes anteriores preservadas.
- 322 testes Python aprovados, incluindo callback legado com metadados,
  sessao profissional e rejeicao de replay/parametros invalidos.
- Fonte26fa9bf publicada na VPS com backup previo e retorno preparado;
  somente API atualizada, sem migration. HTTPS readiness200, monitor0 e tres
  servicos saudaveis. Smoke sintetico publico aceita metadados, nega codigo
  invalido/replay e nao cria sessao. Confirmacao pessoal continua pendente.

## 2026-10-16 — Publicacao WEB explicitamente delegada na VPS

- Responsavel autorizou substituir o site mantendo dominio/TLS/OIDC e dados.
  Pilha anterior, volume e conta preservados; backups banco/configuracoes/
  Certbot criptografados/autenticados, restore real e copias externas conferidas.
- Nova pilha paralela validada antes do cutover de6,444s em01:11:40Z/17outUTC.
  Novo banco isolado recebeu copia e migrations0004–8/grants; nada apagado no
  original. API/proxy nao-root/RO, somente proxy80/443, logs limitados no overlay.
- OIDCcallback legado opt-in preservado, Python317/317 e proxy6/6 aprovados.
  Preflight e dominio publico: convite/conclusao/retry/consulta/CSV; navegador
  executou pratica+principal60s, gravacao16tentativas/12metricas e logout.
- Certbot passou awebroot; dryrun e hook reais aprovados. Rotinas de monitor,
  backup diario e restore semanal instaladas e verificadas; rollback preserva
  ambos os bancos. Runbook operacional DEPLOY_WEB_VPS publicado.
- Confirmacao da sessao Google pessoal solicitada; replica externa automatica
  depende de destino estavel. W16/W21 nao homologadas; somente testes sinteticos.

## 2026-10-16 — W16: pacote de referencia aprovado

- Responsavel aprovou integralmente o pacote registrado em VALIDACAO_WEB.md:
  duas plataformas, tres navegadores e dez replicas por combinacao; parametros
  de equipamento e criterios D5 preservados. Sem medicoes ou aceite inferidos.
- Pendencia passou de escolha da configuracao para disponibilidade/inventario
  dos equipamentos e execucao dos pilotos fisicos. Nenhuma alteracao do motor.

## 2026-10-16 — W20: observabilidade e recuperacao WEB

- Monitor local somente leitura com saude/contagens e alerta fechado, sem dados
  de participantes ou endpoint publico. Falhas e privacidade cobertas em4testes.
- Backup existente reutilizado; servico Compose admite hifen sem relaxar SQL,
  regressao especifica aprovada. Restore usa envvazio explicito e verifica
  integridade WEB. Hardening21/21 aprovado com PostgreSQL sintetico.
- Ensaio real aprovado: dump criptografado, restauracao isolada de8migrations/
  1coleta em7,083s, falha de banco detectada, candidato invalido e retorno a
  imagem aceita com contagens preservadas. Nenhum recurso da previa interrompido.
- Runbook registra RPO24h/RTO4h aprovados como objetivos, grants apos restore,
  rollback compativel sem apagar coletas e limites de homologacao em VPS.

## 2026-10-16 — W19: pacote WEB e acesso sintetico local

- Imagens API/proxy separadas do legado, nao-root, contextos permitidos,
  filesystem RO, redes internas, portas somente do proxy e secrets externos.
- Migrations/provisionamento explicitos; writer/reader separados e funcao de
  lock da migration0008 sem UPDATE de usuarios no runtime. Testes de grants,
  rollback e concorrencia aprovados. Fixture antiga de upgrade preservada.
- Smoke HTTPS real aprovado: coleta, retry, consulta/exportacao e reinicio do
  banco com persistencia. Corrigida lista YAML de tmpfs e verificacao de portas
  via bindings reais do Docker. Scanner inclui templates/exemplos e recusou
  placeholder antigo; exemplo agora usa marcador curto sem segredo ficticio.
- Previa sintetica local disponibilizada; navegador acessou build compilado
  e tela de convite sem erros JS. Sem deploy, dados reais ou aceite temporal.

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
