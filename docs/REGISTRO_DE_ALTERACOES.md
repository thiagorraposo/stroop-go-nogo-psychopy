# Registro de alteracoes

Este arquivo preserva fatos datados; nao define estado ou aceite vigente.
Consulte o [backlog canonico](Projeto%20Stroop%20Test.md).

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
