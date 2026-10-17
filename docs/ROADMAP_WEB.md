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
| W09A | Planejada; refinamento pontual de abertura, tutorial e encerramento, preservando identidade visual e protocolo |
| W10 | Concluida em 2026-10-16; pratica jsPsych, 77 testes logica/DOM, 18 browser e regressao Python 240 aprovados |
| W11 | Concluida em 2026-10-16; motor jsPsych, 120 testes logica/DOM e 24 browser aprovados |
| W12 | Concluida em 2026-10-16; resumo, CSV de 21 campos, paridade Python/TypeScript e importacao real validados |
| W13 | Integracao anterior validada; fluxo completo de cadastro pela interface pendente em W13A |
| W13A | Implementada e validada tecnicamente; aceite de operacao pelo responsavel pendente |
| W15 | Painel inicial validado; paridade funcional com legado pendente em W15A–W15E |
| W15A | Planejada; completar filtros combinados e consulta entre projetos autorizados |
| W15B | Planejada; completar tabela, detalhe, graficos e visoes por instrumento |
| W15C | Planejada; exportar a visao filtrada em CSV agregado |
| W15D | Planejada; administrar usuarios, projetos e vinculos pela interface |
| W15E | Planejada; importar CSV pela WEB com escopo, minimizacao e auditoria |
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
testados; W09A planeja a experiencia revisada do participante e permanece
pendente de implementacao/aceite visual. W13A e W15A–W15E impedem considerar completos o cadastro, o dashboard
e a substituicao funcional do legado pelo navegador. W13A e a proxima prioridade
de implementacao, seguida dos complementos W15 conforme dependencias, antes
do aceite funcional W21/W22. A instrucao atual retoma a implementacao autonoma local; publicacao e aceite
operacional permanecem sujeitos aos gates e autorizacoes especificos.
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

### W09A — Refinamento da experiencia do participante sem troca de identidade

- **Estado:** planejada, nao implementada. Solicitacao atual exclusivamente
  documental: registrar a proposta neste roadmap, sem alterar frontend, outros
  documentos de UX/copy, imagens, dependencias, protocolo ou publicacao.
- **Objetivo:** tornar abertura, orientacoes e encerramento mais claros e
  contemporaneos com mudancas pontuais de composicao e texto. Preservar o
  trabalho visual existente; nao redesenhar todo o produto ou copiar o legado.
- **Referencias examinadas:**15capturas locais em `../telas ref/`, relativas
  a raiz do repositorio, datadas de2026-07-05. Abertura/instrucoes:11-16-10;
  introducao pratica:11-32-51; feedback:11-34-13/11-36-34;
  transicao:11-35-28/11-35-58; resultados:11-38-27. As demais capturas mostram
  exemplos/tentativas e uma coleta demografica. Os arquivos estao fora do
  repositorio e nao serao copiados para assets/bundle nem exigidos em CI.
  Os horarios acima identificam os nomes `Captura de tela de 2026-07-05 HH-MM-SS.png`.
- **Comparacao com a WEB atual:** [abertura/instrucoes](../web/src/App.tsx)
  ja possuem cards, exemplos e identidade propria;
  [preparacao](../web/src/components/PracticePreparation.tsx) ja verifica teclado,
  permite repetir pratica e controla acesso ao principal;
  [resumo](../web/src/components/ResultSummary.tsx) ja mostra metricas, estados de
  envio e finalizacao. A proposta melhora hierarquia, orientacao e acabamento
  desses componentes, preservando seus controles e estados reais.
- **Direcao escolhida:** aproveitar das referencias a clareza de uma acao
  principal por tela, a separacao entre explicacao e exemplo, os passos curtos,
  a transicao explicita entre pratica/principal e o destaque do resumo final.
  Adaptar esses principios a composicoes originais do projeto. Nao reproduzir
  marca, telas, fundos, textos ou assets da referencia. Seus tempos, mensagens
  de pontuacao, coleta de idade/sexo e alegacoes clinicas nao definem requisitos
  deste experimento.
- **Identidade preservada:** fundo escuro atual, superficies claras dos cards,
  marca/simbolo existentes, tipografia de sistema, cores de destaque atuais,
  botoes e linguagem visual de bordas/espacamentos. Reaproveitar os estilos
  existentes, refinando proporcao, agrupamento e hierarquia; sem novo tema,
  biblioteca visual, fonte externa, imagens decorativas ou rebranding.
- **Escopo de telas e proposta editorial:** textos abaixo sao propostas para
  implementacao futura, nao copy ja aplicada nem alteracao metodologica.

  | Tela/momento | Mudanca planejada | Direcao de texto/acao |
  |---|---|---|
  | Inicio | Abertura mais compacta, titulo atual preservado, exemplo visual proprio ao lado e uma acao dominante; reduzir repeticao entre card principal e guia lateral | Apresentar atividade com palavras/cores; botao `Iniciar tutorial`; informar teclado fisico e que o bloco principal dura cerca de1minuto, sem prometer duracao total incluindo pratica |
  | Tutorial | Organizar orientacoes em passos curtos: observar, responder quando coincidir e aguardar quando diferir; exemplos Go/No-Go visiveis com labels e tecla ilustrada | `Quando a palavra e a cor das letras forem iguais, pressione Espaco.` / `Quando forem diferentes, aguarde sem pressionar.`; acao final `Ir para a pratica` |
  | Acesso por convite | Integrar visualmente o formulario ao percurso, explicando sua finalidade sem pedir metadados novamente | `Informe o convite enviado pela equipe para iniciar esta sessao.`; preservar validacao de uso unico e mensagens fechadas |
  | Preparacao/pratica | Agrupar verificacao de teclado/foco, instrucao e botao; mostrar passos da preparacao sem competir com a tarefa | `Primeiro, vamos praticar.`; explicar quatro tentativas e feedback; manter verificacao real de pressionar/soltar Espaco |
  | Pratica concluida | Cartao de transicao claro, com inicio do principal em destaque e repeticao como alternativa secundaria | `Pratica concluida. Quando estiver pronto, comece a tarefa.`; `Comecar tarefa` / `Repetir pratica`; explicitar ausencia de feedback por tentativa no principal |
  | Resultado recebido | Destaque de conclusao/recebimento, resumo com hierarquia clara, precisao e RT com unidades, contagens em segundo plano visual | `Tarefa concluida. Obrigado por participar.` e, somente com recibo, `Seu resultado foi recebido pela equipe.`; preservar todas as metricas descritivas e explicacao da mediana |
  | Envio em andamento ou pendente | Separar conclusao das tentativas de confirmacao do servidor; mensagem e acao adequadas ao estado | `Enviando resultado…` / `O recebimento ainda nao foi confirmado.`; manter reenvio seguro e saida sem confirmacao explicitamente identificada |
  | Acesso encerrado | Confirmacao curta apos concluir a limpeza/encerramento real da sessao, sem reconduzir imediatamente a uma nova coleta | `Participacao encerrada. Voce pode fechar esta pagina.`; nova participacao permanece acao secundaria e requer outro convite |

- **Navegacao:** indicar orientacoes, pratica e tarefa nas telas preparatorias,
  sem acrescentar HUD/progresso novo durante tentativas. Uma acao primaria por
  estado, voltar/repetir quando permitido e foco previsivel por teclado.
  Tutorial pode repartir texto em passos navegaveis, mas exemplos instrucionais
  permanecem estaticos, sem introduzir novas tentativas, treino adaptativo ou
  novo criterio de aprovacao. Evitar modais sobrepostos quando um painel de
  pagina resolver a transicao. Nao acrescentar sons, confete ou animacoes na
  tarefa. Nao iniciar experimento automaticamente ao avancar orientacoes.
- **Dependencias:** W09/W10/W12/W13 ja implementadas como base. Coordenar
  acessos/rotulos com W13A sem duplicar cadastro da sessao no participante;
  W15A–W15E continuam escopos separados de dashboard. Pode ser preparada
  independentemente desses complementos; integrar antes do aceite W21/W22.
- **Entregaveis futuros:** inventario dos estados afetados, especificacao curta
  de layout/copy e comparativos antes/depois com dados sinteticos; componentes
  React/CSS refinados apenas nas telas escolhidas; atualizacao posterior de
  [UX](experimento/UX_DECISIONS.md) e
  [copy](experimento/COPY_DAS_TELAS.md) com secao WEB explicita, sem sobrescrever
  o historico PsychoPy nem reutilizar frase de gravacao local para coleta WEB.
  Preservar links/rotas e controles existentes, salvo ajuste pontual justificado.
- **Criterios de aceite:**
  1. Identidade atual reconhecivel em comparativo antes/depois; mudancas
     concentradas na abertura, tutorial, preparacao/transicao e encerramento.
     Dashboard/cadastro recebem apenas coerencia de componentes compartilhados,
     sem reformulacao ampla incidental.
  2. Texto curto, portugues consistente, exemplos inequivocos e uma proxima
     acao visivel em cada estado; nenhuma promessa normativa/clinica ou de
     medicao de habilidades que nao tenha sido aprovada. O resumo permanece
     descritivo, sem ranking, score proprietario ou incentivo a repetir para
     melhorar resultado. Indicador visual de precisao, se usado, acompanha
     numero/rotulo; nao substitui metricas nem sugere faixa de normalidade.
  3. Motor, ordem/regras, condicoes, dez cores dos estimulos, tempos, feedback,
     HUD, tratamento de foco/Escape, numero de tentativas e CSV inalterados.
     Nao importar tempo de3segundos/2minutos ou feedback manual das referencias.
     Mensagens dos feedbacks cronometrados permanecem fora desta correcao.
  4. Sem atalho de navegacao vazando resposta para a primeira tentativa;
     preservar soltura de tecla, verificacao de teclado/foco e fluxo de start.
     Nao rotular ambiente como homologado enquanto W16 estiver pendente.
  5. Sucesso de envio somente apos recibo; permitir reenvio apenas conforme
     contrato; finalizar nao mascara envio pendente, erro de logout ou falha
     de limpeza. A nova confirmacao de encerramento so aparece apos sucesso
     real; acesso a novo convite nao reaproveita sessao anterior.
  6. Layout legivel em desktop/notebook, zoom e navegacao por teclado; labels,
     contraste, foco e mensagens acessiveis, sem depender apenas de cor.
     Responsividade da navegacao nao amplia ambientes liberados para a tarefa.
- **Validacoes futuras:** revisao de textos contra protocolo/copy, testes DOM
  dos estados e acoes, TypeScript/build, Playwright dos percursos mouse/teclado,
  foco/tecla mantida, repetir pratica, erros e encerramento. Regressao do motor,
  resumo/metricas, ausencia de persistencia local e envio/recibo em HTTPS real
  sintetico. Registrar comparativos visuais originais para revisao do responsavel.
  Mudancas visuais nao concedem W16; pilotos devem usar a versao final relevante.
- **Conclusao:** somente apos implementacao, evidencias de regressao e aceite
  visual do responsavel. Nesta solicitacao apenas a ficha/estado do roadmap sao
  alterados; nao gerar mockups, modificar frontend, executar piloto ou publicar.

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

- **Estado:** implementada e validada tecnicamente em 2026-10-17; aceite de
  operacao pelo responsavel pendente, sem conclusao antecipada. Complemento corretivo de
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

O painel inicial foi validado no escopo implementado. A comparacao abaixo
identificou cobertura parcial do legado; seus complementos W15A–W15E ainda
nao foram implementados nem aceitos. O CSV oficial individual existente nao
substitui a exportacao agregada da visao filtrada.

- **Objetivo:** oferecer consulta na nova interface sem retirar o painel atual.
- **Entregaveis:** filtros, cards, graficos, detalhe e exportacao consumindo a
  API; documentar recursos cuja migracao fica explicitamente fora do MVP.
- **Dependencias:** W09, W14.
- **Conclusao:** mesmas metricas de referencia; plataformas/instrumentos
  identificados; acesso profissional e erros tratados; nenhuma interpretacao clinica.
- **Validacoes:** componentes e ponta a ponta por perfil, paridade de valores,
  filtros sem resultados, teclado e regressao do Streamlit.
- **Leitura:** `dashboard/README.md`, contrato HTTP e acesso web.

#### Comparacao funcional com o legado — inspecao de 2026-10-16

Comparacao estatica do codigo e dos contratos, sem abrir dados reais, executar
coletas ou acessar a VPS. As descricoes abaixo sao capacidades observadas,
nao evidencia de testes executados nesta unidade. Em caso de texto historico
desatualizado, o comportamento do codigo inspecionado fundamenta a comparacao.

Fontes legadas: [composicao e areas](../dashboard/app.py),
[cards, graficos, tabela e detalhe](../dashboard/components.py),
[filtros e exportacao agregada](../dashboard/transformations.py),
[visoes por instrumento](../dashboard/instrumentos.py),
[guia do dashboard](../dashboard/README.md) e
[upload autenticado](dados/UPLOAD_LOCAL.md).
Fontes WEB: [painel atual](../web/src/components/ProfessionalDashboard.tsx),
[agregacoes](../web/src/dashboard/analysis.ts),
[acesso profissional](../web/src/App.tsx),
[consultas/CSV](../api/assessments.py),
[projetos/vinculos/convites](../api/sessions.py) e
[projecoes profissionais](../stroop/application/web_assessments.py).

| Recurso | Legado observado | WEB observada e tratamento planejado |
|---|---|---|
| Login, perfil, logout e aviso descritivo | Google, cadastro previo, areas por perfil e aviso nao clinico | Base presente; manter e revalidar nos novos fluxos |
| Periodo inicial/final | Filtro por assessment_date | Ausente na interface e na API de listagem; W15A |
| Projetos | Multisselecao de rotulos no conjunto carregado | Um projeto por consulta; completar comparacao autorizada entre projetos em W15A |
| Participantes e visitas | Multisselecao entre opcoes disponiveis | Campos de igualdade para um codigo/visita; completar selecao combinada em W15A |
| Avaliador | Filtro por rotulo do avaliador | evaluator_id chega ao cliente, mas nao ha filtro; W15A, somente identificacao tecnica |
| Instrumento, versao e plataforma | Instrumento unico e multisselecao de versoes | Instrumento unico/plataforma presentes; versao ausente; W15A |
| Nome do participante | Filtro/coluna presentes no legado | Ausencia intencional: nao migrar nome/iniciais para a WEB nem ampliar grants |
| Sete cards Stroop | Avaliacoes, participantes, precisao media/mediana, RT mediano, omissoes e comissoes | Presentes no escopo de um projeto; preservar formulas/ausencias e conferir no conjunto ampliado, W15A/W15B |
| Avaliacoes por data e precisao por visita | Graficos descritivos | Presentes como barras/meter; validar coerencia com os filtros ampliados, W15B |
| Distribuicao de RT | Barras dos valores por avaliacao | WEB agrupa em faixas de0,5s; representacao diferente, nao ausencia de dados. Documentar faixas/unidades e conservar ausencia de hits, W15B |
| Omissoes/comissoes por projeto | Series agrupadas por projeto | WEB mostra totais do projeto selecionado; falta comparacao por projeto, W15B |
| Evolucao de participante | Seletor proprio e grafico por visita | WEB oferece apenas tabela quando ha filtro de participante; completar seletor/grafico, W15B |
| Tabela agregada | Data, projeto, participante, visita, avaliador, versao, precisao total/Go/No-Go, omissoes, comissoes e RT, alem de nome local | WEB mostra participante, visita, inicio, plataforma, versao, precisao e RT; completar colunas permitidas/metricas, W15B |
| Detalhe e rastreabilidade | Metadados, metricas completas, contagem das quatro respostas e tentativas | WEB tem metricas/tentativas e parte dos metadados; falta apresentar IDs/avaliador/conclusao e contagens dedicadas. Paths/nome de arquivo fonte nao devem ser copiados; W15B |
| Instrumentos adicionais | Visao demonstrativa tem cards, graficos, tabela e exportacao proprios | WEB consulta summaries.metrics/detalhe, mas nao renderiza cards/graficos especificos e nao exporta agregado; W15B/W15C. Nao criar novos testes clinicos |
| Exportacao agregada filtrada | CSV manual com uma linha por avaliacao da visao filtrada | Ausente; W15C. CSV individual de tentativas existente deve continuar separado |
| Exportacao oficial Stroop individual | Formato oficial existe no fluxo de dados, distinto do CSV agregado do painel | Presente na WEB; preservar 21 colunas, mascaramento e autorizacao |
| Importacao CSV | Area autenticada, UTF-8 ate5MiB, validacao, rejeicao de duplicatas e auditoria | Nao ha tela nem rota WEB de importacao; W15E |
| Usuarios e permissoes | Listar, cadastrar, mudar perfil/e-mail auxiliar e ativar/bloquear, protegendo ultimo administrador | Nao ha tela nem rotas WEB de gestao de usuarios; W15D. Identidade continua iss+sub |
| Projetos e vinculos | Modelo de escopo de projetos da WEB nao possui tela equivalente no Streamlit | API WEB existe, mas falta interface; W15D, requisito operacional WEB adicional |
| Dados historicos | Consulta dos registros do banco legado | API WEB exige mapa explicito ADR-003; manter essa barreira e testar coexistencia, sem associar rotulos automaticamente |

### W15A — Filtros completos e conjunto autorizado coerente

- **Estado/objetivo:** planejada; completar filtros do dashboard mantendo a
  autorizacao por projeto, com W14/W15 anteriores como base.
- **Entregaveis:** periodo, projetos, participantes, visitas, avaliadores
  tecnicos, versoes, instrumento unico e plataforma; opcoes a partir de dados
  autorizados, resumo dos filtros, aplicar/limpar e estado sem resultados.
  Atualizar contrato HTTP, cursores, cliente e consultas para os filtros novos;
  nao basta acrescentar controles que a API atual rejeitaria.
- **Dependencias:** W14/W15. Pode ser preparada independentemente de W13A;
  seu aceite integrado deve incluir sessoes criadas pelo formulario W13A.
- **Criterios de aceite:** filtros combinados produzem o mesmo conjunto na
  tabela/cards/graficos/exportacao; todas as paginas sao consideradas sem
  duplicatas e sem apresentar totais parciais como completos. Falha em um
  projeto/pagina invalida o agregado e permite recuperacao explicita. Periodo
  tem limites inclusivos, campo de data/fuso documentados e tratamento de
  horarios legados sem fuso sem inventar UTC. Selecionar projetos nunca concede
  acesso sem vinculo, mesmo para admin. Identificar participantes pela dupla
  projeto+codigo nos totais/comparacoes; nao fundir pessoas de estudos distintos
  por coincidencia de pseudonimo. Manter instrumento unico e nenhuma consulta
  por nome/iniciais. Definir limites e estrategia de paginacao/agregacao para
  volume esperado sem carregar historico ilimitado ou agregar apenas uma pagina.
- **Validacoes:** fixtures com projetos/codigos coincidentes, varios avaliadores,
  versoes, datas-limite e multiplas paginas; contrato/cursor vinculado a filtros,
  SQL parametrizado, acesso cruzado, perda de vinculo durante leitura, falha
  parcial, vazio, teclado e cancelamento de respostas antigas. Comprovar API,
  PostgreSQL e navegador reais sinteticos, alem de testes isolados.

### W15B — Tabela, detalhe e visualizacoes completas

- **Estado/objetivo:** planejada; completar apresentacao dos resultados sem
  mudar formulas, inventar interpretacao clinica ou exigir visual identico ao
  Streamlit. Reutilizar recursos presentes, sem reimplementacao desnecessaria.
- **Dependencias:** W15A para o conjunto filtrado final; W14/W15 como base.
- **Entregaveis:** colunas permitidas do legado, com projeto, avaliador tecnico,
  precisao Go/No-Go e contagens de erros; detalhe com IDs de avaliacao/sessao,
  projeto, avaliador, inicio/conclusao, versoes/protocolo e metadados aplicaveis;
  contagens de hit/omission/correct_rejection/commission e tentativas. Exibir
  proveniencia importada somente quando minimizada e prevista em contrato,
  sem path/nome de arquivo original. Acrescentar comparacao de erros por projeto,
  seletor de participante e grafico longitudinal; cards/graficos/tabela proprios
  para instrumentos ja registrados, incluindo a demonstracao sintetica.
- **Criterios de aceite:** unidades e rotulos explicitos; precisao e RT em
  escalas separadas para nao comparar unidades diferentes no mesmo eixo.
  Ordenacao longitudinal deterministica, visitas repetidas visiveis e nenhuma
  fusao de codigos entre projetos. Metricas ausentes aparecem como ausencia,
  nao zero medido; preservar RT sem hits e regras do nucleo. Nao somar metricas
  de instrumentos distintos. Tabela/detalhe/graficos concordam com o conjunto
  W15A e o CSV. Completar projecoes HTTP quando necessario, sem disparar uma
  consulta de detalhe por linha apenas para montar a tabela agregada. Graficos
  possuem alternativa textual/tabular e mantem resultados descritivos.
- **Validacoes:** paridade numerica com nucleo/fixtures legadas, Go/No-Go,
  ausencias, multiplas visitas/projetos, instrumentos sem tentativas, dataset
  vazio, teclado/labels e regressao do que ja funciona. Validar apresentacao
  e dados com backend real; grafico por si nao comprova paridade estatistica.

### W15C — CSV agregado da visao filtrada

- **Estado/objetivo:** planejada; recuperar o download manual de uma linha
  por avaliacao filtrada, distinto do CSV oficial Stroop de21colunas.
- **Dependencias:** W15A/W15B para contrato de filtros e colunas.
- **Entregaveis:** acao de exportar visao filtrada, contrato/rota profissional
  com esquema tabular permitido por instrumento e nome de arquivo seguro;
  manter exportacao oficial individual existente sem alterar seu contrato.
- **Criterios de aceite:** arquivo reflete exatamente filtros, projetos,
  instrumento, colunas e conjunto completo autorizado; registrar criterio de
  consistencia se houver alteracoes durante geracao/paginacao. Reautorizar no
  clique/servidor e nao permitir download por conta bloqueada ou vinculo
  revogado. Todos os tres perfis profissionais vinculados conservam exportacao
  permitida. Sem nomes/iniciais, credenciais ou paths; avaliar seguranca de
  celulas de planilha, encoding, separadores, unidades e valores ausentes.
  Download manual, no-store, sem persistir exportacao no servidor. Nao declarar
  CSV agregado importavel como tentativas pelo importador oficial.
- **Validacoes:** comparar linhas/valores com tabela e consulta autorizada,
  incluindo multiplas paginas, filtros combinados, caracteres especiais,
  formula injection, permissao revogada e erro durante download. Testar
  instrumentos distintos separadamente e preservar o CSV individual/importador.

### W15D — Administracao de usuarios, projetos e vinculos

- **Estado/objetivo:** planejada; permitir operacao profissional pelo navegador.
  Usuarios/perfis sao paridade do legado; projetos/vinculos sao complemento do
  modelo WEB. Nenhuma dessas telas existe atualmente na nova interface.
- **Dependencias:** W06/W07, W15; nao depende dos novos graficos/exportacao.
- **Entregaveis:** navegacao por areas/perfil; listar/cadastrar usuarios,
  alterar perfil, e-mail auxiliar opcional e estado ativo/bloqueado; interface
  para listar/criar projetos e gerir seus membros com as rotas existentes.
  Criar contratos/rotas de usuarios reutilizando casos de uso legados e
  protecoes transacionais; documentar como obter/fornecer a propria identidade
  Google verificada para solicitar cadastro, sem autocadastro ou senha nova.
- **Criterios de aceite:** somente administracao gere contas/projetos/vinculos;
  proteger ultimo administrador ativo, inclusive sob concorrencia; impedir
  elevacao de privilegios por payload. Identidade permanece iss+sub; e-mail
  auxiliar nao autoriza e so aparece no contexto administrativo permitido.
  Mudancas sensiveis mostram alvo/efeito e exigem acao explicita, CSRF/origem,
  reautorizacao e auditoria sem dados sensiveis. Admin global nao herda acesso
  aos resultados: requer vinculo explicito. Bloqueio/revogacao preserva coletas
  e invalida operacoes/convites ativos conforme contrato. Sem exclusao de contas
  ou resultados e sem interface para preencher mapa legado por coincidencia.
  Reutilizar apenas operacoes de projeto ja suportadas; nao inventar API de
  alteracao/desativacao de projeto como se estivesse implementada.
- **Validacoes:** perfis/contas nao cadastradas, ultimo admin, concorrencia,
  CSRF, alteracao indevida de alvo, revogacao/bloqueio, acesso cruzado,
  paginacao de usuarios/membros e cadastro->vinculo->W13A->consulta com backend
  real sintetico. Auditar efeitos e erros fechados sem imprimir e-mail/claims.

### W15E — Importacao CSV autenticada na WEB

- **Estado/objetivo:** planejada; recuperar importacao pelo navegador com
  isolamento e minimizacao compativeis com W03/ADR-003. A existencia do
  importador Python/Streamlit nao implica uma rota HTTP WEB pronta.
- **Dependencias:** W03/W04/W14, W15D para operacao dos vinculos; W15B para
  apresentar o resultado importado. Reutilizar ingestao/dominio existentes.
- **Entregaveis:** especificar primeiro contrato de upload, formatos/versoes,
  minimizacao dos arquivos e destino de projeto explicitamente autorizado;
  implementar depois rota dedicada, cliente/tela, estados recebido/validado/
  importado/rejeitado e consulta do resultado da operacao. Preservar suporte aos
  instrumentos ja registrados sem adicionar instrumentos novos por presuncao.
- **Criterios de aceite:** importacao/administracao com vinculo valido;
  transacao atomica, duplicata rejeitada sem sobrescrever dados, auditoria e
  estado verificavel apos timeout ou falha de auditoria, sem repeticao cega.
  Legado suporta um CSV UTF-8 ate5MiB; planejar limite equivalente apenas na
  rota dedicada, com limites de memoria/tempo/concorrencia e streaming quando
  necessario. Preservar64KiB nas demais rotas; nao elevar limite global.
  Rejeitar arquivo vazio, NUL, encoding/extensao/schema invalidos e tamanho
  excedido; descartar temporarios privados e nunca renderizar/logar conteudo
  bruto ou usar nome fornecido como path. Definir e validar politica que impeça
  transmissao de nomes/iniciais para a WEB antes de habilitar upload: CSV
  minimizado aceito, arquivos identificaveis permanecem no fluxo local seguro.
  Nao habilitar envio de CSV nominal apenas porque o legado o aceitava.
  Especificar compatibilidade dessa politica com os validadores existentes.
  Importar nao deve vincular rotulo legado a projeto por coincidencia nem
  escrever mapa ADR-003 pela API; provisionamento explicito continua separado.
  Importacao nao converte linha PsychoPy em coleta WEB nem libera pesquisa real.
- **Validacoes:** fixtures integralmente sinteticas de formatos aceitos e
  rejeitados, minimizacao, permissao/projeto cruzado, duplicatas/concorrencia,
  rollback transacional, limite dedicado sem regressao64KiB, limpeza de
  temporarios, falha parcial/auditoria, reconsulta apos resposta perdida e
  navegacao importacao->consulta/detalhe/exportacao com backend real.

#### Execucao e aceite dos complementos do dashboard

Nesta solicitacao, somente comparacao e planejamento documental. Em retomada
de implementacao: priorizar W13A e W15A–W15C; W15D pode avancar independentemente
dos graficos quando houver beneficio, e W15E exige seu contrato/minimizacao
definidos antes do codigo de upload. Atualizar UX/HTTP/acesso/dados nas fontes
canonicas conforme cada entrega, sem alterar arquitetura ou privacidade por
presuncao. Validar testes proporcionais, suite Python quando houver backend,
`npm ci`, testes DOM, TypeScript, build, Playwright e HTTPS/PostgreSQL sinteticos
reais. Imagens novas exigem build/smoke e publicacao autorizada com retorno
seguro. Validar links e diff; mocks, skips e documentacao nao concedem aceite.
W21/W22 precisam cobrir os novos fluxos por perfil; W23 deve apresentar matriz
final de cobertura e eventuais diferimentos explicitamente aceitos pelo usuario.
Nao descontinuar Streamlit enquanto os recursos substitutos nao forem aceitos.

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
- **Dependencias:** W09A, W13A, W15A–W15E, W16, W17, W18, W20.
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
O aceite da interface publicada tambem depende de W09A, W13A e W15A–W15E;
a publicacao ja realizada nao comprova cadastro de sessao, dashboard completo
ou substituicao das areas operacionais do legado pelo navegador.

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
