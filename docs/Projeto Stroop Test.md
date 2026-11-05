# Projeto Stroop Test — backlog canônico da plataforma WEB

Última verificação documental: **2026-11-05**. Missão e limites:
[arquitetura](ARQUITETURA_WEB.md); inventário: [auditoria](AUDITORIA_REPLANEJAMENTO.md);
especificação: [requisitos e matriz](REQUISITOS_E_RASTREABILIDADE.md).
Este é o único registro executável de marcos, tarefas, estados, dependências,
aceite, progresso, riscos, bloqueios e próxima tarefa. Documentos históricos não
concedem autorização nem mantêm progresso atual. IDs WEB nunca são renumerados.

## Governança e cálculo

Estados: PENDENTE (dependência/escopo ainda não pronto), PRONTA (dependências e
decisões satisfeitas, falta execução/autorização de sessão), EM_ANDAMENTO
(trabalho ativo), BLOQUEADA (impedimento identificado com ação de desbloqueio),
EM_VALIDACAO (entrega disponível, critérios em conferência), CONCLUIDA (todos
critérios comprovados). Não há crédito parcial. Autorização de sessão é distinta
de prontidão técnica. A missão documental encerrou em M0; o comando posterior
`continue o projeto`, em 2026-11-04, autorizou M1 até seu encerramento.
O comando de 2026-11-05 autorizou M2, já concluído. Novo `continue o projeto`
autoriza M3, condicionado às decisões de suas tarefas; DEC-04 continua pendente.

Uma tarefa CONCLUIDA tem todos critérios, comandos/resultados/data, componente,
referências de teste e Git. Documento é evidência suficiente apenas para entrega
explicitamente documental; código/push não prova integração. Skips, testes com
double e piloto automatizado não substituem verificações reais exigidas.
Marcos encerram somente com todas suas tarefas e gate da ficha atendidos. Não
avançar automaticamente para outro marco; encerrar unidade no marco autorizado,
indicar o próximo e aguardar instrução que o autorize. Bloqueios locais permitem
outras tarefas independentes do mesmo marco autorizado.

Unidade de progresso: contagem de entregáveis WEB aceitos / tarefas vigentes,
sem pesos nem prazo artificial. Cada ficha abaixo é um entregável; complexidades
não são pesos. M0 conta preparação documental, não implementação WEB. Mudanças
de denominador exigem motivo e IDs novos, sem renumerar/remover histórico.
Histórico legado: 87% das etapas 1–12 e aceites Wxx ficam nos arquivos congelados;
não são transferidos, nem se declaram inválidos por esta revalidação de novo escopo.

Progresso atual: **11/45 entregáveis aceitos (WEB-000 a WEB-010)**.
WEB-005 é documental; WEB-006 aceita o receptor backend e contratos em banco
sintético. M1 e M2 concluídos; atomicidade e paridade aceitas em EV-M2-007/008.
A captura incremental no motor e seus gates temporais continuam em M3/M4.

## Painel visual de acompanhamento

Atualizado em **2026-11-05**, a partir das fichas deste backlog.

| Entregáveis aceitos | Ainda sem aceite | Marco autorizado | Próxima ação |
|---|---|---|---|
| **11 de 45 · 24,4%** | **34** | **M3 · apresentação e DEC-04 pendentes** | Aprovar apresentação/D3 e identificação/D4 → WEB-042/043; campanha [WEB-011](#web-011--executar-campanha-de-engenharia-temporal-em-ambientes-declarados) ainda exige DEC-04 |

```text
Aceites   █████░░░░░░░░░░░░░░░   24,4%
```

A barra global é aproximada; os números são exatos, com percentual arredondado.
O indicador conta entregáveis aceitos, sem pesos ou crédito parcial; não mede
percentual de código pronto, prazo restante ou prontidão para pesquisa/produção.
M0 e WEB-005 são documentais; a baseline de M1 tem os limites descritos em EV-M1.

### Visão por marco

Cada quadrado representa **um entregável** do respectivo marco:
🟩 aceito · ⬜ sem aceite. Clique no marco para consultar escopo e critérios.
A ordem da tabela segue os IDs; dependências e paralelismo estão na
[ordem de execução](#ordem-caminho-crítico-e-paralelismo).

| Marco | Entrega principal | Aceites | Situação |
|---|---|---|---|
| [M0](#m0--auditoria-e-replanejamento-documental) | Auditoria e replanejamento documental | 🟩 **1/1** | ✅ Concluído |
| [M1](#m1--fundação-e-baseline-reproduzível) | Fundação e baseline reproduzível | 🟩🟩🟩🟩 **4/4** | ✅ Concluído |
| [M2](#m2--backend-e-contratos-de-dados-consolidados) | Backend e contratos de dados consolidados | 🟩🟩🟩🟩 **4/4** | ✅ Concluído |
| [M3](#m3--viabilidade-e-motor-experimental-no-navegador) | Viabilidade e motor experimental no navegador | 🟩🟩⬜⬜⬜⬜⬜ **2/7** | ◐ Apresentação e DEC-04 pendentes |
| [M4](#m4--fluxo-ponta-a-ponta-de-avaliações) | Fluxo ponta a ponta de avaliações | ⬜⬜⬜⬜ **0/4** | ○ Pendente |
| [M5](#m5--interface-administrativa-e-analítica-react) | Interface administrativa e analítica React | ⬜⬜⬜⬜ **0/4** | ○ Pendente |
| [M6](#m6--autenticação-permissões-e-segurança) | Autenticação, permissões e segurança | ⬜⬜⬜⬜ **0/4** | ○ Pendente |
| [M7](#m7--integração-compatibilidade-histórica-e-transição) | Integração, compatibilidade histórica e transição | ⬜⬜⬜⬜ **0/4** | ○ Pendente |
| [M8](#m8--ci-infraestrutura-e-preparação-operacional) | CI, infraestrutura e preparação operacional | ⬜⬜⬜⬜ **0/4** | ○ Pendente |
| [M9](#m9--validação-técnica-e-metodológica) | Validação técnica e metodológica | ⬜⬜⬜⬜ **0/4** | ○ Pendente |
| [M10](#m10--implantação-controlada-e-documentação-operacional) | Implantação controlada e documentação operacional | ⬜⬜⬜⬜⬜ **0/5** | ○ Pendente |

### Entregáveis aceitos

Clique no ID para conferir critérios, evidências e limites do aceite.

| Entregável | O que foi aceito | Natureza da evidência |
|---|---|---|
| ✅ [WEB-000](#web-000--base-documental-auditada-e-plano-executável) | Base documental auditada e plano executável | Documental |
| ✅ [WEB-001](#web-001--reproduzir-baseline-sintética-do-código-auditado) | Reproduzir baseline sintética do código auditado | Baseline funcional sintética |
| ✅ [WEB-002](#web-002--conferir-preservação-das-métricas-e-clis-na-baseline) | Conferir preservação das métricas e CLIs na baseline | Baseline funcional sintética |
| ✅ [WEB-003](#web-003--verificar-fronteiras-modulares-e-contratos-de-extensão) | Verificar fronteiras modulares e contratos de extensão | Baseline funcional sintética |
| ✅ [WEB-004](#web-004--ensaiar-desenvolvimento-local-e-retomada-do-marco) | Ensaiar desenvolvimento local e retomada do marco | Baseline funcional sintética |
| ✅ [WEB-005](#web-005--fechar-contratos-de-participante-preparação-e-política-de-perda) | Fechar contratos de participante, preparação e política de perda | Documental |
| ✅ [WEB-006](#web-006--revalidar-entrada-de-conclusão-e-proveniência-do-protocolo) | Receptor incremental, vínculos e proveniência | PostgreSQL real sintético e HTTPS focado |
| ✅ [WEB-007](#web-007--comprovar-atomicidade-replay-e-papéis-postgresql) | Atomicidade, replay e papéis | PostgreSQL real sintético |
| ✅ [WEB-008](#web-008--comprovar-paridade-oficial-de-métricas-e-ausência-de-medida) | Paridade das 12 métricas e ausência de medida | Domínio/API/CSV/PG/SQLite/UI e HTTPS focado |
| ✅ [WEB-009](#web-009--conferir-snapshot-condições-e-paleta-efetiva-da-web) | Condições, paleta efetiva e tempos do snapshot WEB | Fontes Builder/CSV/JSON, DOM e testes de motor |
| ✅ [WEB-010](#web-010--revalidar-plugins-jspsych-ciclo-de-vida-e-janela-de-resposta) | Plugins, ciclo de vida e regras de resposta/interrupção | jsPsych real, StrictMode, testes de teclado e navegadores visíveis; estabilidade de suporte ainda não aceita |

### Foco do marco atual

| ✅ Aceito | ✅ Aceito | ⬜ Bloqueado | ⬜ Sem aceite |
|---|---|---|---|
| [WEB-009](#web-009--conferir-snapshot-condições-e-paleta-efetiva-da-web): condições e paleta | [WEB-010](#web-010--revalidar-plugins-jspsych-ciclo-de-vida-e-janela-de-resposta): plugins e lifecycle | [WEB-011](#web-011--executar-campanha-de-engenharia-temporal-em-ambientes-declarados): campanha temporal | [WEB-012](#web-012--registrar-viabilidade-e-limites-de-suporte-do-motor): suporte |

| ⬜ Bloqueado | ⬜ Bloqueado | ⬜ Sem aceite |
|---|---|---|
| WEB-042: estímulos/centro | WEB-043: HUD sem precisão | WEB-044: regressão visual/funcional/temporal |

M2 permanece concluído em EV-M2 e EV-M2-007/008. M3 autorizado;
WEB-009/010 preservam aceite. CHG-003 adiciona WEB-042/043 (BLOQUEADAS pela
aprovação da apresentação frente a D3/D4) e WEB-044 (PENDENTE).
WEB-011 continua BLOQUEADA por DEC-04 e depende agora do layout final testado;
WEB-012 permanece PENDENTE. Nenhuma tarefa funcional pronta nesta conferência.

**Acompanhar impedimentos:** [riscos](#registro-de-riscos) ·
[decisões externas](#decisões-externas-e-condições-de-desbloqueio).
**Acompanhar a continuidade:** [Retomada](#retomada), com próxima ação, Git e limites.

Este painel integra o backlog canônico. Ao registrar um novo aceite, atualizar
os totais, barras e tabelas desta seção junto com as fichas e a Retomada;
validar que as contagens continuam correspondendo aos estados das tarefas.

## Ordem, caminho crítico e paralelismo

Prioridade inicial: WEB-001 → WEB-002/003 → WEB-004. Depois M2 e M3 podem seguir
em paralelo, e M8 pode preparar pilha isolada. M6 depende de M2 e antecede M4.
Caminho crítico de integração: M0 → M1 → M2 → M6 → M4 → M5 → M7 → M8(gate final)
→ M9 → M10 (WEB-041 → WEB-037/038/039/040). Ramo temporal M1 → M3 → M4/M9 é igualmente impeditivo; M3 deve ser
validado cedo. M8 inicia após M1, mas WEB-032 depende de M7. Em M9, WEB-033,
WEB-034 e WEB-035 são independentes após seus pré-requisitos e convergem em WEB-036.
Nenhum paralelismo autoriza editar o mesmo componente ou avançar marco sem escopo.
Os pré-requisitos de cada marco também se aplicam às suas tarefas, além dos
vínculos locais das fichas; dependências menores não autorizam antecipação fora
do marco. Paralelismo entre marcos requer autorização explícita do conjunto.
Complexidade relativa: P (local), M (vários componentes), G (integração/campanha
ou dependência externa); sem estimativa de horas e sem compromisso de prazo.

Ramo de CHG-003 em M3: WEB-009/010 → aprovação metodológica da apresentação
(D3/D4, visibilidade do HUD e versão) → WEB-042/043 → WEB-044 → WEB-011
(com transporte incremental ativo e DEC-04) → WEB-012 → M4/M9. WEB-042/043
podem ser executadas independentemente após aprovação, com integração sem edição
concorrente dos motores. A campanha nunca antecede o layout final aprovado.
Não antecipa M4/M5 nem cria marco de redesign.

## M0 — Auditoria e replanejamento documental

- Objetivo: estabelecer base verificável e governança para futura implementação.
- Justificativa: nova missão exige consolidar implementação já existente e eliminar estados concorrentes.
- Inclui: inventário, requisitos, arquitetura/ADR, tarefas, riscos, rastreabilidade, workflow e links.
- Exclui: qualquer código funcional, schema, infraestrutura operacional, dados reais e deploy.
- Pré-requisito: missão documental autorizada; dependências: nenhuma.
- Entregáveis/componentes: documentos desta missão; preservação dos planos históricos.
- Testes: links relativos, integridade de IDs/dependências/matriz, escopo Git e diff check.
- Riscos: R10; decisões externas: não impedem documento, devem estar explícitas.
- Aceite e encerramento: os 17 itens abaixo verificados, alterações somente documentais, commit/push conferidos sem PR/merge. Não encerra migração.

### WEB-000 — Base documental auditada e plano executável

- Marco: M0. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: nenhuma. Responsável: Codex, revisão técnica desta sessão.
- Critérios: (1) inventário por componente; (2) missão formal; (3) requisitos A–L;
  (4) arquitetura atual/alvo; (5) M0–M10; (6) IDs/dependências; (7) gates por marco;
  (8) riscos críticos; (9) decisões externas; (10) contagem de aceites; (11) matriz;
  (12) AGENTS/workflow; (13) arquivos históricos; (14) único backlog;
  (15) contradições materiais resolvidas; (16) WEB-001 identificada;
  (17) nenhuma implementação iniciada. Critérios editoriais verificados por inspeção
  e verificações locais descritas em EV-M0; entrega restrita a documentação.
- Evidências: EV-M0 nesta seção e fontes vinculadas; não há aceite funcional implícito.
- Riscos/bloqueios: decisões pendentes registradas; não bloqueiam documentação.
- Referências: REQ-AUD-003, ADR-004, auditoria e requisitos.
- Git: branch docs/replanejamento-stroop-web; commit e envio: ver Retomada.

### EV-M0 — evidência atual, 2026-11-04

Inspeção independente de método, runtime e infraestrutura integrada pelo agente
principal, com caminhos e limites registrados na auditoria. Revisão independente
corrigiu ciclo entre DEC-05/M9, acrescentou WEB-041 para configuração research e
separou preparo local de autorização de deploy. Fontes primárias jsPsych/FastAPI
consultadas e vinculadas no ADR-004.

Correspondência dos 17 critérios: 1→AUDITORIA_REPLANEJAMENTO; 2/4→ARQUITETURA_WEB e
ADR-004; 3/11→REQUISITOS_E_RASTREABILIDADE (36 requisitos A–L com origem/estado);
5/6/7/8/9/10/16→fichas M0–M10, WEB-000…041, riscos R01…10, DEC-01…05 e Retomada
neste backlog; 12→AGENTS/workflow/contribuição; 13→snapshots congelados de legado;
14→ROADMAP_WEB/PROGRESS e workflow antigo redirecionados; 15→revisão independente
mais validação de links/grafo; 17→checagem de escopo exclusivamente Markdown.

Verificações atuais de 2026-11-04: `python3 /tmp/validate_stroop_docs.py`, cujo
conteúdo reproduzível está no workflow, aprovou 83 documentos, 478 links relativos,
3 âncoras, 11 marcos, 42 IDs de tarefas únicos, 36 requisitos/linhas de matriz,
10 riscos e 5 decisões, sem ciclos técnicos. Escopo: 33 arquivos novos/alterados,
todos Markdown. `git diff --check` aprovado. Revisão de código fonte foi estática;
não são resultados das suites funcionais. O commit documental e652f2c1be664241364609443356b0277622c242 foi enviado
com upstream e confirmado por git ls-remote com a mesma SHA; worktree limpa
após o primeiro push. Este fechamento registra o aceite com evidência concreta. Suites funcionais, Docker, migrations, medição temporal, login
Google, produção e CI remota não executados para este marco documental.

## M1 — Fundação e baseline reproduzível

- Objetivo: Preservar a implementação existente e tornar a base verificável antes de alterar funções.
- Justificativa: Evita reconstrução e valida cedo paridade de métricas/segurança.
- Inclui: Checkout isolado, regressão sintética, fronteiras, locks e retomada.
- Exclui: Novas telas/rotas, upgrade incidental, alterações de produção.
- Pré-requisitos: M0 documental aceito e autorização futura de implementação.
- Dependências: M0.
- Entregáveis: Núcleo/CLI preservados, baseline por SHA e percurso local reproduzível.
- Componentes afetados: `stroop/, api/, web/, tests/, docs/`.
- Testes necessários: Regressão Python/PG sem skips, Vitest, tipos/build; scanner conforme baseline.
- Critérios de aceite: Baseline completa ou falhas classificadas/corrigidas no escopo; nenhuma quebra legada; comandos reproduzidos.
- Riscos: R04, R10.
- Decisões externas: Nenhuma para ensaio sintético local; recursos indisponíveis precisam ser registrados.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-001 — Reproduzir baseline sintética do código auditado

- Marco: M1. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-000.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Checkout isolado, comandos/versões/SHA e resultados Python/PG, frontend/tipos/build registrados; skips de PG não aceitam baseline.
- Testes/verificação: `unittest com PG descartável; npm test e npm run build`. Executados na descoberta integral; ver EV-M1.
- Evidências: EV-M1, 2026-11-04; baseline real e verificações de preservação/fronteiras na SHA a644e2c0c53bf6da27630c8179ee887c6436ff1e.
- Riscos/bloqueios: R04 preservado; nenhum impedimento observado na baseline sintética.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m1-baseline-sintetica`; versão funcional ensaiada e fechamento em EV-M1/Retomada.

### WEB-002 — Conferir preservação das métricas e CLIs na baseline

- Marco: M1. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-001.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Fixtures main, sem hits e roundtrip confirmam fórmulas/unidades e comandos/reexports preservados; divergências classificadas.
- Testes/verificação: `tests/test_nucleo_compartilhado.py, test_csv_unificado.py, test_importar_csv_sqlite.py`. Executados na descoberta integral; ver EV-M1.
- Evidências: EV-M1, 2026-11-04; baseline real e verificações de preservação/fronteiras na SHA a644e2c0c53bf6da27630c8179ee887c6436ff1e.
- Riscos/bloqueios: R04 preservado; nenhum impedimento observado na baseline sintética.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m1-baseline-sintetica`; versão funcional ensaiada e fechamento em EV-M1/Retomada.

### WEB-003 — Verificar fronteiras modulares e contratos de extensão

- Marco: M1. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-001.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Dependências atuais mapeadas e testes de fronteira aprovados; somente refatoração necessária registrada, sem instrumento novo.
- Testes/verificação: `tests/test_nucleo_compartilhado.py, test_casos_uso_importacao.py`. Executados na descoberta integral; ver EV-M1.
- Evidências: EV-M1, 2026-11-04; baseline real e verificações de preservação/fronteiras na SHA a644e2c0c53bf6da27630c8179ee887c6436ff1e.
- Riscos/bloqueios: R10 preservado; nenhuma refatoração necessária para esta entrega.
- Referências: REQ-EXT-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m1-baseline-sintetica`; versão funcional ensaiada e fechamento em EV-M1/Retomada.

### WEB-004 — Ensaiar desenvolvimento local e retomada do marco

- Marco: M1. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-002, WEB-003.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Segundo percurso documentado encontra estado/tarefa sem investigação global; local API/React/PG reproduzido; M1 atende sua ficha.
- Testes/verificação: `scripts/verify_web_ci.py browser` e `integration`; segundo percurso de retomada pelas fontes canônicas, conforme EV-M1.
- Evidências: EV-M1, 2026-11-04; React/API/PG e HTTPS reais, Chromium/Firefox, retomada localizada e critérios M1 conferidos.
- Riscos/bloqueios: R09 preservado; nenhum recurso externo necessário ao ensaio sintético local.
- Referências: REQ-EXT-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m1-baseline-sintetica`; versão funcional ensaiada e fechamento em EV-M1/Retomada.

### EV-M1 — baseline sintética, 2026-11-04

Autorização posterior à missão M0: comando `continue o projeto` do responsável.
Branch `test/m1-baseline-sintetica`, derivada de
`a644e2c0c53bf6da27630c8179ee887c6436ff1e` após fetch e confirmação de que main e
origin/main, assim como a branch documental e seu upstream, estavam alinhados.
Base documental preservada com implementação anterior ainda não integrada à main;
nenhum merge implícito. Worktree sparse `/tmp/stroop-m1-baseline-20261104`, sem
materializar data/, database/, production-secrets/ ou ambientes operacionais.

Ambiente observado: Linux 7.0.0-42-generic, Python 3.12.3, Node 24.15.0,
npm 11.16.0, Docker 29.9.2, PostgreSQL 17.6-bookworm na imagem fixada
`sha256:f3bd19c606e442c3d7bdfa8002e03fe260a1023351e0ea4598032022b68dd6e3`.
Container exclusivo `stroop-m1-baseline-20261104`, tmpfs, loopback 32769,
banco `stroop_etapa4_test_m1`, credencial sintética pública de CI. Dois locks
Python e package-lock existentes instalados sem atualização; `pip check` aprovado.

Comandos executados na raiz isolada com `.venv/bin/python scripts/verify_web_ci.py`
e `TEST_DATABASE_URL` apontando exclusivamente para esse banco:

- `sources`: 349 fontes aprovadas pelo Gitleaks 8.30.1; sem dados/histórico Git.
- `secret-self-test`: fonte inócua aceita e token falso bloqueado; sem expor valor.
- `python`: **369 testes aprovados em 97,742s, zero falhas/erros/skips**,
  PostgreSQL real, incluindo migrations e provisionamento restrito em bases sintéticas.
  A mensagem `Auditoria sintetica recusada` é uma prova negativa do runner,
  não execução da auditoria de dependências nem falha da regressão.
- `frontend`: `npm ci`, **273 testes em 16 arquivos**, typecheck e build aprovados.
- `browser`: **98 casos gerais (2,4 min) e quatro temporais seriais (3,6 min)
  aprovados**, Chromium 156.0.8078.4 e Firefox 157.0, em Linux.
- `integration`: **36 casos aprovados em 11,5 min** em Chromium/Firefox com build React,
  API FastAPI, PostgreSQL e HTTPS locais reais. Cookies restritos, convites,
  resultados, importação/exportação, revogação, perda de recibo e reenvio
  sem duplicação exercitados; processos/certificados efêmeros encerrados pelo harness.

WEB-002: descoberta integral exercitou `test_nucleo_compartilhado`,
`test_csv_unificado`, `test_importar_csv_sqlite`, `test_casos_uso_importacao`,
`test_web_results` e `test_web_export`. Cinco fixtures compartilhadas incluem
medianas par/ímpar, ausência de hits e RT positivo pequeno. Exportação → leitura
CSV → recálculo → SQLite preserva 21 colunas, 16 tentativas principais e 12
métricas. Sentinela legada 0.0 e ausência HTTP null continuam distintas;
conversão ms→s acontece uma vez. Reexports mantêm identidade de funções/exceções;
CLI por caminho/módulo, fora da raiz, duplicidade/force e launchers verificados
pela suite sintética. Nenhuma fórmula, CSV ou regra experimental alterada.

WEB-003: revisão AST dos imports em 31 módulos (8 domain, 3 ingestion,
11 application, 9 persistence) e testes de subprocesso aprovados. Domínio só
importa domínio/biblioteca padrão; ingestão depende do domínio; aplicação e
persistência não importam CLI/dashboard/framework HTTP. Persistência usa erros
de aplicação e ingestão existentes, sem nova abstração. Contratos
`NormalizedAssessment`, `InstrumentAdapter`, `test_code`/`test_version` preservados;
coexistência do demo sintético testada em `test_multiplos_instrumentos`.
Mapa e receita reproduzível: [baseline local](desenvolvimento/BASELINE_LOCAL.md).
Nenhuma necessidade de refatoração identificada nesta conferência.
O scanner foi repetido incluindo a receita adicionada: 350 fontes aprovadas.

WEB-004: segundo percurso em processo novo leu apenas AGENTS → workflow →
Retomada/ficha → receita local e localizou M1/WEB-004 sem repetir inventário.
O ensaio integrado acima reproduziu API/React/PG; todos os critérios das quatro
tarefas e da ficha M1 foram conferidos. M1 aceito em 2026-11-04; nenhuma quebra
legada observada nas suites executadas. Verificação documental: 83 Markdown
materializados, 485 links relativos e três âncoras sem erros; 11 marcos,
42 tarefas, 36 requisitos/linhas de matriz, 10 riscos e cinco decisões, grafo sem
ciclos. Validador do workflow adaptado ao checkout sparse: destinos excluídos
confirmados por metadados Git, sem abrir dados; staged incluído por diff HEAD.
Container descartável removido após o ensaio, sem tocar em serviços alheios.
`git diff --check` e verificação do diff staged aprovados. Os cinco arquivos
da entrega são Markdown; nenhuma alteração funcional/config/schema/lock.

Limites: evidência local da SHA funcional acima, sem mudança de runtime/locks/schema.
Auditorias públicas de dependências e Actions não executadas nesta baseline;
OIDC externo, latência física, equivalência psicométrica, homologação M9 e
produção não comprovados por estes ensaios. Riscos R01–R10 permanecem abertos.

## M2 — Backend e contratos de dados consolidados

- Objetivo: Fechar ambiguidades de produto/dados e revalidar API e persistência existentes.
- Justificativa: Integridade e cálculo oficial são base do fluxo de pesquisa.
- Inclui: Contratos atuais versus código, decisões DEC-01/02, transações, métricas e compatibilidade. CHG-002 acrescenta desenho de vínculos estáveis e persistência incremental, validado pelo responsável em 2026-11-05; ensaios de implementação ainda exigidos.
- Exclui: Novo cadastro global, offline ou schema por conveniência.
- Pré-requisitos: M1 aceito; decisões para o trabalho que depender delas.
- Dependências: M1.
- Entregáveis: Contrato fechado e testes reais de conclusão/replay, papéis e paridade de cálculos.
- Componentes afetados: `api/, stroop/domain/, application/, persistence/, scripts/migrations/`.
- Testes necessários: API negativa, PG real com papéis provisionados, rollback pré-commit, duplicação/concorrência, fixtures métricas.
- Critérios de aceite: Todos casos válidos/inválidos/concorrentes comprovados; ausência de RT e import/export sem divergência semântica.
- Riscos: R03, R04, R06.
- Decisões externas: DEC-01 e DEC-02; registrar alternativa aceita antes de ampliar entidade/captura.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-005 — Fechar contratos de participante, preparação e política de perda

- Marco: M2. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-004; DEC-01 e DEC-02.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Comparação contrato/código e modelo por projeto aprovados; estratégia definitiva de persistência e matriz de invalidação explicitamente validadas pelo responsável antes de código/schema. Contratos de vínculos, recibo, replay, incompletude e risco residual fechados. RAM final-only não é alternativa aceita após CHG-002.
- Testes/verificação: revisão estática contrato/código/schema lógico executada; achados em EV-M2-005. DEC-01 e DEC-02 respondidas; estratégia/matriz validadas expressamente na resposta “valido” do responsável em 2026-11-05. Suites funcionais não reexecutadas nesta revisão documental.
- Evidências: EV-M2-005, código inspecionado em `bcd896b`; resposta e revisão documental em EV-M2-005-R1 (2026-11-05). EV-M2-005-R2 registra validação definitiva pelo responsável. Aceite é documental; comparação e aprovação não constituem aceite funcional.
- Riscos/bloqueios: DEC-01/02 satisfeitas para o aceite documental com a resposta “valido” de 2026-11-05. R03/R07 continuam abertos e exigem ensaios e governança próprios; não impedem encerrar o contrato. WEB-006 está pronta para detalhamento técnico conforme dependências; nenhuma migration operacional, M3 ou produção autorizada por esta validação.
- Referências: REQ-PAR-002, REQ-AVA-002, REQ-INT-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `docs/m2-contratos-participacao`, baseada em `bcd896b` para preservar M1 ainda não integrado à main; fechamento em Retomada.

### EV-M2-005 — comparação preparada para decisão, 2026-11-05

Revisão estática na HEAD `bcd896b`,
sem executar banco, acessar dados reais ou alterar runtime/schema. Fontes:
[contrato HTTP](desenvolvimento/CONTRATO_API_WEB.md),
[modelo](dados/MODELO_DE_DADOS.md), [arquitetura](ARQUITETURA_WEB.md) e
[D2](experimento/PROTOCOLO_WEB.md). A revisão abaixo descreve implementação;
não substitui as decisões de produto/metodologia nem os ensaios WEB-006/007/008.

| Aspecto | Contrato e evidência no código | Consequência para decisão |
|---|---|---|
| Participante | `api/sessions.py::CreateInvitation` admite apenas participant_id/visit; RequestModel fecha campos. `stroop/application/web_sessions.py::_label` valida rótulos; migration 0005 vincula convite a projeto/emissor. | Alternativa DEC-01: manter pseudônimo/visita por projeto, sem pessoa global, demografia ou cadastro longitudinal. |
| Preparação | `stroop/persistence/web_sessions.py::create_invitation` grava convite e reserva session_id; `redeem` cria a sessão preparing e ordem. Migration 0005 confirma vínculo, expiração e uso único. | Avaliação planejada é representada pelo convite; não há agenda autônoma. Nova emissão gera outro convite/sessão, sem reabrir a execução anterior. |
| Resultado | `complete_participant_session` cria assessment_id e grava avaliação/tentativas/métricas/proveniência/recibo na transação. Migration 0006 liga resultado à sessão de forma única. | Avaliação oficial só existe após conclusão integral válida; não criar linha oficial para preparação, aborto ou expiração. Atomicidade real permanece a comprovar em WEB-007. |
| Perda e interrupção | `web/src/participant/ParticipantRun.ts` conserva payload em memória, aborta running carregada com reload, descarta payload ao encerrar/expirar e só confirma após recibo/consulta. | Alternativa DEC-02: manter RAM final-only e D2, aceitando perda antes do envio, sem checkpoint/offline/retomada. |
| Falha após envio | O contrato prevê consulta/reenvio idêntico enquanto credencial válida; ParticipantRun.send consulta recibo após falha incerta e conserva o corpo para retry. | Falta de resposta não prova ausência de commit. Após expiração, resultado eventualmente salvo só é consultável pelo profissional autorizado. |
| Informação ao participante | `web/src/components/ResultSummary.tsx` distingue enviando/pendente/recebido e avisa que sair sem confirmação não conserva o resultado. | Informação antes da execução e cenários de interrupção devem ser conferidos na tarefa de fluxo WEB-015 após a decisão; não presumir que o aviso tardio cobre toda perda pré-envio. |

DEC-01/02 foram apresentadas ao responsável com alternativas explícitas de
preservar o modelo atual ou descrever ampliação. Nenhuma resposta foi inferida
do comando genérico de continuidade. Se houver ampliação, registrar requisitos,
contratos, testes e autorização de schema/método antes de implementação dependente.
A contagem de aceites permanece inalterada; não há tarefa independente pronta
em M2 enquanto WEB-005 aguarda as duas decisões.

### EV-M2-005-R1 — resposta e proposta documental, 2026-11-05

Responsável aprovou DEC-01 e rejeitou final-only em DEC-02 na mensagem desta
sessão. Exigiu preservação incremental, recibo/idempotência, sessões incompletas/
inválidas, nova sessão com prática após interrupção e validação antes de código.
Não é aprovação presumida da estratégia que foi elaborada depois da resposta.

Entregues: [ADR-005](arquitetura/ADR-005-persistencia-incremental.md), desenho
lógico no [modelo](dados/MODELO_DE_DADOS.md), transporte candidato no
[contrato HTTP](desenvolvimento/CONTRATO_API_WEB.md), matriz de invalidação no
[protocolo](experimento/PROTOCOLO_WEB.md); requisitos e arquitetura alinhados.
Revisão técnica documental: múltiplas visitas/avaliações, isolamento composto,
evolução aditiva, fila/ACK, prefixo/hash, replay divergente, corridas, expiração
sem aviso e perda residual conferidos. Worker não promete impacto temporal zero;
sem rede a perda pode abranger todo sufixo não confirmado, inclusive o bloco todo.
Nenhuma execução de worker, banco, navegador ou integração nessa revisão.

Validação local: procedimento Python do workflow (links/âncoras, 42 tarefas,
36 requisitos/matriz, 11 marcos, 10 riscos, 5 decisões, grafo e escopo Markdown)
e `git diff --check`; resultados numéricos e Git no fechamento em Retomada.
Conteúdo funcional de referência: `bc2f4b3` (somente documentação desde M1).
Não altera contagem de aceites nem encerra WEB-005/M2.

### EV-M2-005-R2 — validação explícita e aceite documental, 2026-11-05

Após a apresentação do ADR-005, contrato alvo e matriz D2/D5 versionados em
`270377b89ea477bf864114d0e8a3017e3520a84f`, o responsável respondeu **“valido”**.
Aprova a estratégia definitiva, a janela residual de perda explicitada e os
critérios metodológicos, satisfazendo a validação prévia exigida na sua mensagem.
Aprovação não implica ensaios implementados, schema operacional ou produção.

Critérios WEB-005 conferidos: comparação atual/alvo em EV-M2-005; participante
por projeto e vínculos estáveis no modelo, aprovados por DEC-01; persistência por
worker com prefixo/ACK, idempotência, corridas/invalidação e incompletude no
ADR-005/contrato; matriz metodológica e nova sessão com prática no protocolo;
limitações e perda residual explicitadas e validadas por DEC-02. Nenhum critério
funcional transferido a esta entrega documental. WEB-005 CONCLUIDA;
WEB-006 PRONTA, WEB-007/008 PENDENTES; M2 permanece não concluído.

Validação documental atual: procedimento Python do workflow e `git diff --check`;
resultados e Git na Retomada. Não reexecutadas suites de código, PG ou browser.
Históricos EV-M2-005/R1 preservam o contexto anterior à validação, agora superado.

### WEB-006 — Revalidar entrada de conclusão e proveniência do protocolo

- Marco: M2. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-005.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Após validação DEC-02, schema fechado e vínculos participante/visita/projeto; ordem/snapshot, unidades e versões; contratos de checkpoint/start/abort/complete e invalidação tardia coincidem com código. Especificar migration aditiva e mapear sessões existentes sem inferir associação de legado. Validar partial versus oficial conforme ADR-005; não iniciar implementação antes do gate WEB-005.
- Testes/verificação: `tests/test_web_results.py`, `tests/test_web_sessions.py`, `tests/test_web_checkpoints.py`, migrations/provisionamento, regressão Python, Vitest/tipos/build e ensaio HTTPS focado no receptor; resultados em EV-M2.
- Evidências: EV-M2; critérios de entrada, vínculos, proveniência e ciclo incremental conferidos em código/PG real e HTTPS. Sem aceite antecipado de M2 ou de captura incremental no motor.
- Riscos/bloqueios: nenhum bloqueio desta unidade. R02/R03 continuam abertos; recepção no servidor não prova worker, ausência de perda ou validade física/metodológica. WEB-007/008 mantêm seus gates próprios.
- Referências: REQ-INT-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: `feat/m2-persistencia-incremental`, base `72cca1f`; fechamento local em EV-M2 e Retomada, sem push conforme instrução final do responsável.

### EV-M2 — receptor incremental e banco sintético, 2026-11-05

Unidade concluída de WEB-006. A instrução final do responsável limita esta
sessão ao fechamento seguro e commit local; WEB-007/008 não recebem aceite
por antecipação. Critérios conferidos: schema fechado e vínculos compostos,
ordem/snapshot, unidades/versões, start/abort/checkpoint/complete, invalidação
tardia e preservação de parciais separados do resultado oficial. Migration
aditiva mapeia só convites WEB; nenhuma associação de legado inferida.

Entregas: migration aditiva 0011 com UUIDs por projeto/participante/visita,
backfill exclusivamente de convites WEB, FKs compostas e tabelas separadas de
observações/recibos/invalidação; receptor de checkpoints, consulta de recibo e
estado profissional, reconciliação de complete e invalidação auditável. Observações
confirmadas sobrevivem a rollback final; inválidos ficam fora de listas, facetas,
agregados e CSV oficiais. Clientes existentes validam os campos novos e impedem
usar resumo invalidado. Não há worker, fila ou transporte incremental no motor:
esses componentes e seus gates temporais continuam em M3/M4.

Revisão corrigiu o limite de expiração durante as escritas da conclusão: desfazer
sufixo/resultado se o prazo vencer antes do commit, conservando ACK anterior e
sem liberar/readquirir lock para materializar expiração. Writer só atualiza
campos de avanço do recibo, sem mudar proveniência ou observações. Fórmulas,
unidades, CSV, versões experimentais, OIDC e limites de acesso preservados.

Git inicial: branch adequada já existente com alterações locais de WEB-006,
preservadas e integradas nesta unidade, sem descarte. Base `72cca1f`; fetch
executado. `origin/main=db56b40`, `main=fe8f24f`; preservada a base documental/M1
não integrada, sem rebase/merge nem tentativa de sincronização não fast-forward.
Os testes usam container exclusivo `stroop-m2-validation-20261105`, PostgreSQL
17.6, tmpfs, porta loopback 32769 e banco `stroop_etapa4_test_m2_validation`.
Não foram abertos `.env` operacional, coletas ou backups.

Verificações locais desta unidade (Python 3.12.3, Node 24.15.0/npm 11.16.0,
Linux 7.0.0-42-generic; Playwright 1.64.1, Chromium 156.0.8078.4/Firefox 157.0):

- `.venv/bin/python scripts/verify_web_ci.py python`, com TEST_DATABASE_URL
  apontando somente ao banco sintético acima: **387 testes aprovados, zero skips**
  (111,582 s). Inclui limites de entrada/proveniência, replay, conflitos,
  rollback, corridas, vínculos, métricas/CSV e negações de acesso.
- `npm test` em web: **275 testes em 16 arquivos aprovados**;
  `npm run build` (inclui typecheck): aprovado. Dependências existentes
  reutilizadas, sem instalação/atualização incidental; `pip check` aprovado.
- `.venv/bin/python scripts/verify_web_ci.py browser`: **98 testes gerais +
  quatro timing aprovados**, Chromium/Firefox. É regressão do motor atual,
  sem transporte incremental ativo; não concede aceite M3, latência física ou
  equivalência psicométrica.
- Após a última correção de grants, `.venv/bin/python -m unittest
  tests.test_web_database_provision -v`: **9 aprovados**; inclui invalidação
  tardia pelo writer restrito e recusa de SELECT em reaction_time_ms.
- Em web, `npx playwright test --config playwright.integration.config.ts
  --grep 'receptor incremental HTTPS'`, no mesmo banco sintético após o fim da
  suíte Python: **2 aprovados (9,3 s)**. API real, proxy HTTPS local e papéis
  provisionados, sem mocks HTTP; confirmou ACK/replay, consulta do prefixo,
  conclusão, invalidação tardia, detalhe sem resumo e exportação negada. Suite
  HTTPS integral não reexecutada neste fechamento da menor unidade.
- Scanner `scripts/verify_web_ci.py sources`: aprovado, 354 fontes no inventário
  após staging dos arquivos novos. Links/estrutura e `git diff --check`
  aprovados no fechamento; resultados documentais finais registrados em Retomada.

Falhas intermediárias preservadas como evidência: o teste novo de prazo usava
clock_timestamp duas vezes e violava por microssegundos o limite de 30 min da
própria fixture; corrigido para statement_timestamp, confirmado no conjunto de
387 testes. O primeiro HTTPS focado falhou nos dois browsers com 503 na
invalidação: faltava SELECT de assessment_id/trial_number/trial_end_ms ao writer.
Grant limitado às três colunas, teste negativo de RT e repetição 9+2 aprovados.
O conjunto de 387 antecede exclusivamente essa correção final de grant/teste;
a revalidação final correspondente são os 9 testes de provisionamento e 2 HTTPS.

Limites e continuidade: WEB-007 deve conferir formalmente toda a matriz de
atomicidade/replay/papéis e completar qualquer lacuna; WEB-008 revalida a paridade
como aceite próprio. Nenhum aceite de M2, worker/fila, M3/M4, pesquisa real ou
produção. R03 permanece aberto, incluindo perda do sufixo sem ACK. Somente o
container criado nesta sessão foi removido ao encerrar, sem tocar recursos preexistentes.

Git: commit local identificável por `git log -1 --format=%H
--grep='feat(web): implementa receptor incremental e vínculos de sessões'`,
na branch `feat/m2-persistencia-incremental`. Sem push por instrução final do
responsável; sem upstream desta branch. `gh run list --branch
feat/m2-persistencia-incremental` não retornou execução; Actions não executada
para esta entrega local. Sem PR, merge, deploy ou migration em dados reais.

### WEB-007 — Comprovar atomicidade, replay e papéis PostgreSQL

- Marco: M2. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-006.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Banco real provisionado prova rollback pré-commit, checkpoint com ACK pós-commit, retry igual/sobreposto, conflito divergente, prefixo sem lacuna e concorrência checkpoint/abort/complete; expiração/invalidação preservam observações, resultado oficial é atômico e não duplica. Vínculos compostos e múltiplas avaliações por visita comprovados; reader sem DML e writer sem owner. Ensaios de CHG-002/ADR-005 são adicionais, não cobertos por teste histórico.
- Testes/verificação: `tests/test_web_checkpoints.py, tests/test_web_sessions.py, tests/test_web_database_provision.py, tests/test_postgres_migrations.py`; execução e matriz em EV-M2-007/008.
- Evidências: aceite próprio de WEB-007 em EV-M2-007/008; 59 testes focados aprovados e 11 de confirmação das asserções finais, sem skips. Matriz e limites registrados abaixo.
- Riscos/bloqueios: R03, R06; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-INT-002, REQ-INF-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: `feat/m2-persistencia-incremental`, testes em `c7ae0a4`, push confirmado; CI não executada. Fechamento documental identificável em EV-M2-007/008.

### WEB-008 — Comprovar paridade oficial de métricas e ausência de medida

- Marco: M2. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-007.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: 12 métricas/unidades/classificações e no-hit conferidos nos adaptadores; nenhuma normalização destrutiva do histórico; M2 aceito. CHG-002: preservar fórmulas e comprovar exclusão de incompletos/ inválidos do resultado oficial.
- Testes/verificação: `tests/test_nucleo_compartilhado.py, tests/test_web_results.py, tests/test_web_export.py, tests/test_web_checkpoints.py, tests/test_web_assessments.py, web/src/dashboard/analysis.test.ts`; resultados em EV-M2-007/008.
- Evidências: aceite próprio em EV-M2-007/008: 12 métricas e unidades, no-hit, CSV/importação e exclusão de incompletos/ inválidos comprovados. M2 concluído; M3 não iniciado.
- Riscos/bloqueios: R04; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-MET-001, REQ-MET-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: `feat/m2-persistencia-incremental`, testes em `c7ae0a4`, push confirmado; CI não executada. Fechamento documental identificável em EV-M2-007/008.

### EV-M2-007/008 — atomicidade e paridade, 2026-11-05

Autorização desta sessão: novo `continue o projeto`, tarefas restantes de M2.
Base `76f71f8dd37018eca40cf4f4d948a77a9a3ea6d9`, worktree inicial limpa;
branch adequada `feat/m2-persistencia-incremental` preservada. Fetch confirmou
`origin/main=db56b40` e `main=fe8f24f`; mantida a base documental/M1/M2 ainda
não integrada, sem merge/rebase. O limite de commit local de EV-M2 era daquela
sessão; este comando retoma o fluxo vigente de commit/push em branch.

Conferência dos critérios de WEB-007 e linhas aplicáveis do ADR-005:

| Critério / cenário | Evidência real nesta sessão |
|---|---|
| ACK após commit e resposta perdida | Novo `test_ack_waits_for_commit_and_is_visible_to_independent_connection`: constraint trigger adiado bloqueia o commit; requisição pendente e nenhuma observação/recibo visível por conexão independente; desbloqueio confirma hash/prefixo e replay. `test_ack_prefix_hash_overlap_replay_and_lost_response` comprova consulta do recibo sem reenvio de dados brutos. |
| Rollback / perda do sufixo | `test_rollback_before_ack_and_final_rollback_preserve_only_confirmed_prefix` força erro real de PG, sem observações antes do ACK; falha final conserva apenas prefixo confirmado e retry conclui uma vez. Não simula desligamento físico do servidor. |
| Replay / lacuna / divergência / concorrência | Testes de checkpoint e complete com conexões concorrentes; novas asserções conferem prefixo sem duplicação e cardinalidade oficial por sessão. Divergência não sobrescreve; abort/complete e invalidate/complete mantêm resultados atômicos e validade coerente. |
| Expiração / incompletude / invalidação | Casos 0/5/16, prazo durante escritas, revogação, aborto, aviso tardio e expiração sem aviso conservam prefixo; nenhum resultado parcial promovido. Inválidos não aparecem na lista/facetas/CSV e detalhe não fornece resumo oficial. |
| Participante / visita / convite | Provisionamento real comprova concorrência sem duplicar vínculo, duas visitas, duas avaliações na mesma visita e pseudônimo em dois projetos; FK composta rejeita cruzamento. Suite de sessões cobre uso único, resgate concorrente, revogação, expiração, vínculo, CSRF e estados. |
| Papéis | Fluxo checkpoint/complete/invalidate pelo writer provisionado e consulta pelo reader; negações DML/DDL e de colunas. Novas asserções conferem reader sem privilégios de DML nas tabelas públicas e writer sem ownership, superuser, createdb, createrole, bypassrls ou membership. |
| Fronteiras futuras | Protocolo no navegador, prática/nova sessão, worker/fila, impacto temporal/carga e armazenamento JS exigem M3/M4; a matriz ADR-005 não recebe aceite global por testes do servidor. Segurança externa e operação mantêm gates próprios. |

WEB-008: referência numérica independente cobre os 12 códigos/unidades,
quatro classificações, denominadores e mediana fracionária. Fixtures compartilhadas
atravessam domínio → CSV canônico → importação SQLite, conferindo agora valores
e unidades das 12 métricas persistidas, inclusive percentual de omissões.
Teste PG compara métricas/unidades antes/depois dos checkpoints; testes de
consulta recalculam fontes e mantêm 0.0 legado versus null HTTP quando sem hits.
Vitest confere traço, arredondamento Python e agregação sem converter ausência
em zero. Fórmulas, CSV e histórico não foram alterados. Incompletos/ inválidos
continuam fora do resultado oficial, conforme os testes acima.

Ambiente: Python 3.12.3, Node 24.15.0, PostgreSQL 17.6 em tmpfs;
container exclusivo `stroop-m2-acceptance-20261105`, porta loopback 32770,
banco `stroop_etapa4_test_m2_acceptance` e bancos de papéis descartáveis com
mesmo prefixo. Reutilizadas dependências existentes; nenhum `.env`, coleta,
backup ou banco operacional aberto. Somente testes e documentação alterados.

Verificações atuais, todas locais e aprovadas:

- Foco WEB-007: `TEST_DATABASE_URL=<banco sintético acima> .venv/bin/python
  -m unittest tests.test_web_checkpoints tests.test_web_database_provision
  tests.test_postgres_migrations tests.test_web_sessions -v`: **59 testes**,
  67,020 s, zero skips. Após reforçar o trigger adiado e as asserções finais,
  os dois testes de ACK/concorrência mais `tests.test_web_database_provision`:
  **11 aprovados**, 5,219 s, zero skips.
- `TEST_DATABASE_URL=<mesmo banco> .venv/bin/python scripts/verify_web_ci.py
  python`: **388 testes**, 109,479 s, zero skips; inclui as asserções finais
  de WEB-007 e WEB-008. Confirmação final de `tests.test_web_export`: **6 testes**
  aprovados, 0,184 s. `pip check` aprovado. A mensagem de auditoria sintética
  recusada é o caso negativo controlado do runner; a suite terminou OK.
- Em web, `npm test`: **275 testes / 16 arquivos**; `npm run build`, que inclui
  typecheck: aprovado. Nenhuma instalação/atualização de dependências.
- Depois da suite Python, `TEST_DATABASE_URL=<mesmo banco> npx playwright test
  --config playwright.integration.config.ts --grep 'receptor incremental HTTPS|resultados completos reais|CSV real corresponde'`
  em web: **6 testes aprovados**, 28,4 s, Chromium 156.0.8078.4 / Firefox 157.0,
  Playwright 1.64.1, Linux 7.0.0-42-generic. API real/HTTPS local/PG com writer e
  reader provisionados, sem mocks HTTP; prefixo/recibo, invalidação tardia,
  resultados/unidades/visitas/projetos, CSV/paginação/filtros e revogação.
- `scripts/verify_web_ci.py sources`: **354 fontes**, aprovado; `git diff
  --check` e procedimento documental do workflow aprovados (exceto restrição
  exclusivamente Markdown de M0). Contagens finais em Retomada.

Não houve falha funcional observada nesta sessão. Suite HTTPS integral e
campanha temporal não foram reexecutadas; os seis casos acima são focados em M2.
WEB-005/006 mantêm seu aceite e evidências próprias; WEB-007/008 têm todos os
critérios comprovados nesta revisão. **M2 concluído**, sem aceite de M3/M4,
latência física, equivalência psicométrica ou autorização de uso real.
R01/R02/R03/R04/R06 continuam abertos nos gates posteriores e limites residuais.

Git: testes em `c7ae0a4b5259b9e731d27c03e19ee3ade5eb0af2`, enviado com upstream
para `origin/feat/m2-persistencia-incremental` e confirmado por `git ls-remote`
na mesma SHA. Inclui a entrega anterior `76f71f8`, antes apenas local.
Consulta `gh run list --branch feat/m2-persistencia-incremental` após push:
nenhuma execução; CI remota não executada, não equivalente à validação local.
Fechamento documental identificável por `git log -1 --format=%H
--grep='docs: registra aceite de M2 e continuidade para M3'`; envio verificável
pela igualdade de HEAD, upstream e referência remota da mesma branch. Nenhum
PR/merge/deploy ou operação sobre dados reais. Container criado para esta
sessão removido ao fechar; recursos preexistentes preservados.

## M3 — Viabilidade e motor experimental no navegador

- Objetivo: Revalidar jsPsych/plugins e temporização antes de consolidar operação.
- Justificativa: Maior risco científico/técnico não pode ficar para depois da UI.
- Inclui: Pool/paleta/snapshot, ciclo do Host, janela/teclado, interrupção, apresentação CHG-003 (WEB-042/043/044) e campanha de engenharia no layout final.
- Exclui: Equivalência psicométrica, suporte móvel, troca de paradigma ou limiares.
- Pré-requisitos: M1 aceito; matriz de ensaio identificada; DEC-04 para aceite de suporte.
- Dependências: M1.
- Entregáveis: Relatório reproduzível com falhas preservadas e matriz técnica explicitada.
- Componentes afetados: `condicoes/, web/src/experiment/, web/pilots/, stroop/domain/web_results.py`.
- Testes necessários: Estáticos, motores unitários, navegadores visíveis; 10 execuções sintéticas por ambiente declarado com gate D5.
- Critérios de aceite: Condições/regras preservadas, apresentação aprovada sem precisão agregada (feedback individual da prática mantido), contorno sem caixa, HUD testado e gates D5 no layout final com transporte ativo; limites e ambientes não medidos explícitos.
- Riscos: R01, R02.
- Decisões externas: DEC-04 define ambientes/equipamento e tratamento de falhas sem presumir equivalência.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-009 — Conferir snapshot, condições e paleta efetiva da Web

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-004.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Pools, versões, cores renderizadas versus CSV histórico, prática/main e tempos coincidem com fontes aprovadas sem alterar protocolo.
- Testes/verificação: `tests/test_fase3_condicoes_tempos.py`, `web/src/experiment/environment.test.ts`, `practice.test.ts`, `main.test.ts`; 34 testes Python focados, 278 Vitest e tipos/build aprovados. Comandos e limites em EV-M3-009/010.
- Evidências: EV-M3-009/010, 2026-11-05; condições, paleta e tempos revalidados sem mudança de protocolo. Aceite restrito à WEB-009; nenhuma campanha temporal ou suporte aprovado por antecipação.
- Riscos/bloqueios: nenhum impedimento desta tarefa. R02 preservado: paridade de fontes não comprova equivalência física/psicométrica.
- Referências: REQ-EXP-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `feat/m3-motor-experimental`, base `832abfd`; SHA/commit/push/CI no fechamento EV-M3-009/010 e Retomada.

### WEB-010 — Revalidar plugins jsPsych, ciclo de vida e janela de resposta

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-009.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Comparativo ADR-004 confrontado com motor; setup/cleanup e primeira nova pressão/fim exclusivo/interrupções passam; React não dirige quadro.
- Testes/verificação: `web/src/experiment/main.test.ts`, `practice.test.ts`, `ExperimentHost.test.tsx`, `web/e2e/main.spec.ts`, `practice.spec.ts`; critérios funcionais comprovados em lógica/lifecycle e navegador, com captura Firefox visível completa validada no domínio. Falhas E2E e limites preservados em EV-M3-009/010.
- Evidências: EV-M3-009/010; ADR-004 confrontado, setup/cleanup StrictMode e fronteiras de resposta/interrupção comprovados; execução visível completa em ambos navegadores, Firefox com 64 transições e validação Python oficial. Aceite funcional desta tarefa não concede estabilidade/suporte da campanha WEB-011/012.
- Riscos/bloqueios: R01/R02 abertos. Invalidação temporal Firefox na rodada E2E permanece sem causa determinada; captura posterior válida não a apaga. Campanha WEB-011 deve preservar e investigar falhas/transporte ativo na matriz DEC-04. Não inferir suporte estável nem alterar runtime/tolerâncias sem evidência de causa.
- Referências: REQ-EXP-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `feat/m3-motor-experimental`, base `832abfd`; testes e evidência funcional versionados conforme EV-M3-009/010 e Retomada, aceite restrito aos critérios funcionais desta tarefa.

### WEB-011 — Executar campanha de engenharia temporal em ambientes declarados

- Marco: M3. Prioridade: P0. Complexidade: G. Estado: BLOQUEADA.
- Dependências: WEB-010, WEB-044; DEC-04 para matriz.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: 10 execuções sintéticas por ambiente selecionado, trilhas brutas/falhas preservadas, quadro e desvio total conferidos contra D5; sem substituir falha por rerun omitido. CHG-002: incluir transporte incremental ativo, ACK lento/perdido, retries e falha de servidor, sem alongar tentativas; comparar impacto contra D5. CHG-003: campanha na SHA do layout final aprovado, com contorno branco uniforme, sem retângulo/precisão agregada, progresso/cronômetro revisados e transporte incremental ativo. Registrar custo observado de renderização/HUD/retries; campanha somente no visual anterior não basta. Limites D5 e tolerâncias intactos.
- Testes/verificação: `PLANEJADO: campanha técnica D5; web/pilots/w16-local.spec.ts como ferramenta, não prova física`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: trilhas antes/depois identificadas por versão/SHA e falhas preservadas; comparar tempos e condições aprovadas DEC-04.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R01. Bloqueio observado: matriz/equipamento DEC-04 ainda não aprovados; pergunta ao responsável enviada nesta sessão sem resposta até o fechamento. Responsável metodológico deve declarar ambientes/versões/recursos e alcance da campanha; Codex então prepara transporte ativo e executa os ensaios autorizados. WEB-012 depende desta entrega.
- Referências: REQ-EXP-003; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-001 a REQ-UX-007; R11.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-012 — Registrar viabilidade e limites de suporte do motor

- Marco: M3. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-011.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Relatório técnico discrimina automação/latência física e ambientes não medidos; responsável aceita suporte ou bloqueia motor; M3 atendido sem equivalência presumida. CHG-002: discriminar impacto medido do transporte e janela de perda observada, sem promessa de perda zero. CHG-003: aceite explicita apresentação visual e HUD suportados, versão e limitações da campanha final; nenhum suporte herdado de screenshots antigos.
- Testes/verificação: `PLANEJADO: revisão de evidências M3 e DEC-04`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: revisão do protocolo visual e matriz DEC-04.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R01, R02; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md). CHG-003; R11.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### EV-M3-009/010 — fontes, plugins e diagnóstico, 2026-11-05

Autorização: novo `continue o projeto`, limitado a M3. Base `832abfd`, branch
`feat/m3-motor-experimental`, criada após fetch com worktree limpa. M2 preservado;
main local `fe8f24f` e origin/main `db56b40` não foram integradas à branch.
Testes versionados em `7cad3476e2142c98b863dd28c043c4b2e44d083a`
e enviados com upstream, confirmado por igualdade HEAD/upstream/ls-remote.
CI consultada após envio: nenhuma execução na branch, sem aprovação Actions.
Fechamento documental identificável por `git log -1 --format=%H --
 'docs/Projeto Stroop Test.md'`; não há autorreferência artificial de SHA.

WEB-009: CSVs-fonte com 4 condições de prática (2/2) e 16 principais (8/8),
dez cores, palavras e respostas conferidos. Testes novos comparam snapshot WEB
com a paleta efetiva e os tempos extraídos do XML Builder, incluindo feedback
separado; hexadecimais históricos do CSV não são usados para renderizar.
Motor principal renderiza as 16 palavras/condições e dez cores sobre cartão
claro. Versão WEB `0.2.2-web.1` e snapshot único preservados; testes do validador
conferem identificação/ordem/unidades. WEB-009 atende seus critérios de fontes;
nenhum aceite de latência física decorre dessa paridade.

WEB-010: comparação ADR-004 conferida com `main.ts`, `practice.ts` e motores.
Plugins jsPsych reais controlam DOM/teclado/rAF, Host React apenas monta/limpa;
plugins padrão exigiriam nova prova da janela fixa, HUD e tecla mantida, e React
por quadro permanece incompatível com a fronteira escolhida. Testes existentes
cobrem primeira pressão, RT positivo/fim exclusivo, entrega tardia, repeat,
tecla mantida, foco/aba/Escape e cleanup. Testes novos montam os plugins reais
sob StrictMode, comprovam única instância ativa após remontagem, cancelamento
de timers e ausência de callbacks após desmontagem. Relógio controlado/jsdom
não substitui navegador real. Critérios funcionais complementados pela captura
visível abaixo; a estabilidade do ambiente pertence à campanha WEB-011/012,
ainda sem aceite. As falhas anteriores permanecem explícitas.

Verificações locais desta sessão (sem dados reais):

- `.venv/bin/python -m unittest tests.test_fase3_condicoes_tempos tests.test_web_results -v`:
  **34 aprovados, zero falhas/erros/skips**, 0,023 s.
- Em `web/`, `npm ci && npm test && npm run build`: lock preservado,
  **278 testes/16 arquivos aprovados**, 1,69 s; TypeScript e Vite aprovados.
- `WEB_TEST_PORT=4273 npx playwright test e2e/practice.spec.ts e2e/main.spec.ts --workers=1 --trace=off --headed`:
  **7 aprovados, 5 falhas**, 3,1 min; zero retries. Chromium falhou no principal
  por interrupção sem causa determinada, na espera de prática (22 s) e na
  navegação inicial por teclado; Firefox falhou na espera de prática (22 s)
  e na espera do estímulo principal (8 s). Ambos passaram feedback dos quatro
  desfechos, tecla mantida/interrupção/reinício da prática e bloqueio de celular;
  Firefox também passou navegação por teclado. Nenhum timeout/gate foi relaxado.
  Artefatos exclusivamente sintéticos em `web/test-results/`, ignorados pelo Git;
  não versionar contextos, screenshots ou logs. Falhas não são apagadas por rerun.

- Comparação sem janela visível: mesmo comando sem `--headed`, com
  `--output=test-results/m3-headless`: **11 aprovados, 1 falha**, 4,5 min,
  zero retries. Principal completo de 60 s e Escape aprovados em Chromium e
  Firefox; falha restante na navegação inicial Chromium. Esta comparação não
  substitui nem apaga os resultados visíveis.
- Diagnóstico do teste de navegação: `page.goto` aguardava load mas não a
  montagem React. A instalação dos listeners precede o effect de foco inicial
  em `App.tsx`. Acrescentada espera observável por `main` focado antes de
  Espaço/Enter; não há sleep fixo, mudança de runtime ou relaxamento de D2/D5.

- Probe diagnóstico visível separado em Chromium, com o mesmo helper sintético,
  eventos focus/blur/visibility e fases amostradas em RAM: prática concluída,
  primeiros dois trials principais observados, sem alertas ou eventos de perda
  de foco; encerrado deliberadamente pelo harness antes de concluir o bloco.
  Primeiros 600 intervalos rAF: mediana 16,7 ms, máximo 50 ms. Isso evidencia
  variação no ambiente, mas não estabelece a causa das cinco falhas anteriores.
  Script/JSON temporários em `/tmp/stroop-m3-headed-probe.{mjs,json}`, sem
  credenciais/identificadores; não é réplica válida nem gate D5 ou prova física.

- Após corrigir a sincronização, navegação isolada sem janela:
  `WEB_TEST_PORT=4273 npx playwright test e2e/practice.spec.ts --grep 'navegacao por teclado' --workers=1 --trace=off --output=test-results/m3-navigation-headless`:
  **2 aprovados**, 4,2 s, Chromium/Firefox.
- Revalidação visível dos casos anteriormente falhos:
  `WEB_TEST_PORT=4273 npx playwright test e2e/main.spec.ts e2e/practice.spec.ts --grep 'principal|navegacao por teclado' --workers=1 --trace=off --headed --output=test-results/m3-headed-recheck`:
  **5 aprovados, 1 falha**, 2,9 min, zero retries. Chromium aprovou principal
  completo, Escape e navegação; Firefox aprovou Escape e navegação, mas o
  principal foi invalidado pelo gate temporal D5 em 40,8 s de teste, exibindo
  pedido de novo convite/prática. O ambiente Firefox visível não demonstrou
  execução completa estável; causa de atraso não determinada. Não remover
  Firefox do suporte aprovado por inferência nem enfraquecer gate/timeout.
  Diagnóstico local por captura das transições segue autorizado em WEB-010;
  DEC-04 condiciona campanha/suporte. Esta rodada não concede aceite de M3.

- Captura funcional diagnóstica Firefox visível com ferramenta W16 existente,
  flag `VITE_W16_TIMING_CAPTURE=synthetic-only` e `/pratica?w16=1`, script
  temporário `/tmp/stroop-m3-firefox-probe.mjs`: prática e principal completos,
  **16 tentativas, 64 transições, outcome completed, sem perda de foco/aba**.
  Quadro medido 16,69000000000051 ms, desvio nominal máximo 3 ms, duração
  59.997 ms; verificações locais/nominais dentro do gate. Tempos reconstruídos
  do trace e submetidos a `stroop.domain.web_results.validate_result` com
  ordem/CSV-fonte: aceitos, sem HTTP/PG ou persistência. Nenhuma resposta de
  teclado foi sintetizada nesse principal; fronteiras/teclas são comprovadas
  pelos testes de motor, prática e rodadas E2E acima. Artefatos exclusivamente
  sintéticos `/tmp/stroop-m3-firefox-{timing,probe}.json`, não versionados.
  Amostragem diagnóstica não é campanha de dez réplicas nem mede latência física.
- WEB-010: critérios funcionais conferidos (comparativo ADR-004, setup/cleanup,
  primeira nova pressão/fim exclusivo/interrupções e independência do React),
  com evidência controlada e navegador real. Captura completa complementa
  Firefox visível; falha E2E anterior continua aberta para campanha, sem afirmar
  que foi corrigida. WEB-010 CONCLUIDA; M3 ainda não aceito e sem suporte estável
  declarado. Não foi necessário mudar runtime, tempos ou tolerâncias.

Ambiente observado: Linux `7.0.0-42-generic`, Python 3.12.3, Node 24.15.0,
npm 11.16.0, Playwright 1.64.1; Chromium 156.0.8078.4 e Firefox 157.0;
display gráfico configurado e `--headed` explícito. API double, teclado sintético,
HTTP/Vite local; não é integração HTTPS/API/PG nem campanha DEC-04. Nenhuma nova
suite PostgreSQL foi necessária para alterações restritas a testes do motor.
WEB-011 bloqueada e WEB-012 sem aceite; matriz DEC-04 solicitada ao responsável,
sem resposta registrada até este ponto. Transporte incremental ativo, campanha
D5 e suporte exigem evidências próprias; nenhuma reutilização da exceção W16.

### WEB-042 — Refinar estímulos e hierarquia visual experimental

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: BLOQUEADA.
- Dependências: WEB-009, WEB-010; aprovação metodológica CHG-003 frente a D3/D4.
- Responsável: Codex na execução; responsável metodológico aprova apresentação, HUD e identificação da variante.
- Critérios de aceite: Remover retângulo branco sem caixa substituta; contorno branco uniforme por token com tinta das dez cores/fundo/tipografia preservados. Avaliar stroke e alternativa compatível; centro geométrico inalterado e HUD periférico sem deslocamento. Nenhuma mudança em condições, tempos, ordem, escala por responsividade ou cores. Registrar versão aprovada e screenshots sintéticos de todas as cores em Chromium/Firefox e resoluções permitidas.
- Testes/verificação: PLANEJADO: ampliar web/src/experiment/main.test.ts, practice.test.ts e web/e2e/main.spec.ts/practice.spec.ts para DOM, geometria e screenshots; testes novos terão caminhos registrados quando criados.
- Evidências: PLANEJADAS; nenhum runtime alterado/teste funcional reexecutado para CHG-003. Evidência da auditoria em EV-CHG-003.
- Riscos/bloqueios: R01/R02/R11; impedimento observado: D3 exige HUD anterior; falta aprovação metodológica explícita e definição de identificação/versionamento frente a D4. Ação: responsável aprovar apresentação e registrar decisão antes de código. DEC-04 da campanha permanece pendente.
- Referências: REQ-UX-001/002/007; UX-01/05; componentes main-engine.ts/practice-engine.ts e tokens visuais existentes. [UX](experimento/UX_DECISIONS.md); CHG-003.
- Git da entrega: implementação/commit/testes ainda não aplicáveis; registrar SHA, push e CI quando executada.

### WEB-043 — Reformular HUD e retirar precisão agregada do participante

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: BLOQUEADA.
- Dependências: WEB-009, WEB-010; aprovação metodológica CHG-003 frente a D3/D4 e visibilidade de progresso/tempo.
- Responsável: Codex na execução; responsável metodológico aprova apresentação, HUD e identificação da variante.
- Critérios de aceite: Remover nós, barras, percentuais, rótulos, tooltips e equivalentes de desempenho na prática/principal, sem resíduo na árvore acessível/espaçamento. Não substituir por ranking/taxa de erros. Preservar feedback individual da prática, cálculos oficiais e métricas. Progresso fino/discreto deriva etapa/total e tentativas concluídas do contrato, sem números fixos/animação. Cronômetro decorrido MM:SS/tabular/largura estável usa origem monotônica existente; sem relógio React, timer duplicado, deriva ou alteração de RT. Não criar relógio de prática por inferência.
- Testes/verificação: PLANEJADO: main.test.ts/practice.test.ts verificam ausência e feedback, total real/completadas, relógio/lifecycle; E2E verifica DOM/árvore acessível, geometria e resoluções em Chromium/Firefox.
- Evidências: PLANEJADAS; nenhum runtime alterado/teste funcional reexecutado para CHG-003. Evidência da auditoria em EV-CHG-003.
- Riscos/bloqueios: R01/R02/R11; impedimento observado: D3 exige HUD anterior; falta aprovação metodológica explícita e definição de identificação/versionamento frente a D4. Ação: responsável aprovar apresentação e registrar decisão antes de código. DEC-04 da campanha permanece pendente.
- Referências: REQ-UX-003/004/005/006; UX-02/03/04; componentes main-engine.ts/practice-engine.ts, protocol.ts e summary.ts (preservado). [UX](experimento/UX_DECISIONS.md); CHG-003.
- Git da entrega: implementação/commit/testes ainda não aplicáveis; registrar SHA, push e CI quando executada.

### WEB-044 — Validar regressão da apresentação experimental refinada

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-042, WEB-043.
- Responsável: Codex na execução; responsável metodológico aprova apresentação, HUD e identificação da variante.
- Critérios de aceite: Conferir dez cores, contorno/tinta/ausência da caixa, centro/fonte/escala e HUD nas resoluções aprovadas em Chromium/Firefox com screenshots sintéticos. Ausência real de precisão em prática/principal, inclusive árvore acessível, sem espaço residual/substituto; feedback individual permanece. Progresso/cronômetro corretos, sem timers duplicados. Go/No-Go, congruência, quatro resultados, janelas, sequência, lifecycle, interrupções e versão preservados. Paridade das métricas/CSV em fixtures; persistência/relatórios/admin continuam gates reais WEB-016/019/020. Registrar observação temporal preparatória sem aprovar campanha WEB-011/DEC-04. CSS não comprova validade científica.
- Testes/verificação: PLANEJADO: npm test, npm run typecheck, npm run build; Playwright Chromium/Firefox (visual/funcional/temporal proporcional); tests/test_fase3_condicoes_tempos.py, tests/test_nucleo_compartilhado.py e tests/test_web_export.py. Reusar fixtures sintéticas, sem dados reais. Matriz completa na fonte UX e requisitos; registrar comandos, ambiente, falhas/skips e SHA.
- Evidências: PLANEJADAS; nenhum runtime alterado/teste funcional reexecutado para CHG-003. Evidência da auditoria em EV-CHG-003.
- Riscos/bloqueios: R01/R02/R11; dependências de implementação pendentes; DEC-04 continua necessária para campanha/suporte, sem aprovação presumida.
- Referências: REQ-UX-001 a REQ-UX-007/011; REQ-EXP-001/002/003; main/practice/Host/summary e testes existentes; integração de métricas em M4/M5. [UX](experimento/UX_DECISIONS.md); CHG-003.
- Git da entrega: implementação/commit/testes ainda não aplicáveis; registrar SHA, push e CI quando executada.

## M4 — Fluxo ponta a ponta de avaliações

- Objetivo: Integrar preparação pelo avaliador, execução e recebimento oficial.
- Justificativa: Reúne contratos/motor/autorização em um resultado persistido.
- Inclui: Convite, pseudônimo, instruções, prática, principal, falhas de envio e recibo.
- Exclui: Agendamento/cadastro novo não aprovado, recuperação de principal inválido.
- Pré-requisitos: M2, M3 e M6 aceitos; DEC-01/02 resolvidas para o fluxo.
- Dependências: M2, M3, M6.
- Entregáveis: Avaliação sintética completa em HTTPS real, com trilha e encerramento seguro.
- Componentes afetados: `web/src/participant/, components/, api/sessions.py, results.py`.
- Testes necessários: E2E HTTPS/API/PG reais nos navegadores suportados; rede perdida, expiração, revogação, replay.
- Critérios de aceite: Resultado com 16 tentativas e 12 métricas, recibo e consulta; nenhum falso sucesso nem resultado parcial.
- Riscos: R03, R05.
- Decisões externas: DEC-03 apenas se texto de pesquisa real for incorporado; manter modo sintético.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-013 — Integrar preparação profissional e identificação por convite

- Marco: M4. Prioridade: P0. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-008, WEB-012, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Avaliador autorizado prepara/identifica sessão no React; código único, visita, revogação/expiração e isolamento comprovados com API/PG reais. CHG-002: múltiplas visitas e avaliações na mesma visita preservam UUIDs/vínculos, sem cadastro global ou agenda.
- Testes/verificação: `tests/test_web_sessions.py; web/e2e/integrated/`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-PAR-001, REQ-AVA-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-014 — Validar instruções, prática e início principal no fluxo real

- Marco: M4. Prioridade: P1. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-013.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Textos sem coleta nominal/demográfica; prática repetível sem limiar, interrompida reinicia, início/principal usa sessão autorizada e snapshot correto. CHG-003: reorganizar instruções/tecla/confirmação e transições sem mudar semântica/estratégia; feedback individual e repetição opcional sem limiar mantidos, prática sem precisão agregada.
- Testes/verificação: `web/src/experiment/practice.test.ts; web/e2e/integrated/`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: App/practice/Host, teclado, foco e transições em Chromium/Firefox e fluxo HTTPS real.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R02; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-PAR-003; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-008/009, UX-06/07.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-015 — Ensaiar envio, falhas de rede e recuperação de recibo

- Marco: M4. Prioridade: P0. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-014.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Rede falha antes/depois de commit, retry, expiração, revogação e reload têm comportamento declarado; nenhuma confirmação sem recibo nem principal retomado. CHG-002: fila/worker/ACK, prefixo preservado em interrupção, incompletude sem aviso e invalidação tardia; nova sessão exige prática; mensagens distinguem parcial recebido de resultado oficial. CHG-003: distinguir concluído, aguardando envio, enviando, confirmado, falha, interrompido/inválido; não anunciar recebimento antes do recibo. Preservar ACK/replay, parciais sem resultado oficial, sem retomada; resultado individual somente autorizado pelo protocolo.
- Testes/verificação: `web/src/participant/; tests/test_web_results.py; E2E HTTPS real`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: ParticipantRun.test.ts, ResultSummary.test.tsx e E2E real dos estados com perda/reconsulta do recibo.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R03; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-AVA-003; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-010; ADR-005.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-016 — Aceitar avaliação completa com consulta persistida

- Marco: M4. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-015.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: E2E real confere 1 avaliação/16 tentativas/12 métricas e proveniência; logout limpa RAM e sessão, acesso cruzado nega; M4 aceito. CHG-002: sessão interrompida conserva observações e não gera resultado final; nenhuma mistura entre nova sessão e anterior. CHG-003: fluxo real sem precisão durante prática/principal conserva feedback individual, 12 métricas persistidas e separação das observações parciais; novo layout e estados de envio cobertos.
- Testes/verificação: `web/e2e/integrated/, tests/test_web_participant_logout.py`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: ausência DOM/árvore acessível, recibos, incompletas/inválidas e paridade oficial em HTTPS/API/PG.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R03, R05; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-005/006/008/009/010.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

## M5 — Interface administrativa e analítica React

- Objetivo: Comprovar capacidades necessárias para dispensar Streamlit na operação final.
- Justificativa: Já existe UI; auditar paridade evita perder ferramentas úteis.
- Inclui: Filtros/listas, contas/projetos/vínculos, detalhe, gráficos descritivos e exportação filtrada.
- Exclui: Relatórios clínicos, novos instrumentos, redesign sem requisito.
- Pré-requisitos: M4 aceito e autorização profissional revalidada em M6.
- Dependências: M4.
- Entregáveis: Operação profissional reproduzível no React com escopo consistente.
- Componentes afetados: `web/src/components/, dashboard/, api/assessments.py, administration.py`.
- Testes necessários: Vitest/DOM e E2E reais; acesso cruzado/último admin/CSV filtrado; acessibilidade básica fora do motor.
- Critérios de aceite: Todas capacidades incluídas operáveis, sem nomes/iniciais em resultados nem perda de unidades/proveniência.
- Riscos: R05, R10.
- Decisões externas: Proprietário revisa lacunas materiais de paridade no M7; não inventar relatórios.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-017 — Revalidar filtros, lista e agregações autorizadas

- Marco: M5. Prioridade: P1. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-016.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Filtros/paginação/contagens cobrem conjunto coerente; troca de projeto e respostas tardias não vazam dados; UI acessível fora do motor. CHG-002: sessões incompletas e avaliações invalidadas não entram nos conjuntos válidos/agregações, com acesso a parciais separado e autorizado.
- Testes/verificação: `tests/test_web_assessments.py, web/src/dashboard/analysis.test.ts; Playwright`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-REL-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-018 — Revalidar administração React de contas e vínculos

- Marco: M5. Prioridade: P1. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-016.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Permissões e bloqueio/revogação reais; proteção do último admin sob concorrência, sem exclusão de coletas ou herança de acesso a resultados.
- Testes/verificação: `tests/test_web_administration_provisioned.py; Playwright administrativo`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-REL-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-019 — Validar detalhe, tentativas, métricas e proveniência

- Marco: M5. Prioridade: P1. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-017.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Unidades/ausência RT, quatro respostas e versões visíveis; sem nomes/iniciais; gráficos e rótulos descritivos com testes UI/API. CHG-003: revisar somente tokens/componentes compartilhados, teclado/foco/legibilidade, loading/erro e resoluções; dashboard mantém precisão/gráficos autorizados. Não redesenhar integralmente o painel nem ocultar métricas administrativas.
- Testes/verificação: `tests/test_web_assessments.py, test_web_results.py; Vitest/Playwright`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: componentes Vitest, árvore acessível e Chromium/Firefox; regressão de ResearchVisualizations/ResultsTable/analysis.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R04; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-MET-003, REQ-REL-002; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-006/011.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-020 — Conferir exportação do conjunto filtrado no React

- Marco: M5. Prioridade: P1. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-018, WEB-019.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: CSV individual/agregado coincide com consulta autorizada; revogação pré-download nega; células protegidas; M5 aceito. CHG-003: remoção do HUD não altera CSV individual/agregado nem relatórios e 12 métricas.
- Testes/verificação: `tests/test_web_export.py, test_web_aggregate_export.py; HTTPS real`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: paridade de exportações/relatórios existentes contra fixtures sintéticas.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-CSV-003; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-006.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

## M6 — Autenticação, permissões e segurança

- Objetivo: Revalidar Google OIDC e autorização central antes do primeiro fluxo integrado.
- Justificativa: Reposicionado antes de M4; segurança não será fase tardia.
- Inclui: Callback real autorizado, credenciais separadas, perfis/vínculos, revogação, CSRF e revisão de ameaças.
- Exclui: Redução de proteção, troca de provedor, novas políticas institucionais inferidas.
- Pré-requisitos: M2 aceito; credenciais apenas no ambiente autorizado para ensaio real.
- Dependências: M2.
- Entregáveis: Matriz de autorização e evidência de login/logout com conta cadastrada.
- Componentes afetados: `api/auth.py, google_oidc.py, stroop/domain/auth.py, segurança e proxy`.
- Testes necessários: OIDC negativo/replay, cookies/CSRF/Origin, IDOR, bloqueio, grants; login Google interativo autorizado separado de fixtures.
- Critérios de aceite: Controles positivos/negativos comprovados; login real não pode ser substituído por mock ou alegação histórica.
- Riscos: R05, R07.
- Decisões externas: Conta/cliente OIDC de teste e ambiente autorizado; se indisponível bloquear somente WEB-021/gate dependente.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-021 — Revalidar OIDC e executar login real em ambiente de teste autorizado

- Marco: M6. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-008; conta/cliente de teste autorizado.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Casos negativos e callback/PKCE/state/nonce passam; login/logout Google interativo documentado com identidade cadastrada e sem claims/tokens no artefato público.
- Testes/verificação: `tests/test_web_oidc_callback.py, test_google_oidc.py; PLANEJADO: login real`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-AUT-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-022 — Comprovar matriz de perfis, projetos e revogações

- Marco: M6. Prioridade: P0. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-008.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Consulta/importacao/admin e participante testados em operações positivas/negativas; admin sem projeto não herda resultados; revogação efetiva.
- Testes/verificação: `tests/test_web_auth.py, test_web_assessments.py, test_web_sessions.py`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-AUT-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-023 — Revalidar sessão, cookies, CSRF e isolamento de credenciais

- Marco: M6. Prioridade: P0. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-022.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Origin e CSRF ausentes/divergentes negam; expiração/logout/replay e cookies separados comprovados em HTTPS; sem armazenamento durável.
- Testes/verificação: `tests/test_web_auth.py, test_web_sessions.py; integração HTTPS`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05, R07; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-AUT-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-024 — Concluir revisão de segurança com evidências negativas

- Marco: M6. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-021, WEB-023.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Threat model atualizado, XSS/IDOR/limites/erros/logs e grants verificados; achados impeditivos corrigidos, sem reduzir proteções; M6 aceito.
- Testes/verificação: `tests/test_web_security_review.py, test_web_proxy_config.py; scanner`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R05, R07; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-AUD-001, REQ-SEG-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

## M7 — Integração, compatibilidade histórica e transição

- Objetivo: Preparar substituição operacional sem retirar legado nem modificar coletas.
- Justificativa: Coexistência segura e paridade devem preceder desativação.
- Inclui: CSV complementar, vínculo explícito legado, matriz de capacidades e plano de transição.
- Exclui: Remoção de PsychoPy/Streamlit, migração real ou acesso a banco de coleta.
- Pré-requisitos: M5 e M6 aceitos.
- Dependências: M5, M6.
- Entregáveis: Intercâmbio sintético e cobertura funcional revisada pelo proprietário.
- Componentes afetados: `stroop/ingestion/, api/imports.py, web/src/imports/, CLIs, docs/operacao/`.
- Testes necessários: Roundtrip, sanitização, idempotência, legado por mapa explícito; CLIs/launchers e consultas preservados.
- Critérios de aceite: Cobertura necessária comprovada, lacunas resolvidas/explicitamente excluídas com aprovação; sem concessão de acesso por rótulo.
- Riscos: R06, R08.
- Decisões externas: Revisão do proprietário da cobertura; retirada física é autorização futura independente.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-025 — Revalidar importação minimizada e status idempotente

- Marco: M7. Prioridade: P0. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-020, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Arquivo original intacto, minimização em RAM e rejeição server-side de nominal; erros, limites e UUID/estado/duplicata comprovados.
- Testes/verificação: `tests/test_web_imports.py, web/src/imports/minimize.test.ts; HTTPS real`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R07; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-CSV-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-026 — Comprovar intercâmbio histórico por fixtures sintéticas

- Marco: M7. Prioridade: P1. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-025.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: CSV 21 campos roundtrip API/CLI, unidades e tentativas main preservados; sem leitura/migração de coletas existentes.
- Testes/verificação: `tests/test_csv_unificado.py, test_importar_csv_sqlite.py, test_web_export.py`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R04, R06; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-CSV-001; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-027 — Revalidar vínculo explícito de dados legados

- Marco: M7. Prioridade: P1. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-026.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Projeto de rótulo coincidente sem mapa não acessa; mapa autorizado e desativação cobertos; reader somente leitura; sem provisionar mapa real.
- Testes/verificação: `tests/test_web_assessments.py, test_web_database_provision.py`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R06; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-AUD-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-028 — Revisar cobertura e plano de substituição operacional

- Marco: M7. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-027.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Matriz Streamlit/React com capacidades requeridas testadas, lacunas tratadas e proprietário aprova transição; legado permanece, sem remoção; M7 aceito.
- Testes/verificação: `PLANEJADO: revisão de cobertura e regressão CLIs/launchers`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R10; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

## M8 — CI, infraestrutura e preparação operacional

- Objetivo: Revalidar pipeline/empacotamento/recuperação que já existem.
- Justificativa: CI e restauração já implementadas não podem ser tratadas como só futuras.
- Inclui: Build isolado, pipeline por SHA, HTTPS, backup, réplica/agenda e restauração de massa sintética.
- Exclui: Deploy, alteração de VPS/DNS/certificado operacional ou gatilho nesta fase documental.
- Pré-requisitos: M1 aceito; integração final com M7 antes de M9.
- Dependências: M1; WEB-032 exige M7.
- Entregáveis: Release candidata reproduzível e retorno compatível com schema.
- Componentes afetados: `Dockerfiles, compose.web.yaml, web/deploy/, deploy/, scripts/verify_web_ci.py, .github/workflows/`.
- Testes necessários: Build/smoke isolados, pipeline local e Actions autorizado, recuperação e benchmark limitados ao ambiente medido.
- Critérios de aceite: Sem skip obrigatório, evidências por SHA, restauração íntegra e runbooks executáveis no escopo autorizado.
- Riscos: R08, R09.
- Decisões externas: Destino de réplica e chaves sob custódia; teste externo só com autorização específica; definir verificação formal sem PR sem mudar proteções.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-029 — Revalidar imagens e Compose isolado em HTTPS

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-004.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Build e saúde reais, proxy único público, limites/headers e rejeição de fontes aprovados; pilha temporária separada dos volumes operacionais.
- Testes/verificação: `scripts/smoke_web_compose.py, tests/test_web_runtime.py, test_web_proxy_config.py`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-INF-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-030 — Reproduzir pipeline e definir validação formal sem PR automático

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-029.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Runner local passa testes/PG, frontend/build, scanner/auditoria, browsers e integração; verificação Actions por SHA quando autorizada, sem alterar proteções/gatilhos por conveniência.
- Testes/verificação: `scripts/verify_web_ci.py, tests/test_verify_web_ci.py; PLANEJADO: Actions por SHA`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-EXT-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-031 — Ensaiar restauração, réplica e retorno compatível

- Marco: M8. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-029; destino externo de teste autorizado se necessário.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Massa sintética restaurada isoladamente, schema/dados/recibo conferidos; réplica+agenda+alerta e retorno de imagem ensaiados, RPO/RTO medidos e limites aceitos.
- Testes/verificação: `scripts/smoke_web_recovery.py, tests/test_web_backup_replication.py, test_vps_rollback.py`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-INF-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-032 — Fechar release candidata e runbooks reproduzíveis

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-028, WEB-030, WEB-031.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Manifesto por SHA/imagens/schema, capacidade no ambiente medido, runbooks backup/retorno/incidente e custódia revisados; M8 aceito sem publicação.
- Testes/verificação: `scripts/benchmark_web.py; PLANEJADO: revisão de release e CI real aplicável`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

## M9 — Validação técnica e metodológica

- Objetivo: Separar aceitação de software da autorização de pesquisa.
- Justificativa: Aceite reduzido histórico W16 não equivale a equivalência nem matriz física atual.
- Inclui: Política institucional, campanha aprovada, integração/capacidade, revisão metodológica e barreira de coleta.
- Exclui: Declarar equivalência automaticamente ou realizar estudo com pessoas nesta tarefa técnica.
- Pré-requisitos: M7, M8 e M3 aceitos; responsável/equipamento disponíveis.
- Dependências: M7, M8, M3.
- Entregáveis: Relatório técnico com limites e decisão metodológica assinada/registrada pelo responsável.
- Componentes afetados: `docs/VALIDACAO_WEB.md, homologação, segurança, protocolo e gates existentes`.
- Testes necessários: Campanha de engenharia e física conforme DEC-04; paridade matemática, dados e limites de capacidade; sem dados reais implícitos.
- Critérios de aceite: Falhas resolvidas ou escopo de suporte explicitamente reduzido com aprovação; nenhuma alegação além das evidências; prontidão real decidida.
- Riscos: R01, R02, R07.
- Decisões externas: DEC-03/04 para prontidão; DEC-05 é autorização posterior a M9; se estudo científico necessário, planejar protocolo separado e não fabricar resultados.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-033 — Registrar prontidão institucional e privacidade

- Marco: M9. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-028; DEC-03.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Responsável registra política, finalidades, minimização/retenção, informação aplicável, responsabilidades e eventual autorização institucional; sem inferir consentimento legal.
- Testes/verificação: `PLANEJADO: revisão institucional/documental DEC-03`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R07; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-SEG-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-034 — Executar validação temporal e metodológica aprovada

- Marco: M9. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-012; DEC-04.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Campanha com matriz/equipamento/protocolo aprovados, medidas físicas se exigidas, falhas e limites registrados; comparação com PsychoPy apenas se estudo autorizado. CHG-003: validar protocolo visual atualizado: contorno branco, ausência de caixa, HUD/visibilidade e retirada da precisão; avaliar percepção das cores, saliência/atenção e diferenças entre browsers/versões. Confrontar tempos observados antes/depois com proveniência; automação não prova equivalência com PsychoPy nem validade psicométrica.
- Testes/verificação: `PLANEJADO: campanha M9; docs/VALIDACAO_WEB.md é referência histórica`. Arquivos citados existem; verificações PLANEJADAS não têm resultado. Adicional PLANEJADO: campanha metodológica aprovada DEC-04, revisão sintética das dez cores e efeitos de apresentação, evidências finais WEB-011/044.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R01, R02; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-001 a REQ-UX-007/011; R01/R02/R11.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-035 — Homologar candidato integrado e capacidade no ambiente autorizado

- Marco: M9. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-032, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: API/PG/navegadores reais, falhas/reinício/limites de concorrência ensaiados em ambiente autorizado; sem extrapolar local→VPS ou carga→timing físico.
- Testes/verificação: `web/e2e/integrated/, scripts/benchmark_web.py; PLANEJADO: homologação do candidato`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-036 — Obter aceite técnico e decisão explícita de liberação

- Marco: M9. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-033, WEB-034, WEB-035.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Responsável aceita prontidão técnica/metodológica e limites de suporte após 033/034/035; não concede deploy/coleta real. Barreira synthetic preservada; pedido concreto de DEC-05 pode ser preparado depois de M9.
- Testes/verificação: `PLANEJADO: ata de aceite por responsável e revisão das barreiras de operação`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R01, R07; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-SEG-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

## M10 — Implantação controlada e documentação operacional

- Objetivo: Publicar somente release aceita e autorizada com recuperação comprovada.
- Justificativa: Protege sistema publicado, histórico e responsáveis.
- Inclui: Configuração research condicionada à aprovação (WEB-041), plano autorizado, backup/retorno, publicação/smoke, réplica/alerta e handoff.
- Exclui: Deploy automático, migração destrutiva, coleta real ou retirada do legado por inferência.
- Pré-requisitos: M9 aceito; DEC-03/05 para configurar research. Preparação/testes locais não dependem de autorização de deploy; intervenção em produção e eventuais dados/schema exigem autorização específica antes de WEB-038.
- Dependências: M9.
- Entregáveis: Registro da release, recuperação e operação assistida com decisão de uso.
- Componentes afetados: `Runbooks, release, infraestrutura autorizada e documentação de operação`.
- Testes necessários: Smoke pós-publicação sem dados reais, ensaio isolado de restauração/rollback e aceite operacional.
- Critérios de aceite: Release íntegra, riscos/limites conhecidos, runbooks e custódia entregues; uso real só se DEC-05 autorizado.
- Riscos: R07, R08, R09.
- Decisões externas: Autorização de deploy somente antes de WEB-038, após plano concreto; credenciais/recursos; integração main se desejada exige autorização separada; coleta e retirada legado independentes.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-037 — Preparar publicação e retorno da release aceita

- Marco: M10. Prioridade: P0. Complexidade: M. Estado: PENDENTE.
- Dependências: WEB-041.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Plano concreto e candidata validada identificam release, janela, backup, schema, responsáveis, smoke/critério de retorno; resultado preparado para aprovação final do deploy antes de WEB-038, sem tocar produção.
- Testes/verificação: `PLANEJADO: checklist pré-publicação`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-038 — Executar implantação controlada autorizada e smoke

- Marco: M10. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-037; autorização específica de deploy registrada.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Somente ações autorizadas executadas; HTTPS/login/fluxo sintético/consulta/exportação e versão públicos conferidos; falha dispara retorno previsto.
- Testes/verificação: `PLANEJADO: smoke pós-deploy e evidência da release`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-039 — Confirmar recuperação e handoff operacional

- Marco: M10. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-038.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Agenda/réplica/alerta e custódia confirmadas; restauração isolada e rollback compatível conferidos para release publicada; operador reproduz runbook sem dados no log.
- Testes/verificação: `PLANEJADO: ensaio operacional autorizado e handoff`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-040 — Encerrar transição com aceite do proprietário

- Marco: M10. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-039, WEB-041; DEC-05 para uso real.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Aceite final identifica limites, suporte, política de uso e incidentes; legado preservado salvo autorização específica; liberação real, se concedida, rastreada e verificada; M10 aceito.
- Testes/verificação: `PLANEJADO: aceite operacional e revisão final de rastreabilidade`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R07, R10; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### WEB-041 — Implementar configuração controlada para pesquisa real após aprovação

- Marco: M10. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-036, DEC-03 e autorização DEC-05 específica para a implementação/configuração de pesquisa; nenhuma ação sobre dados reais por implicação.
- Responsável: Codex no código e testes; proprietário/instituição nas regras e autorização; operador na ativação real separada.
- Critérios de aceite: especificar e implementar o contrato já previsto em seguranca/ACESSO_WEB.md para modo research, aviso versionado, elegibilidade/informação aplicáveis, confirmação datada por responsável e habilitação administrativa explícita por projeto. Default continua synthetic; ausência/incompletude/revogação da configuração bloqueia emissão/resgate research. Não alterar D1–D6, métricas nem acrescentar coleta nominal. Qualquer schema novo é aditivo e testado apenas em banco sintético. Revalidar autorização, integração e critérios M9 afetados na nova SHA candidata antes de WEB-037; registrar se requisito metodológico novo exigir replanejamento em vez de implementar por inferência.
- Testes/verificação: PLANEJADOS, novos testes de configuração completa/incompleta, modos, papéis, revisão/retirada da habilitação e aviso no fluxo real com participantes inequivocamente sintéticos; regressão Python/PG, frontend e HTTPS real. Arquivos/testes novos só serão nomeados quando implementados.
- Evidências: PLANEJADAS; nenhuma configuração/código de coleta real implementado nesta sessão.
- Riscos/bloqueios: R05/R07; sem DEC-03/05 permanece PENDENTE/BLOQUEADA conforme impedimento observado. Não há tarefa independente que permita declarar operação real concluída sem esta entrega.
- Referências: REQ-SEG-003, REQ-SEG-002, REQ-PAR-003, REQ-AVA-001; ARQUITETURA_WEB e seguranca/ACESSO_WEB.md.
- Git: branch/commit/push/CI a registrar na execução autorizada; não habilitar produção por commit ou teste.

## Registro de riscos

Probabilidade qualitativa é hipótese de planejamento, não estatística. Severidade
considera integridade, validade e continuidade. R01–R10 ABERTOS desde 2026-11-04; R11 registrado em 2026-11-05. A presença
de mitigação no código não elimina risco sem ensaio. Atualizar somente aqui.

| ID | Descrição e causa | Impacto | Probabilidade | Severidade | Mitigação e evidência exigida | Marco | Responsável | Estado |
|---|---|---|---|---|---|---|---|---|
| R01 | Timing de navegador varia com hardware, SO, carga e compositor | RT/onset incompatíveis com uso pretendido | Alta | Crítica | M3 cedo, trilhas/gates, matriz medida e campanha aprovada; não inferir latência física; CHG-003 mede layout final/HUD com transporte ativo, custo de stroke e browsers sem relaxar D5 | M3/M9 | Técnico + metodológico | ABERTO |
| R02 | Confundir PsychoPy, variante WEB e aceites históricos | Conclusões científicas indevidas | Alta | Crítica | D1–D6 e versões separadas, preservar falhas W16, validação metodológica distinta; identificar apresentação antes/depois e variante aprovada frente a D3/D4 | M2/M3/M9 | Metodológico | ABERTO |
| R03 | RAM até envio final, falha/reload/expiração e corrida de commit | Perda ou duplicação de tentativas/resultados | Alta | Crítica | CHG-002/ADR-005; validar estratégia incremental e matriz antes de código; ensaiar ACK/replay, perda do sufixo e corridas; final-only rejeitado | M2/M4 | Backend + produto | ABERTO |
| R04 | Diferenças de sentinela RT, unidade, mediana/arredondamento entre consumidores | Regressão nos cálculos/análises | Média | Alta | Golden fixtures sintéticas e paridade núcleo/API/CSV/UI, sem mudança silenciosa | M1/M2/M5 | Técnico | ABERTO |
| R05 | Alterar OIDC ou perfis/vínculos sem revalidar negações | Acesso cruzado, sessão indevida, perda de administração | Média | Crítica | Login real autorizado, CSRF/Origin/IDOR, revogação, último admin, reader/writer | M6/M4/M5 | Segurança/técnico | ABERTO |
| R06 | Novo schema ou rótulo de projeto apropria/muda histórico | Corrupção ou acesso a coletas | Média | Crítica | Aditividade, mapa explícito, fixtures, nenhum dado real sem autorização | M2/M7 | Backend + proprietário | ABERTO |
| R07 | Pseudônimo tratado como anônimo; coleta/liberação sem política institucional | Exposição de pessoas e uso indevido | Média | Crítica | DEC-03/05, minimização e barreira synthetic, sem nomes/logs, revisão institucional | M6/M9/M10 | Proprietário/instituição | ABERTO |
| R08 | Publicação interrompe aplicação; backup não restaurável/retorno incompatível | Indisponibilidade/perda | Média | Crítica | Ensaio isolado schema/dados/imagens, réplica/agenda/alerta, deploy autorizado e retorno | M7/M8/M10 | Operador/proprietário | ABERTO |
| R09 | Dependências de VPS/DNS/TLS/OIDC/chaves/destino externo ou CI sem PR | Bloqueio de homologação/recuperação e falsa prontidão | Média | Alta | Preparar local independente; inventário de recursos e validação por SHA, sem mudar proteção para contornar bloqueio | M1/M8/M10 | Operador + técnico | ABERTO |
| R10 | Reescrever o que existe, ampliar instrumentos e manter backlogs concorrentes | Retrabalho e escopo sem controle | Alta | Alta | Auditoria, backlog único, critérios pequenos, IDs e controle de mudança; sem crédito histórico automático | Todos | Coordenador técnico | ABERTO |

| R11 | Contorno/retirada da caixa e precisão, HUD e diferenças de renderização alteram percepção/saliência/atenção | Versões experimentais incompatíveis e evidência anterior insuficiente | Média | Alta | Aprovar apresentação frente a D3/D4; dez cores/screenshots sintéticos Chromium/Firefox, versão/SHA distinta, WEB-044/011 e revisão WEB-034 com DEC-04. Não inferir melhoria de desempenho/validade pela redução de informação potencialmente distrativa | M3/M4/M9 | Técnico + metodológico | ABERTO |

Risco mais importante: R01, com R02 como limite de interpretação. R03 é o
principal risco de integridade do fluxo atual e precisa decisão antes de ampliar captura.

## Decisões externas e condições de desbloqueio

As hipóteses não são autorização. Uma decisão deve registrar autor/data, opção,
justificativa, requisito/contrato, tarefas/testes e necessidade de novo ADR ou
versão experimental. Somente bloquear tarefa dependente, sem paralisar documentação.

| ID | Questão / hipótese preservada | Responsável | Condição objetiva / impacto | Tarefas relacionadas | Estado |
|---|---|---|---|---|---|
| DEC-01 | Participante pseudonimizado por projeto, múltiplas visitas/avaliações e preparação por convite; sem cadastro central ou agenda separada nesta versão | Proprietário; decisão explícita em 2026-11-05 | APROVADA a direção; vínculos estáveis e evolução aditiva no modelo. Implementação/ensaios ainda não realizados; retenção institucional continua DEC-03 | WEB-005/006/007/013 | APROVADA |
| DEC-02 | Final-only rejeitado; persistência incremental com recibo/idempotência e preservação de incompletas/ inválidas, sem retomada; nova sessão com prática | Proprietário + metodológico; diretriz e validação explícitas em 2026-11-05 | Resposta “valido” à proposta `270377b` aprova ADR-005, contrato alvo, matriz D2/D5 e perda residual; gate documental WEB-005 satisfeito. Implementação/ensaios técnicos e temporais ainda exigidos | WEB-005/006/007/011/012/015 | APROVADA |
| DEC-03 | Regras institucionais de informação, consentimento aplicável, retenção e incidentes | Proprietário/instituição | Documento aprovado e responsabilidades/canal definidos; nenhuma base legal inventada pelo Codex | WEB-033/036 | PENDENTE |
| DEC-04 | Matriz de hardware/SO/browser e validação física/metodológica necessária | Responsável metodológico | Plano e recursos aprovados para layout final CHG-003, manter D1/D5 e limites W16; alterações de suporte/gate justificadas e aprovadas | WEB-011/012/034 | PENDENTE |
| DEC-05 | Após prontidão M9, autorizar separadamente configuração research, deploy e eventual uso real | Proprietário + metodológico/operador | WEB-036 comprovada; registrar autorização específica antes de WEB-041 e, para produção/uso, de WEB-038/040; mudanças da candidata passam revalidação dos gates afetados; não retirar synthetic apenas por aprovação técnica | WEB-041/038/040 | PENDENTE |

Recursos externos não decisórios: conta/cliente OIDC de teste WEB-021; destino de
réplica e custódia para WEB-031; ambiente de homologação WEB-035; VPS/DNS/TLS e
acesso de operação WEB-037. Solicitar somente quando a entrega dependente estiver
concreta; não pedir secrets na conversa. Adoção técnica de stack está no ADR-004,
não depende de reaprovação científica. Não há bloqueio documental remanescente.

## Registro de mudanças de escopo

- CHG-001, 2026-11-04: nova missão de plataforma e governança única por instrução
  do proprietário. Substitui execução Wxx/etapas antigas por M0–M10/WEB sem
  invalidar aceites históricos. Impacta requisitos A–L, AGENTS/workflow e critérios
  de revalidação; nenhuma mudança em protocolo, fórmula, schema ou runtime.
  ADR-004 e auditoria fundamentam reutilização de React/FastAPI/jsPsych existentes.
- CHG-002, 2026-11-05: resposta explícita do responsável aprova pseudônimos por
  projeto com múltiplas visitas/avaliações, convite único/acesso/validade e evolução
  longitudinal aditiva; sem cadastro central/agenda nesta versão. Rejeita RAM
  final-only; requer checkpoints confirmados/idempotentes e preservação de dados
  incompletos/ inválidos, sem retomada do principal. D2/D5, prática, métricas e CSV
  preservados. ADR-005 é proposta posterior à resposta, a validar antes de código.
  Impacta REQ-PAR-001/002, REQ-AVA-001/002/003, REQ-INT-001/002/003; modelo, HTTP,
  arquitetura e protocolo alinhados. WEB-005 fecha desenho/aceite; WEB-006/007
  passam a cobrir vínculos/schema aditivo e checkpoints; WEB-008 revalida paridade
  e exclusão de parciais; WEB-011/012 medem transporte ativo; WEB-013/015 integram
  vínculos, fila e mensagens; WEB-016/017 revalidam exclusão de inválidos nas
  consultas. Ensaios adicionais no ADR-005, ainda PLANEJADOS. Nenhum novo aceite,
  tarefa/denominador ou autorização de implementação/migration/produção inferidos.
### CHG-003 — Refinamento visual e redução de elementos distrativos do Stroop Web

- Origem/data: missão explícita do proprietário em 2026-11-05 nesta sessão.
- Justificativa/objetivos: priorizar estímulo, reduzir informação de desempenho
  potencialmente distrativa e tornar instruções/transições/entrega compreensíveis;
  não manipular resultados nem presumir ganho de desempenho/validade.
- Incluído: UX-01–08; contorno branco sem cartão, HUD/progresso/cronômetro,
  retirada completa de precisão agregada na prática/principal, hierarquia,
  instruções, feedback individual preservado, estados de envio e acessibilidade.
- Excluído: paradigma, cores, tempos, sequência, modalidades, fórmulas/métricas,
  CSV, dashboard completo, bibliotecas novas, banco operacional, produção/deploy,
  retomada do principal e qualquer declaração de equivalência psicométrica.
- Classificação: A — visual não experimental (tipografia tabular, alinhamento,
  foco/estados de UI); B — apresentação que pode alterar percepção/atenção
  (contorno, caixa, HUD e retirada da precisão); C — revisão de D3 e identificação
  frente a D4, sem autorização de protocolo inferida da direção UX. Itens A
  acoplados ao HUD não contornam o bloqueio B/C com implementação parcial.
- Requisitos: novos REQ-UX-001…011; relações ampliadas com REQ-EXP-001/002/003,
  REQ-MET-001/002/003, REQ-AVA-003, REQ-INT-002/003 e REQ-REL-002/CSV-003.
- Componentes: motores main/practice, plugins jsPsych, ExperimentHost, protocol,
  App/styles, ParticipantRun/ResultSummary; fórmulas/relatórios apenas regressão.
- Marcos: M3 (WEB-042/043/044 novos; WEB-011/012 ampliados), M4
  (WEB-014/015/016), M5 (WEB-019/020 só componentes compartilhados/regressão), M9
  (WEB-034). M0/M1/M2 aceites preservados; sem impacto concreto em M6/7/8/10.
- Dependências/caminho crítico: WEB-009/010 → aprovação de apresentação e versão
  → WEB-042/043 → WEB-044 → WEB-011 com DEC-04/transporte DEC-02 → WEB-012.
  M4/M5 mantêm seus gates; nenhuma dependência circular criada.
- Aceite: onze requisitos rastreados e critérios verificáveis nas fichas e UX;
  documentação válida não significa retirada funcional. Aceites históricos não
  reabertos; novo escopo possui fichas próprias. Critérios funcionais/visuais e
  temporais detalhados em WEB-042/043/044/011 e integração em WEB-016/019/020/034.
- Riscos/testes: R01/R02 revisados, R11 aberto; Vitest/tipos/build, DOM/árvore
  acessível, Chromium/Firefox/resoluções e screenshots sintéticos, paridade Python,
  integração real de métricas/recibos, campanha D5 no layout final e revisão M9.
- Decisões externas: D3 exige precisão ao vivo; responsável deve aprovar nova
  apresentação, visibilidade de HUD e identificação/versionamento frente a D4.
  DEC-04 continua PENDENTE. Sem aceite científico ou equivalência por solicitação.
- Impacto no progresso: +3 entregáveis vigentes, 42→45; numerador preservado 11,
  26,2%→24,4% por expansão rastreada, sem perda de aceite. M3 passa 2/4→2/7.
- Condições de implementação: somente M3 autorizado, decisões e dependências
  satisfeitas e documentação validada primeiro. Nenhuma tarefa funcional pronta
  nesta auditoria; não antecipar M4/M5 ou encerrar M3. Aprovação solicitada nesta
  sessão, ainda sem resposta registrada no fechamento da integração.

### EV-CHG-003 — auditoria direcionada, 2026-11-05

Base limpa `0fdca9de8d44a20c6934c8c935495971e360b9e8`, branch existente
`feat/m3-motor-experimental` preservada por conter M2/M3 ainda não integrados.
Fetch conferiu HEAD/upstream iguais; main local `fe8f24f`, origin/main `db56b40`;
sem sincronização/rebase/merge. Fontes consultadas: AGENTS raiz/docs/web/scripts,
workflow/backlog, requisitos/arquitetura, D1–D6, ADR-004/005, UX/copy,
versionamento/Contribuição, código e testes frontend relacionados.

| Achado relevante atual | Código/teste real inspecionado | Impacto planejado |
|---|---|---|
| Palavras e caixa branca criadas por ambos motores; fundo `#F8FAFC` somente na fase stimulus | main-engine.ts/render e practice-engine.ts/render; main.test.ts/practice.test.ts afirmam fundo branco | WEB-042/044 substituem apresentação após aprovação; não apagar provas anteriores |
| Cores do snapshot e fontes CSV; texto system-ui/sans-serif, peso 700, tamanho min(9vh,9vw), cartão 82vh x 24vh | protocol.ts, condicoes/web_protocol.json, environment.test.ts, main.test.ts | Preservar dez cores, fonte e centro; avaliar stroke por token uniforme |
| HUD não é componente React compartilhado; cada motor cria precisão/barra/progresso/time | main-engine.ts/updateHud, practice-engine.ts/updateHud | Retirar nós/percentuais sem atingir gráficos administrativos; rever espaço |
| Precisão usa correct/completed; principal arredonda half-even, prática Math.round; barra textual de dez segmentos | ambos motores e main.test.ts/practice.test.ts | Remover apresentação; não alterar cálculo oficial Python, resumo técnico ou feedback individual |
| Principal mostra tentativa atual com total 16 literal; prática usa order.length; não há barra gráfica de progresso compartilhada | ambos updateHud | Total/etapa do contrato e contagem concluída em WEB-043 |
| Cronômetro principal já usa elapsed monotônico do motor, cache por segundo e MM:SS; prática mostra placeholder | main-engine.ts, practice-engine.ts | Preservar semântica; token tabular e estabilidade sem intervalo React |
| Plugins jsPsych invocam runtimes e limpam teclado/timeouts/listeners; Host useEffect monta/retorna cleanup | main.ts, practice.ts, ExperimentHost.tsx, ExperimentHost.test.tsx | Manter propriedade do DOM/relógio fora de React |
| Instruções navegam em App; PracticePreparation monta prática/principal via Host e mantém transições/resumo; ParticipantFlow coordena telas e ParticipantRun distingue pending/sending/saved e recibo | App.tsx, PracticePreparation.tsx, ParticipantFlow.tsx, practice-engine.ts, ParticipantRun.ts, ResultSummary.tsx; E2E main/practice e testes de componentes | Refinamentos em M4, sem pressupor fluxo incremental final integrado |
| Gráficos/tabelas profissionais possuem precisão separada do HUD | ResearchVisualizations.tsx, ProfessionalDashboard.tsx, ResultsTable.tsx, analysis.test.ts | Preservar métricas/relatórios e escopo de acesso em M5 |
| D3 exige HUD com precisão e D4 fixa variante; novo visual ainda não aprovado metodologicamente | PROTOCOLO_WEB e DECISOES_DO_EXPERIMENTO | WEB-042/043 BLOQUEADAS; DEC-04 não substituída por direção UX |

Configuração remota lida por `gh api repos/thiagorraposo/stroop-go-nogo-psychopy`:
allow_merge_commit=true, allow_squash_merge=false, allow_rebase_merge=true.
Preferência do proprietário: PR quando autorizado, Merge Commit tradicional,
preservando commits; sem squash em novas integrações. Rebase habilitado no
remoto não muda essa preferência; nenhuma configuração/proteção foi alterada.
PR continua não automático conforme AGENTS/Contribuição.

- Revisão futura: usar ID CHG novo com motivo, requisito alterado, componentes,
  testes a revisar, dependências afetadas e aprovação externa quando exigida.
  Não reabrir tarefa concluída sem regressão comprovada ou novo escopo registrado.

## Retomada

### Retomada vigente — CHG-003, 2026-11-05

Marco autorizado **M3**, sem avanço implícito. Integração documental de CHG-003
não implementa UX: barra/cartão anteriores continuam presentes no runtime.
**11/45 entregáveis aceitos (24,4%), 34 sem aceite; M3 2/7**. Novas fichas
WEB-042/043 BLOQUEADAS pela aprovação de apresentação/D3 e identificação/D4;
WEB-044 PENDENTE. WEB-011 BLOQUEADA por DEC-04 e dependente do visual final;
WEB-012 PENDENTE. WEB-000…010 e todas as evidências históricas preservadas.

Próxima ação exata: responsável aprovar apresentação experimental revisada
(contorno/ausência de cartão e precisão), HUD visível e identificação/versionamento
frente a D3/D4. **Nenhuma tarefa funcional pronta** antes disso. Então implementar
WEB-042/043 → WEB-044, somente em M3; WEB-011 depende ainda de DEC-04 e transporte
incremental ativo. Não repetir baseline global nem campanha antiga por inferência.
R01/R02/R11 continuam abertos, sem promessa de validade ou equivalência.

Versionamento/verificações desta integração: ver EV-CHG-003 e fechamento abaixo.
Os registros seguintes são históricos e não substituem esta Retomada vigente.

### Fechamento da integração CHG-003 — 2026-11-05

Integração documental conferida: CHG formal, UX-01–08 em onze requisitos,
preservação de cálculos/feedback, fichas/dependências/aceites/testes, riscos,
workflow, painel e matriz. Critérios 1–17 da missão documental atendidos;
“próxima executável” identifica expressamente ausência de tarefa funcional pronta
e ação objetiva de desbloqueio, sem inventar prontidão. Nenhum aceite funcional
novo: 11 CONCLUIDAS, 3 BLOQUEADAS e 31 PENDENTES. M3 não encerrado.

Validações locais nesta sessão, Python **3.12.3**, checkout Linux atual:

- `python3 scripts/verify_web_docs.py`: aprovado; **11 marcos, 45 tarefas,
  47 requisitos/matriz, 11 riscos, cinco decisões, 11 aceitos; 84 documentos,
  561 links locais e 42 âncoras**, sem referências inexistentes/ciclos.
  Total difere das 85 leituras históricas porque o novo validador exclui `data/`
  e destinos protegidos/symlinks antes da leitura, conforme AGENTS; não houve
  acesso a coletas. Contagens dinâmicas e IDs já versionados preservados.
- `python3 -m unittest tests.test_verify_web_docs -v`: **7 testes aprovados**,
  sem skips, incluindo expansão, perda de IDs, ciclos/estados, matriz,
  painel/percentuais e links/âncoras com proteção de dados em Git temporário.
- `git diff --check`: aprovado. Revisão principal integrou conferência
  independente de catálogo/cobertura e corrigiu tabela de foco do marco e
  referência desatualizada do aceite REQ-INF-001, sem reabrir tarefas históricas.

Escopo: dez documentos e validador Python com teste sintético. Sem alteração
React/jsPsych, fórmulas, snapshot, dependências, migrations ou dados. Vitest,
typecheck/build Vite, Playwright e regressão Python experimental **não executados**:
nenhum runtime experimental mudou e as tarefas de implementação permanecem
bloqueadas por aprovação metodológica; testes futuros estão marcados PLANEJADOS.
Screenshots novos não foram produzidos nem alegados como evidência.

Git da integração: branch adequada `feat/m3-motor-experimental`, base `0fdca9d`;
entrega identificável por `git log -1 --format=%H
--grep='docs: integra refinamento UX ao planejamento canônico'`.
Commit/envio/consulta CI efetivos serão registrados no fechamento após a entrega.
Nenhum PR/merge/deploy autorizado ou executado.

### Retomada anterior — revalidação funcional M3 (histórico preservado)

Marco autorizado: **M3**, por novo `continue o projeto` em 2026-11-05.
WEB-009/010 **CONCLUIDAS**: condições/paleta/tempos e critérios funcionais do
motor, plugins, lifecycle e resposta/interrupção comprovados em EV-M3-009/010.
M0–M2 preservam aceite; WEB-000 a WEB-010: **11/42** entregáveis aceitos
(26,2%), 31 sem aceite; M3 **2/4**, ainda não aceito.

WEB-011 **BLOQUEADA** pela matriz/equipamento DEC-04 não aprovados; WEB-012
PENDENTE de WEB-011. Pergunta ao responsável enviada nesta sessão, sem resposta
registrada até o fechamento. R01/R02 abertos: Firefox visível teve invalidação
D5 na rodada E2E e uma captura diagnóstica posterior completa válida; isso não
comprova estabilidade nem explica a causa da falha. Nenhuma falha foi omitida,
nenhuma mudança em D1–D6 ou redução de suporte autorizada por inferência.

Próxima ação exata: responsável metodológico aprovar DEC-04 (ambientes,
equipamentos/versões e alcance da campanha). Depois, em WEB-011, preparar o
transporte incremental ativo e capturas planejadas/observadas para 10 execuções
por ambiente, incluindo falhas/retries previstos; investigar a invalidação
Firefox com evidências. Aceite de suporte em WEB-012 só após campanha e revisão.
Não iniciar outro marco nem repetir baseline global por implicação.

Branch `feat/m3-motor-experimental`, criada de `832abfd` (M2), worktree inicial
limpa, origin atualizado por fetch. Branch M2/upstream em `832abfd`;
main local `fe8f24f`, origin/main `db56b40`: diferença preservada sem sincronizar
ou integrar por implicação. A branch contém trabalho M2 ainda não integrado;
base mantida para revalidar motor contra o receptor atual. Nenhum PR/merge/deploy.

Git da entrega: testes em **`7cad3476e2142c98b863dd28c043c4b2e44d083a`**,
push com upstream confirmado por HEAD/upstream/ls-remote na mesma SHA.
CI consultada após esse push: nenhuma execução na branch (não equivale a
aprovação). Fechamento documental identificável por `git log -1 --format=%H
--grep='docs: registra revalidação funcional de M3 e gate temporal pendente'`;
seu envio é verificável por igualdade HEAD/upstream/ls-remote. Falha de envio
deve ser registrada sem force push; sem PR/merge automático.

Validação documental local final: procedimento Python do workflow sem a asserção
exclusivamente Markdown de M0: **85 documentos, 548 links, 42 âncoras**, zero
erros; 42 tarefas, 36 requisitos/matriz, 11 marcos, 10 riscos, cinco decisões e grafo
sem ciclos. Contagens visuais conferidas contra fichas: 11 concluídas, uma
bloqueada e 30 pendentes. `git diff --check` e novo `npm run typecheck` após
corrigir o E2E aprovados. Quatro arquivos de testes e três documentos no escopo;
runtime, protocolo, dependências, migrations e dados preservados.

Evidências atuais: EV-M3-009/010; históricos M2 em EV-M2 e EV-M2-007/008.
Rodadas com falha permanecem explícitas; correção de sincronização do teste não
corrige nem oculta invalidação Firefox. Artefatos sintéticos somente em locais
ignorados/temporários, sem exports/logs versionados.


Histórico Git do aceite: branch `docs/m2-contratos-participacao`, base `270377b`, worktree
inicial limpa, upstream conferido após fetch; main/origin/main em `fe8f24f`.
Proposta `270377b89ea477bf864114d0e8a3017e3520a84f` enviada e confirmada no
upstream/remoto antes desta revisão. Commit deste aceite identificável por
`git log -1 --format=%H -- docs/arquitetura/ADR-005-persistencia-incremental.md`.
Envio ao upstream existente verificável por igualdade entre `git rev-parse HEAD`,
`git rev-parse @{upstream}` e `git ls-remote --heads origin
 docs/m2-contratos-participacao`; registrar falha se ocorrer, sem force push.
Validação documental local em 2026-11-05: procedimento Python do workflow
(85 documentos, 507 links relativos, 3 âncoras; 42 tarefas, 36 requisitos/matriz,
11 marcos, 10 riscos, 5 decisões, sem ciclos) e `git diff --check` aprovados.
Escopo: nove documentos Markdown; nenhuma suite funcional reexecutada.
CI da branch consultada: nenhuma execução; não equivale a aprovação funcional.
Sem PR, merge, deploy, instalação, migration ou acesso a dados reais.

Checkout de desenvolvimento: `/home/raposo/Projetos/experimentos-psicopy/stroop-cognifit`.
Worktree sintética M1 `/tmp/stroop-m1-baseline-20261104` preservada em HEAD
destacada; não repetir baseline global sem divergência concreta.

Git M1: baseline versionada em `e15892c5d8a396223b5f33d842a003e882e4ee6d`,
enviada com upstream e confirmada por `git ls-remote --heads origin
test/m1-baseline-sintetica` na mesma SHA. O commit posterior de aceite de
WEB-004/M1 é identificável por `git log -1 --format=%H -- 'docs/Projeto Stroop Test.md'`
e usa o mesmo upstream; conferir HEAD/remoto no encerramento. Consulta
`gh run list --branch test/m1-baseline-sintetica` retornou nenhuma execução: CI
remota não executada nesta branch; testes acima são locais. Sem PR/merge/deploy.

Histórico de fechamento de M0 (preservado, não descreve a sessão M1):

Git documental: branch `docs/replanejamento-stroop-web`, baseada na HEAD auditada
87f6a9c (contém main fe8f24f e trabalho não integrado). Os commits desta entrega
podem ser identificados por `git log --oneline --grep='docs: consolida planejamento da plataforma Stroop Web'`;
o registro de fechamento acrescenta o SHA real sem tentar autorreferenciar o
próprio commit. Conferir worktree, upstream e commits locais antes de retomar.
Entrega documental: commit `e652f2c1be664241364609443356b0277622c242`, enviado e
confirmado por `git ls-remote --heads origin docs/replanejamento-stroop-web` na
mesma SHA em 2026-11-04. O commit de fechamento de M0 foi
`a644e2c0c53bf6da27630c8179ee887c6436ff1e`, conferido com upstream na inicialização
de M1. M0 documental concluído; nenhum marco funcional havia sido iniciado naquele
fechamento. Os 33 arquivos da entrega eram todos Markdown; inventário recuperável
por `git diff --name-only 87f6a9c..a644e2c`.

Commit/push documental não autorizam integração à main. CI remota desta entrega
não executada/não verificada; workflow existente só dispara PR/main/manual.
Não há PR nem merge autorizado. Produção e dados reais permanecem fora do escopo autorizado.


### Entrega documental — painel visual, 2026-11-05

Por solicitação do responsável, acrescentados painel de aceites, barras por marco
e navegação visual em PROGRESS, com índice e registro de alterações alinhados.
Nenhum estado, aceite, requisito ou próxima tarefa funcional foi alterado.
Validação local: procedimento documental do workflow aprovado com 85 documentos,
542 links relativos, 36 âncoras, 42 tarefas, 36 requisitos/matriz, 11 marcos,
10 riscos, cinco decisões e grafo sem ciclos; contagens visuais conferidas contra
as fichas. `git diff --check` aprovado; quatro arquivos Markdown no escopo.
Suites funcionais não reexecutadas para esta alteração de apresentação.

Git: branch `docs/m2-contratos-participacao`, base `fc56d93`, inicialmente limpa e
alinhada ao upstream após fetch; main/origin/main em `fe8f24f`, sem integração.
Commit desta entrega identificável por `git log -1 --format=%H
--grep='docs: adiciona painel visual de acompanhamento'`.
Envio verificável pela igualdade de HEAD, upstream e referência remota dessa
branch; eventual falha deve ser registrada sem force push. CI remota desta entrega
não verificada; validação acima é local. Sem PR, merge ou deploy.
Próxima tarefa funcional naquela entrega era WEB-006; registro histórico
superado pela Retomada e EV-M2 desta implementação.
