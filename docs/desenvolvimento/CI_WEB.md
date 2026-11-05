# Verificacoes reproduziveis WEB

O workflow [WEB validada](../../.github/workflows/web.yml) executa verificacoes em
pull requests, pushes em `main` e disparos manuais. Push em branch de trabalho
nao duplica a execucao do PR. Nao faz deploy, publica artefatos,
configura VPS nem usa credenciais externas. O job falha diante de teste,
skip Python, vulnerabilidade conhecida ou deteccao de secrets; nao existe
`continue-on-error`. Regras de branch protegida devem exigir o check `verify`
no repositorio remoto para bloquear merge; essa configuracao externa nao e
criada pelo arquivo de workflow.

Contribuicoes seguem [GitHub Flow](../../CONTRIBUTING.md). O agente aguarda CI
e regras/revisoes exigidas antes de Merge Commit tradicional por PR; nao usa
bypass administrativo, Squash Merge, Rebase Merge ou push direto em main.
O resultado integrado e verificado novamente por push em `main`.
Registro historico de 2026-11-04 (historico linear substituido abaixo): `verify` do app GitHub Actions,
branch atualizada, PR obrigatorio, historico linear e conversas resolvidas,
inclusive para administradores. Nao se adicionou aprovador externo obrigatorio;
revisoes existentes continuam respeitadas. Force push/exclusao de main bloqueados;
branches temporarias sao removidas automaticamente depois do merge permitido.

## Metodo de merge e protecoes — 2026-11-05

Auditoria via API autenticada com permissao administrativa: Merge Commit ja
habilitado, Squash e Rebase habilitados, historico linear obrigatorio. Alterados
somente `allow_squash_merge` para false e `required_linear_history` para false;
Merge Commit permanece habilitado. Rebase permanece habilitado na configuracao
do repositorio, mas o workflow do Codex usa exclusivamente Merge Commit.

A reconsulta confirmou PR obrigatorio, `verify` do GitHub Actions (app 15368),
branch atualizada (`strict`), descarte de revisoes obsoletas, conversas resolvidas
e aplicacao das regras a administradores. Quantidade de aprovacoes exigidas
continua zero; code owners e ultima aprovacao por outro autor continuam como
antes. Force push e exclusao de main continuam bloqueados; assinaturas continuam
sem exigencia. Nenhum ruleset de repositorio ou herdado foi encontrado, nem regra
adicional efetiva; proprietario e conta pessoal. Auto-merge continua desabilitado:
aguardar checks e usar `gh pr merge --merge`, sem alterar essa configuracao.
Workflows, permissoes de usuarios e demais configuracoes foram preservados.

Exportacao original, alvo, resultado verificado e rollback estao no diretorio
local `/home/raposo/.local/state/stroop-merge-commit/20261105T172953Z`, fora do Git.
Regra afetada: protecao classica de `main`, endpoint
`repos/thiagorraposo/stroop-go-nogo-psychopy/branches/main/protection`; sem ruleset
para alterar. Para rollback, reconsultar a API e comparar alteracoes concorrentes;
restaurar os dois valores originais conforme `ROLLBACK.txt`, usando os payloads
`rollback-repository.json` (PATCH do repositorio) e `rollback-protection.json`
(PUT da protecao). Nao restaurar cegamente sobre mudancas posteriores. Nenhum
historico de commit e alterado pelo rollback de configuracao.

Validacao da configuracao feita por API e comparacao integral da protecao:
a unica diferenca foi historico linear. Metodos de merge e configuracoes nao
relacionadas conferidos separadamente. Isso nao equivale a CI aprovada nem a
ensaio de merge: resultados de Actions devem ser consultados por SHA no PR.

## Ambiente e isolamento

Use Python 3.12.3, Node 24.15.0, Docker, OpenSSL, Git e Linux com os navegadores
Chromium/Firefox do Playwright fixado em [package-lock.json](../../web/package-lock.json).
As actions sao fixadas por SHA; PostgreSQL17.6-bookworm usa o mesmo digest do
Compose. O build frontend ja executa typecheck, sem chamada duplicada ao tsc.
Dependencias Python
vêm dos locks [dashboard](../../dashboard/requirements.lock) e
[API](../../api/requirements.lock), sem resolver novas versoes da aplicacao.
O checkout do workflow usa sparse-checkout antes de materializar os arquivos:
exclui `data/`, `database/`, `production-secrets/` e `.env*` operacionais, incluindo
somente os dois exemplos de ambiente. O runner nao le `.env` e nao requer dados
locais ou autenticacao Google externa.

Crie um banco exclusivamente descartavel, com nome `stroop_etapa4_test_*`.
O harness HTTPS recria o schema desse banco e usa somente fixtures sinteticas.
O workflow usa PostgreSQL em tmpfs, portas aleatorias e credencial publica
inequivocamente sintetica. Nunca use uma URL de banco operacional.

Para reproduzir o checkout sem copiar dados historicos, prepare primeiro uma
worktree separada sem checkout. Substitua `REVISAO` pelo commit a validar e
`/tmp/stroop-web-ci-checkout` por um caminho novo:

```bash
git worktree add --detach --no-checkout /tmp/stroop-web-ci-checkout REVISAO
git -C /tmp/stroop-web-ci-checkout sparse-checkout set --no-cone --stdin <<'SPARSE'
/*
!/data/
!/database/
!/production-secrets/
!**/.env*
/.env.example
/.env.production.example
SPARSE
git -C /tmp/stroop-web-ci-checkout checkout --detach REVISAO
cd /tmp/stroop-web-ci-checkout
```

Assim, `npm ci` atua somente na worktree isolada e preserva ambientes/previas
abertos no checkout de desenvolvimento. Nunca crie um checkout integral para
so depois apagar dados ou secrets.

Exemplo local: crie um container novo, sem volumes persistentes e com porta
local livre. Nao reutilize nem encerre containers de outros trabalhos.

```bash
docker run --detach --name stroop-web-ci-local \
  --tmpfs /var/lib/postgresql/data:rw \
  --publish 127.0.0.1::5432 \
  --env POSTGRES_USER=synthetic \
  --env POSTGRES_PASSWORD=synthetic-ci-only \
  --env POSTGRES_DB=stroop_etapa4_test_ci postgres:17.6
docker port stroop-web-ci-local 5432/tcp
```

Defina `TEST_DATABASE_URL` com a porta retornada, por exemplo, substituindo
`PORTA` por um numero:

```bash
export TEST_DATABASE_URL='postgresql://synthetic:synthetic-ci-only@127.0.0.1:PORTA/stroop_etapa4_test_ci'
python3 -m venv .venv
.venv/bin/python -m pip install -r dashboard/requirements.lock -r api/requirements.lock
.venv/bin/python -m pip check
docker pull ghcr.io/gitleaks/gitleaks:v8.30.1
.venv/bin/python scripts/verify_web_ci.py sources
.venv/bin/python scripts/verify_web_ci.py secret-self-test
.venv/bin/python scripts/verify_web_ci.py python
.venv/bin/python scripts/verify_web_ci.py frontend
.venv/bin/python scripts/verify_web_ci.py audit
(cd web && npx playwright install --with-deps chromium firefox)
.venv/bin/python scripts/verify_web_ci.py browser
.venv/bin/python scripts/verify_web_ci.py integration
```

Aguarde `docker exec stroop-web-ci-local pg_isready -U synthetic -d
stroop_etapa4_test_ci` retornar sucesso antes da suite. Ao terminar, remova
somente esse container descartavel com `docker rm --force stroop-web-ci-local`.
Os mesmos estagios podem ser executados sequencialmente com
`.venv/bin/python scripts/verify_web_ci.py all`, apos instalar os navegadores.
O primeiro erro encerra o runner com codigo diferente de zero. A auditoria
executa depois do frontend e antes de instalar/executar navegadores e integrar
HTTPS, evitando essas verificacoes longas quando as dependencias sao recusadas.

## Cobertura e limites

- Python executa a descoberta integral, incluindo API/contratos HTTP e
  PostgreSQL real, e rejeita skips como aceite incompleto.
- Frontend executa `npm ci`, testes de logica/DOM, tipos e build. Navegadores
  executam casos gerais e depois `@timing` serial, sem trace. O runner usa
  exclusivamente `127.0.0.1:4273`, preservando uma previa em 4173. A configuracao
  Playwright aceita `WEB_TEST_PORT` numerica, sem alterar host ou reutilizar
  servidores existentes; uma porta ocupada causa falha.
- Integracao HTTPS usa 4373/4381, certificado efemero e API/PostgreSQL reais.
  Convites/cookies e resultados sao sinteticos; o harness remove seus proprios
  processos/certificados. Nao comprova Google externo, TLS de producao ou latencia
  fisica, que conservam gates no [roadmap](../ROADMAP_WEB.md).
- `npm audit --audit-level=low` e `pip-audit==2.10.1 --strict --no-deps
  --disable-pip` consultam bases publicas de vulnerabilidades conhecidas. O
  auditor Python fica em venv temporaria, removida ao final; nao altera os locks
  ou instala ferramentas no ambiente da aplicacao. Falha de consulta bloqueia
  a verificacao; ausencia de achados nao e garantia de ausencia de falhas.
- Secrets: [Gitleaks 8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)
  analisa um snapshot temporario das fontes enumeradas por `git ls-files`.
  Nao abre `data/`, `database/`, secrets operacionais, arquivos ignorados ou
  historico Git. `.env` operacional versionado bloqueia por caminho, antes de
  ler conteudo; os dois exemplos de ambiente sao permitidos. Chaves/certificados
  `.key`, `.pem`, `.p12` e `.pfx` versionados bloqueiam
  por caminho, sem leitura; Dockerfile/Makefile e configuracoes de texto entram
  no snapshot. Symlinks em fontes exigem revisao. Nao ha exclusoes por marcadores
  sinteticos ou pasta de testes.
  O scanner nao possui rede, recebe snapshot somente leitura e imprime somente
  caminho/linha/regra validados em caso de deteccao, sem valores ou saida bruta.
  Falha exige investigacao local segura.

Nao ha upload de traces, screenshots, dumps, CSVs, logs ou relatorios de secrets
como artefatos do workflow. O build e efemero; nao e publicacao. A worktree original conserva seus arquivos preexistentes. O checkout sparse e
o scanner de fontes nao concedem validacao ou permissao para acessar dados de
coleta fora do escopo.

Fontes das ferramentas: [pip-audit](https://github.com/pypa/pip-audit),
[Gitleaks Docker/CLI](https://github.com/gitleaks/gitleaks),
[servicos PostgreSQL no Actions](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers).

O estagio `secret-self-test` executa Gitleaks em um Git temporario: uma fonte
inocua deve passar e um token falso gerado na hora deve bloquear. Valores e
findings nao sao impressos. Isso comprova o caminho de falha, sem desabilitar
verificacoes ou introduzir um secret versionado. Os testes do runner tambem
protegem falha imediata, rejeicao de skips e validacao do banco descartavel.


## Evidencia local de execucao

Em 2026-10-16, `verify_web_ci.py all` passou no checkout sparse limpo de
721c86c, Python3.12.3/Node24.15.0 e PostgreSQL17.6 em tmpfs: 284 testes Python
sem skips, 188 frontend, typecheck/build, 40 casos gerais de navegador, quatro
temporais seriais e 18 HTTPS/API/PostgreSQL reais sob CSP. Gitleaks248fontes,
falso PAT controlado e auditorias npm/Python aprovados. Dados historicos nao
foram materializados. O checkout permaneceu sem alteracoes versionadas.

Actionlint1.7.7 identificou/corrigiu o contexto da porta de servico no workflow;
a correcao em 3b20144 foi validada estaticamente, sem mudar codigo/runner
exercitados. SHAs das tres actions foram conferidos na API oficial do GitHub.
Nao houve push ou execucao no GitHub hospedado: os comandos do pipeline foram
executados localmente, e a configuracao do workflow foi validada por lint.
Resultados e proximos passos ficam em [PROGRESS](../PROGRESS.md).
