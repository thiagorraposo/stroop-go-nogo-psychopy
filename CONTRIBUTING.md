# Contribuição e GitHub Flow adaptado

Leia [AGENTS](AGENTS.md), [workflow](docs/WORKFLOW_CODEX_CLI.md) e a tarefa do
[backlog único](docs/Projeto%20Stroop%20Test.md). A missão documental original M0 não
autorizava implementação funcional; o marco e a autorização vigentes devem ser
consultados no backlog. Produção sempre exige autorização específica.

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
Quando autorizada a integração por PR, usar **Merge Commit tradicional**,
preservando os commits originais; sem Squash Merge em novas integrações. A
preferência não autoriza criar PR/merge automaticamente ou alterar proteções.
Configuração remota conferida em 2026-11-05: Merge Commit habilitado, Squash Merge
desabilitado; Rebase Merge habilitado não substitui a preferência do proprietário.

CI existente em [.github/workflows/web.yml](.github/workflows/web.yml) executa
verify em PR, push main e disparo manual; push de branch normalmente não dispara.
Não alterar/desabilitar gatilhos para evitar checks. Pipeline inclui scanner,
Python/PG sem skips, frontend/build, auditorias, Chromium/Firefox e HTTPS real.
[CI_WEB](docs/desenvolvimento/CI_WEB.md) descreve reprodução. Distinguir testes
locais de Actions por SHA; nunca declarar CI aprovada sem evidência. M8 prevê
revisar formalização desse pipeline no fluxo sem PR; pipeline não faz deploy.
