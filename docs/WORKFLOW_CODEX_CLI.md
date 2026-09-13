# Protocolo operacional do Codex CLI

Planejamento, execucao, validacao e definicao das proximas etapas acontecem
exclusivamente na sessao do Codex CLI aberta neste repositorio. Os comandos
abaixo sao mensagens do usuario na sessao, nao comandos de shell ou scripts.
O [AGENTS.md raiz](../AGENTS.md) exige a leitura deste protocolo.

A unica fonte de etapas, pesos, dependencias, escopo, criterios de aceite,
estado, progresso, proxima etapa e decisoes externas pendentes e o
[backlog canonico](Projeto%20Stroop%20Test.md). Documentos tecnicos detalham
contratos; baselines e registros sao evidencias datadas, sem estado concorrente.

## `continue o projeto`

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
[procedimentos Docker](INFRAESTRUTURA_DOCKER.md). Justificar verificacoes nao
aplicaveis; indisponibilidade de teste obrigatorio nunca significa nao aplicabilidade.
O PsychoPy permanece local e fora do Docker. Alteracoes experimentais exigem
validacao estrutural e checklist Pilot autorizado, sem coleta real.

## Bloqueios e decisoes

Nao conceder progresso parcial nem concluir etapa com teste obrigatorio falhando,
pulado ou indisponivel. Manter o progresso anterior, registrar causa e evidencia
no registro de alteracoes e o bloqueio no backlog, sem marcar conclusao. Informar
exatamente qual decisao ou acao permite retomar. Se a revalidacao contradisser uma
conclusao antiga, registrar a divergencia sem recalcular progresso silenciosamente.

Perguntar ao usuario dentro da sessao sobre decisoes materiais, clinicas,
semanticas, arquiteturais, metodologicas, de privacidade, seguranca, producao ou
envolvendo dados reais que alterem o resultado. Registrar a decisao no documento
tecnico pertinente e sua pendencia/resolucao no backlog. Nenhum aceite depende de
outro chat; nao gerar novo prompt externo para cada etapa.

Nao abrir, copiar, migrar ou publicar dados reais. Nao acessar ou configurar OCI
antes da Etapa 11; nessa etapa, decisoes de producao exigem autorizacao explicita
na sessao. Nao antecipar etapas posteriores, instalar dependencias sem necessidade
comprovada ou executar `git add`, `git commit`, `git tag` ou `git push`.
