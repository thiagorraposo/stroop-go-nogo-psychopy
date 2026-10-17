# Roadmap WEB — execucao incremental

Este arquivo e a unica fonte de escopo, dependencias, aceite, estado e proxima
etapa da evolucao web. O [backlog legado](legado/Projeto%20Stroop%20Test.md) conserva
seu proprio escopo e progresso; seus 87% nao medem a implementacao web.
Decisoes tecnicas: [ADR-001](arquitetura/ADR-001-evolucao-web.md).
Mapa de arquivos: [estrutura](ESTRUTURA_DO_PROJETO.md).

## Estado e retomada

| Etapas | Estado |
|---|---|
| W00 | Concluida em 2026-10-16; evidencias no registro de alteracoes |
| W01 | Concluida em 2026-10-16; D1–D6 aprovadas e fontes/39 testes focados validados |
| W02 | Concluida em 2026-10-16; contrato HTTP e cenarios, seis JSONs e links validados |
| W03 | Concluida em 2026-10-16; matriz de acesso/finalidades e cenarios negativos revisados, 16 links validados |
| W04 | Concluida em 2026-10-16; casos de uso/persistencia extraidos, 173 testes e smoke na imagem aprovados |
| W05 | Concluida em 2026-10-16; API FastAPI, limites/erros seguros, readiness real PostgreSQL, 189 testes e smoke Uvicorn |
| W06 | Concluida em 2026-10-16; OIDC, sessao segura, CSRF, autorizacao e limites de login |
| W07 | Concluida em 2026-10-16; ciclo de sessao, autorizacao, limites e migrations validados |
| W08 | Concluida em 2026-10-16; conclusao atomica, protocolo/tempos, recalculo e replay validados em 240 testes |
| W09 | Concluida em 2026-10-16; React/TypeScript, cliente HTTP, 36 testes DOM/logica e 10 browser aprovados |
| W10 | Concluida em 2026-10-16; pratica jsPsych, 77 testes logica/DOM, 18 browser e regressao Python 240 aprovados |
| W11 | Concluida em 2026-10-16; motor jsPsych, 120 testes logica/DOM e 24 browser aprovados |
| W12 | Concluida em 2026-10-16; resumo, CSV de 21 campos, paridade Python/TypeScript e importacao real validados |
| W13 | Integracao anterior validada; fluxo completo de cadastro pela interface pendente em W13A |
| W13A | Planejada; cadastro da sessao pela equipe e gestao do convite ainda nao implementados na interface |
| W15 | Concluida; painel autorizado, metricas/graficos/CSV e perfis validados em HTTPS real |
| W16 | Pacote de referencia aprovado; bloqueada por disponibilidade dos equipamentos e evidencias dos pilotos |
| W17 | Concluida; hardening, CSP, 284 testes Python, HTTPS e auditorias aprovados |
| W18 | Concluida; pipeline completo em checkout sparse limpo, testes e auditorias aprovados |
| W19 | Concluida; imagens nao-root, Compose isolado e smoke HTTPS/coleta/reinicio aprovados |
| W20 | Concluida; monitor, backup criptografado/restauracao isolada, alerta e rollback validados |
| W21 | VPS definida/inventariada; pendentes W16, capacidade e aceite de homologacao |
| W23 | Nao iniciada; depende da implantacao/aceite W22 |
| W14 | Concluida em 2026-10-16; consulta/CSV autorizados, papel SELECT, mapa legado e testes PostgreSQL validados |
| W22 | Publicada na VPS por delegacao explicita, somente testes sinteticos; confirmacao Google pessoal pendente |

As evidencias anteriores de W00–W15 e W17–W20 permanecem validas para os escopos
testados; a lacuna funcional W13A impede considerar completo o fluxo de cadastro
e execucao pelo navegador. W13A e a proxima prioridade de implementacao, antes
do aceite funcional W21/W22. Por instrucao mais recente, esta unidade se limita
ao planejamento documental; nao inicia codigo, testes funcionais ou publicacao.
A publicacao de testes W22 foi explicitamente
delegada e executada; W16 e W21 continuam pendentes. Nenhuma dessas pendencias
concede conclusao geral ou autoriza coleta real. Retomada detalhada em
[PROGRESS.md](PROGRESS.md). Evidencias em
[registro de alteracoes](REGISTRO_DE_ALTERACOES.md).
Bloqueio de produto/metodo resolvido pela aprovacao explicita na sessao.
Finalidade: coleta do grupo de pesquisa do usuario; participantes da pesquisa
sem restricao demografica nova. Usuario responsavel por protocolo, validacao,
operacao e incidentes. Hospedagem: VPS adquirida e dominio existente, conforme
[ADR-002](arquitetura/ADR-002-hospedagem-vps.md). Configuracao real, evidencias
de homologacao, OIDC e backup externo permanecem entregas futuras; nao bloqueiam
implementacao local com dados sinteticos nem equivalem a aceite antecipado.
Nao atribuir percentual por quantidade de etapas: elas possuem esforcos distintos.

Comandos para o Codex CLI, a partir da raiz do repositorio:

- `continue web`: retomar a primeira etapa elegivel e continuar automaticamente
  pelas proximas tarefas viaveis, respeitando dependencias e prioridades.
- `execute Wxx`: iniciar pela etapa indicada, com dependencias concluidas, e
  continuar o ciclo, salvo limite explicito do usuario.
- `mostrar status web`: somente leitura deste estado e das evidencias.
- `validar etapa web Wxx`: revalidar a etapa indicada, sem iniciar outra.

O [protocolo](desenvolvimento/WORKFLOW_CODEX_CLI.md) detalha as regras comuns e as condicoes
reais de parada. Acoes de producao dependem do usuario; solicitacoes somente
documentais ou de consulta nao iniciam o roadmap nem retomam objetivos pausados.

### Contexto minimo por sessao

1. Ler `AGENTS.md`, este estado e a ficha da etapa; consultar os `AGENTS.md`
   aplicaveis aos arquivos que serao alterados.
2. Ler o ADR e apenas os contratos indicados em **Leitura**. O mapa estrutural
   substitui uma nova varredura completa do projeto. Conferir Git e os trechos
   afetados; investigar novamente somente divergencias concretas.
3. Apresentar plano curto; implementar o entregavel da etapa, sem antecipar
   trabalho com dependencias pendentes. Integrar e revisar tarefas delegadas.
4. Executar as validacoes da ficha e a regressao afetada. Documentacao pura
   exige links e diff; nao precisa iniciar banco ou servicos.
5. Atualizar a linha da etapa neste arquivo conforme as evidencias e adicionar
   evidencia datada ao registro. Ao separar uma etapa concluida do intervalo,
   manter uma unica linha de estado por ID. Registrar comandos, resultados e
   decisoes pendentes.
6. Salvar contexto conciso em [PROGRESS.md](PROGRESS.md), fazer commit local
   coerente apos validacao e iniciar a proxima etapa elegivel automaticamente.
   Se houver bloqueio localizado, registrar e selecionar trabalho independente;
   encerrar somente nas condicoes do protocolo ou por limite expresso do usuario.

Nao copiar contratos ou tabelas de progresso para READMEs. Quando uma decisao
alterar arquitetura, escrever outro ADR; quando alterar paradigma, registrar
primeiro em `experimento/DECISOES_DO_EXPERIMENTO.md`. Nao considerar aceite funcional como
validacao psicometrica.

### Validacao comum

- Usar apenas fixtures e bancos sinteticos descartaveis; nunca `data/`,
  `database/`, secrets ou coletas existentes.
- Mudancas Python: testes focados e suite `unittest` existente. Integracoes
  exigem `TEST_DATABASE_URL` em banco cujo nome comece por `stroop_etapa4_test`.
  Skips de integracao nao concedem aceite de uma etapa que depende de banco.
- Preservar CLIs por caminho e modulo, launchers, CSV oficial e dashboard.
- Depois de existir codigo web: testes de logica/DOM, TypeScript e build.
  Testes ponta a ponta validam fluxo; nao certificam latencia fisica do hardware.
- Desde a primeira rota protegida: autorizacao negativa, erros sanitizados,
  limites de entrada e ausencia de dados sensiveis em logs.
- Sempre `git diff --check`; mudancas de imagem exigem build e smoke isolado.
- Versoes e documentacao externa sao verificadas na etapa que instala a
  dependencia. Fixar dependencias e lockfiles; nao atualizar as existentes
  incidentalmente.

Para repetir a suite de banco, criar container exclusivo, sem volume operacional:

```bash
docker run --detach --rm --name stroop-web-test \
  --tmpfs /var/lib/postgresql/data:rw \
  -e POSTGRES_DB=stroop_etapa4_test_web \
  -e POSTGRES_USER=synthetic -e POSTGRES_PASSWORD=synthetic-local-only \
  -p 127.0.0.1::5432 postgres:17.6-bookworm
docker exec stroop-web-test pg_isready -U synthetic -d stroop_etapa4_test_web
docker port stroop-web-test 5432/tcp
```

Aguardar a prontidao; substituir `PORTA` pela porta retornada, sem ler `.env`:

```bash
TEST_DATABASE_URL=postgresql://synthetic:synthetic-local-only@127.0.0.1:PORTA/stroop_etapa4_test_web \
  .venv/bin/python -m unittest discover -s tests -v
docker stop stroop-web-test
```

O ciclo pode ser refeito por sessao. Interromper somente o container criado
para o teste. O PostgreSQL 17.6 e a referencia atual do projeto, nao uma
recomendacao para manter essa versao em producao futura sem revisao.

Uma fase se conclui quando todas as suas etapas possuem aceite comprovado.
Dependencias, criterios de conclusao e validacoes detalhados nas fichas abaixo
compoem o aceite da respectiva fase; o registro de pendencias nao concede aceite.

## Fase 0 — Preparacao estrutural

Objetivo: tornar as regras reutilizaveis preservando a operacao existente.
Entregavel da fase: nucleo extraido, compatibilidade e plano verificavel.

### W00 — Estrutura, arquitetura e roadmap

- **Objetivo:** preparar a evolucao sem implementar funcionalidade web.
- **Entregaveis:** pacote `stroop/domain` e `stroop/ingestion`, compatibilidade
  em `scripts`, copia do pacote na imagem, READMEs em `api/` e `web/`, mapa,
  ADR, roadmap e instrucoes de retomada.
- **Dependencias:** baseline e inspecao do sistema atual.
- **Conclusao:** regras extraidas sem alteracao de semantica; comandos antigos
  funcionando; nenhuma rota, tela, dependencia ou migration web criada.
- **Validacoes:** regressao integral sintetica, testes de imports e CLIs,
  comparacao das definicoes movidas, links, Compose, build e smoke da imagem.
- **Leitura:** `legado/BASELINE_ETAPA_1.md`, `ESTRUTURA_DO_PROJETO.md` e ADR-001.

## Fase 1 — Especificacao e contratos

Objetivo: fechar comportamento e fronteiras antes da implementacao.
Entregavel da fase: protocolo, contrato HTTP e decisoes de acesso/dados.
Dependencia da fase: W00; concluir as tres fichas antes de persistir sessoes web.

### W01 — Protocolo e aceite experimental web

- **Objetivo:** fixar a versao web e seus limites de medicao.
- **Entregaveis:** `docs/experimento/PROTOCOLO_WEB.md` referenciando as regras canonicas;
  matriz de fluxos e casos de resposta, politica de foco/interrupcao, navegadores
  e dispositivos suportados, criterio temporal verificavel e versao da tarefa.
- **Dependencias:** W00.
- **Conclusao:** decidir com o usuario o MVP desktop/teclado, politica de aba,
  repeticao de pratica e identificacao da variante web; separar comportamento
  atual de propostas antigas. Nao mudar silenciosamente tempos ou HUD.
- **Validacoes:** conferir `.psyexp` e condicoes; cobrir pratica, quatro tipos
  de resposta, limites da janela, tecla mantida, abortamento e ausencia de hits.
  Revisar exemplos antigos do CSV contra suas 21 colunas oficiais.
- **Leitura:** `experimento/DECISOES_DO_EXPERIMENTO.md`, `experimento/VALIDACAO_CONDICOES.md`,
  `experimento/CSV_UNIFICADO.md` e `legado/ESPECIFICACAO_VISUAL_E_FLUXO.md` (proposta historica).

### W02 — Contrato de sessao, resultados e HTTP

- **Objetivo:** especificar o intercambio entre navegador e backend.
- **Entregaveis:** `docs/desenvolvimento/CONTRATO_API_WEB.md` com operacoes, payloads sinteticos,
  estados de sessao, erros, limites, idempotencia, timestamps e unidades.
- **Dependencias:** W01.
- **Conclusao:** distinguir protocolo, versao do app e plataforma de coleta;
  definir RT de transporte e conversao para segundos; separar metadados web do
  CSV de 21 colunas. `NormalizedAssessment` nao vira contrato HTTP por acidente.
- **Validacoes:** percorrer criacao, conclusao, conflito, reenvio, expiracao,
  interrupcao e resultado invalido; definir verificacao de quantidade, condicoes,
  versao, ordem efetivamente apresentada e janela de resposta.
- **Leitura:** protocolo web, `experimento/CSV_UNIFICADO.md` e `dados/MODELO_DE_DADOS.md`.

### W03 — Acesso, participantes e minimizacao de dados

- **Objetivo:** definir o acesso remoto antes da primeira coleta.
- **Entregaveis:** `docs/seguranca/ACESSO_WEB.md`, matriz de autorizacao por operacao,
  escopo por projeto/avaliador e atualizacao do threat model/tratamento de dados.
- **Dependencias:** W02.
- **Conclusao:** decidir acesso supervisionado ou convite, expiracao e uso unico,
  identidade de participantes, dados permitidos no servidor e finalidade de cada
  campo. Nome/iniciais hoje locais nao sao transmitidos automaticamente.
- **Validacoes:** cenarios de acesso cruzado, token vazado/reutilizado, bloqueio,
  consentimento aplicavel e exportacao; registrar decisoes do usuario pendentes,
  sem inventar finalidade ou politica de retencao.
- **Leitura:** `seguranca/AUTENTICACAO_E_PERMISSOES.md`, `experimento/FORMULARIO_DE_SESSAO.md`,
  `seguranca/THREAT_MODEL.md` e `seguranca/TRATAMENTO_DE_DADOS.md`.

## Fase 2 — Backend reutilizavel

Objetivo: expor o nucleo por HTTP sem duplicar regras ou depender do Streamlit.
Entregaveis: casos de uso, adaptadores de persistencia e API autenticada minima.
Dependencias da fase: W01–W03 para os contratos; W04 preserva comportamento.

### W04 — Extracao da persistencia e dos casos de uso

- **Objetivo:** separar a logica de importacao da execucao CLI.
- **Entregaveis:** modulos concretos em `stroop/application/` e
  `stroop/persistence/`, criados somente ao mover os casos reais; CLIs delegam.
- **Dependencias:** W00.
- **Conclusao:** transacoes, duplicidade, `--force`, metricas, erros e SQL
  continuam equivalentes; dominio nao importa drivers nem scripts. Evitar
  repositorios genericos ou unificar validadores com semanticas diferentes.
- **Validacoes:** suite SQLite/PostgreSQL, rollback, concorrencia, paridade e
  CLIs; conservar caminhos e hashes das migrations ja aplicadas.
- **Leitura:** `dados/IMPORTACAO_SQLITE.md`, `dados/IMPORTACAO_POSTGRESQL.md`,
  `dados/MIGRACOES_POSTGRESQL.md` e os importadores atuais.

### W05 — Base HTTP, configuracao e testes da API

- **Objetivo:** criar o primeiro adaptador FastAPI sem rotas de coleta.
- **Entregaveis:** ponto de entrada em `api/`, configuracao por ambiente,
  dependencias fixadas, health/readiness e tratamento seguro de erros.
- **Dependencias:** W02, W04.
- **Conclusao:** processo inicia sem Streamlit; falha de configuracao e
  indisponibilidade de banco sao tratadas; regras permanecem no nucleo.
- **Validacoes:** cliente de teste HTTP, configuracao ausente, readiness,
  erros sem conexoes/secrets no corpo e suite Python existente.
- **Leitura:** contrato HTTP, ADR-001 e `operacao/HARDENING_PRODUCAO.md`.

### W06 — Autenticacao e autorizacao HTTP

- **Objetivo:** proteger a API com identidade verificada no servidor.
- **Entregaveis:** adaptador OIDC, sessao segura e autorizacao reutilizavel;
  extrair partes de `dashboard/auth.py` somente quando necessario, com compatibilidade.
- **Dependencias:** W03, W05.
- **Conclusao:** validar assinatura, emissor, audiencia e expiracao antes de
  autorizar; preservar `iss` + `sub`, bloqueio e perfis. Claims JSON fornecidos
  pelo cliente nao substituem validacao criptografica. Definir CSRF conforme a sessao.
- **Validacoes:** identidade/chave RSA sinteticas, assinatura invalida, emissor,
  audiencia, nonce, token vencido, usuario bloqueado, perfil insuficiente e
  regressao da autenticacao Streamlit. Sem credenciais Google reais em testes.
  Acesso cruzado entre projetos sera validado em W14, quando a API consultar
  objetos de projeto; W06 ainda nao possui essa superficie HTTP.
- **Leitura:** acesso web e `seguranca/AUTENTICACAO_E_PERMISSOES.md`.

## Fase 3 — Sessoes e persistencia web

Objetivo: receber uma execucao completa de forma autorizada e atomica.
Entregaveis: ciclo de sessao e persistencia validada; ainda testaveis sem frontend.
Dependencias da fase: W01–W06.

### W07 — Criacao e ciclo de vida da sessao

- **Objetivo:** iniciar uma sessao vinculada ao protocolo e acesso aprovados.
- **Entregaveis:** migration aditiva; gestao minima de projetos e vinculos,
  emissao/revogacao de convites e rotas de resgate, consulta, inicio e
  abortamento; identificadores, expiracao e restricoes conforme W02/W03.
- **Dependencias:** W01, W02, W03, W06.
- **Conclusao:** distinguir sessao de avaliacao concluida; tentativa abortada
  nao aparece como avaliacao valida; nenhum schema antigo e reescrito.
- **Validacoes:** banco vazio e atualizado, autorizacao negativa, sessao
  expirada, identificador imprevisivel e concorrencia na criacao/resgate.
- **Leitura:** contratos web, `dados/MODELO_DE_DADOS.md` e migrations existentes.

### W08 — Conclusao e recebimento de resultados

- **Objetivo:** persistir uma avaliacao completa sem confiar nas metricas do cliente.
- **Entregaveis:** rota de conclusao, validacao do protocolo e caso de uso que
  recalcula metricas com o nucleo, gravando tudo numa transacao.
- **Dependencias:** W07.
- **Conclusao:** mesma sessao/payload reenviados nao duplicam avaliacao;
  payload conflitante e rejeitado; sessao alheia/invalida nao grava dados.
  Preservar a identificacao da plataforma para evitar mistura silenciosa de coletas.
- **Validacoes:** quatro classificacoes, RT/unidades, dados ausentes,
  condicoes/contagem/versao adulteradas, rollback, concorrencia e replay.
- **Leitura:** protocolo, contrato HTTP e `stroop/domain/stroop.py`.

## Fase 4 — Execucao no navegador

Objetivo: reproduzir o protocolo aprovado com componentes de interface testaveis.
Entregaveis: fluxo completo local, motor experimental e exportacao compativel.
Dependencias da fase: W01–W03; integrar ao backend somente em W13.

### W09 — Base da interface e ambiente de testes

- **Objetivo:** preparar React/TypeScript e o limite do motor experimental.
- **Entregaveis:** projeto em `web/`, dependencias/lockfile, build, testes de
  componentes e cliente HTTP; documentar comandos no README local.
- **Dependencias:** W01, W02, W03.
- **Conclusao:** navegacao minima e estados de carregamento/erro funcionam;
  segredos ficam no servidor; motor nao depende de renderizacoes React por frame.
- **Validacoes:** TypeScript, testes, build e navegadores suportados.
- **Leitura:** contratos web, ADR-001 e `experimento/COPY_DAS_TELAS.md`.

### W10 — Preparacao e pratica

- **Objetivo:** ensinar a regra e conferir elegibilidade do ambiente.
- **Entregaveis:** identificacao aprovada, instrucoes, contagens e pratica
  jsPsych com condicoes-fonte e feedback conforme W01.
- **Dependencias:** W09.
- **Conclusao:** navegacao e resposta experimental sao distintas; espaco das
  instrucoes nao vaza para a tentativa; pratica nao entra no resultado oficial.
- **Validacoes:** mouse/teclado na navegacao, tecla mantida, feedback das quatro
  respostas, foco, contraste e bloqueio do dispositivo nao suportado.
- **Leitura:** protocolo web, `experimento/COPY_DAS_TELAS.md` e condicoes de pratica.

### W11 — Motor do bloco principal

- **Objetivo:** executar as tentativas e registrar apresentacao/resposta localmente.
- **Entregaveis:** motor isolado com randomizacao, tempos, HUD e politica de
  interrupcao; registro da ordem apresentada e dados temporais aprovados.
- **Dependencias:** W10.
- **Conclusao:** preserva balanceamento e janelas do protocolo; primeira resposta
  valida nao encurta o estimulo; teclas fora da janela nao contam; nao usa RTT
  da API nem o relogio civil como cronometro experimental.
- **Validacoes:** testes de estados/limites com relogio controlado, ordem sem
  reposicao, quatro respostas, perda de foco e verificacao em navegador real.
- **Leitura:** protocolo e `experimento/VALIDACAO_CONDICOES.md`.

### W12 — Resumo e exportacao compativel

- **Objetivo:** apresentar resultados descritivos e gerar o arquivo oficial.
- **Entregaveis:** resumo, serializador CSV e fixtures compartilhaveis entre
  testes Python/TypeScript, com apenas tentativas principais.
- **Dependencias:** W11.
- **Conclusao:** CSV conserva ordem das 21 colunas, unidades e nome seguro;
  ausencia de hits/arredondamentos seguem a decisao W01; exportacao respeita W03.
- **Validacoes:** arquivo web sintetico aceito pelo importador atual, formulas
  comparadas com o nucleo, caracteres especiais e ausencia de dados no nome.
- **Leitura:** `experimento/CSV_UNIFICADO.md`, `dados/MODELO_DE_DADOS.md` e protocolo web.

## Fase 5 — Integracao e consulta

Objetivo: ligar coleta, armazenamento e consulta sob o mesmo controle de acesso.
Entregaveis: fluxo completo, consultas autorizadas e painel web descritivo.
Dependencias da fase: backend e execucao local aprovados.

### W13 — Fluxo integrado e falhas de envio

- **Objetivo:** conectar criacao, execucao e conclusao de sessao.
- **Entregaveis:** integracao web/API, confirmacao de recebimento e reenvio
  controlado de resultado completo, respeitando a politica de armazenamento W03.
- **Dependencias:** W08, W12.
- **Conclusao:** mensagem de salvo depende de confirmacao do servidor;
  queda de rede nao duplica dados; interrupcao nao vira avaliacao completa.
- **Validacoes:** ponta a ponta sintetico, timeout, retry, duplo clique,
  refresh, expiracao da sessao e limpeza de dados temporarios conforme contrato.
- **Leitura:** contratos web e casos de uso de conclusao.

### W13A — Cadastro da sessao pela equipe e emissao de convite

- **Estado:** planejada, sem implementacao ou aceite. Complemento corretivo de
  W13/W15 identificado pelo responsavel apos testar a versao publicada; preserva
  os IDs existentes e nao transforma testes anteriores em evidencia deste fluxo.
- **Problema:** o participante consegue informar um convite, mas a equipe nao
  dispoe de formulario web para preparar uma sessao. A API ja recebe projeto,
  codigo do participante e visita, vinculando o avaliador autenticado. Convites
  preparados por scripts nao satisfazem a operacao completa pelo navegador.
- **Referencias de origem:** [Fase 1 do plano legado](legado/PLANO_DE_IMPLEMENTACAO_DASHBOARD.md),
  [formulario de sessao](experimento/FORMULARIO_DE_SESSAO.md), adaptacao aprovada
  no [protocolo WEB](experimento/PROTOCOLO_WEB.md) e
  [contrato HTTP](desenvolvimento/CONTRATO_API_WEB.md). O formulario legado inclui
  nome/iniciais; a WEB conserva a decisao de nao coleta-los.
- **Dependencias:** W06/W07 (autenticacao, projetos, vinculos e convites),
  W09 (interface), W13 (execucao integrada) e W15 (area da equipe).
- **Fluxo previsto:** entrar em `/equipe` com Google -> selecionar projeto
  autorizado -> cadastrar codigo pseudonimizado e visita -> conferir avaliador
  e dados da sessao -> gerar convite -> entregar codigo ao participante -> abrir
  `/pratica`, validar convite e executar -> conferir resultado na area da equipe.
- **Campos e regras:**

  | Informacao | Comportamento planejado |
  |---|---|
  | Projeto/protocolo | Selecao entre projetos existentes acessiveis; somente projeto ativo e vinculo valido permitem emitir convite |
  | Codigo do participante | Obrigatorio, pseudonimizado; entrada manual com validacao do contrato WEB, sem cadastro nominal de pacientes |
  | Numero ou codigo da visita | Obrigatorio; aceita identificador de visita, sem restringir a numeros |
  | Avaliador responsavel | Exibido como a conta autenticada e sua identificacao tecnica; fixado pelo servidor, sem atribuir a outra pessoa pelo formulario |
  | Datas, identificadores e protocolo | Gerados/vinculados pelo sistema conforme contrato; nao digitados pelo operador |

- **Entregaveis:** formulario acessivel na area autenticada, cliente HTTP para
  criar/revogar convite e confirmacao com projeto, participante, visita,
  avaliador, codigo de uso unico e expiracao. Disponibilizar acesso a `/pratica`
  sem incluir o convite na URL. Permitir revogar o convite enquanto o contrato
  permitir; nova emissao deve ser uma acao explicita e criar sessao distinta.
  Codigo permanece apenas em memoria durante sua exibicao; nao e recuperavel
  apos sair/recarregar. Explicar como proceder se a resposta/codigo for perdido,
  sem simular revogacao de convite cujo identificador nao foi recebido.
- **Limites:** reutilizar as rotas e a persistencia existentes, sem presumir
  necessidade de migration. Sem nome, iniciais do participante, CPF, contato,
  idade, sexo, texto livre ou novo prontuario. Cadastro de projetos, usuarios e
  selecao de avaliador diferente do emissor nao integram esta correcao. Nao
  alterar tempos, estimulos, metricas, CSV ou gates W16/W21. Somente dados
  sinteticos enquanto a coleta real nao estiver autorizada/habilitada.
- **Criterios de aceite:**
  1. Operador com perfil `importacao`/`administracao` e vinculo ativo consegue
     preparar a sessao e gerar convite pela interface, sem CLI ou acesso ao banco.
     Perfil `consulta` nao recebe controles de escrita; servidor continua
     recusando escrita indevida, inclusive para administrador sem vinculo.
  2. Campos obrigatorios e limites seguem o contrato WEB; remover espacos nas
     extremidades, indicar erros por campo e preservar valores para correcao.
     Nenhum convite e emitido quando a validacao falha.
  3. Projeto, codigo, visita e avaliador corretos persistem do convite ao
     resultado/CSV; identidade do avaliador vem do servidor. Dados de outra
     sessao/projeto nao podem ser reaproveitados acidentalmente.
  4. Bloquear duplo envio; nao repetir POST automaticamente apos timeout/falha
     de rede. Diferenciar sucesso confirmado de resultado desconhecido da
     solicitacao, sem declarar criacao ou revogacao sem resposta valida.
  5. Revogacao confirmada impede resgate/continuidade conforme contrato.
     Expiracao, reutilizacao, sessao vencida, bloqueio de conta, perda de vinculo,
     CSRF/origem e indisponibilidade possuem mensagens fechadas e operacao segura.
  6. Trocar projeto, sair da conta ou desmontar a tela cancela operacoes locais
     pendentes e limpa dados/codigo exibidos, sem aplicar respostas atrasadas ao
     novo contexto. Cancelamento local nao presume desfazer uma escrita remota.
  7. Fluxo integral validado em HTTPS real: cadastro pela tela -> convite ->
     pratica -> principal -> recibo -> consulta/CSV com metadados conferidos.
     Mocks isolados e geracao por scripts nao substituem este aceite.
  8. Interface funciona por teclado, com labels, foco e estados de espera/erro;
     sem metadados/convites em logs, URLs ou armazenamento persistente do browser.
- **Sequencia de execucao futura:** conferir contratos e registrar a UX ->
  implementar cliente/formulario -> testar componentes e navegador -> validar
  com API/PostgreSQL reais sinteticos -> atualizar guias e evidencias -> preparar
  imagem e retorno seguro -> publicar conforme autorizacao vigente e executar
  smoke sintetico publico -> solicitar aceite do operador. Nesta unidade apenas
  se documenta a sequencia; nenhuma publicacao e executada.
- **Validacoes previstas:** testes de cliente/DOM para entrada e respostas;
  Playwright para perfis, cadastro, revogacao, falhas e troca de projeto; HTTPS
  real e PostgreSQL descartavel para persistencia/autorizacao/ponta a ponta;
  `npm ci`, `npm test`, `npm run typecheck`, `npm run build`,
  `npm run test:browser` e integracao conforme ambiente documentado. Executar
  regressao Python se houver mudanca no backend e build/smoke de imagem quando
  houver nova imagem. Sempre conferir links e `git diff --check`. Registrar
  limites/skips como pendencias; estes ensaios nao homologam timing fisico W16.
- **Conclusao:** somente apos os criterios acima terem evidencia e o responsavel
  conseguir operar o cadastro pela interface. Atualizar guias da equipe e
  participante, registro/progresso e matriz de cobertura W23; W21/W22 devem
  incluir esse fluxo em seu aceite funcional.

### W14 — Consulta autorizada e exportacao via API

- **Objetivo:** disponibilizar resultados com filtros e paginacao.
- **Entregaveis:** rotas de listagem, detalhe e exportacao; consultas concretas
  reutilizaveis extraidas de `dashboard/data_access.py` onde viavel.
- **Dependencias:** W08, W06.
- **Conclusao:** filtra por permissao no servidor, separa plataformas e
  instrumentos, limita pagina/tamanho e usa credencial de leitura adequada.
- **Validacoes:** acesso cruzado, filtros, paginacao, ausencia de dados,
  exportacao autorizada, paridade com consultas existentes e schema invalido.
- **Leitura:** acesso web, `dados/DASHBOARD_POSTGRESQL.md` e `dados/MULTIPLOS_INSTRUMENTOS.md`.

### W15 — Painel web e coexistencia com Streamlit

- **Objetivo:** oferecer consulta na nova interface sem retirar o painel atual.
- **Entregaveis:** filtros, cards, graficos, detalhe e exportacao consumindo a
  API; documentar recursos cuja migracao fica explicitamente fora do MVP.
- **Dependencias:** W09, W14.
- **Conclusao:** mesmas metricas de referencia; plataformas/instrumentos
  identificados; acesso profissional e erros tratados; nenhuma interpretacao clinica.
- **Validacoes:** componentes e ponta a ponta por perfil, paridade de valores,
  filtros sem resultados, teclado e regressao do Streamlit.
- **Leitura:** `dashboard/README.md`, contrato HTTP e acesso web.

## Fase 6 — Qualidade, seguranca e automacao

Objetivo: produzir evidencias repetiveis antes da exposicao externa.
Entregaveis: validacao temporal, auditoria de seguranca e pipeline de verificacoes.
Dependencias da fase: fluxo integrado; seguranca basica ja e obrigatoria desde W06.

### W16 — Piloto e validacao temporal

- **Objetivo:** medir o comportamento real nos ambientes suportados.
- **Entregaveis:** `docs/VALIDACAO_WEB.md` com matriz navegador/SO/tela/teclado,
  protocolo de piloto, evidencias sinteticas e limites conhecidos.
- **Dependencias:** W13.
- **Conclusao:** criterios de temporizacao W01 comprovados, interrupcoes
  detectadas e formulas verificadas. Sem evidencias manuais necessarias,
  registrar pendencia; testes automatizados nao substituem medicao fisica.
- **Validacoes:** piloto autorizado, variacao de frames, latencia/variabilidade,
  tecla mantida, perda de foco e comparacao controlada quando exigida pelo estudo.
- **Leitura:** protocolo web e documentacao de temporizacao do jsPsych.

### W17 — Revisao de seguranca da aplicacao

- **Objetivo:** revisar o conjunto integrado e fechar vulnerabilidades concretas.
- **Entregaveis:** threat model atualizado, correcoes e evidencias de testes;
  configuracao de CORS/origin, CSRF, cookies, CSP e limites coerentes com o fluxo.
- **Dependencias:** W13, W15.
- **Conclusao:** nenhum bloqueio de seguranca sem tratamento; erros e logs
  sem payload identificavel; tokens nao aparecem em URL/logs; operacoes
  profissionais e participantes tem limites distintos quando aplicavel.
- **Validacoes:** autorizacao negativa, acesso a objeto alheio, XSS, replay,
  payload excessivo, rate limit, dependencias e secrets; sem ataques em producao.
- **Leitura:** `seguranca/THREAT_MODEL.md`, `operacao/HARDENING_PRODUCAO.md` e acesso web.

### W18 — CI e verificacoes reproduziveis

- **Objetivo:** automatizar a validacao do codigo e dos contratos.
- **Entregaveis:** pipeline com Python/PostgreSQL descartavel, frontend,
  contrato HTTP, testes ponta a ponta, build e verificacao de dependencias/secrets.
- **Dependencias:** W13, W15.
- **Conclusao:** checkout limpo passa sem dados locais ou secrets reais;
  falha de teste bloqueia a entrega; nao incluir deploy automatico nesta etapa.
- **Validacoes:** executar pipeline e falha controlada de uma verificacao;
  reproducao dos comandos documentados, artefatos sem dados de participantes.
- **Leitura:** READMEs de testes/API/web e protocolo de validacao.

## Fase 7 — Empacotamento e operacao

Objetivo: preparar operacao reversivel em ambiente isolado.
Entregaveis: imagens, integracao Compose e procedimentos de recuperacao.
Dependencias da fase: integracao e seguranca validadas; nenhuma acao em OCI.

### W19 — Imagens e Compose da aplicacao web

- **Objetivo:** empacotar frontend/API sem alterar o caminho operacional legado.
- **Entregaveis:** imagens e perfil Compose web separado, proxy, healthchecks,
  redes, secrets externos, limites e configuracao de migracoes explicita.
- **Dependencias:** W17, W18.
- **Conclusao:** somente proxy publica portas no perfil de producao preparado;
  imagens sem PsychoPy, dados ou secrets; execucao com privilegios minimos.
- **Validacoes:** Compose com valores ficticios, build, smoke HTTPS sintetico,
  persistencia/reinicio e verificacao de rotas e conexoes internas.
- **Leitura:** `operacao/INFRAESTRUTURA_DOCKER.md`, `operacao/HARDENING_PRODUCAO.md` e ADR-001.

### W20 — Observabilidade e recuperacao

- **Objetivo:** tornar falhas detectaveis e atualizacoes reversiveis.
- **Entregaveis:** sinais de saude e contagens sem conteudo identificavel,
  runbook web, backup/restauracao e plano de rollback de app/schema.
- **Dependencias:** W19.
- **Conclusao:** reutilizar ferramentas de backup existentes; definir objetivos
  de recuperacao e validar restauracao isolada. Rollback nao apaga novas coletas
  nem presume que toda migration tem reversao destrutiva segura.
- **Validacoes:** backup criptografado sintetico, restauracao, indisponibilidade
  de banco, alerta simulado e retorno a versao anterior compativel.
- **Leitura:** `seguranca/RESPOSTA_A_INCIDENTES.md`, `seguranca/TRATAMENTO_DE_DADOS.md` e backup atual.

## Fase 8 — Homologacao, implantacao e transicao

Objetivo: liberar uma versao aprovada e manter continuidade operacional.
Entregaveis: aceite, procedimentos de publicacao e criterios de transicao.
Dependencias da fase: evidencias funcionais, temporais, de seguranca e operacao.

### W21 — Homologacao e capacidade

- **Objetivo:** validar o pacote completo no ambiente de homologacao autorizado.
- **Entregaveis:** relatorio de aceite, limite de concorrencia medido, roteiro
  operacional e lista fechada de pendencias; dados sempre sinteticos.
- **Dependencias:** W13A, W16, W17, W18, W20.
- **Conclusao:** fluxos por perfil, protocolo e recuperacao aprovados;
  capacidade e limites medidos no ambiente alvo, sem estimativas como evidencia.
- **Validacoes:** ponta a ponta, carga controlada fora do motor experimental,
  reboot, restore, rollback e ausencia de vazamentos em logs/exports.
- **Leitura:** runbook web, validacao web e contratos de acesso/protocolo.

### W22 — Implantacao em producao pelo usuario

Autorizacao posterior nesta sessao: responsavel delegou explicitamente ao Codex
a substituicao da aplicacao na VPS existente, mantendo dominio e infraestrutura.
Publicacao exclusivamente sintetica permitida antes do aceite W16/W21; isso
nao conclui essas etapas. Evidencias e manutencao em
[DEPLOY_WEB_VPS](operacao/DEPLOY_WEB_VPS.md); confirmacao Google pessoal solicitada.
O aceite funcional da interface publicada tambem depende de W13A; a publicacao
ja realizada nao comprova o cadastro de sessao pela equipe no navegador.

- **Objetivo:** publicar a versao homologada com decisao operacional explicita.
- **Entregaveis:** dominio/TLS, credenciais externas, backup externo,
  responsaveis, runbook executado e evidencias de smoke publico.
- **Dependencias:** W21 e autorizacao/configuracao operacional do usuario.
- **Conclusao:** usuario executa e valida a implantacao; Codex pode preparar ou
  revisar evidencias quando solicitado. `continue web` nao autoriza acesso a VPS,
  custos, publicacao, dados reais ou mudanca do estado por presuncao.
- **Validacoes:** HTTPS real, login configurado, portas internas fechadas,
  backup/restauracao, reboot e rollback com evidencias do ambiente publicado.
- **Leitura:** runbook web e ADR-002; `legado/OCI_ETAPA11.md` e somente historico legado.
  Verificar SO, recursos e dominio da VPS existente antes da implantacao.

### W23 — Transicao e eventual descontinuacao

- **Objetivo:** encerrar a migracao com compatibilidade e documentacao de uso.
- **Entregaveis:** guias atualizados, matriz de recursos cobertos, suporte ao
  historico e plano de manutencao; proposta de retirada de componentes opcionais.
- **Dependencias:** W22 e decisao explicita sobre qualquer retirada.
- **Conclusao:** usuario aceita a versao; imports/exportacoes historicos seguem
  rastreaveis; nao excluir PsychoPy, Streamlit ou dados por iniciativa automatica.
  Sem autorizacao de retirada, concluir a transicao mantendo coexistencia.
- **Validacoes:** regressao final, exportacao/importacao, rollback documentado,
  links e revisao de procedimentos por quem operara o sistema.
- **Leitura:** guias de usuario/instalacao, runbook e matriz de aceite.
