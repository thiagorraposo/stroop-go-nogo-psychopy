# Reprodução local da base WEB

Este procedimento usa somente fontes e fixtures sintéticas. Estado, resultados,
SHA, limitações e próxima tarefa ficam no [backlog canônico](../Projeto%20Stroop%20Test.md).
O [workflow](../WORKFLOW_CODEX_CLI.md) seleciona a tarefa; o
[runner existente](CI_WEB.md) define ferramentas e isolamento.

## Preparar e verificar

1. Conferir status, branch, HEAD e upstream sem ler `.env`, coletas ou backups.
2. Criar worktree sparse na revisão escolhida conforme CI_WEB, excluindo dados
   e secrets **antes** do checkout. Usar uma branch coesa para registrar a entrega;
   preservar a base documental ainda não integrada à main.
3. Criar `.venv` nessa worktree e instalar os dois locks Python existentes.
   Executar `.venv/bin/python -m pip check`. Não resolver versões novas.
4. Criar apenas o container PG descartável descrito em CI_WEB, com nome exclusivo,
   tmpfs, porta aleatória em loopback e banco `stroop_etapa4_test_*`.
   Esperar `pg_isready` e configurar `TEST_DATABASE_URL` com essa porta.
5. Na raiz isolada, executar:

```bash
.venv/bin/python scripts/verify_web_ci.py sources
.venv/bin/python scripts/verify_web_ci.py secret-self-test
.venv/bin/python scripts/verify_web_ci.py python
.venv/bin/python scripts/verify_web_ci.py frontend
```

Python rejeita skips. Frontend executa `npm ci`, Vitest e build com typecheck.
Falha deve ser classificada antes de qualquer aceite. A mensagem de auditoria
sintética recusada durante os testes do runner é uma prova negativa controlada;
o resultado final da suite determina seu sucesso.

## Preservação de métricas, CLIs e fronteiras

Os testes abaixo já participam da descoberta integral. Para investigar uma
regressão localizada, podem ser executados separadamente:

```bash
.venv/bin/python -m unittest \
  tests.test_nucleo_compartilhado tests.test_casos_uso_importacao \
  tests.test_csv_unificado tests.test_importar_csv_sqlite \
  tests.test_multiplos_instrumentos tests.test_web_results tests.test_web_export -v
```

`test_web_export` percorre fixtures compartilhadas de principal, ausência de hits,
CSV canônico, recálculo e importação SQLite. `test_web_results` confere conversão
ms→s e distingue sentinela legada de ausência HTTP. Os testes do núcleo/casos de
uso verificam reexports, identidade de exceções, CLI por caminho/módulo, execução
fora da raiz, duplicidade e `--force`, apenas em arquivos temporários.

Mapa atual de dependências, conforme [arquitetura](../ARQUITETURA_WEB.md):

| Camada | Dependências internas observadas / contrato |
|---|---|
| `domain` | Próprio domínio e biblioteca padrão; sem acesso a arquivos/banco/rede |
| `ingestion` | Domínio e ingestão; leitura CSV e normalização |
| `application` | Domínio, ingestão, persistência e casos de uso |
| `persistence` | Domínio, ingestão, persistência e erros de aplicação |
| `scripts`, API, dashboard | Adaptadores consumidores do núcleo |

Casos de uso e persistência compartilham exceções de aplicação, sem importar
CLIs, dashboard ou HTTP. Os testes em subprocesso sem `site-packages` verificam
que normalização e importação SQLite não carregam interfaces ou PostgreSQL.
`NormalizedAssessment`, `InstrumentAdapter` e `test_code`/`test_version` são os
pontos existentes de extensão; o instrumento demonstrativo permanece sintético.
Não acrescentar instrumento nem abstração para reproduzir a base.

## Ensaio local integrado e retomada

Após a suite Python encerrar, usando o mesmo PG exclusivamente descartável:

```bash
.venv/bin/python scripts/verify_web_ci.py browser
.venv/bin/python scripts/verify_web_ci.py integration
```

Navegadores Playwright devem estar disponíveis nas versões do lock; caso faltem,
seguir CI_WEB. O primeiro comando usa a prévia Vite em 4273. O segundo reconstrói
o React e inicia API real em 4381 e proxy HTTPS local em 4373, com certificado
sintético efêmero. O harness recria o schema do banco descartável, provisiona
papéis restritos e encerra seus processos. Não compartilhar esse banco com a
suite Python em execução. OIDC externo e produção não participam desse ensaio.

Para retomar sem novo inventário: ler AGENTS → workflow → Retomada/ficha do
backlog → esta receita; conferir Git e usar o SHA registrado na evidência.
Consultar apenas contratos/testes da tarefa selecionada. Registrar resultados
locais separadamente de Actions; push de branch não implica CI executada.
Encerrar/remover somente o container criado para o ensaio. Conservar os commits
e a worktree de entrega; não remover trabalho preexistente.
