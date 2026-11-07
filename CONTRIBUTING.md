# Contribuição e GitHub Flow

Leia [AGENTS](AGENTS.md), [workflow](docs/WORKFLOW_CODEX_CLI.md) e a tarefa do
[backlog único](docs/Projeto%20Stroop%20Test.md). A missão documental original M0 não
autorizava implementação funcional; o marco e a autorização vigentes devem ser
consultados no backlog. Produção sempre exige autorização específica.

Use main estável e branch coesa docs/feat/fix/refactor/test/chore por entrega ou
marco. Antes, confira status/branch/remotos/HEAD/upstream, preserve alterações
locais e faça fetch se acessível. Sincronize com ff-only só quando seguro; não
perca commits não integrados para trocar base. Reutilize branch apropriada.

Após unidade coerente e validada, revise diff/status e `git diff --check`; adicione
somente arquivos/hunks da tarefa. Use [Conventional Commits em português](docs/desenvolvimento/PADRAO_DE_COMMITS.md).
Commit e push são autônomos; no primeiro envio, `git push -u origin BRANCH`.
Registrar evidências/SHA/push no backlog. Se falhar, preservar trabalho e registrar
impedimento. Não versionar secrets, dados reais, SQLite, exports, logs ou backups.

Abertura e atualização de Pull Request (`gh pr create`) para `main` fazem parte do
fluxo de trabalho, com descrição objetiva do problema, comportamento entregue, validação
executada e limites relevantes:

```bash
git diff --check
git add CAMINHOS-DA-TAREFA
git commit -m "tipo(escopo): descrição do comportamento entregue"
git push -u origin BRANCH
gh pr create --base main --head BRANCH --title "tipo(escopo): descrição" --body-file /caminho/resumo.md
gh pr checks --watch --fail-fast
```

Use exclusivamente **Merge Commit tradicional**, preservando todos os commits originais.
Confira o SHA revisado antes do merge:

```bash
gh pr view --json headRefOid
gh pr merge --merge --match-head-commit SHA-REVISADO
git switch main
git pull --ff-only
```

PR e check `verify` são obrigatórios, inclusive para administradores. Nunca integre
por Squash Merge, Rebase Merge ou push direto em `main`. Mantenha o auto-merge do
GitHub desabilitado; nunca use `--auto`. Aguarde as verificações e aprovações exigidas
antes de executar o merge tradicional. Se a branch mudar, valide o novo SHA; se `main`
avançar, atualize a branch por merge normal quando exigido e aguarde novamente os checks.
Conflitos, falhas ou conversas pendentes impedem a integração. Após o merge, confirme
que os commits originais são ancestrais de `origin/main` e registre o resultado.

Se a worktree tiver alterações alheias, preserve-as antes da troca; nunca use
reset destrutivo ou force push. Não use `--admin` para contornar proteções.
Exclua somente branches temporárias integradas. Não existe branch de integração
permanente adicional. Deploy, tags e operações destrutivas exigem autorização específica;
merge não faz deploy.

## Validação e CI

O workflow [WEB validada](.github/workflows/web.yml) tem um job `verify`:
scanner de secrets com prova negativa, suíte Python sem skips com PostgreSQL
descartável, testes frontend, tipos/build, Chromium/Firefox, integração HTTPS
com API/banco reais e auditorias de dependências. Usa somente dados sintéticos,
ações fixadas por SHA, permissões de leitura e nenhum secret operacional.

PRs executam a verificação; pushes em branches de trabalho isoladas não duplicam esse
job. Push em `main` verifica o resultado integrado; disparo manual permanece
disponível via `workflow_dispatch`. A concorrência cancela execuções antigas da mesma referência.

Execute localmente os checks proporcionais à mudança e sempre `git diff --check`.
Para reproduzir o pipeline completo, inclusive preparar banco isolado e dependências,
siga [CI_WEB](docs/desenvolvimento/CI_WEB.md). Nunca use `.env` operacional ou um banco de
coleta para testes. Falhas, skips e ferramentas obrigatórias indisponíveis impedem o
aceite; mocks não substituem integração real.
