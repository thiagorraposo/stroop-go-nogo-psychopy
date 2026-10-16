# Protocolo operacional do Codex CLI

Este protocolo orienta o trabalho do Codex CLI neste repositorio. Os comandos
abaixo sao mensagens do usuario na sessao, nao comandos de shell ou scripts.
O [AGENTS.md raiz](../../AGENTS.md) exige a leitura deste protocolo.

Ha uma fonte de estado por escopo: o [backlog legado](../legado/Projeto%20Stroop%20Test.md)
governa as etapas 1–12 da operacao existente; o [roadmap WEB](../ROADMAP_WEB.md)
governa a nova versao, com IDs Wxx. Os estados nao se somam. Documentos tecnicos
detalham contratos; baselines e registros sao evidencias datadas.

## Evolucao web — execucao continua

`continue web` retoma uma etapa em andamento/bloqueada ou seleciona a primeira
nao concluida cujas dependencias estejam concluidas. `execute Wxx` permite
selecionar explicitamente uma etapa inicial elegivel. Ambos continuam
automaticamente para a proxima etapa viavel apos validar e registrar a atual,
salvo limite de escopo expresso pelo usuario. Uma solicitacao apenas documental
ou de revisao nao inicia esse ciclo nem retoma objetivo pausado.

Na inicializacao, ler os `AGENTS.md` aplicaveis, roadmap, arquitetura e
[memoria de retomada](../PROGRESS.md); conferir Git e as evidencias atuais sem
descartar alteracoes. Identificar aceite, pendencias e dependencias. Apresentar
plano breve e iniciar a primeira tarefa executavel sem pedir autorizacao para
escolhas tecnicas rotineiras. Nas etapas seguintes, ler apenas o contexto minimo,
limites, entregaveis e validacoes da ficha; nao repetir a analise global quando
o mapa e os contratos existentes forem suficientes.

Seguir o ciclo planejar -> implementar -> testar -> corrigir -> validar ->
documentar -> avancar. Delegar tarefas independentes a subagentes conforme o
AGENTS raiz, com escopo e arquivos definidos, integrando e validando o resultado.
Nao antecipar trabalho com dependencia pendente nem substituir implementacao
por documentacao ou simulacoes. Bloqueios localizados sao registrados e nao
impedem outras etapas independentes elegiveis.

`mostrar status web` apenas consulta estado e evidencias. `validar etapa web
Wxx` revalida somente a etapa indicada, sem implementar outra. Para uma etapa
documental, validar documentos/links/diff; para codigo, executar a regressao
afetada e os criterios da ficha. Registrar aprovados, falhas, erros e skips.

Atualizar o estado apenas com aceite comprovado e registrar comandos/resultados
em `REGISTRO_DE_ALTERACOES.md`. Uma pendencia manual exigida nao e um teste
aprovado. Manter `PROGRESS.md` conciso com contexto de retomada, arquivos,
decisoes, impedimentos, verificacoes e proxima acao; o estado formal continua
somente no roadmap. Nao gerar prompts nem copias de tabelas de progresso.

Trabalhar em branch de desenvolvimento separada e fazer commits locais pequenos
apos validacao, conforme o AGENTS raiz e `PADRAO_DE_COMMITS.md`, sem incluir
alteracoes preexistentes. Nao fazer push, merge na principal, tags ou deploy
sem autorizacao explicita. O versionamento manual abaixo pertence ao legado.

Nao encerrar entre etapas para relatar resultados. Continuar enquanto houver
tarefa viavel e recursos, usando a janela de 5 horas quando disponivel, sem
inventar trabalho ou cota restante. Encerrar com roadmap integralmente validado,
bloqueio incontornavel sem alternativa viavel, interrupcao externa ou limite
de uso impeditivo; respeitar pausa do usuario. Quando o limite estiver proximo
e essa informacao for conhecida, priorizar validacao da unidade atual e salvar
o estado exato em `PROGRESS.md`. Na entrega final, informar arquivos, evidencias,
limitacoes e proxima acao de forma objetiva.

W22 pertence ao usuario: nenhum comando de continuacao autoriza acesso OCI,
deploy, contratacao ou dados reais. As restricoes operacionais de seguranca
abaixo continuam validas; o ritmo e o versionamento do legado aplicam-se somente
aos comandos legados. `continue o projeto`, `mostrar status` e `validar etapa
atual` sem qualificacao conservam o significado legado.

## Workflow legado

As Etapas 11 e 12 serao planejadas, executadas e validadas diretamente pelo
usuario. O Codex nao inicia essas etapas com `continue o projeto`, nao acessa
OCI por iniciativa propria e nao concede aceite sem evidencias dos criterios do
backlog. Pode consultar o estado e revisar ou registrar evidencias documentais
quando o usuario solicitar.

## `continue o projeto`

Se a primeira etapa nao concluida for a 11 ou a 12, informar que sua execucao
pertence ao usuario e encerrar sem iniciar trabalhos dessa etapa. O procedimento
abaixo aplica-se apenas a etapas executadas pelo Codex.

1. Ler integralmente os `AGENTS.md` aplicaveis, este protocolo e o backlog canonico.
2. Inspecionar codigo, Git e documentacao, preservando alteracoes preexistentes.
   Consultar arquivos-fonte e testes, sem abrir dados locais identificaveis.
3. Identificar a primeira etapa nao concluida pela ordem do backlog. Se houver
   etapa em andamento ou bloqueada, retoma-la; nao saltar para a seguinte.
4. Confirmar dependencias, pre-requisitos, estado atual e evidencias do repositorio.
   Nao confiar somente em relatorios anteriores. Investigar e registrar qualquer
   divergencia antes de corrigir a documentacao ou iniciar implementacao.
5. Apresentar plano curto com escopo, arquivos provaveis e validacoes de aceite.
6. Executar somente essa etapa, preservando comportamento fora do escopo.
7. Conferir cada criterio de aceite contra evidencias concretas, indicando
   comando, resultado ou arquivo que o comprova.
8. Executar testes especificos, suite completa, verificacoes Docker aplicaveis e
   `git diff --check`. Contar aprovados, falhas, erros e skips separadamente.
9. Usar somente fixtures e dados inequivocamente sinteticos em todas as verificacoes.
10. Somente apos aprovacao integral, atualizar documentacao, registro de alteracoes,
    quantidade de testes e backlog. Atualizar o progresso pela soma dos pesos
    integralmente concluidos. O registro factual de um bloqueio e permitido antes
    do aceite e nunca equivale a conclusao ou credito parcial.
11. Apresentar arquivos alterados, evidencias, comandos/resultados, quantidade de
    testes, riscos, decisoes pendentes, progresso e proxima etapa; confirmar que
    nenhuma etapa posterior foi iniciada.
12. Sugerir exatamente uma mensagem Conventional Commits em portugues conforme
    [PADRAO_DE_COMMITS.md](PADRAO_DE_COMMITS.md), sem executar versionamento, e
    encerrar. Uma segunda etapa so comeca com novo `continue o projeto` do usuario.

Se todas as etapas estiverem concluidas, informar o estado sem inventar trabalho.

## `mostrar status`

Ler instrucoes, protocolo e backlog; inspecionar Git, codigo e documentacao em
modo somente leitura. Informar etapas concluidas, progresso, contagem de testes
registrada, data/evidencias disponiveis, bloqueios e proxima etapa. Distinguir
resultados historicos de verificacoes atuais. Nao executar testes que escrevam
artefatos, iniciar servicos, editar arquivos, corrigir inconsistencias ou avancar
etapas. Informar divergencias encontradas na resposta.

## `validar etapa atual`

O alvo e a etapa em andamento ou bloqueada; na ausencia dela, a ultima concluida.
Para as Etapas 11 e 12, revisar somente as evidencias que o usuario disponibilizar,
sem executar infraestrutura, testes operacionais ou alterar o progresso por
presuncao. Os passos de revalidacao abaixo aplicam-se a etapas executadas pelo
Codex.
Identificar explicitamente esse alvo antes da validacao. Ler as mesmas fontes,
confirmar pre-requisitos e executar novamente todos os seus criterios de aceite,
testes especificos, suite completa, Docker aplicavel e `git diff --check`, somente
com dados sinteticos. Nao implementar funcionalidades ou antecipar outra etapa.
Registrar evidencias e, se tudo passar, atualizar o registro de revalidacao e a
contagem de testes no backlog, sem contar novamente o peso de etapa concluida.
Uma etapa incompleta permanece sem credito ate comprovar todo o escopo e aceite.
Encerrar com resultado, riscos e exatamente uma sugestao de commit, sem executa-lo.

## Validacao e isolamento

Comando da suite completa na raiz (Linux/macOS):

```bash
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

Para a integracao PostgreSQL, configurar `TEST_DATABASE_URL` exclusivamente para
um banco novo e descartavel com nome iniciado por `stroop_etapa4_test`, conforme
`tests/test_postgres_migrations.py`. Os testes apagam o schema desse banco; nunca
usar banco operacional. Sem essa variavel, os skips nao aprovam a suite integral.
Nao imprimir credenciais ou ler `.env` operacional para obter acesso aos testes.

Verificacao de configuracao Docker com valores ficticios:

```bash
docker compose --env-file .env.example config --quiet
```

Quando exigidos pelo escopo/aceite, verificar build, inicializacao, healthchecks,
smoke, persistencia e recuperacao em ambiente isolado sintetico, seguindo os
[procedimentos Docker](../operacao/INFRAESTRUTURA_DOCKER.md). Justificar verificacoes nao
aplicaveis; indisponibilidade de teste obrigatorio nunca significa nao aplicabilidade.
O PsychoPy permanece local e fora do Docker. Alteracoes experimentais exigem
validacao estrutural e checklist Pilot autorizado, sem coleta real.

## Bloqueios e decisoes

Nao conceder progresso parcial nem concluir etapa com teste obrigatorio falhando,
pulado ou indisponivel. Manter o progresso anterior, registrar causa e evidencia
no registro de alteracoes e o bloqueio no backlog, sem marcar conclusao. Informar
exatamente qual decisao ou acao permite retomar. Se a revalidacao contradisser uma
conclusao antiga, registrar a divergencia sem recalcular progresso silenciosamente.

Nos trabalhos executados pelo Codex, perguntar ao usuario dentro da sessao sobre
decisoes de produto ou metodologicas indispensaveis, credenciais, autorizacoes
de risco e recursos externos inacessiveis. Resolver escolhas tecnicas rotineiras
autonomamente, documentando decisoes arquiteturais relevantes em ADR. Nao
presumir escolhas clinicas, semanticas, de privacidade, seguranca, producao ou
envolvendo dados reais que alterem os requisitos. Registrar a decisao no documento
tecnico pertinente e sua pendencia/resolucao no backlog. Nenhum aceite depende de
outro chat; nao gerar novo prompt externo para cada etapa.

Nao abrir, copiar, migrar ou publicar dados reais. O Codex nao acessa ou configura
OCI por iniciativa propria; decisoes de producao e execucao das Etapas 11 e 12
cabem ao usuario. Nao antecipar etapas posteriores, instalar dependencias sem
necessidade comprovada ou ignorar as regras de Git do escopo: commits locais
validados no WEB autonomo; versionamento manual no legado. Na execucao WEB,
uma etapa posterior com dependencias concluidas passa a ser trabalho elegivel.
