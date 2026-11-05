# Contribuição e GitHub Flow adaptado

Leia [AGENTS](AGENTS.md), [workflow](docs/WORKFLOW_CODEX_CLI.md) e a tarefa do
[backlog único](docs/Projeto%20Stroop%20Test.md). A missão documental atual não
autoriza implementação funcional nem produção.

Use main estável e branch coesa docs/feat/fix/refactor/test/chore por entrega ou
marco. Antes, confira status/branch/remotos/HEAD/upstream, preserve alterações
locais e faça fetch se acessível. Sincronize com ff-only só quando seguro; não
perca commits não integrados para trocar base. Reutilize branch apropriada.

Após unidade coerente e validada, revise diff/status e git diff --check; adicione
somente arquivos/hunks da tarefa. Use [Conventional Commits em português](docs/desenvolvimento/PADRAO_DE_COMMITS.md).
Commit e push são autônomos; no primeiro envio, git push -u origin BRANCH.
Registrar evidências/SHA/push no backlog. Se falhar, preservar trabalho e registrar
impedimento. Não versionar secrets, dados reais, SQLite, exports, logs ou backups.

**Não criar PR automaticamente, não fazer merge automático e não enviar direto
à main.** Integração depende de autorização específica e proteções/revisões
existentes. Se main exigir PR, não contornar nem reduzir proteção; o proprietário
definirá procedimento de integração. Sem force push, exclusão remota ou bypass.
Deploy, tags, alterações destrutivas e dados reais exigem autorização específica.

CI existente em [.github/workflows/web.yml](.github/workflows/web.yml) executa
verify em PR, push main e disparo manual; push de branch normalmente não dispara.
Não alterar/desabilitar gatilhos para evitar checks. Pipeline inclui scanner,
Python/PG sem skips, frontend/build, auditorias, Chromium/Firefox e HTTPS real.
[CI_WEB](docs/desenvolvimento/CI_WEB.md) descreve reprodução. Distinguir testes
locais de Actions por SHA; nunca declarar CI aprovada sem evidência. M8 prevê
revisar formalização desse pipeline no fluxo sem PR; pipeline não faz deploy.
