# Workflow canônico do Codex CLI

Mensagens abaixo são comandos de trabalho do usuário, não scripts. Fontes:
[AGENTS](../AGENTS.md), [backlog único](Projeto%20Stroop%20Test.md),
[requisitos](REQUISITOS_E_RASTREABILIDADE.md), [arquitetura](ARQUITETURA_WEB.md).
Históricos Wxx/etapas 1–12 não selecionam execução. Esta versão adota o
fluxo estruturado por marcos com Pull Request, Push e Merge Commit tradicional.

## Inicialização mínima

1. Ler AGENTS raiz e os aplicáveis, workflow e Retomada do backlog.
2. Conferir status, branch, remotos, HEAD, upstream e commits locais sem push;
   preservar cada alteração preexistente. Não abrir secrets/dados reais.
3. Ler ficha do marco/tarefa autorizados, dependências/decisões e evidências.
   Consultar requisitos, contrato científico/HTTP e testes apenas do escopo.
4. Verificar divergência concreta antes de repetir inventário. Registrar conflito
   documentação/código sem apagar aprovação histórica nem inferir funcionamento.
5. Apresentar plano breve e executar o trabalho autorizado. Não pedir confirmação
   para escolhas técnicas reversíveis; registrar hipótese quando não for decisão
   científica/de produto/privacidade que exija responsável.

## mostrar status

Somente leitura, inclusive backlog e Git. Informar contagem de entregáveis
aceitos, marco, tarefa em andamento, bloqueios/decisões, prioridade, próxima
executável e risco principal. Separar evidência histórica da executada na sessão;
ciência de teste anterior não é reexecução. Não alterar arquivos, instalar,
fazer commit/fetch/push ou consultar produção implicitamente. Se houver dúvida
sobre estado remoto, informar que não foi atualizado.

## continue o projeto

Autoriza implementação no marco vigente selecionado pelo backlog, salvo escopo
expresso mais restrito. Após M0, a primeira autorização posterior seleciona M1 e
WEB-001. A missão documental original não concedia essa autorização; consultar
o registro da sessão e o marco vigente na Retomada do backlog.

Para reproduzir a base existente em M1, seguir a
[receita local](desenvolvimento/BASELINE_LOCAL.md), com evidência apenas no backlog.

Selecionar tarefa PRONTA ou dependência interna coesa pronta. Verificar decisões
externas antes do trabalho dependente. Mudar para EM_ANDAMENTO quando iniciar.
Implementar comportamento observável preservando legado/contratos; sem funções
antecipadas ou dados reais. Testar e corrigir falhas introduzidas; registrar
comandos, ambiente, resultado, falhas/skips, limites e SHA. Usar EM_VALIDACAO
quando entrega estiver disponível e aceite ainda em conferência.

Atualizar matriz com testes reais e referência à evidência do backlog; conferir
cada critério e só então CONCLUIDA. Registrar branch, commits, push e CI por SHA.
Aprovar marco apenas quando todas tarefas e critérios da ficha forem comprovados.
Continuar automaticamente tarefas independentes autorizadas **dentro do marco**;
não avançar a outro marco sem autorização posterior. Encerrar com próxima ação
exata e estado persistido; nenhuma sessão conclui tarefa só por terminar o turno.

Se bloqueado: causa, evidência, responsável, ação de desbloqueio e dependentes no
backlog; marcar BLOQUEADA apenas quando impedimento concreto impedir a tarefa.
Dependência ainda não concluída mantém PENDENTE. Pode executar outra pronta do
mesmo marco. Credenciais, decisão metodológica/produto material, autorização de
risco ou recurso inacessível são os pontos de intervenção humana indispensáveis.

## validar marco atual

Não implementa funcionalidade nova. Conferir todos critérios/tarefas, executar
verificações proporcionais e registrar data/HEAD/comando/resultado. Distinguir
aprovação local, skips, double, integração real, medição física e Actions. Falta
de ferramenta/evidência obrigatória mantém critério não comprovado, não vira
aceite com ressalva automático. Apontar regressão e abrir correção autorizável;
não apagar conclusão histórica: registrar evidência nova e impacto atual.

Documentação: links relativos/âncoras, IDs/dependências, fonte única, Git diff
--check e revisão de escopo. Código: testes focados e regressão apropriada;
PG real descartável nos critérios transacionais; frontend tipos/build/DOM;
HTTPS/Playwright e medições manuais apenas quando exigidos. Não executar suites
pesadas apenas para validar uma edição documental.

## replanejar

Registrar motivo e evidência, mudança CHG no backlog, requisitos afetados,
componentes/testes a revisar, decisões/ADRs, dependências/prioridades e necessidade
de aprovação externa. Preservar IDs e histórico; não marcar concluído como
pendente sem regressão comprovada ou novo escopo explícito. Arquivar fonte
anterior quando a reorganização for material; deixar ponte de navegação, sem
segundo backlog ativo. Progresso muda só por aceites/alteração rastreada de escopo.
Replanejamento não autoriza implementação por implicação.

## Git e encerramento

GitHub Flow com Pull Request, Push e Merge Commit tradicional, conforme [CONTRIBUTING](../CONTRIBUTING.md).
Status/branch/remotos → preservar worktree → fetch quando acessível em sessão de
escrita → conferir base → sincronização ff-only se segura → branch coesa.
Não criar outra branch se a atual for adequada. Base com trabalho não integrado
pode ser preservada com justificativa, sem descartar commits para partir de main.

Ciclo de entrega e integração:
1. Validar unidade coerente: `git diff --check`, testes do marco/tarefa, validação documental.
2. Commit atômico com Conventional Commits em português e push autônomo com upstream: `git push -u origin BRANCH`.
3. Abertura/atualização de Pull Request para `main`:
   ```bash
   gh pr create --base main --head BRANCH --title "tipo(escopo): descrição" --body-file /caminho/resumo.md
   ```
4. Verificação de CI remota: aguardar a conclusão dos checks obrigatórios (`verify`).
5. Merge autorizado via Merge Commit tradicional:
   ```bash
   gh pr merge --merge --match-head-commit SHA_VALIDADO
   git switch main
   git pull --ff-only
   ```
   Nunca usar Squash Merge, Rebase Merge ou push direto em `main`. Manter o auto-merge
   do GitHub desabilitado.

Push falhou: investigar sem sobrescrever histórico, registrar causa/pendência; não
força, não altera proteção. Se houver bloqueio de CI ou pendência de revisão, manter
o PR aberto e registrar o motivo. Deploy, tags, dados reais e operações destrutivas
têm aprovação específica e não decorrem de commit/push/merge.

No backlog: ID, estado/aceite, branch, SHA real, testes/evidências/data, limitações,
push, PR e CI. Evitar autorreferência de SHA: registrar hash da entrega no fechamento
posterior ou consulta Git inequívoca para o próprio fechamento. Não criar commits
artificiais só para atualizar hash. Actions não executado/não verificado é um estado
válido de registro, não equivalente a aprovado. Nunca desabilitar checks para
adaptar fluxo.

Final: resultado, arquivos, validações, riscos/pendências, branch/commits/push/PR/CI/merge
e próxima tarefa.

## Compatibilidade de comandos antigos

`mostrar status web` é alias de mostrar status. `continue web`, `execute Wxx`,
`validar etapa atual` e `validar etapa web Wxx` não reiniciam fichas arquivadas:
identificar intenção e mapear tarefa WEB/marco vigente com escopo explícito.
Na ausência de mapeamento seguro, informar referência histórica e pedir apenas a
clarificação indispensável. Nunca retomar antigas ações W22/VPS por um alias.

## Verificação documental reproduzível

Executar na raiz, com Python padrão e sem instalar dependências:

```bash
python3 scripts/verify_web_docs.py
python3 -m unittest tests.test_verify_web_docs -v
git diff --check
```

O [validador](../scripts/verify_web_docs.py) substitui o bloco inline inicial de
M0 que fixava 42 tarefas/36 requisitos/10 riscos/5 decisões/11 marcos. Contagens
agora derivam das fichas/tabelas canônicas; IDs existentes em HEAD não podem
sumir. Expansão exige CHG com motivo e atualização do denominador. Valida IDs
únicos/sequenciais, estados/campos, referências existentes, grafo acíclico,
matriz requisito→tarefa/marco, links/âncoras e painel/progresso contra fichas.
Não lê dados identificáveis nem considera dados/artefatos ignorados como fixtures.
A inspeção de escopo Git continua obrigatória: somente Markdown era uma restrição
da missão original M0, não uma regra para futuras missões com código autorizado.
Asserções relevantes não devem ser removidas para permitir expansão passar.

Isso não comprova critério funcional ou científico, ciclos semânticos externos,
qualidade visual ou aprovação de DEC-04. Revisar critérios, testes e evidência/SHA.
Os números históricos de M0 ficam preservados no backlog.

## Integração UX no fluxo vigente — CHG-003

Nenhum comando novo, marco de redesign ou segundo backlog. Consultar as fichas
WEB-042/043/044, REQ-UX-001…011 e [UX](experimento/UX_DECISIONS.md).

- `mostrar status`: incluir novas dependências e impedimentos; requisito
  documentado não significa barra de precisão removida. Consultar runtime e
  evidências atuais; não reinterpretar os aceites anteriores como teste do visual
  novo. Não confundir progresso do backlog com indicador de tentativas.
- `continue o projeto`: somente tarefas do marco autorizado com dependências,
  critérios/testes e decisões satisfeitos. Priorizar risco científico. A revisão visual D3/D4
  de 2026-11-05 pelo proprietário aprova stroop-web-outline/1.0.0 e desbloqueia
  a implementação de WEB-042/043; não aprova a matriz DEC-04. Escolhas A puramente
  visuais só são independentes quando não burlam aprovação B/C da apresentação.
  Executar prontas de M3, sem antecipar instruções/fluxo M4 ou dashboard M5.
  WEB-011 deve usar layout final aprovado/testado e transporte DEC-02 ativo;
  não aceitar campanha exclusivamente do visual antigo ou reduzir gates D5.
- `validar marco atual`: conferir funcionalidade, screenshots das dez cores,
  ausência real de caixa/precisão agregada em prática/principal (DOM e árvore
  acessível), feedback individual da prática e cálculos/persistência preservados,
  cronômetro monotônico/progresso real, timing, integridade documental e SHA.
  Vitest/typecheck/build e Playwright/Python conforme fichas, incluindo integração
  real nos marcos próprios. CSS/screenshot não prova validade experimental.
- `replanejar`: registrar próximas solicitações em CHG sequencial, preservar
  fonte única, IDs/aceites/evidências e recalcular entregáveis aceitos/vigentes.

A direção de UX remove informação agregada potencialmente distrativa; não é
promessa de melhoria científica. Implementação, teste, aceite e decisão metodológica
são evidências distintas. Não encerrar M3 sem WEB-011/012 e demais gates.
