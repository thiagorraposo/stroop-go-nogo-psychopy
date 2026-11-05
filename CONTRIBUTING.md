# Contribuir

Use GitHub Flow: `main` estavel e branches curtas `feat/`, `fix/`, `refactor/`,
`docs/` ou `chore/`. Leia os `AGENTS.md` aplicaveis, preserve alteracoes locais
alheias e consulte o [roadmap WEB](docs/ROADMAP_WEB.md) para dependencias e aceite.
Nao inclua coletas, bancos, exports, chaves ou configuracoes privadas.

## Fluxo essencial

Com worktree conferida, parta de `main` atualizada:

```bash
git switch main
git pull --ff-only
git switch -c feat/nome-curto
```

Implemente e valide a unidade. Use Conventional Commits em portugues conforme
o [padrao](docs/desenvolvimento/PADRAO_DE_COMMITS.md), adicionando apenas os
arquivos ou hunks da tarefa. Exemplo:

```bash
git diff --check
git add CAMINHOS-DA-TAREFA
git commit -m "feat(web): descreve o comportamento entregue"
git push -u origin feat/nome-curto
gh pr create --base main --title "feat(web): descreve o comportamento entregue" --body-file /tmp/pr.md
gh pr checks --watch --fail-fast
```

A descricao deve explicar o problema, o comportamento entregue, a validacao
executada e limites relevantes. Para textos multilinha, use arquivo com
`--body-file`; nao interpole secrets ou dados em comandos/comentarios.

Integre somente com CI aprovada, revisoes exigidas e regras satisfeitas.
Use exclusivamente Merge Commit tradicional, preservando todos os commits
originais. Confira o SHA revisado antes do merge:

```bash
gh pr view --json headRefOid
gh pr merge --merge --match-head-commit SHA-REVISADO
git switch main
git pull --ff-only
```

PR e check `verify` sao obrigatorios, inclusive para administradores. Nunca
integre por Squash Merge, Rebase Merge ou push direto em `main`. Quando o
repositorio permitir auto-merge, pode usar `gh pr merge --merge --auto
--match-head-commit SHA-REVISADO`. Se indisponivel, aguarde as verificacoes e
aprovacoes exigidas e use o merge normal acima, sem habilitar excecoes. Se a
branch mudar, valide o novo SHA; se `main` avancar, atualize a branch por merge
normal quando exigido e aguarde novamente os checks. Conflitos, falhas ou
conversas obrigatorias pendentes impedem a integracao. Apos o merge, confirme
que os commits originais sao ancestrais de `origin/main` e registre o resultado.

Se a worktree tiver alteracoes alheias, preserve-as antes da troca; nunca use
reset destrutivo ou force push. Nao use `--admin` para contornar protecoes.
Exclua somente branches temporarias integradas. Nao existe branch de
integracao permanente adicional. Deploy, tags e operacoes destrutivas exigem
autorizacao especifica; merge nao faz deploy.

## Validacao e CI

O workflow [WEB validada](.github/workflows/web.yml) tem um job `verify`:
scanner de secrets com prova negativa, suite Python sem skips com PostgreSQL
descartavel, testes frontend, tipos/build, Chromium/Firefox, integracao HTTPS
com API/banco reais e auditorias de dependencias. Usa somente dados sinteticos,
acoes fixadas por SHA, permissoes de leitura e nenhum secret operacional.

PRs executam a verificacao; pushes em branches de trabalho nao duplicam esse
job. Push em `main` verifica o resultado integrado; disparo manual permanece
disponivel. A concorrencia cancela execucoes antigas da mesma referencia.

Execute localmente os checks proporcionais a mudanca e sempre `git diff --check`.
Para reproduzir o pipeline completo, inclusive preparar banco isolado e
dependencias, siga [CI_WEB](docs/desenvolvimento/CI_WEB.md). Nunca use `.env`
operacional ou um banco de coleta para testes. Falhas, skips e ferramentas
obrigatorias indisponiveis impedem o aceite; mocks nao substituem integracao real.

Ao concluir, registre fatos no [registro](docs/REGISTRO_DE_ALTERACOES.md) e
retomada em [PROGRESS](docs/PROGRESS.md), sem duplicar estado do roadmap.
