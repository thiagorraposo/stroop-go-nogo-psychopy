# Projeto Stroop Test — backlog canônico da plataforma WEB

Última verificação documental: **2026-11-12**. Missão e limites:
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
autoriza M3, condicionado às decisões de suas tarefas. Em 2026-11-05, o proprietário
aprovou DEC-04 no alcance local de engenharia descrito em EV-M3-011; validação
física/metodológica permanece pendente para M9. Após o aceite de M3, novo `continue o projeto` em 2026-11-06 autorizou M6, já
concluído. Novo `continue o projeto` em 2026-11-06 concluiu o escopo inicial de M4 (`WEB-013` a `WEB-016`). Em 2026-11-07, a missão documental `CHG-005` ([ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md)) revisou formalmente `DEC-01` e expandiu `M4` (`WEB-045`, `WEB-046`) e `M5` (`WEB-047`), além de atualizar `M5`, `M7`, `M8`, `M9` e `M10`. Em 2026-11-07, instrução explícita do responsável formalizou no workflow do projeto a adoção de Pull Request, Push e Merge Commit tradicional, e autorizou a execução do marco **M5** (`WEB-017` e `WEB-018`). Em 2026-11-08, o PR #4 (`feat/m5-interface-administrativa-react`) entregou a navegação modular e painéis base (`EV-M5-047-NAV`); o PR #5 (`feat/m5-filtros-kpis-administracao`) entregou o catálogo de filtros combinados e administração React (`EV-M5-017/018`); o PR #6 (`feat/m5-crud-pacientes-avaliadores-vinculos`) entregou o CRUD completo de pacientes e avaliadores (`EV-M5-047`); o PR #8 (`feat/m5-detalhes-resultados-metricas`) entregou detalhe, métricas e análises descritivas (`EV-M5-019`); e o PR #10 (`feat/m5-exportacoes-csv-filtradas`) entregou as exportações CSV multi-granularidade (`EV-M5-020`), concluindo integralmente o marco M5 (5/5). Em 2026-11-08, a missão documental **CHG-006** ([ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md)) formalizou o replanejamento da interface profissional e do pipeline de sessões em 3 eixos fundamentais inspirados no Streamlit e no PsychoPy Runner, preparando a validação de transição em M7.

Em 2026-11-11, novo `continue o projeto` autoriza M8 e suas tarefas prontas e sucessoras, preservando a proibição específica de merge do PR #18 e os gates externos de WEB-031.

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

Progresso atual: **37/56 entregáveis aceitos (WEB-000 a WEB-028, WEB-029/030, WEB-042/043/044, WEB-045/046 e WEB-047)**.
WEB-005 é documental; WEB-006 aceita o receptor backend e contratos em banco
sintético. M1, M2, M3, M4, M5, M6 e M7 concluídos; atomicidade e paridade aceitas em EV-M2-007/008;
autenticação local e revisão de segurança aceitas em EV-M6-021/024; M4 integralmente concluído (6/6);
M5 concluído (5/5 aceitos); M7 concluído (4/4 aceitos), com retirada de upload CSV do produto
(WEB-025, EV-M7-025), roundtrip 21 colunas e SQLite (WEB-026, EV-M7-026), vínculo explícito e auditado
de legados sem merge automático (WEB-027, EV-M7-027), e cobertura operacional em 3 eixos (WEB-028, EV-M7-028).

## Painel visual de acompanhamento

Atualizado em **2026-11-12**, a partir das fichas deste backlog.

| Entregáveis aceitos | Ainda sem aceite | Marco autorizado | Próxima ação |
|---|---|---|---|
| **37 de 56 · 66,1%** | **19** | **M8 em execução (2/12 aceitos)** | WEB-050: completar catálogo e UX7-AA; WEB-048 pronta; WEB-031 bloqueada |

```text
Aceites   █████████████░░░░░░░   66,1%
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
| [M3](#m3--viabilidade-e-motor-experimental-no-navegador) | Viabilidade e motor experimental no navegador | 🟩🟩🟩🟩🟩🟩🟩 **7/7** | ✅ Concluído |
| [M4](#m4--fluxo-ponta-a-ponta-de-avaliações) | Fluxo ponta a ponta de avaliações | 🟩🟩🟩🟩🟩🟩 **6/6** | ✅ Concluído |
| [M5](#m5--interface-administrativa-e-analítica-react) | Interface administrativa e analítica React | 🟩🟩🟩🟩🟩 **5/5** | ✅ Concluído |
| [M6](#m6--autenticação-permissões-e-segurança) | Autenticação, permissões e segurança | 🟩🟩🟩🟩 **4/4** | ✅ Concluído |
| [M7](#m7--integração-compatibilidade-histórica-e-transição) | Integração, compatibilidade histórica e transição | 🟩🟩🟩🟩 **4/4** | ✅ Concluído |
| [M8](#m8--ci-infraestrutura-e-preparação-operacional) | CI, infraestrutura e preparação operacional | 🟩🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ **2/12** | ◐ Parcial; CHG-007, réplica externa e release pendentes |
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
| ✅ [WEB-010](#web-010--revalidar-plugins-jspsych-ciclo-de-vida-e-janela-de-resposta) | Plugins, ciclo de vida e regras de resposta/interrupção | jsPsych real, StrictMode, testes de teclado e navegadores visíveis; suporte restrito aceito separadamente em WEB-012 |
| ✅ [WEB-011](#web-011--executar-campanha-de-engenharia-temporal-em-ambientes-declarados) | Campanha local de engenharia com transporte ativo | Vinte capturas completas, dez por navegador, uma falha de preparação preservada; API double, sem latência física |
| ✅ [WEB-012](#web-012--registrar-viabilidade-e-limites-de-suporte-do-motor) | Viabilidade técnica local e limites do motor | Campanha EV-M3-011 e aceite explícito do responsável em EV-M3-012-ACEITE |
| ✅ [WEB-013](#web-013--integrar-preparação-profissional-e-identificação-por-convite) | Preparação profissional com login local, convite único, múltiplas visitas/avaliações e isolamento | React/FastAPI/PostgreSQL/HTTPS reais em Chromium e Firefox |
| ✅ [WEB-014](#web-014--validar-instruções-prática-e-início-principal-no-fluxo-real) | Instruções sem coleta nominal/demográfica, prática repetível sem precisão agregada e início principal | Vitest, Playwright browser e fluxo HTTPS/API/PG reais |
| ✅ [WEB-015](#web-015--ensaiar-envio-falhas-de-rede-e-recuperação-de-recibo) | Dedicated Worker incremental integrado, prefixo parcial em interrupção, invalidação tardia e estados de recibo | Vitest, Python/PG e E2E HTTPS/API/PG reais em Chromium e Firefox |
| ✅ [WEB-016](#web-016--aceitar-avaliação-completa-com-consulta-persistida) | Avaliação completa com 16 tentativas, 12 métricas, recibo, logout participante e consulta protegida | E2E HTTPS/API/PG reais em Chromium e Firefox e testes Python/PG |
| ✅ [WEB-042](#web-042--refinar-estímulos-e-hierarquia-visual-experimental) | Palavras com contorno branco sem cartão e centro preservado | DOM, dez cores/screenshots Chromium/Firefox e regressão funcional |
| ✅ [WEB-043](#web-043--reformular-hud-e-retirar-precisão-agregada-do-participante) | HUD sem precisão, progresso real e cronômetro estável | DOM/árvore acessível, unidade e navegadores; gates de campanha separados |
| ✅ [WEB-044](#web-044--validar-regressão-da-apresentação-experimental-refinada) | Regressão consolidada visual, funcional, métricas/CSV e observação temporal preparatória | Testes e fluxos consolidados; campanha WEB-011 aceita, suporte WEB-012 separado |
| ✅ [WEB-045](#web-045--modelar-e-implementar-fundação-de-cadastros-centrais-de-pacientes-e-avaliadores-e-vínculos-de-preparação) | Cadastros centrais de pacientes e avaliadores, códigos PAT/EVA automáticos, homônimos, auditoria e vínculos | PostgreSQL real sintético, migration 0014, grants e rotas HTTP |
| ✅ [WEB-046](#web-046--integrar-formulário-completo-de-preparação-da-avaliação-com-seleção-cadastral-e-conferência) | Formulário completo de preparação com seleção/cadastro inline, resumo para conferência e fluxo ponta a ponta | Vitest, Python/PG e Playwright HTTPS/API/PG reais em Chromium e Firefox |
| ✅ [WEB-017](#web-017--revalidar-filtros-lista-e-agregações-autorizadas) | Catálogo completo de filtros combinados (REQ-REL-004) e KPIs descritivos na Visão Geral | Vitest, DOM e Playwright Chromium e Firefox reais |
| ✅ [WEB-018](#web-018--revalidar-administração-react-de-contas-e-vínculos) | Administração React de contas e vínculos com distinção arquitetural explícita ADR-006/007 | Vitest, API e Playwright administrativo |
| ✅ [WEB-047](#web-047--implementar-crud-administrativo-completo-de-pacientes-e-avaliadores-histórico-longitudinal-e-correção-auditada-de-vínculos) | CRUD de pacientes e avaliadores, histórico longitudinal e correção auditada de vínculos | Vitest, Python/PG e Playwright HTTPS/API/PG reais em Chromium e Firefox |
| ✅ [WEB-020](#web-020--conferir-exportação-do-conjunto-filtrado-no-react) | Exportação CSV multi-granularidade filtrada | Interface React, API e PostgreSQL real sintético |
| ✅ [WEB-021](#web-021--implementar-autenticação-local-e-integrar-login-profissional-seguro) | Autenticação profissional local com Argon2id, sessões, rotação/recuperação e corte OIDC | React/FastAPI/PG/HTTPS reais, Compose isolado e restore com recuperação |
| ✅ [WEB-022](#web-022--comprovar-matriz-de-perfis-projetos-e-revogações) | Perfis, projetos, administração sem vínculo e revogação | PostgreSQL real sintético, API e HTTPS |
| ✅ [WEB-023](#web-023--revalidar-sessão-cookies-csrf-e-isolamento-de-credenciais) | Sessões separadas, Origin/CSRF, expiração, logout e replay | PostgreSQL/API e navegadores em HTTPS local |
| ✅ [WEB-024](#web-024--concluir-revisão-de-segurança-com-evidências-negativas) | Revisão de segurança com evidências negativas AUTH-L01–L09 e regressões de M6 | Testes negativos HTTP/PG/HTTPS, scanner, auditorias, Compose e restore |
| ✅ [WEB-029](#web-029--revalidar-imagens-e-compose-isolado-em-https) | Imagens, Compose/HTTPS, saúde, headers, isolamento e recusa de fontes | Build/proxy/API/PostgreSQL reais em pilha sintética isolada |
| ✅ [WEB-030](#web-030--reproduzir-pipeline-e-definir-validação-formal-sem-pr-automático) | Pipeline integral local e Actions por SHA; procedimento sem PR | Scanner/auditorias, PG, frontend, navegadores e HTTPS reais |
| ✅ [WEB-025](#web-025--revalidar-importação-minimizada-e-status-idempotente) | Retirada de upload CSV da UI e bloqueio 410 no modo produto (EXP-CSV-01) | Vitest, Playwright browser/integrated e API/PostgreSQL |
| ✅ [WEB-026](#web-026--comprovar-intercâmbio-histórico-por-fixtures-sintéticas) | Roundtrip de exportação canônica 21 colunas e granularidades com analisador Python e SQLite | Testes sintéticos com analisar_stroop.py e import_sqlite |
| ✅ [WEB-027](#web-027--revalidar-vínculo-explícito-de-dados-legados) | Vínculo explícito auditado de legados a cadastros centrais sem merge automático | web_legacy_entity_links e web_registry_audit_events no PostgreSQL |
| ✅ [WEB-028](#web-028--revisar-cobertura-e-plano-de-substituição-operacional) | Cobertura operacional em 3 eixos (ADR-008/CHG-006) e paridade com Streamlit/PsychoPy | ADR-008, TRANSICAO_WEB.md e preservação total de launchers/CLIs |

### Foco do marco atual

Novo `continue o projeto` de **2026-11-11** autoriza **M8 — CI, infraestrutura e
preparação operacional**, com 2/12 aceitos. WEB-050 está EM_ANDAMENTO; WEB-048
PRONTA. A preparação de WEB-031 continua bloqueada por destino externo/custódia
não autorizados; isso impede WEB-032 e o encerramento de M8, sem bloquear
CHG-007 independente. M7 permanece integralmente aceito (4/4). PR #18 deve
permanecer aberto sem merge, inclusive por ancestralidade de outra branch.

| ✅ Aceito | ✅ Aceito | ✅ Aceito | ✅ Aceito |
|---|---|---|---|
| [WEB-025](#web-025--revalidar-importação-minimizada-e-status-idempotente): retirada upload CSV | [WEB-026](#web-026--comprovar-intercâmbio-histórico-por-fixtures-sintéticas): roundtrip 21 colunas/SQLite | [WEB-027](#web-027--revalidar-vínculo-explícito-de-dados-legados): vínculo auditado legados | [WEB-028](#web-028--revisar-cobertura-e-plano-de-substituição-operacional): paridade 3 eixos |

M1, M2, M3, M4, M5, M6 e M7 permanecem 100% concluídos. M8 com 2/12 aceitos (WEB-029/030), após ampliação CHG-007.

**Acompanhar impedimentos:** [riscos](#registro-de-riscos) ·
[decisões externas](#decisões-externas-e-condições-de-desbloqueio).
**Acompanhar a continuidade:** [Retomada](#retomada), com próxima ação, Git e limites.

Este painel integra o backlog canônico. Ao registrar um novo aceite, atualizar
os totais, barras e tabelas desta seção junto com as fichas e a Retomada;
validar que as contagens continuam correspondendo aos estados das tarefas.

## Ordem, caminho crítico e paralelismo

Prioridade inicial: WEB-001 → WEB-002/003 → WEB-004. Depois M2 e M3 podem seguir
em paralelo, e M8 pode preparar pilha isolada. M6 depende de M2 e antecede M4.
Caminho crítico de integração: M0 → M1 → M2 → M6 → M4 (WEB-013..016 → WEB-045 → WEB-046) → M5 (WEB-017/018/047 → WEB-019 → WEB-020) → M7 (WEB-025 → WEB-026 → WEB-027 → WEB-028) → M8(gate final WEB-032)
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

Ramo CHG-007 em M8 (somente após nova autorização): WEB-048 → WEB-049;
WEB-050 → WEB-051; WEB-048/049/050/051 → WEB-052 e WEB-053;
WEB-049 → WEB-054; WEB-052/053/054 → WEB-055 → WEB-032 → WEB-035 → WEB-036.
WEB-031 segue ramo externo independente e converge em WEB-032. WEB-050/051/053
(P0: integridade/autorização) antecedem o aceite visual integrado; não há RC
apenas com redesign. WEB-048/050 são PRONTAS, não autorizadas a implementar nesta
missão. M9 rehomologa a candidata; M10 atualiza documentação da interface final.

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

- Marco: M3. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-010, WEB-044; DEC-04 para matriz.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: 10 execuções sintéticas por ambiente selecionado, trilhas brutas/falhas preservadas, quadro e desvio total conferidos contra D5; sem substituir falha por rerun omitido. CHG-002: incluir transporte incremental ativo, ACK lento/perdido, retries e falha de servidor, sem alongar tentativas; comparar impacto contra D5. CHG-003: campanha na SHA do layout final aprovado, com contorno branco uniforme, sem retângulo/precisão agregada, progresso/cronômetro revisados e transporte incremental ativo. Registrar custo observado de renderização/HUD/retries; campanha somente no visual anterior não basta. Limites D5 e tolerâncias intactos.
- Testes/verificação: `web/pilots/web011.spec.ts`, configuração `playwright.web011.config.ts`, fila/worker reais; campanha serial visível, 20 capturas completas aprovadas por D5 e domínio Python, uma falha original sem trilha preservada no relatório Playwright, suplemento explícito sem apagar a falha. Regressão: 292 Vitest, 51 Python, tipos/build e 6 Playwright visuais aprovados.
- Evidências: EV-M3-011, 2026-11-05/06, SHA 78f8120; suplemento 4d5ab56 altera somente diagnóstico da fixture, com motor/worker idênticos. Critérios conferidos no relatório abaixo. Sem integração HTTPS/API/PG ou medição física.
- Riscos/bloqueios: R01/R02/R11. DEC-04 desbloqueada para engenharia local pela resposta explícita do proprietário em 2026-11-05; matriz identificada em EV-M3-011. Não aprova validação física/metodológica M9, suporte ou redução de gates. WEB-012 depende da campanha e decisão de suporte.
- Referências: REQ-EXP-003; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-001 a REQ-UX-007; R11.
- Git da entrega: branch `feat/m3-motor-experimental`, implementação `78f8120bd40869cdbb9d234cd9e4600ad91dcb96`, diagnóstico `4d5ab56bec47a9d4885e48a20e3871f9e036e925`; envio/CI no fechamento EV-M3-011.

### WEB-012 — Registrar viabilidade e limites de suporte do motor

- Marco: M3. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-011.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Relatório técnico discrimina automação/latência física e ambientes não medidos; responsável aceita suporte ou bloqueia motor; M3 atendido sem equivalência presumida. CHG-002: discriminar impacto medido do transporte e janela de perda observada, sem promessa de perda zero. CHG-003: aceite explicita apresentação visual e HUD suportados, versão e limitações da campanha final; nenhum suporte herdado de screenshots antigos.
- Testes/verificação: relatório EV-M3-012 confronta campanha EV-M3-011, referência preparatória EV-M3-044, D5 e ADR-005; aprovação documental do alcance não substitui aceite do suporte observado.
- Evidências: EV-M3-012, 2026-11-06; relatório e limites aceitos explicitamente pelo responsável em 2026-11-06, resposta “aceito”; conferência dos critérios e fechamento em EV-M3-012-ACEITE.
- Riscos/bloqueios: R01/R02/R11 abertos. Aceite restrito à matriz observada; falhas históricas e perda de sufixo pendente preservadas. Integração M4 e validação física/metodológica M9 mantêm gates próprios.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md). CHG-003; R11.
- Git da entrega: branch `feat/m3-motor-experimental`; relatório identificável por `git log -1 --format=%H --grep="docs: registra campanha DEC-04 e limites de suporte"`; envio/CI no fechamento EV-M3-011.
- CHG-004 (histórico da revisão documental): Sem mudança de estado/aceite: exige decisão explícita sobre os resultados e limites de EV-M3-012. Login local não comprova viabilidade, timing físico ou validade metodológica.
- Git do aceite: branch `docs/m3-aceite-suporte`, base `9979b64`; entrega identificável por `git log -1 --format=%H --grep="docs: registra aceite de suporte e encerra M3"`; envio/CI na Retomada vigente.

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

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-009, WEB-010; revisão D3/D4 aprovada explicitamente pelo proprietário nesta missão em 2026-11-05, variante stroop-web-outline/1.0.0.
- Responsável: Codex na execução; proprietário aprovou apresentação, HUD e identificação visual; nenhuma aprovação atribuída a terceiro.
- Critérios de aceite: Remover retângulo branco sem caixa substituta; contorno branco uniforme por token com tinta das dez cores/fundo/tipografia preservados. Avaliar stroke e alternativa compatível; centro geométrico inalterado e HUD periférico sem deslocamento. Nenhuma mudança em condições, tempos, ordem, escala por responsividade ou cores. Registrar versão aprovada e screenshots sintéticos de todas as cores em Chromium/Firefox e resoluções permitidas.
- Testes/verificação: web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts e fluxos main.spec.ts/practice.spec.ts. Comandos/resultados, screenshots e limites em EV-M3-042/043.
- Evidências: EV-M3-042/043, 2026-11-05; critérios funcionais/visuais desta ficha comprovados em testes e inspeção de screenshots. Nenhum aceite de WEB-044/011/012 ou M3 por implicação.
- Riscos/bloqueios: R01/R02/R11 abertos; gate de apresentação satisfeito pela aprovação explícita do proprietário, que já responde pela pesquisa/validação/operação. WEB-009/010 concluídas. DEC-04 continua pendente para campanha/suporte; não bloqueia esta implementação. Sem exigência documentada de aprovador distinto.
- Referências: REQ-UX-001/002/007; UX-01/05; componentes main-engine.ts/practice-engine.ts e tokens visuais existentes. [UX](experimento/UX_DECISIONS.md); CHG-003.
- Git da entrega: feat/m3-motor-experimental, base 3d9d515; SHA, push e CI no fechamento EV-M3-042/043. Fonte e testes validados juntos.

### WEB-043 — Reformular HUD e retirar precisão agregada do participante

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-009, WEB-010; revisão D3/D4 aprovada explicitamente pelo proprietário nesta missão em 2026-11-05, variante stroop-web-outline/1.0.0.
- Responsável: Codex na execução; proprietário aprovou apresentação, HUD e identificação visual; nenhuma aprovação atribuída a terceiro.
- Critérios de aceite: Remover nós, barras, percentuais, rótulos, tooltips e equivalentes de desempenho na prática/principal, sem resíduo na árvore acessível/espaçamento. Não substituir por ranking/taxa de erros. Preservar feedback individual da prática, cálculos oficiais e métricas. Progresso fino/discreto deriva etapa/total e tentativas concluídas do contrato, sem números fixos/animação. Cronômetro decorrido MM:SS/tabular/largura estável usa origem monotônica existente; sem relógio React, timer duplicado, deriva ou alteração de RT. Não criar relógio de prática por inferência.
- Testes/verificação: web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts e fluxos main.spec.ts/practice.spec.ts. Comandos/resultados, screenshots e limites em EV-M3-042/043.
- Evidências: EV-M3-042/043, 2026-11-05; critérios funcionais/visuais desta ficha comprovados em testes e inspeção de screenshots. Nenhum aceite de WEB-044/011/012 ou M3 por implicação.
- Riscos/bloqueios: R01/R02/R11 abertos; gate de apresentação satisfeito pela aprovação explícita do proprietário, que já responde pela pesquisa/validação/operação. WEB-009/010 concluídas. DEC-04 continua pendente para campanha/suporte; não bloqueia esta implementação. Sem exigência documentada de aprovador distinto.
- Referências: REQ-UX-003/004/005/006; UX-02/03/04; componentes main-engine.ts/practice-engine.ts, protocol.ts e summary.ts (preservado). [UX](experimento/UX_DECISIONS.md); CHG-003.
- Git da entrega: feat/m3-motor-experimental, base 3d9d515; SHA, push e CI no fechamento EV-M3-042/043. Fonte e testes validados juntos.

### WEB-044 — Validar regressão da apresentação experimental refinada

- Marco: M3. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-042, WEB-043.
- Responsável: Codex na execução; aprovação visual do proprietário já registrada; gates DEC-04/M9 mantêm responsáveis e critérios próprios.
- Critérios de aceite: Conferir dez cores, contorno/tinta/ausência da caixa, centro/fonte/escala e HUD nas resoluções aprovadas em Chromium/Firefox com screenshots sintéticos. Ausência real de precisão em prática/principal, inclusive árvore acessível, sem espaço residual/substituto; feedback individual permanece. Progresso/cronômetro corretos, sem timers duplicados. Go/No-Go, congruência, quatro resultados, janelas, sequência, lifecycle, interrupções e versão preservados. Paridade das métricas/CSV em fixtures; persistência/relatórios/admin continuam gates reais WEB-016/019/020. Registrar observação temporal preparatória sem aprovar campanha WEB-011/DEC-04. CSS não comprova validade científica.
- Testes/verificação: npm test e npm run build (inclui typecheck); Playwright visual Chromium/Firefox e captura temporal Chrome/Firefox; tests/test_fase3_condicoes_tempos.py, tests/test_nucleo_compartilhado.py e tests/test_web_export.py. Fluxos completos de EV-M3-042/043 reutilizados; comandos, ambiente, resultados e SHA em EV-M3-044, apenas fixtures sintéticas.
- Evidências: EV-M3-044, 2026-11-05, SHA 5c355f7; 281 Vitest, 25 Python, tipos/build, seis visuais e duas capturas preparatórias aprovados. Fluxos completos de EV-M3-042/043 reutilizados após comprovar identidade de fontes/testes; critérios conferidos individualmente, sem aceite implícito de campanha/suporte.
- Riscos/bloqueios: R01/R02/R11; WEB-042/043 aceitas; regressão consolidada aceita nesta ficha; DEC-04 continua necessária para campanha/suporte, sem aprovação presumida.
- Referências: REQ-UX-001 a REQ-UX-007/011; REQ-EXP-001/002/003; main/practice/Host/summary e testes existentes; integração de métricas em M4/M5. [UX](experimento/UX_DECISIONS.md); CHG-003.
- Git da entrega: branch feat/m3-motor-experimental; fontes/testes ensaiados em 5c355f7; registro documental, push e CI no fechamento EV-M3-044. Sem alteração de runtime.

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

- Marco: M4. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-008, WEB-012, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Avaliador autorizado prepara/identifica sessão no React; código único, visita, revogação/expiração e isolamento comprovados com API/PG reais. CHG-002: múltiplas visitas e avaliações na mesma visita preservam UUIDs/vínculos, sem cadastro global ou agenda.
- Testes/verificação: `tests/test_web_sessions.py, tests/test_local_auth.py; web/e2e/integrated/invitations.spec.ts, web/e2e/integrated/sessions-security.spec.ts`. Executados sem skips em PG descartável e HTTPS/API/PG reais em Chromium e Firefox; ver `EV-M4-013/016`.
- Evidências: `EV-M4-013/016` (2026-11-06); preparação após login local, código de convite de uso único, múltiplas visitas (`T1`, `T2`), múltiplas avaliações na mesma visita, isolamento de pseudônimo entre projetos, revogação/expiração e credencial participante independente comprovados.
- Riscos/bloqueios: R05 permanece aberto como risco residual para marcos posteriores (M5/M7/M9/M10); nenhum impedimento aberto em M4.
- Referências: REQ-PAR-001, REQ-PAR-002, REQ-AVA-001, REQ-AVA-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `feat/m4-fluxo-avaliacoes`; entrega e fechamento registrados em `EV-M4-013/016`.
- CHG-004: Login local aceito em WEB-021/024 precede preparação e emissão de convite em `invitations.spec.ts`; AUTH-L04/L07 regressado com pseudônimos, visitas, expiração/revogação, isolamento entre projetos e credencial participante independente.

### WEB-014 — Validar instruções, prática e início principal no fluxo real

- Marco: M4. Prioridade: P1. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-013.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Textos sem coleta nominal/demográfica; prática repetível sem limiar, interrompida reinicia, início/principal usa sessão autorizada e snapshot correto. CHG-003: reorganizar instruções/tecla/confirmação e transições sem mudar semântica/estratégia; feedback individual e repetição opcional sem limiar mantidos, prática sem precisão agregada.
- Testes/verificação: `web/src/experiment/practice.test.ts, web/src/experiment/ExperimentHost.test.tsx, web/src/participant/ParticipantRun.test.ts, tests/test_web_security_review.py; web/e2e/practice.spec.ts, web/e2e/main.spec.ts, web/e2e/participant.spec.ts, web/e2e/integrated/participant.spec.ts`. Executados sem skips em Vitest, Python/PG e Chromium/Firefox; ver `EV-M4-013/016`.
- Evidências: `EV-M4-013/016` (2026-11-06); ausência de campos nominais/demográficos (`age`/`idade`/`sex`/`sexo`/`gender`/`birth`/`cpf`/`email`/`phone`) e de precisão agregada no DOM/árvore acessível durante prática e principal, repetição opcional sem limiar, reinício da prática interrompida, transições por teclado/foco sem disparo por tecla mantida e início do principal com sessão autorizada/ordem do snapshot comprovados.
- Riscos/bloqueios: R02 permanece aberto para validação física/metodológica (M9); nenhum impedimento aberto em M4.
- Referências: REQ-PAR-003; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-008/009, UX-06/07.
- Git da entrega: branch `feat/m4-fluxo-avaliacoes`; entrega e fechamento registrados em `EV-M4-013/016`.

### WEB-015 — Ensaiar envio, falhas de rede e recuperação de recibo

- Marco: M4. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-014.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Rede falha antes/depois de commit, retry, expiração, revogação e reload têm comportamento declarado; nenhuma confirmação sem recibo nem principal retomado. CHG-002: fila/worker/ACK, prefixo preservado em interrupção, incompletude sem aviso e invalidação tardia; nova sessão exige prática; mensagens distinguem parcial recebido de resultado oficial. CHG-003: distinguir concluído, aguardando envio, enviando, confirmado, falha, interrompido/inválido; não anunciar recebimento antes do recibo. Preservar ACK/replay, parciais sem resultado oficial, sem retomada; resultado individual somente autorizado pelo protocolo.
- Testes/verificação: `web/src/participant/ParticipantRun.test.ts, web/src/api/participant.test.ts, web/src/transport/checkpoint-queue.test.ts, tests/test_web_results.py, tests/test_web_checkpoints.py, tests/test_web_proxy_config.py; web/e2e/main.spec.ts, web/e2e/integrated/participant.spec.ts, web/e2e/integrated/complete-results.spec.ts`. Executados sem skips em Vitest, Python/PG e E2E HTTPS/API/PG reais em Chromium e Firefox; ver `EV-M4-013/016`.
- Evidências: `EV-M4-013/016` (2026-11-06); Dedicated Worker incremental (`checkpoint-worker.ts`) integrado ao `ParticipantRun` e `PracticePreparation`/`ParticipantFlow` com `worker-src 'self'` em `web/security-headers.json`, drain assíncrono em interrupção preservando prefixo parcial em `web_session_observations` sem criar `assessments`, invalidação tardia via `POST /api/v1/participant/session/invalidate`, reload/perda de foco abortando `running`, nova sessão exigindo prática e mensagens distinguindo observações parciais de recibo oficial comprovados.
- Riscos/bloqueios: R03 permanece aberto como risco residual de perda de sufixo não transmitido antes de queda abrupta conforme `ADR-005`; nenhum impedimento aberto em M4.
- Referências: REQ-AVA-003, REQ-INT-003; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-010; ADR-005.
- Git da entrega: branch `feat/m4-fluxo-avaliacoes`; entrega e fechamento registrados em `EV-M4-013/016`.

### WEB-016 — Aceitar avaliação completa com consulta persistida

- Marco: M4. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-015.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: E2E real confere 1 avaliação/16 tentativas/12 métricas e proveniência; logout limpa RAM e sessão, acesso cruzado nega; M4 aceito. CHG-002: sessão interrompida conserva observações e não gera resultado final; nenhuma mistura entre nova sessão e anterior. CHG-003: fluxo real sem precisão durante prática/principal conserva feedback individual, 12 métricas persistidas e separação das observações parciais; novo layout e estados de envio cobertos.
- Testes/verificação: `web/e2e/integrated/invitations.spec.ts, web/e2e/integrated/participant.spec.ts, web/e2e/integrated/complete-results.spec.ts, web/e2e/integrated/sessions-security.spec.ts, tests/test_web_participant_logout.py, tests/test_web_assessments.py`. Executados sem skips em PG descartável e E2E HTTPS/API/PG reais em Chromium e Firefox; ver `EV-M4-013/016`.
- Evidências: `EV-M4-013/016` (2026-11-06); avaliação completa ponta a ponta com login local, 16 checkpoints incrementais (`observations = 16`, `confirmed_through = 16`), 1 avaliação oficial, 16 tentativas principais, 12 métricas oficiais, `app_version` `web-0.1.0+visual.1.0.0`, logout participante limpando RAM/cookie e recusando replay, negação de acesso cruzado e exclusão de sessões interrompidas/invalidadas dos resultados oficiais comprovados. M4 aceito (4/4).
- Riscos/bloqueios: R03 e R05 permanecem abertos como riscos residuais para marcos posteriores; nenhum impedimento aberto em M4.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md). REQ-UX-005/006/008/009/010.
- Git da entrega: branch `feat/m4-fluxo-avaliacoes`; entrega e fechamento registrados em `EV-M4-013/016`.
- CHG-004: Login profissional local e consulta protegida integrados no E2E real sem alterar persistência incremental, recibo, interrupções ou 12 métricas; AUTH-L07 comprovado.

### EV-M4-013/016 — fluxo ponta a ponta, transporte incremental e aceitação M4, 2026-11-06

Autorização: comando canônico `continue o projeto` no marco vigente **M4**
(após M2, M3 e M6 aceitos), executando todas as tarefas prontas e encadeadas do
marco (`WEB-013`, `WEB-014`, `WEB-015` e `WEB-016`) na branch
`feat/m4-fluxo-avaliacoes` (base `7e77ef8127c20d5af255969d93a20d4116f8a247`) e
encerrando no limite de M4 sem avançar implicitamente a M5.

Entregas técnicas e de integração consolidadas nesta sessão:

1. **Integração do Dedicated Worker incremental no fluxo real do participante (`WEB-015` / `ADR-005`)**:
   - `web/src/participant/ParticipantRun.ts`, `web/src/components/PracticePreparation.tsx`
     e `web/src/components/ParticipantFlow.tsx` integram `prepareCheckpointWorker`
     ao início do bloco principal (`start()`) e encaminham cada tentativa principal
     concluída via `onMainTrialComplete={(trial, framePeriod) => run.recordTrial(trial, framePeriod)}`
     para o Dedicated Worker (`web/src/transport/checkpoint-worker.ts`).
   - `ParticipantRun.start()` dispara `startParticipant` de forma síncrona (preservando
     o vínculo imediato de `AbortSignal`) e aguarda a preparação do worker antes de
     habilitar `engineStarted = true` e `phase: 'main'`, falhando fechado sem
     degradar para envio final apenas em RAM.
   - `web/src/transport/checkpoint-queue.ts` aceita `state: 'preparing' | 'running'`
     com `confirmed_through === 0` e `expires_at` coincidente na sondagem de
     prontidão do worker, permitindo retry idempotente quando `POST /api/v1/participant/start`
     já transitou a sessão para `running`.
   - `web/src/transport/checkpoint-worker.ts` realiza drain assíncrono (`dispose(true)`)
     ao interromper o bloco principal, aguardando o envio do prefixo já concluído
     antes de encerrar o Dedicated Worker.
   - `web/security-headers.json` atualiza a diretiva CSP de `worker-src 'none'`
     para `worker-src 'self'`, autorizando exclusivamente Dedicated Workers da
     mesma origem (`ADR-005` item 2) no proxy HTTPS e mantendo bloqueados workers
     externos/`blob:`.
2. **Invalidação tardia e distinção explícita entre observações parciais e recibo oficial (`WEB-015` / `CHG-002` / `CHG-003`)**:
   - `web/src/api/client.ts` e `web/src/api/participant.ts` adicionam
     `invalidateParticipant` (`POST /api/v1/participant/session/invalidate` com
     `keepalive: true`, cabeçalho `X-CSRF-Token` e validação estrita do recibo
     `state: 'invalidated'`), integrado a `ParticipantRun.invalidate(...)` e ao
     fallback de `abort` em conflito `409`.
   - `web/src/api/participant.ts`, `web/src/participant/ParticipantRun.ts` e
     `web/src/components/ResultSummary.tsx` distinguem explicitamente observações
     parciais (`web_session_observations`), resultado pendente de confirmação e
     recibo oficial (`state: 'completed'`), vedando retomada do bloco principal
     (`D2`) e exigindo nova sessão com prática.
3. **Cobertura ponta a ponta com login local, múltiplas visitas/avaliações, ausência de precisão/demografia e consulta persistida (`WEB-013`, `WEB-014`, `WEB-015`, `WEB-016`)**:
   - `web/e2e/practice.spec.ts` e `web/e2e/main.spec.ts` verificam ausência de
     campos nominais/demográficos (`age`/`idade`/`sex`/`sexo`/`gender`/`birth`/`cpf`/`email`/`phone`)
     e de precisão agregada no DOM e na árvore acessível durante a prática e o
     bloco principal, além dos 16 checkpoints enviados ao worker em `main.spec.ts`.
   - `web/e2e/integrated/invitations.spec.ts` autentica o profissional pelo
     formulário real de login local em `/equipe` (`CHG-004` / `AUTH-L07`),
     confere `observations = 16`, `confirmed_through = 16` e
     `app_version = 'web-0.1.0+visual.1.0.0'`, e adiciona cenário cobrindo
     múltiplas visitas (`T1`, `T2`), múltiplas avaliações na mesma visita,
     isolamento de pseudônimo entre projetos e independência entre credenciais
     profissional e participante.
   - `web/e2e/integrated/participant.spec.ts` confere os 16 checkpoints
     confirmados pelo Dedicated Worker no fluxo completo e adiciona cenário de
     interrupção no meio do bloco principal (após 2 tentativas concluídas + perda
     de foco na 3ª), comprovando `state = 'aborted'`, `observations = 2`
     preservadas em `web_session_observations`, `assessments = 0` na consulta
     profissional e exigência de nova prática ao iniciar nova sessão para a mesma
     visita.

Ambiente observado nesta sessão: Linux `7.0.0-42-generic` x86_64, Python `3.12.3`,
Node `24.15.0`, npm `11.16.0`, Docker `29.9.2`, PostgreSQL `17.6-bookworm`
(`sha256:f3bd19c606e442c3d7bdfa8002e03fe260a1023351e0ea4598032022b68dd6e3`)
em container descartável `stroop_etapa4_test_m4` (tmpfs, porta `127.0.0.1:55439`,
banco `stroop_etapa4_test_m4`, removido ao final), Playwright `1.64.1`,
Chromium `156.0.8078.4` e Firefox `157.0`. Nenhum container preexistente, dado
real ou arquivo `.env` operacional foi tocado.

Comandos executados e resultados reais (0 skips em todas as suítes):

- `npm --prefix web test && npm --prefix web run build`:
  **303/303 testes Vitest aprovados em 19 arquivos** (2,95 s), `tsc --noEmit` e
  `vite build` (598 ms, gerando bundle do Dedicated Worker
  `dist/assets/checkpoint.worker-DokVT_sh.js`) aprovados.
- `TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55439/stroop_etapa4_test_m4" PYTHONPATH=. .venv/bin/python -m unittest tests.test_web_sessions tests.test_web_results tests.test_web_checkpoints tests.test_web_participant_logout tests.test_web_assessments tests.test_web_auth -v`:
  **92 aprovados em 64,234 s**, 0 falhas, 0 skips.
- `TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55439/stroop_etapa4_test_m4" PYTHONPATH=. .venv/bin/python -m unittest tests.test_local_auth -v`:
  **17 aprovados em 16,593 s**, 0 falhas, 0 skips.
- `PYTHONPATH=. .venv/bin/python -m unittest tests.test_web_proxy_config -v`:
  **6 aprovados em 0,049 s**, 0 falhas, 0 skips.
- Em `web`: `npx playwright test e2e/participant.spec.ts e2e/practice.spec.ts e2e/navigation.spec.ts e2e/w09a-review.spec.ts`:
  **32/32 aprovados em 1,4 min** (Chromium e Firefox), 0 falhas, 0 skips.
- Em `web`: `npx playwright test e2e/main.spec.ts --workers=1 --trace=off`:
  **4/4 aprovados em 3,6 min** (Chromium e Firefox), 0 falhas, 0 skips.
- Em `web`: `TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55439/stroop_etapa4_test_m4" npx playwright test --config playwright.integration.config.ts e2e/integrated/complete-results.spec.ts e2e/integrated/sessions-security.spec.ts`:
  **4/4 aprovados em 29,2 s** (Chromium e Firefox), 0 falhas, 0 skips.
- Em `web`: `TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55439/stroop_etapa4_test_m4" npx playwright test --config playwright.integration.config.ts e2e/integrated/invitations.spec.ts e2e/integrated/participant.spec.ts`:
  **20/20 aprovados em 10,8 min** (10 cenários por navegador em Chromium e
  Firefox), 0 falhas, 0 skips.

Falhas intermediárias preservadas nesta sessão:
- Primeira tentativa de subir container PostgreSQL descartável na porta `55432`
  recusou bind por porta já alocada no loopback; container recriado na porta
  livre `55439` (`stroop_etapa4_test_m4`) e removido após os ensaios.
- Primeira invocação `npx --prefix web playwright test ...` a partir da raiz do
  repositório falhou imediatamente porque o Playwright resolveu o diretório de
  trabalho na raiz sem carregar `web/playwright.config.ts` (`baseURL` e
  `webServer`); corrigido executando a partir de `cd web && npx playwright test ...`
  e removendo o diretório vazio `test-results/` criado na raiz.
- Primeira invocação de `tests.test_web_local_auth` falhou com `ModuleNotFoundError`
  porque o módulo canônico chama-se `tests.test_local_auth`; executado
  `tests.test_local_auth` (17/17 aprovados).
- Primeira execução integrada de `e2e/integrated/invitations.spec.ts` teve
  **1 falha** no primeiro teste (`Preparando a execução.` não avançou para o
  estímulo principal) porque `web/security-headers.json` continha
  `worker-src 'none'`, fazendo o proxy HTTPS bloquear a instanciação do
  Dedicated Worker (`new Worker(...)`) por CSP e o `ParticipantRun.start()`
  falhar fechado conforme projetado. Atualizado `worker-src 'none'` para
  `worker-src 'self'` em `web/security-headers.json`, validado em
  `tests.test_web_proxy_config` (6/6) e na suíte integrada completa
  (`invitations.spec.ts` + `participant.spec.ts`: **20/20 aprovados** em
  Chromium e Firefox).

Conferência de todos os critérios de `WEB-013`, `WEB-014`, `WEB-015`, `WEB-016`
e do escopo inicial de `M4`: todos comprovados. `WEB-013`, `WEB-014`, `WEB-015` e `WEB-016`
passam a `CONCLUIDA` (`EV-M4-013/016`). Com a expansão `CHG-005` (2026-11-07), `M4` recebe `WEB-045` (`PRONTA`) e `WEB-046` (`PENDENTE`) para implementar os cadastros centrais fundamentais de pacientes e avaliadores e o formulário completo de preparação da sessão antes de avançar para `M5`.
Git, envio e CI registrados no fechamento da Retomada correspondente.

### WEB-045 — Modelar e implementar fundação de cadastros centrais de pacientes e avaliadores e vínculos de preparação

- Marco: M4. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-016, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Migration aditiva `0014_central_patients_evaluators.sql` (sem reescrever `0001`–`0013`) criando `web_patients`, `web_evaluators`, `web_registry_audit_events` e `web_legacy_entity_links`, além de colunas aditivas `patient_id` e `evaluator_uuid` (`ON DELETE RESTRICT`) em `web_project_participants`, `web_invitations` e `web_assessments`; geração automática e livre de colisão de `id UUID` e códigos estáveis `participant_code` (`PAT-...`) e `evaluator_code` (`EVA-...`); validação de `full_name` (2–120 chars) e `initials` (0–16 chars); busca normalizada e prevenção de duplicidade/homônimos (`409 duplicate_candidate_found` sem `confirm_homonym=true`); separação estrita entre conta local compartilhada de autenticação (`issued_by`) e avaliador responsável (`evaluator_uuid`); proibição de `DELETE` físico pelo runtime (`active=false` para inativação lógica); preservação de registros históricos anteriores a `CHG-005`.
- Testes/verificação: `tests/test_web_patients.py, tests/test_web_evaluators.py, tests/test_postgres_migrations.py, tests/test_web_database_provision.py e tests/test_web_sessions.py com PostgreSQL descartável stroop_etapa4_test_m4_chg005 (CAD-01, CAD-02, CAD-03 e PREP-01 aprovados sem skips)`.
- Evidências: `EV-M4-045/046` (2026-11-07).
- Riscos/bloqueios: R05, R06, R07, R12, R13; revisão formal de `DEC-01` aprovada pelo proprietário em `CHG-005` (`ADR-007`). Uso com pessoas reais permanece bloqueado até `DEC-03`/`WEB-033`.
- Referências: REQ-PAR-004, REQ-AVA-004, REQ-INF-001, REQ-AUD-001; [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), [modelo de dados](dados/MODELO_DE_DADOS.md), [contrato HTTP](desenvolvimento/CONTRATO_API_WEB.md).
- Git da entrega: branch `feat/m4-fluxo-avaliacoes`; envio e CI registrados no fechamento de `EV-M4-045/046`.

### WEB-046 — Integrar formulário completo de preparação da avaliação com seleção cadastral e conferência

- Marco: M4. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-045.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Formulário de preparação da avaliação em React e API recuperando integralmente os campos pertinentes do formulário original do PsychoPy Builder (`project`, `participant_id` automático via seleção de paciente, `participant_name`, `initials`, `visit`, `evaluator` via seleção de avaliador responsável e `test_code`); possibilidade de selecionar paciente/avaliador existente com busca e alerta de homônimos ou cadastrar inline sem digitar IDs internos manualmente; pré-preenchimento de dados cadastrados evitando dupla digitação; metadados técnicos (`assessment_id`, `session_id`, `invitation_id`, `assessment_date`, `started_at`, `test_version`, `protocol_id`, `app_version`) mantidos automáticos e não editáveis; etapa explícita de **resumo para conferência** antes de emitir o convite; preservação integral do convite de uso único, sessão de 30 min, prática, interrupção D2, persistência incremental por Dedicated Worker (`ADR-005`), recibo e 12 métricas oficiais, sem expor dados nominais no bootstrap do participante.
- Testes/verificação: `tests/test_web_sessions.py, web/src/api/sessions.test.ts, web/src/components/SessionInvitation.test.tsx, web/e2e/invitations.spec.ts e web/e2e/integrated/invitations.spec.ts + participant.spec.ts em Chromium e Firefox (PREP-01 e E2E-FLOW-01 aprovados sem skips)`.
- Evidências: `EV-M4-045/046` (2026-11-07).
- Riscos/bloqueios: R03, R05, R12, R13; depende de `WEB-045`.
- Referências: REQ-AVA-005, REQ-PAR-004, REQ-AVA-004, REQ-AVA-001, REQ-AVA-002; [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), [UX](experimento/UX_DECISIONS.md).
- Git da entrega: branch `feat/m4-fluxo-avaliacoes`; envio e CI registrados no fechamento de `EV-M4-045/046`.

### EV-M4-045/046 — cadastros centrais de pacientes e avaliadores, preparação completa com conferência e encerramento M4 (6/6), 2026-11-07

Autorização: comando canônico `continue o projeto` (2026-11-07) no marco vigente
**M4**, executando as tarefas prontas e encadeadas `WEB-045` e `WEB-046` na
branch `feat/m4-fluxo-avaliacoes` (base `cdbd195a191fb4d042665c8bf3ba79ea693f1c3c`)
e encerrando no limite do marco **M4 (6/6)** sem avançar implicitamente a **M5**.

Entregas técnicas e de integração consolidadas nesta sessão:

1. **Migration aditiva `0014_central_patients_evaluators.sql` e provisionamento de papéis (`WEB-045` / `ADR-007` / `CAD-01`)**:
   - `scripts/migrations/0014_central_patients_evaluators.sql` adiciona as sequências
     `web_patient_code_seq` e `web_evaluator_code_seq`, as tabelas `web_patients`,
     `web_evaluators`, `web_registry_audit_events` e `web_legacy_entity_links` com
     constraints `CHECK`, índices normalizados e chaves estrangeiras `ON DELETE RESTRICT`,
     além das colunas aditivas `patient_id` e `evaluator_uuid` em
     `web_project_participants`, `web_invitations` e `web_assessments`, preservando
     intactas as migrations `0001`–`0013` e todos os registros históricos.
   - `scripts/provision_web_database.py` concede `SELECT, INSERT, UPDATE` (estritamente
     sem `DELETE`) sobre `web_patients` e `web_evaluators`, `SELECT, INSERT` sobre
     `web_registry_audit_events` e `web_legacy_entity_links`, `UPDATE (patient_id)`
     sobre `web_project_participants` e `USAGE` nas sequências para o papel `WRITER`.
2. **Domínio, persistência e rotas HTTP de pacientes e avaliadores (`WEB-045` / `CAD-02` / `CAD-03`)**:
   - `stroop/domain/registry.py` implementa normalização determinística de nomes
     (`normalize_person_name`), derivação e validação de iniciais (`derive_initials`,
     `validate_initials`), nota de desambiguação, códigos `PAT-YYYYMMDD-NNNNNN` e
     `EVA-NNNNNN` e validação de `test_code`.
   - `stroop/persistence/web_registry.py`, `stroop/application/web_registry.py`,
     `api/patients.py` e `api/evaluators.py` implementam listagem paginada e
     pesquisável, verificação prévia e bloqueio de duplicidade/homônimos
     (`409 duplicate_candidate_found` com lista `candidates`, exigindo
     `confirm_homonym=true`), criação concorrente serializada por `pg_advisory_xact_lock`,
     edição/inativação lógica (`active=false`) com trilha auditável em
     `web_registry_audit_events` e `auth_audit_events`, e ficha detalhada de
     paciente/avaliador restrita aos projetos autorizados, mantendo separada a
     conta local compartilhada (`issued_by`) do avaliador responsável (`evaluator_uuid`).
3. **Formulário completo de preparação da avaliação com seleção/cadastro inline e conferência (`WEB-046` / `PREP-01` / `E2E-FLOW-01`)**:
   - `stroop/persistence/web_sessions.py`, `stroop/application/web_sessions.py` e
     `api/sessions.py` estendem `POST /api/v1/projects/{project_id}/invitations`
     para aceitar `{patient_id, evaluator_id, visit, test_code, initials}`,
     validando paciente e avaliador ativos, gerando automaticamente o vínculo em
     `web_project_participants` com `participant_code` (`PAT-...`) e retornando o
     bloco `summary` completo para conferência, além de gravar `evaluator_code`
     (`EVA-...`), `patient_id` e `evaluator_uuid` na conclusão da sessão sem expor
     dados nominais no bootstrap do participante (`assessments.participant_name = 'NAO_COLETADO'`).
   - `web/src/api/patients.ts`, `web/src/api/evaluators.ts`, `web/src/api/sessions.ts`,
     `web/src/api/client.ts` e `web/src/components/SessionInvitation.tsx` integram
     seleção pesquisável e cadastro inline de paciente e avaliador com alerta e
     confirmação de homônimos, preenchimento automático `readOnly` do código
     `PAT-...` e pré-preenchimento de `initials`, seleção de `test_code`
     (`stroop_go_nogo_ptbr` · `0.2.2-web.1`) e etapa explícita de **Resumo para conferência**
     (`Revisar preparação` → `Confirmar e emitir convite`).

Ambiente observado nesta sessão: Linux `7.0.0-42-generic` x86_64, Python `3.12.3`,
Node `24.15.0`, npm `11.16.0`, Docker `29.9.2`, PostgreSQL `17.6-bookworm` em
container descartável `stroop_etapa4_test_m4_chg005` (tmpfs, porta `127.0.0.1:55441`,
banco `stroop_etapa4_test_m4_chg005`, removido ao final), Playwright `1.64.1`,
Chromium `156.0.8078.4` e Firefox `157.0`. Nenhum dado real ou `.env` operacional
foi tocado.

Comandos executados e resultados reais (0 skips em todas as suítes):

- `TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55441/stroop_etapa4_test_m4_chg005" .venv/bin/python scripts/verify_web_ci.py python`:
  **435/435 testes Python/PostgreSQL aprovados em 138,770 s, 0 skips** (incluindo
  `tests.test_web_patients`, `tests.test_web_evaluators`, `tests.test_postgres_migrations`,
  `tests.test_web_database_provision`, `tests.test_web_sessions` com `PREP-01` e
  `tests.test_local_auth`).
- `npm --prefix web test && npm --prefix web run build`:
  **306/306 testes Vitest aprovados em 20 arquivos** (2,41 s, incluindo
  `SessionInvitation.test.tsx` e `sessions.test.ts`), `tsc --noEmit` e `vite build`
  aprovados.
- `cd web && npx playwright test e2e/invitations.spec.ts`:
  **20/20 testes aprovados** (22,1 s) em Chromium e Firefox, incluindo o cenário
  `PREP-01`.
- `TEST_DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:55441/stroop_etapa4_test_m4_chg005" npm --prefix web run test:integration -- e2e/integrated/invitations.spec.ts e2e/integrated/participant.spec.ts`
  e reexecução de `e2e/integrated/invitations.spec.ts`:
  **22/22 cenários integrados HTTPS/API/PostgreSQL aprovados** em Chromium e
  Firefox (12/12 em `participant.spec.ts`, 10/10 em `invitations.spec.ts`,
  incluindo `PREP-01 e E2E-FLOW-01` com cadastro inline de paciente e avaliador,
  resumo para conferência, execução experimental completa com 16 checkpoints
  confirmados pelo Dedicated Worker sem expor dados nominais no bootstrap e
  conferência do resultado persistido com `PAT-...` e `EVA-...`).

Falhas intermediárias observadas e corrigidas antes do aceite:

- Em `tests/test_web_evaluators.py`, o payload sintético inicial de tentativa usava
  a chave `key` em vez de `key_pressed`; ajustado para o contrato oficial de
  `POST /api/v1/participant/complete`.
- Em `web/src/api/patients.ts` e `web/src/api/evaluators.ts`, o validador de
  resposta exigia `normalized_name` (campo interno não retornado no payload
  hidratado) e formato curto de código; ajustado para aceitar `PAT-YYYYMMDD-NNNNNN`
  e `EVA-NNNNNN` conforme `stroop/domain/registry.py`.
- Em `tests/test_local_auth.py`, a asserção estática de upgrade a partir da
  migration `0011` esperava apenas `0012` e `0013`; atualizada para incluir
  `0014_central_patients_evaluators.sql`.

Conferência de todos os critérios de `WEB-045`, `WEB-046` e do marco `M4`: todos
comprovados. `WEB-045` e `WEB-046` passam a `CONCLUIDA`, encerrando **M4 (6/6)**.

## M5 — Interface administrativa e analítica React

- Objetivo: Comprovar capacidades necessárias para dispensar Streamlit na operação final e consolidar a experiência administrativa completa da plataforma (`CHG-005`).
- Justificativa: Já existe UI base; expandir para os 8 módulos administrativos, CRUD completo de pacientes e avaliadores, catálogo avançado de filtros e exportação CSV multi-granularidade consolida o sistema como fonte operacional única.
- Alinhamento CHG-006: As capacidades granulares comprovadas nos 5 entregáveis aceitos de M5 constituem os blocos funcionais que passam a ser consolidados nos 3 eixos fundamentais de navegação (Resultados e Análise Unificada; Aplicação Direta / Nova Avaliação; Gestão Cadastral e Acessos) conforme [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md), eliminando a dispersão em abas isoladas.
- Inclui: Arquitetura de informação em 8 módulos (`Visão geral`, `Pacientes`, `Avaliadores`, `Preparar avaliação`, `Avaliações e histórico`, `Resultados e análises`, `Exportações`, `Administração/configurações`), CRUD administrativo completo de pacientes e avaliadores com histórico longitudinal (`WEB-047`), catálogo completo de filtros combinados (`WEB-017`), contas/projetos/vínculos (`WEB-018`), detalhe/visualizações interativas descritivas (`WEB-019`) e exportação CSV avançada multi-granularidade (`WEB-020`).
- Exclui: Relatórios clínicos/normativos, novos instrumentos cognitivos não aprovados, alteração do motor experimental jsPsych.
- Pré-requisitos: M4 integralmente aceito (incluindo `WEB-045` e `WEB-046`) e autorização profissional revalidada em M6.
- Dependências: M4.
- Entregáveis: Operação profissional completa reproduzível no React com escopo consistente e UX acessível.
- Componentes afetados: `web/src/components/, dashboard/, api/patients.py, evaluators.py, assessments.py, administration.py`.
- Testes necessários: Vitest/DOM e E2E reais em Chromium/Firefox (DASH-01, CAD-02/03, EXP-CSV-01, E2E-FLOW-01); acesso cruzado/último admin/CSV filtrado; acessibilidade WCAG AA fora do motor.
- Critérios de aceite: Todas as capacidades incluídas operáveis, separação controlada entre identificação desidentificada padrão e dados nominais autorizados, e zero perda de unidades/proveniência.
- Riscos: R04, R05, R07, R10, R12, R13.
- Decisões externas: Proprietário revisa cobertura final de substituição operacional no M7 (`WEB-028`); exportação nominal de dados reais sujeita a `DEC-03`.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-017 — Revalidar filtros, lista e agregações autorizadas

- Marco: M5. Prioridade: P1. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-046, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Filtros/paginação/contagens cobrem conjunto coerente; troca de projeto e respostas tardias não vazam dados; UI acessível fora do motor. CHG-002: sessões incompletas e avaliações invalidadas não entram nos conjuntos válidos/agregações, com acesso a parciais separado e autorizado. CHG-005: implementar módulo `Visão geral (Dashboard)` (KPIs de pacientes cadastrados, avaliações por período/instrumento/projeto/status/avaliador, evolução temporal e resumos descritivos das métricas oficiais com origem, definição, unidade e tratamento de nulos explícitos) e o catálogo completo de filtros combinados (`REQ-REL-004`: paciente/código/busca textual, avaliador responsável, projeto, instrumento, versão, visita, período, status, condição experimental, tipo de resposta/erro, faixas de precisão e RT, multisseleção, ordenação e tratamento explícito de RT ausente).
- Testes/verificação: `tests/test_web_assessments.py, web/src/dashboard/analysis.test.ts, web/src/components/ResearchFilters.test.tsx; Playwright browser (dashboard.spec.ts, research-filters.spec.ts)`. 319 testes Vitest e 110 testes Playwright aprovados sem skips.
- Evidências: `EV-M5-017/018` (2026-11-08); catálogo de filtros combinados (`REQ-REL-004`) integrado e testado no React, KPIs de pacientes e avaliações por status/avaliador/instrumento e tabela de metadados oficiais Stroop ativos.
- Riscos/bloqueios: R04, R05, R13; mitigados na entrega modular.
- Referências: REQ-REL-001, REQ-REL-004; [arquitetura](ARQUITETURA_WEB.md), [contrato HTTP](desenvolvimento/CONTRATO_API_WEB.md).
- Git da entrega: branch `feat/m5-filtros-kpis-administracao`; pull request e merge commit registrados no fechamento.
- CHG-004: Login local em WEB-021 fornece entrada protegida; revalidar 401/403/404, filtros/gráficos e logout/expiração (AUTH-L07).

### WEB-018 — Revalidar administração React de contas e vínculos

- Marco: M5. Prioridade: P1. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-046, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Permissões e bloqueio/revogação reais; proteção do último admin sob concorrência, sem exclusão de coletas ou herança de acesso a resultados. CHG-005: integrar a área `Administração/configurações` à navegação administrativa de 8 módulos, mantendo explícita na UI e na API a distinção entre a conta local compartilhada de autenticação (`ADR-006`) e o cadastro central de avaliadores responsáveis (`WEB-047`).
- Testes/verificação: `tests/test_web_administration_provisioned.py, web/src/components/AdministrationPanel.test.tsx; Playwright administrativo (administration.spec.ts)`. Aprovados sem skips.
- Evidências: `EV-M5-017/018` (2026-11-08); painel de administração integrado com banner de aviso arquitetural explícito sobre a separação da conta compartilhada de login (`ADR-006`) do cadastro central de avaliadores (`ADR-007` / `WEB-047`), mantendo proteção do último admin e gestão de vínculos de projetos.
- Riscos/bloqueios: R05, R12; mitigados na entrega modular.
- Referências: REQ-REL-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `feat/m5-filtros-kpis-administracao`; pull request e merge commit registrados no fechamento.
- CHG-004: Adequar UI administrativa à conta local única; gestão de vínculos/perfis/bloqueio preservada, sem cadastro público ou oferta de novas contas nesta versão. Contrato antigo de criação OIDC permanece histórico; AUTH-L06/L07 regressa último admin e acesso por projeto.

### WEB-047 — Implementar CRUD administrativo completo de pacientes e avaliadores, histórico longitudinal e correção auditada de vínculos

- Marco: M5. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-046, WEB-017.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Módulos dedicados `Pacientes` e `Avaliadores` na interface profissional React e endpoints correspondentes: listagens pesquisáveis, filtráveis e paginadas; criação com verificação de duplicidade/homônimos e confirmação consciente; edição cadastral com registro em `web_registry_audit_events`; inativação/reativação lógica (`active`) sem exclusão destrutiva; ficha detalhada do paciente exibindo projetos vinculados, visitas, sessões e histórico longitudinal de avaliações e resultados; ficha detalhada do avaliador exibindo projetos/instrumentos e histórico de avaliações conduzidas; procedimento administrativo auditado para correção de vínculo incorreto de paciente/avaliador sem apagar avaliações; conformidade de design system e acessibilidade (`REQ-UX-012`).
- Testes/verificação: CAD-02, CAD-03 e DASH-01 em `tests/test_web_patients.py`, `tests/test_web_evaluators.py`, Vitest (`PatientsPanel.test.tsx`, `EvaluatorsPanel.test.tsx`) e Playwright HTTPS/API/PG reais em Chromium e Firefox.
- Evidências: `EV-M5-047` (2026-11-08); edição cadastral com motivo e auditoria em `web_registry_audit_events`, histórico longitudinal de avaliações e sessões preparadas na ficha do paciente, instrumentos utilizados e avaliações conduzidas na ficha do avaliador, e procedimentos administrativos auditados de correção de vínculo (`relink_assessment` e `relink_invitation`).
- Riscos/bloqueios: R05, R06, R07, R12, R13; resolvidos no escopo do marco M5.
- Referências: REQ-PAR-005, REQ-PAR-004, REQ-AVA-004, REQ-UX-012, REQ-AUD-001; [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), [UX](experimento/UX_DECISIONS.md).
- Git da entrega: branch `feat/m5-crud-pacientes-avaliadores-vinculos`, commit `93bb8f1`, PR #6 aprovado na CI (Run `42508601295`) e integrado à `main` via Merge Commit tradicional (`b050e4c`).

### WEB-019 — Validar detalhe, tentativas, métricas e proveniência

- Marco: M5. Prioridade: P1. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-017, WEB-047.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Unidades/ausência RT, quatro respostas e versões visíveis; gráficos e rótulos descritivos com testes UI/API. CHG-003: revisar tokens/componentes compartilhados, teclado/foco/legibilidade, loading/erro e resoluções; dashboard mantém precisão/gráficos autorizados. CHG-005: consolidar os módulos `Avaliações e histórico` (acompanhamento operacional de convites/sessões, checkpoints `ADR-005` e invalidações) e `Resultados e análises` (`REQ-REL-005`: detalhe completo com vínculos de paciente e avaliador responsável, visualizações interativas de evolução longitudinal do paciente entre visitas/testes, distribuição de RTs, precisão e erros por condição experimental Go/No-Go e congruente/incongruente, projeto, visita e avaliador, sempre com tabelas acessíveis equivalentes e sem normas clínicas).
- Testes/verificação: `tests/test_web_assessments.py, test_web_results.py; Vitest/Playwright (DASH-01)`. Aprovados integralmente localmente e na suíte CI do GitHub Actions (`verify`).
- Evidências: `EV-M5-019` (2026-11-08); detalhe completo de avaliações com proveniência e integridade operacional, quatro respostas visíveis (hits, omissions, correct_rejections, commissions), ausência de RT explícita sem zero arbitrário, distribuição de RTs por faixas, desempenho por condição Go/No-Go e comparações por visita e por avaliador em tabelas acessíveis equivalentes (`<caption>`, `<th>`, `<td>`).
- Riscos/bloqueios: R04, R05, R13; resolvidos no escopo do marco M5.
- Referências: REQ-MET-003, REQ-REL-002, REQ-REL-005; [arquitetura](ARQUITETURA_WEB.md), [UX](experimento/UX_DECISIONS.md). REQ-UX-006/011/012.
- Git da entrega: branch `feat/m5-detalhes-resultados-metricas`, commit `48839a2`, PR #8, Run de CI `42517336016` e Merge Commit tradicional `6be3042` na `main`.


### WEB-020 — Conferir exportação do conjunto filtrado no React

- Marco: M5. Prioridade: P1. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-018, WEB-019.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: CSV individual/agregado coincide com consulta autorizada; revogação pré-download nega; células protegidas; M5 aceito. CHG-003: remoção do HUD não altera CSV individual/agregado nem relatórios e 12 métricas. CHG-005: implementar módulo `Exportações` (`REQ-CSV-005`) com exportação CSV do subconjunto filtrado nas granularidades `pacientes`, `avaliacoes`, `tentativas`, `metricas` e `stroop_21_colunas`, seleção de colunas permitidas, pré-visualização com contagem de linhas (`POST /api/v1/exports/preview`), identificação explícita dos critérios aplicados, modo `deidentified` por padrão e modo `nominal` restrito a autorização de perfil e habilitação `DEC-03`, exclusão estrita de sessões parciais/invalidadas e neutralização contra *CSV formula injection*.
- Testes/verificação: `tests/test_web_multi_export.py, test_web_export.py, test_web_aggregate_export.py; Vitest/Playwright (EXP-CSV-01)`. Aprovados integralmente na CI Actions (`verify`, Run `42522885308`).
- Evidências: `EV-M5-020` (2026-11-08); exportações CSV nas 5 granularidades com seleção de colunas, prévia de contagem e amostra, controle estrito de anonimização (nominal exclusivo para administração), escape contra injeção de fórmulas e exclusão de parciais/invalidadas.
- Riscos/bloqueios: R04, R05, R07, R13 mitigados.
- Referências: REQ-CSV-003, REQ-CSV-005; [arquitetura](ARQUITETURA_WEB.md), [contrato HTTP](desenvolvimento/CONTRATO_API_WEB.md). REQ-UX-006.
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.

### EV-M5-047-NAV — navegação modular em 8 módulos e painéis de pacientes e avaliadores no React, 2026-11-08

Autorização e integração: Pull Request #4 (`feat/m5-interface-administrativa-react`)
submetido para `main`, verificado com sucesso na suíte de CI (`verify`, Run
`42418294072`) e integrado à `main` via Merge Commit tradicional (`18e288917e16759186dd3b18731cbec20d495bf4`),
preservando integralmente os commits `cb7745e` e `e85c3d1`.

Entregas técnicas consolidadas:

1. **Navegação administrativa modular em 8 módulos (`ADR-007` / `CHG-005`)**:
   - `web/src/components/ProfessionalDashboard.tsx`: implementa componente de navegação
     com botões acessíveis (`aria-pressed`, `aria-label`, foco por teclado) para os
     oito módulos operacionais definidos no replanejamento arquitetural:
     1. `Visão geral (Dashboard)`: KPIs, resumos descritivos e visão agregada;
     2. `Pacientes`: catálogo e histórico de pacientes;
     3. `Avaliadores`: cadastro e histórico de avaliadores;
     4. `Preparar avaliação`: formulário integrado de emissão de convite com conferência;
     5. `Avaliações e histórico`: monitoramento operacional de sessões e checkpoints;
     6. `Resultados e análises`: detalhe de tentativas, métricas e visualizações;
     7. `Exportações`: hub avançado de exportação CSV multi-granularidade;
     8. `Administração/configurações`: gestão de contas locais e vínculos de projetos.
   - Restrição estrita de visualização: módulo `Administração` disponível exclusivamente
     para o perfil `administracao`; demais perfis consultam apenas módulos autorizados.
2. **Painel e CRUD de Pacientes (`PatientsPanel.tsx` / `api/patients.ts`)**:
   - Listagem paginada e pesquisável de pacientes por nome e código (`PAT-YYYYMMDD-NNNNNN`),
     com filtro por estado ativo/inativo;
   - Formulário de cadastro inline com validação de homônimos/duplicidades (`409 duplicate_candidate_found`)
     e checkbox explícito de confirmação consciente (`confirm_homonym=true`);
   - Inativação e reativação lógica (`active`) com registro de auditoria, sem exclusão física;
   - Ficha detalhada do paciente exibindo código, iniciais, projetos vinculados, visitas
     e histórico longitudinal completo de avaliações realizadas.
3. **Painel e Cadastro de Avaliadores (`EvaluatorsPanel.tsx` / `api/evaluators.ts`)**:
   - Listagem paginada e pesquisável de avaliadores por nome e código (`EVA-NNNNNN`),
     com derivação e validação determinística de iniciais e notas de desambiguação;
   - Aviso arquitetural claro e destacado na UI alertando que o avaliador cadastrado é
     uma entidade de referência profissional e científica, estritamente separada da
     conta técnica compartilhada de autenticação local (`ADR-006`);
   - Ficha detalhada do avaliador exibindo código, iniciais, projetos vinculados e
     histórico de avaliações conduzidas.
4. **Testes automatizados e conformidade**:
   - Vitest: `ModularNavigation.test.tsx` (2 testes cobrindo alternância de módulos,
     controle de acesso por papel e preservação de seletores diretos de alerta),
     `PatientsPanel.test.tsx` (2 testes cobrindo renderização, busca, homônimos e ficha),
     `EvaluatorsPanel.test.tsx` (2 testes cobrindo listagem, criação, aviso arquitetural e ficha);
   - Testes E2E e CI aprovados na Run `42418294072`.

### EV-M5-017/018 — catálogo de filtros combinados (REQ-REL-004), KPIs descritivos do dashboard e revalidação de administração React, 2026-11-08

Autorização e escopo: tarefas prontas encadeadas `WEB-017` e `WEB-018` autorizadas
para execução em `M5` na branch dedicada `feat/m5-filtros-kpis-administracao` a partir
de `main` (`18e2889`).

Entregas consolidadas nesta sessão:

1. **Catálogo completo de filtros combinados (`REQ-REL-004` / `WEB-017`)**:
   - `web/src/components/ResearchFilters.tsx`: formulário acessível estendido com
     busca textual por código de paciente ou termo (`searchText`), seletor de status
     da avaliação (`valid` [oficiais válidas padrão], `all` [todas], `invalid` [interrompidas/invalidadas]),
     faixas de precisão percentual (`under50`, `50to80`, `80plus`), faixas de tempo
     de reação mediano (`under500ms`, `500to1000ms`, `1000to1500ms`, `1500msPlus`),
     checkbox explícito de controle de RT ausente (`includeNullRt`), seletor de tipo
     de resposta/erro (`hits`, `omissions`, `commissions`, `correct_rejections`),
     condição experimental (`go`, `nogo`) e ordenação determinística por data, código
     de participante, precisão ou tempo mediano em ordem ascendente ou descendente.
   - `web/src/dashboard/analysis.ts`: funções analíticas puras `filterAssessments` e
     `sortAssessments` que combinam todas as dimensões com semântica determinística,
     preservando a separação estrita de dados científicos válidos e tratando nulos de RT.
   - `web/src/components/ResearchFilters.test.tsx`: suíte Vitest cobrindo renderização,
     preenchimento, emissão estruturada de `query.advanced` e limpeza com restauração
     de valores padrão.
2. **KPIs descritivos e dicionário científico oficial na Visão Geral (`CHG-005` / `WEB-017`)**:
   - `web/src/components/ProfessionalDashboard.tsx`:
     - Seção `overview-summary-kpis` com grade de cartões informando o total de
       pacientes cadastrados no projeto (carregado via `listPatients` da API),
       total de avaliações válidas no recorte, avaliações interrompidas/invalidadas e
       número de avaliadores envolvidos;
     - Seção `metrics-dictionary` com tabela descritiva das 6 métricas oficiais
       do Stroop Go/No-Go (`accuracy`, `accuracy_go_trials`, `accuracy_no_go_trials`,
       `response_time_seconds`, `omission_errors`, `commission_errors`), informando
       explicitamente origem da fórmula matemática, definição conceitual, unidade
       de mensuração e política estrita de tratamento de valores nulos (RT nulo nunca
       convertido para zero).
   - `web/src/dashboard/analysis.ts`: função `computeOverviewKPIs` e constante
     `OFFICIAL_METRICS_DICTIONARY` validadas em `analysis.test.ts`.
3. **Revalidação da administração React e distinção arquitetural (`WEB-018`)**:
   - `web/src/components/AdministrationPanel.tsx`: integrado à navegação modular de
     8 módulos com banner de destaque arquitetural alertando que a conta técnica
     local compartilhada (`ADR-006`) é restrita ao acesso operacional da equipe,
     sendo estritamente separada do cadastro central de avaliadores responsáveis
     (`ADR-007` / `WEB-047`), com link de navegação rápida para o módulo `Avaliadores`;
   - Preservação da proteção do último administrador sob concorrência, controle
     de papéis (`consulta`, `importacao`, `administracao`) e vinculação a projetos;
   - `web/src/components/AdministrationPanel.test.tsx`: teste unitário comprovando
     renderização do banner arquitetural, navegação entre módulos e listagem de contas.
4. **Verificação de testes e compatibilidade**:
   - Vitest: **319/319 testes aprovados em 25 arquivos de teste** (incluindo
     `ResearchFilters.test.tsx`, `AdministrationPanel.test.tsx`, `analysis.test.ts`,
     `ModularNavigation.test.tsx`, `PatientsPanel.test.tsx`, `EvaluatorsPanel.test.tsx`);
   - Playwright Browser: **110/110 testes aprovados** em Chromium e Firefox sem skips
     (incluindo `dashboard.spec.ts`, `research-filters.spec.ts`, `administration.spec.ts`,
     `navigation.spec.ts`, `invitations.spec.ts`, `practice.spec.ts`).

Conferência de critérios de aceite de `WEB-017` e `WEB-018`: todos satisfeitos.
`WEB-017` e `WEB-018` passam a `CONCLUIDA`. Marco `M5` avança para **2/5 aceitos**;
próxima tarefa pronta: `WEB-047`.

### EV-M5-020 — exportações CSV multi-granularidade no React, 2026-11-08

Autorização e escopo: tarefa pronta `WEB-020` autorizada para execução em `M5`
na branch dedicada `feat/m5-exportacoes-csv-filtradas` a partir de `main` (`d426c2f`).

Entregas técnicas consolidadas:

1. **Domínio de exportações multi-granularidade (`REQ-CSV-005`, `DEC-03`)**:
   - `stroop/domain/web_multi_export.py`:
     - Catálogo formal e canônico das 5 granularidades: `pacientes`, `avaliacoes`,
       `tentativas`, `metricas` e `stroop_21_colunas`.
     - Projeção dinâmica de colunas solicitadas respeitando a lista permitida de cada catálogo.
     - Anonimização estrita: modo `deidentified` mascara nomes e identificadores diretos
       por padrão; modo `nominal` restrito exclusivamente ao perfil `administracao`
       (retorna `403 permission_denied` em outros perfis).
     - Proteção contra *CSV formula injection* (`_safe_cell` prefixa células que iniciam
       com `=`, `+`, `-`, `@`, `\t`, `\r` ou `\n` com `'`).
     - Ausências de RT mantêm célula vazia `""` sem conversão espúria para zero.

2. **Persistência SQL filtrada e íntegra (`stroop/persistence/web_multi_export.py`)**:
   - Consultas SQL otimizadas filtradas por projeto e intervalo de datas.
   - Exclusão rigorosa de sessões incompletas ou invalidadas (`valid_session = TRUE` e
     `invalidated_at IS NULL`), garantindo integridade dos dados exportados para pesquisa.

3. **Endpoints de pré-visualização e download (`api/exports.py`, `api/main.py`)**:
   - `POST /api/v1/exports/preview`: retorna contagem total de registros do subconjunto filtrado,
     total de colunas projetadas e amostra tabular das 5 primeiras linhas.
   - `POST /api/v1/exports/download`: gera token HMAC efêmero assinado (15 min) e entrega o
     arquivo CSV com headers `Content-Disposition`, `X-Content-Type-Options: nosniff` e
     `Cache-Control: no-store`.

4. **Interface React modular de exportação (`web/src/components/ExportHubPanel.tsx`)**:
   - Seletor acessível das 5 granularidades com contagem e descrição clara de escopo.
   - Seleção granular de colunas com botões rápidos "Selecionar todas" e "Limpar seleção".
   - Controle de modo de identificação com bloqueio visual e aviso explícito para não-administradores.
   - Painel de prévia com contagem em destaque, critérios aplicados e amostra das primeiras linhas.
   - Download direto do arquivo CSV via Blob seguro com feedback de progresso e tratamento de erro.
   - Cliente HTTP tipado em `web/src/api/exports.ts` com proteção CSRF.

5. **Validação automatizada e CI remota**:
   - 329 testes unitários aprovados no Vitest (`npm --prefix web test`).
   - 22 testes unitários de exportação aprovados no backend (`tests/test_web_multi_export.py`,
     `tests/test_web_export.py`, `tests/test_web_aggregate_export.py`).
   - Typecheck TypeScript (`tsc --noEmit`) e build de produção do Vite aprovados sem advertências impeditivas.
   - Suíte completa de CI Actions (`verify`, Run `42522885308`) 100% verde na branch de entrega.
   - Merge Commit tradicional na `main` (`ff45b7a`) via Pull Request #10.

Com a aceitação de `EV-M5-020`, **todas as 5 tarefas de M5 estão CONCLUIDAS**. Marco `M5`
concluído com **5/5 entregáveis aceitos**. Progresso global avança para **33 de 48 entregáveis aceitos (68,8%)**.

### EV-M5-019 — detalhe de avaliações, histórico operacional e análises descritivas, 2026-11-08

Autorização e escopo: tarefa pronta `WEB-019` autorizada para execução em `M5`
na branch dedicada `feat/m5-detalhes-resultados-metricas` a partir de `main` (`421bc58`).

Entregas técnicas consolidadas:

1. **Acompanhamento operacional de avaliações e sessões no módulo Histórico (`ADR-005`, `CHG-005`)**:
   - `web/src/components/ProfessionalDashboard.tsx`, `web/src/components/ResultsTable.tsx`:
     - Tabela de avaliações com identificação de proveniência (plataforma WEB com `session_id`,
       `protocol_id`, `app_version` e `frame_period_ms` vs. importação legado PsychoPy local),
       status de integridade/resultado e botão acessível de abertura do painel de detalhe.
     - Painel de detalhe com proveniência completa, metadados cadastrais (`participant_id` PAT-...,
       `evaluator_id` EVA-...), motivo de invalidação em destaque quando aplicável e fechamento
       acessível com retorno de foco.

2. **Detalhamento completo de respostas, métricas e tentativas (`REQ-REL-005`)**:
   - Resumo descritivo com contagens das quatro respostas principais: Acertos (`hits`),
     Erros de omissão (`omission_errors`), Rejeições corretas (`correct_rejections`) e
     Erros de comissão (`commission_errors`).
   - Apresentação das 12 métricas oficiais do Stroop com rótulos padronizados e unidades
     (`%`, `s`, contagem). Tratamento explícito de tempo de reação ausente (`—`) quando
     `hits = 0`, sem conversão espúria para zero.
   - Tabela de tentativas completas com bloco, tentativa (#), palavra, cor da tinta,
     condição experimental, tecla pressionada (ou `—`), classificação e tempo de reação (s e ms).

3. **Visualizações analíticas descritivas no módulo Resultados e análises (`REQ-REL-005`)**:
   - `web/src/components/ResearchVisualizations.tsx`:
     - Evolução longitudinal do paciente por avaliação ordenada cronologicamente, com
       gráficos acessíveis (`<meter>`) de precisão e RT mediano e tabela de evolução equivalente.
     - Distribuição de tempos de reação (RTs) por faixas (< 0,5s, 0,5 a < 1s, 1 a < 1,5s,
       1,5 a < 2s, ≥ 2s e ausente), com contagens, proporções e tabela acessível.
     - Precisão e contagens de erros por condição experimental Go vs. No-Go.
     - Comparações descritivas por visita e por avaliador responsável.
     - Toda informação mantida estritamente com rótulos descritivos de pesquisa, sem inferência
       diagnóstica, laudos ou normas clínicas.

Verificações e testes:
- Backend: `tests/test_web_assessments.py` (20 testes aprovados com PostgreSQL descartável),
  `tests/test_web_results.py` (19 testes aprovados de validação, 4 classificações e ausência de RT);
- Frontend: 327 testes Vitest aprovados (`ModularNavigation.test.tsx`, `ResearchVisualizations.test.tsx`,
  `analysis.test.ts`, etc.);
- Typecheck (`tsc --noEmit`) e Vite build (`dist/`) concluídos com sucesso;
- CI oficial remota (`verify`, Run `42517336016`) aprovada em todos os steps (scanners,
  backend com PostgreSQL real, Vitest, Playwright em Chromium e Firefox e integração ponta a ponta).

Git da entrega: branch `feat/m5-detalhes-resultados-metricas`, commit `48839a2`,
PR #8 aprovado na CI e integrado à `main` via Merge Commit tradicional (`6be3042`).

### EV-M5-047 — CRUD administrativo de pacientes, avaliadores e correção auditada de vínculos, 2026-11-08

Autorização e escopo: tarefa pronta `WEB-047` autorizada para execução em `M5`
na branch dedicada `feat/m5-crud-pacientes-avaliadores-vinculos` a partir de `main` (`b625ab6`).

Entregas técnicas consolidadas:

1. **Edição cadastral com justificativa obrigatória e auditoria (`REQ-AUD-001`, `REQ-PAR-005`, `REQ-AVA-004`)**:
   - Backend (`stroop/persistence/web_registry.py`, `stroop/application/web_registry.py`):
     - Atualização cadastral de pacientes (`update_patient`) e avaliadores (`update_evaluator`)
       exigindo `reason_code` (`typo`, `legal_update`, `clinical_correction`, `link_rectification`,
       `other`) e gerando registros imutáveis na tabela `web_registry_audit_events` com
       `action='update'`, `actor_account_id`, `before_state`, `after_state` e `reason_code`.
   - Frontend (`PatientsPanel.tsx`, `EvaluatorsPanel.tsx`):
     - Formulário acessível de edição cadastral permitindo alterar nome civil, notas e
       campos opcionais com seleção obrigatória de motivo e confirmação consciente.
     - Histórico de auditoria visível na ficha detalhada com data, ação, operador e motivo.

2. **Histórico longitudinal e visualização de sessões do paciente (`REQ-PAR-004`)**:
   - `web/src/components/PatientsPanel.tsx`:
     - Ficha detalhada do paciente expandida com duas seções operacionais completas:
       1. `Convites e sessões preparadas`: listagem de convites gerados para o paciente,
          indicando código do convite, projeto, visita, avaliador responsável e status;
       2. `Histórico longitudinal de avaliações`: listagem de todas as avaliações
          concluídas ou em andamento vinculadas ao paciente através de seus convites e visitas,
          com dados de precisão, tempo de reação mediano e status.

3. **Instrumentos utilizados e avaliações conduzidas pelo avaliador (`REQ-AVA-004`)**:
   - `web/src/components/EvaluatorsPanel.tsx`:
     - Ficha detalhada do avaliador expandida com catálogo de instrumentos utilizados
       (ex.: `stroop_vic`), total de avaliações conduzidas e lista detalhada das
       sessões com paciente atendido, projeto e data.

4. **Procedimento administrativo auditado para retificação e revinculação (`relink`)**:
   - Endpoints HTTP REST:
     - `POST /api/v1/projects/{project_id}/assessments/{assessment_id}/relink`: retifica
       vínculo de paciente e/ou avaliador em avaliação já persistida;
     - `POST /api/v1/projects/{project_id}/invitations/{invitation_id}/relink`: retifica
       vínculo em convite preparado.
   - Casos de uso e persistência:
     - Resolução automática e consistente de chaves estrangeiras compostas:
       inserção/busca idempotente em `web_project_participants` e `web_participant_visits`,
       atualização atômica em `web_assessments`, `assessments` e `web_invitations`.
     - Registro bidirecional de auditoria em `web_registry_audit_events`: eventos para
       o registro de destino e para o registro anterior com `action='relink'`, registrando
       `previous_patient_id`/`new_patient_id` e `previous_evaluator_id`/`new_evaluator_id`.
   - Interface React (`PatientsPanel.tsx`, `EvaluatorsPanel.tsx`):
     - Botão e modal acessível `Corrigir vínculo` em cada linha de avaliação do histórico,
       permitindo selecionar novo paciente ou novo avaliador por código/nome, com
       justificativa obrigatória e atualização imediata da listagem.

5. **Testes automatizados e CI**:
   - Backend PostgreSQL: testes dedicados `test_revinculacao_auditada_paciente_e_controles`
     em `tests/test_web_patients.py` e `test_revinculacao_auditada_avaliador_e_controles`
     em `tests/test_web_evaluators.py` executados contra banco descartável sem skips (100% aprovados).
   - Frontend Vitest: **325/325 testes aprovados em 25 arquivos de teste** (incluindo
     novos testes de edição cadastral, auditoria e revinculação em `PatientsPanel.test.tsx`
     e `EvaluatorsPanel.test.tsx`).
   - Playwright Browser: **110/110 testes aprovados** em Chromium e Firefox sem skips.
   - Pull Request #6 submetido para `main`, aprovado na suíte de CI (`verify`, Run
     `42508601295`) e integrado à `main` via Merge Commit tradicional (`b050e4c`).

Conferência de critérios de aceite de `WEB-047`: todos satisfeitos.
`WEB-047` passa a `CONCLUIDA`. Marco `M5` avança para **3/5 aceitos**;
próxima tarefa pronta: `WEB-019`.

## M6 — Autenticação, permissões e segurança

- Objetivo: Substituir Google OIDC por login local e preservar autorização central antes do primeiro fluxo integrado (CHG-004).
- Justificativa: Reposicionado antes de M4; segurança não será fase tardia.
- Inclui: Conta administrativa local única, senha/hash, provisionamento e recuperação protegidos, sessões separadas, perfis/vínculos, revogação, CSRF e revisão de ameaças.
- Exclui: Cadastro público, ampliação para múltiplas contas, redução de proteção e políticas institucionais inferidas.
- Pré-requisitos: M2 aceito; ensaios com conta sintética provisionada em ambiente isolado HTTPS/API/PG, sem recurso Google.
- Dependências: M2.
- Entregáveis: Matriz de autorização e evidência de login/logout com conta cadastrada.
- Componentes afetados: `api/auth.py, config.py, administration.py, stroop/domain/auth.py, stroop/application/auth.py, stroop/persistence/, web/src/App.tsx`, schema aditivo, segurança e proxy.
- Testes necessários: matriz AUTH-L01–L09 em [validação](VALIDACAO_WEB.md#autenticação-local--plano-de-verificação-chg-004), cookies/CSRF/Origin, IDOR, bloqueio e grants; login real local em HTTPS/API/PG, sem doubles para aceite.
- Critérios de aceite: Controles positivos/negativos comprovados; login real não pode ser substituído por mock ou alegação histórica.
- Riscos: R05, R07, R12.
- Decisões externas: direção local aprovada pelo proprietário nesta missão; uso compartilhado com dados reais exige DEC-03. Implementação requer autorização posterior de M6; nenhum cliente Google é dependência alvo.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-021 — Implementar autenticação local e integrar login profissional seguro

- Marco: M6. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-008.
- Responsável: Codex na execução autorizada de M6; proprietário/operador na custódia e instituição no eventual uso real.
- Critérios de aceite: Login local válido cria sessão nova e abre dashboard; senha inválida, usuário inexistente/bloqueado e acesso não autenticado negam genericamente. Conta única administrativa, sem cadastro público/default/hardcode; Argon2id, provisionamento, alteração/recuperação administrativa e revogação atômica após senha. Rate limiting por conta/origem, cookies seguros, CSRF/Origin inclusive login, inatividade e limite absoluto, logout/invalidação e revogação administrativa conforme contrato. React/FastAPI/PG/HTTPS reais; preservar projetos, grants, último admin, convites e dados históricos; compatibilidade/migração aditiva testadas antes do corte de OIDC. Regressões novas de WEB-022/023 obrigatórias aqui, consolidadas em WEB-024.
- Testes/verificação: `tests/test_local_auth.py, tests/test_local_auth_http.py, tests/test_web_security_review.py, tests/test_postgres_migrations.py, tests/test_web_database_provision.py, tests/test_web_administration_provisioned.py; web/src/components/ProfessionalCredentials.test.tsx; web/e2e/local-auth/auth.spec.ts, web/e2e/integrated/, web/e2e/administration.spec.ts; scripts/smoke_web_compose.py, scripts/smoke_local_auth_restore.py, scripts/verify_web_ci.py` (AUTH-L01–L09 em [validação](VALIDACAO_WEB.md#autenticação-local--plano-de-verificação-chg-004)).
- Evidências: `EV-M6-021-BASE`, `EV-M6-021-HTTP` e encerramento consolidado em `EV-M6-021/024` (2026-11-06). Histórico OIDC sintético preservado em `EV-M6-022/023` e `EV-M8-030` apenas como regressão de compatibilidade.
- Riscos/bloqueios: R05/R07/R12 permanecem abertos para seus gates subsequentes (M4/M5/M8/M9/M10); bloqueio técnico de autenticação profissional resolvido localmente em M6. Nunca abrir secrets operacionais.
- Referências: REQ-AUT-001/004/005, REQ-AUT-002/003; [ADR-006](arquitetura/ADR-006-autenticacao-local.md), CHG-004.
- Git da entrega: branch `feat/m6-autenticacao-local` (base `7872863`, `188eef5` em `EV-M6-021-BASE` e entrega final em `EV-M6-021/024`); envio e CI no fechamento desta seção.

### EV-M6-021-BASE — credencial e persistência locais, 2026-11-06

Unidade parcial de WEB-021, autorizada pelo novo `continue o projeto` após M3.
DDL/associação/grants documentados antes da aplicação sintética em
`docs/dados/MODELO_DE_DADOS.md`. Migration **0012** acrescenta namespace próprio
`urn:stroop:local` ao registro de autorização e associa UUID imutável a credencial;
FKs e registros históricos não são reescritos. Credenciais, sessões, eventos
fechados e buckets persistentes têm tabelas separadas de OIDC. Sem novo vínculo
implícito ou mudança no schema científico; 0001–0011 intactas.

Domínio valida username ASCII normalizado e senha Unicode íntegra. Adaptador
usa [PasswordHasher Argon2id](https://argon2-cffi.readthedocs.io/en/stable/api.html),
`argon2-cffi==25.1.0`/bindings `26.1.0`, selecionados por fonte oficial e índice
PyPI; versões compartilhadas preservadas. Instalação somente dessas duas novas
dependências necessárias, com `--no-deps`, sem upgrade incidental. Parâmetros
64 MiB/t=3/p=1, salt aleatório e hash fictício; semáforo limita verificações por
processo. Lista local inicial de senhas comuns é mínima, não uma base abrangente
de vazamentos: sua ampliação/revisão e custo sob carga continuam na integração
e revisão WEB-024. Nenhuma consulta de senha a serviço externo.

Casos de uso/persistência implementam bootstrap único serializado, recuperação,
login com versão e troca de senha/revogação atômicos, limite de cinco falhas por
identificador/15 minutos, renovação de cookie lógico anterior, sessão com teto
8 h/inatividade 30 min, polling sem renovar e atividade explícita. Revalidação de
versão/bloqueio/perfil preserva autorização; contexto/atividade ainda aguardam
integração HTTP com autorização por objeto/projeto. Limite por origem, envelopes,
CSRF/login e corte não estão implementados pela base isolada. Writer não cria
contas nem altera `app_users`; bloqueio usa `web_lock_emitter`. Reader não lê hash.

CLI nova `scripts/gerenciar_conta_local.py` (caminho e módulo): `bootstrap
<username>` ou `recover <username>`, `API_OPERATOR_DATABASE_URL` ou seu `_FILE`
protegidos, exclusivos do operador. Exige terminal stdin/stderr e entrada oculta
com confirmação; recusa fallback de getpass com eco. Recuperação exige digitar
RECUPERAR, revoga sessões e não concede projetos. Nenhuma senha em argv;
comando legado preservado. Não foi usada com conta/banco reais.

Ambiente: Python 3.12.3; PostgreSQL 17.11 em container novo exclusivo
`stroop-m6-local-20261106`, tmpfs/porta aleatória somente loopback (32776), bancos
`stroop_etapa4_test_m6_local` e `stroop_etapa4_test_m6_terminal`. DSNs e frases
somente sintéticos. Nenhum serviço preexistente foi reutilizado/alterado. Container e bancos
descartáveis removidos após as verificações; logs somente temporários fora do Git.

Validações desta unidade (DSNs sempre descartáveis, prefixo exigido):

- `TEST_DATABASE_URL=<PG sintético> PYTHONPATH=tests .venv/bin/python -m unittest
  discover -s tests -q`: **408 aprovados em 146,321 s, sem skips**, na rodada final.
  Inclui regressões existentes de autenticação OIDC, API, sessões participantes,
  permissões, métricas, exportação, migrations e infraestrutura; não equivale
  a integração HTTP local, pois o alvo ainda não usa os novos casos de uso.
- `TEST_DATABASE_URL=<PG sintético> PYTHONPATH=tests .venv/bin/python -m unittest
  tests.test_local_auth tests.test_postgres_migrations
  tests.test_web_database_provision tests.test_verify_web_docs -q`:
  **38 aprovados, sem skips**, incluindo 11 novos testes locais. Cobre parâmetros/
  salt, senha íntegra/Unicode/ASCII username, semáforo, CLI sem stdin inseguro,
  bootstrap concorrente, recuperação e rotação atômicas com rollback e corrida
  de login, cinco falhas concorrentes, janela expirada, cookie lógico substituído,
  teto/inatividade, polling sem atividade, versão, bloqueio/perfil, writer/reader
  e upgrade com identidade/projeto/vínculo Google preservados.
- CLI em PTY real: bootstrap pelo caminho e recuperação pelo módulo, ambos
  **exit 0**, entrada/confirmacão da senha sem eco; confirmação RECUPERAR explícita.
  Consulta fechada após commit: versão 2, eventos bootstrap/recovery e zero vínculos.
- Argon2id medido sem imprimir material secreto, cinco hashes e cinco verificações:
  medianas **128,2 ms/129,5 ms**, máximos **152,7 ms/163,9 ms**; 64 MiB/t=3/p=1.
  Medida local com a regressão em andamento, sem conclusão de capacidade/DoS.
- `.venv/bin/python -m pip check`: aprovado. `.venv/bin/python
  scripts/verify_web_ci.py audit`: **npm e pip-audit sem vulnerabilidades conhecidas**;
  ferramenta de auditoria isolada temporária pelo runner já existente, sem
  alteração de dependências adicionais do projeto. Não equivale à revisão WEB-024.
- `.venv/bin/python scripts/verify_web_ci.py sources`: scanner oficial sem achados,
  fontes versionadas e novos arquivos staged; dados/secrets/histórico excluídos
  conforme o runner. Documentação e `git diff --check` aprovados antes do commit.
- Frontend/Vitest/tipos/build/Playwright/HTTPS **não reexecutados nesta unidade**:
  nenhum código de API ou frontend alterado; integração local continua gate da
  próxima unidade de WEB-021. Migrations só nos dois bancos sintéticos citados.

Falhas preservadas: primeira rodada local teve sete aprovações/um erro de
privilégio no FOR SHARE direto em app_users; trocado por web_lock_emitter, sem
conceder UPDATE. Rodada seguinte de 28 testes teve duas falhas de expectativas
estáticas do catálogo (nova migration e três FKs); atualizadas para 0012/30 FKs,
sem remover verificações. Teste novo de teto usava clock_timestamp separado
em cada campo da fixture, ultrapassando 8 h por microssegundos; uma rodada
focada e a primeira integral (**407 executados, um erro**) registraram a mesma
violação de CHECK. Fixture passou a usar CURRENT_TIMESTAMP único; constraints
intactas. Os 38 focados e os 408 integrais finais passaram após correção.
Avisos legados de TestClient e mensagens negativas de launcher/CLI/auditoria
são esperados pela suíte; nenhuma atualização incidental para suprimi-los.

Aceite **não concedido**: API/React/HTTPS, limite por origem e troca de senha,
limpeza/limite de cardinalidade de buckets vencidos, gestão/último admin local,
revogação administrativa HTTP, lista local ampliada, Compose/configuração,
regressões e corte OIDC ainda exigem trabalho/validação. M6 permanece 2/4;
20/45 aceitos (44,4%) intactos. Nenhum aceite WEB-021/024 ou avanço de marco.
Branch `feat/m6-autenticacao-local`; entrega identificável por `git log -1
--format=%H --grep='feat(auth): implementa base transacional de credenciais locais'`.
Envio/CI e SHA reais no fechamento desta evidência, sem PR/merge/deploy.

#### Fechamento Git da base local — 2026-11-06

Entrega **`188eef50e8ddce55f889179ea83913eedf792820`**, branch
`feat/m6-autenticacao-local`, enviada com upstream; igualdade HEAD/upstream/
`git ls-remote --heads origin feat/m6-autenticacao-local` confirmada.
`gh run list --branch feat/m6-autenticacao-local --limit 5 --json
headSha,status,conclusion,url` retornou `[]`: nenhuma execução Actions encontrada,
sem dispatch/CI aprovada ou transferência de aprovação de outro SHA.
`python3 scripts/verify_web_docs.py`, sete testes documentais e diff check
aprovados após integração das evidências. Scanner final: 376 fontes sem achados.
Revisados os 16 arquivos da entrega; migrations antigas intactas. Worktree limpa
após commit/push da entrega, antes deste fechamento documental.

Fechamento identificável por `git log -1 --format=%H
--grep='docs: registra envio da base local de M6'`; conferir seu envio por
HEAD/upstream/remoto sem commit artificial de autorreferência. Próxima ação
continua a integração WEB-021 descrita na Retomada: nenhuma nova autorização
necessária para trabalho sintético dentro de M6, nenhum avanço implícito a M4.
Não houve PR, merge, tag, deploy, migração real ou acesso a dados/credenciais reais.

### EV-M6-021-HTTP — integração local e antiabuso, 2026-11-06

Continuidade autorizada pelo comando `continue o projeto` no marco M6, sem alterar
AGENTS/workflow nem presumir decisões institucionais, deploy ou integração à main.
Branch `feat/m6-autenticacao-local`, início limpo em `7872863`, upstream igual
após fetch; base encadeada não integrada preservada, main/origin/main intactas.
Unidade **parcial**, sem aceite WEB-021/024 nem novo crédito de progresso.

Implementados POST login/senha, sessão local nos adaptadores profissionais,
resposta genérica de falha, Origin/CSRF, limite de corpo 4 KiB, renovação segura
de cookie/atividade após operação autorizada e sem renovação em `/me` ou negação.
Revogação administrativa, PATCH por identidade opaca e recusa de cadastro
adicional preservam conta administrativa local e dados/vínculos históricos.
Formulário React acessível limpa senha após envio/erro/saída, suporta Unicode/
espaços e troca de senha; 401 profissional limpa RAM. Sem storage de credenciais.

Antiabuso: origem 20/min e identificador cinco falhas/15 min compartilhado entre
login/troca; buckets HMAC separados, persistentes e serializados. Teto técnico
10.000 buckets, limpeza de janelas com mais de 24 h e negação ao saturar. Hash
novo só após senha atual correta/limites; semáforo também limita criação de hash.
O teto não define retenção de eventos nem aprova capacidade de produção.

Revisão independente encontrou chamadas PG síncronas no event loop e possível
rejeição depois do commit na renovação de atividade. Corrigidas: renovação em
threadpool; falha/revogação posterior apaga cookie sem reinterpretar sucesso já
confirmado. Teste determinístico força revogação real nesse intervalo e confere
commit, resposta e acesso seguinte. Nenhuma decisão científica alterada.

Validações desta unidade e limites:

- `npm --prefix web test`: **300/300**, 19 arquivos; tipos/build aprovados.
  Primeira rodada focada teve 45 aprovações/uma falha de foco em campo ainda
  desabilitado; efeito pós-render corrigido, rodada final integral aprovada.
- `tests.test_local_auth`: **16/16**, sem skips, 17,589 s no PG exclusivo do
  antiabuso (porta 32778, `stroop_etapa4_test_abuse`); concorrência, saturação,
  expiração, origem, falhas compartilhadas e rollback. Container removido.
- `tests.test_local_auth_http`: seis cenários iniciais aprovados com PG real;
  casos adicionais e regressão integral final registrados no fechamento abaixo.
- Em `web`: `TEST_DATABASE_URL=<PG sintético exclusivo>
  npx playwright test --config playwright.local-auth.config.ts`: **10/10** em
  26,7 s, primeira rodada sem retries/skips. React/build/API/PG/HTTPS reais com
  writer/reader restritos, sem Google/conta/serviço externo. Chromium
  **156.0.8078.4**, Firefox **157.0**, PostgreSQL **17.6**, Linux, Python 3.12.3.
  Cinco cenários por navegador: login/cookies/CSRF/zero vínculos; erros genéricos/
  bloqueio/Origin; logout/replay; troca com revogação de duas sessões; último
  admin/cadastro recusado/autorrevogação. Novo harness `web/e2e/local-auth/`,
  portas 4473/4481, banco `stroop_etapa4_test_local_https` (porta PG 32779).
  Container, processos e certificados exclusivos removidos. Não valida produção,
  ambiente institucional, métricas físicas nem campanha científica.

Falhas preservadas: primeira rodada HTTP seis cenários teve quatro falhas por
UTC de `Expires`; conversão explícita para `timezone.utc` corrigiu o cookie.
Rodadas seguintes tiveram uma fixture violando teto de 8 h ao deslocar criação
epois read DSN ausente (503 esperado pelo serviço); ajustadas somente fixtures.
Uma integral (**419 executados, 14 falhas/11 erros**) e uma focada (**42, quatro
falhas/oito erros**) foram invalidadas por erro do executor: ambas usaram o mesmo
banco descartável simultaneamente e recriaram seu schema. Não são aprovação nem
falha funcional atribuída ao produto; repetição sequencial isolada obrigatória.
Nenhum banco/serviço operacional envolvido. Logs só em `/tmp`, não versionados.

Configuração desta unidade é explícita `API_AUTH_MODE=local`, dispensando leitura
de configuração Google; OIDC ainda permanece default enquanto corte/compatibilidade
integral/Compose e revisão WEB-024 aguardam validação. Frontend novo destina-se à
API local configurada; não publicar esta branch como candidata integrada.
Regressão HTTPS integrada anterior, restauração de credenciais/sessões, lista local
de senhas ampliada, imagens/Compose, CI e corte continuam gates sem aceite.
Evidências novas não transferem aceites históricos de WEB-022/023 ou WEB-030.

### WEB-022 — Comprovar matriz de perfis, projetos e revogações

- Marco: M6. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-008.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Consulta/importacao/admin e participante testados em operações positivas/negativas; admin sem projeto não herda resultados; revogação efetiva.
- Testes/verificação: `tests/test_web_auth.py, test_web_assessments.py, test_web_sessions.py`. Executados em PG descartável, junto aos casos de autenticação/importação; dez casos HTTPS reais em Chromium/Firefox. Ver EV-M6-022/023.
- Evidências: EV-M6-022/023, 2026-11-06; critérios positivos/negativos comprovados em banco sintético e HTTPS. Login local alvo permanece WEB-021; evidência histórica OIDC preservada.
- Riscos/bloqueios: R05 preservado para revisão final; matriz local comprovada sem aprovação de OIDC externo.
- Referências: REQ-AUT-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m6-m8-validacao-isolada`; entrega identificável por `git log -1 --format=%H --grep="test(web): comprova permissões e isolamento de sessões em M6"`; envio/CI no fechamento desta execução.
- CHG-004: Aceite histórico EV-M6-022/023 preservado. Regressões locais PLANEJADAS AUTH-L04/L06/L07 em WEB-021/024: conta local admin sem vínculo não lê/exporta/emite convite; vínculos explícitos, bloqueio, perfis consulta/importacao/administracao e último admin preservados. Não ampliar múltiplas contas agora; fixtures de perfis são regressão, não produto novo.

### WEB-023 — Revalidar sessão, cookies, CSRF e isolamento de credenciais

- Marco: M6. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-022.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Origin e CSRF ausentes/divergentes negam; expiração/logout/replay e cookies separados comprovados em HTTPS; sem armazenamento durável.
- Testes/verificação: `tests/test_web_auth.py, test_web_sessions.py; integração HTTPS`. Executados em PG descartável, junto aos casos de autenticação/importação; dez casos HTTPS reais em Chromium/Firefox. Ver EV-M6-022/023.
- Evidências: EV-M6-022/023, 2026-11-06; critérios positivos/negativos comprovados em banco sintético e HTTPS. Login local alvo permanece WEB-021; evidência histórica OIDC preservada.
- Riscos/bloqueios: R05/R07 preservados para revisão final; nenhum impedimento nos critérios locais desta tarefa. Login real não aceito por estes ensaios.
- Referências: REQ-AUT-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m6-m8-validacao-isolada`; entrega identificável por `git log -1 --format=%H --grep="test(web): comprova permissões e isolamento de sessões em M6"`; envio/CI no fechamento desta execução.
- CHG-004: Aceite histórico EV-M6-022/023 preservado. Novo mecanismo não coberto: AUTH-L03/L04/L05 em WEB-021/024 devem provar inatividade, teto absoluto, login CSRF/Origin, rotação da senha, logout/revogação, cookies e isolamento profissional/participante; nenhuma credencial durável no cliente.

### WEB-024 — Concluir revisão de segurança com evidências negativas

- Marco: M6. Prioridade: P0. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-021, WEB-023.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Threat model atualizado, XSS/IDOR/limites/erros/logs e grants verificados; achados impeditivos corrigidos, sem reduzir proteções; M6 aceito.
- Testes/verificação: `tests/test_web_security_review.py, tests/test_web_proxy_config.py, tests/test_local_auth.py, tests/test_local_auth_http.py; web/e2e/local-auth/auth.spec.ts, web/e2e/integrated/sessions-security.spec.ts; scripts/verify_web_ci.py (sources, secret-self-test, python, frontend, browser, integration, audit), scripts/smoke_web_compose.py, scripts/smoke_local_auth_restore.py`.
- Evidências: `EV-M6-021/024` (2026-11-06); AUTH-L01–L09 e regressões de WEB-022/023 comprovados sem skips.
- Riscos/bloqueios: R05, R07 e R12 permanecem abertos como riscos residuais para os marcos posteriores (DEC-03/WEB-033 em M9, WEB-032 em M8 e M10); nenhum achado técnico impeditivo aberto em M6.
- Referências: REQ-AUD-001, REQ-SEG-001, REQ-AUT-004/005/006; [arquitetura](ARQUITETURA_WEB.md), [threat model](seguranca/THREAT_MODEL.md).
- Git da entrega: branch `feat/m6-autenticacao-local`; entrega e fechamento registrados em `EV-M6-021/024`.
- CHG-004: AUTH-L01–L09 e regressões novas de WEB-022/023 comprovados na SHA candidata local: hash/segredos, lista local SecLists (10.898 hashes), força bruta/enumeração/DoS, provisionamento/recuperação, sessões/rotação, admin/IDOR/grants (migration 0013), corte OIDC 404 fora de `APP_ENV=test`, Compose sem Google, restore isolado exigindo `recover` e logs sanitizados. R12 permanece residual; decisão institucional em WEB-033, sem ciclo com M6.

### EV-M6-021/024 — encerramento da autenticação local e revisão de segurança, 2026-11-06

Autorização: comando canônico `continue o projeto` no marco vigente **M6**
(pós-M3 aceito), concluindo `WEB-021` e `WEB-024` na branch
`feat/m6-autenticacao-local` (base `7872863`) e encerrando no limite de M6 sem
avançar implicitamente a M4.

Entregas técnicas consolidadas além de `EV-M6-021-BASE` e `EV-M6-021-HTTP`:

1. **Corte OIDC e configuração padrão (`API_AUTH_MODE=local`)**: `api/config.py`
   adota `auth_mode="local"` por padrão; `oidc` fica restrito a fixtures legadas
   com `APP_ENV=test` e é recusado em `development`/`production`. No modo
   `local`, `GET /api/v1/auth/login`, `/api/v1/auth/callback` e `/oauth2callback`
   retornam `404 not_found` fechado com `Cache-Control: no-store` e cabeçalhos
   de segurança, sem consultar provedor externo.
2. **Lista local de senhas comprometidas/comuns**: `scripts/build_password_blocklist.py`
   gera `stroop/domain/password_blocklist.py` com **10.898 digests SHA-256**
   normalizados (NFKC, 15–128 caracteres) extraídos da SecLists
   (`docs/seguranca/SECLISTS_LICENSE.md`, licença MIT), além das regras de
   substrings proibidas (`stroop`, `cognifit`, `psychopy`, `postgres`, `admin`,
   username) e repetição/sequência trivial, sem consultar serviços externos.
3. **Gestão transacional e último admin local (`0013_local_user_management.sql`)**:
   migração aditiva **0013** atualiza `public.web_manage_user` para proteger o
   último administrador **local** ativo (mesmo na presença de administradores
   Google históricos), recusar criação de principal `urn:stroop:local` pelo
   runtime e revogar todas as sessões locais ativas na mesma transação ao
   bloquear conta ou alterar perfil. `POST /api/v1/admin/users` permanece
   bloqueado com `403 permission_denied` no modo local.
4. **Revisão de segurança e testes negativos (`WEB-024` / `AUTH-L01`–`AUTH-L09`)**:
   `tests/test_web_security_review.py` ampliado com `LocalAuthSecurityReviewTests`
   cobrindo corte OIDC 404 sem acionar provedor, separação de cookies e recusa
   de cookie duplicado no modo local, `Origin` único exato e limite de 4 KiB em
   `/api/v1/auth/login` e `/api/v1/auth/password`, e sanitização de logs em erro
   interno de `/api/v1/auth/login` (nenhum vazamento de senha, hash, token,
   cookie ou username nos registros `api.request`). `web/e2e/administration.spec.ts`
   alinhado ao contrato local CHG-004 (ausência de botão `Cadastrar conta`,
   criação de projetos, vínculo/revogação de membros, `Encerrar sessões` via
   `POST /api/v1/admin/users/{id}/sessions/revoke` e `PATCH` de conta).
5. **Infraestrutura Docker/Compose e restauração isolada sem ressuscitar acesso**:
   `Dockerfile.api`, `compose.web.yaml`, `deploy/web.env.example` e
   `scripts/smoke_web_compose.py` operam com `API_AUTH_MODE=local` sem secrets
   Google obrigatórios. Novo `scripts/smoke_local_auth_restore.py` comprova que,
   após `backup` e `restore` criptografado em banco/projeto exclusivos, a API
   permanece parada até `recover` por terminal de operador, tokens/sessões e
   senhas anteriores ao backup e intermediários são recusados (`401`), o novo
   login pós-recuperação funciona (`credential_version=3`) e a avaliação
   científica (16 tentativas, 12 métricas, 16 observações, recibo canônico e
   vínculos) permanece íntegra.

Ambiente observado nesta sessão: Linux `7.0.0-42-generic` x86_64, Python
`3.12.3`, Node `24.15.0`, npm `11.16.0`, Docker `29.9.2`, PostgreSQL
`17.6-bookworm` (`sha256:f3bd19c606e442c3d7bdfa8002e03fe260a1023351e0ea4598032022b68dd6e3`)
em container descartável `stroop-m6-session-20261106` (tmpfs, porta `127.0.0.1:32781`,
banco `stroop_etapa4_test_m6_session`, removido ao final), Playwright `1.64.1`,
Chromium `156.0.8078.4` e Firefox `157.0`. Nenhum container preexistente, dado
real ou arquivo `.env` operacional foi tocado.

Comandos executados e resultados reais (0 skips em todas as suítes):

- `.venv/bin/python -m unittest tests.test_web_security_review tests.test_web_proxy_config -v`:
  **21 aprovados em 1,078 s**, 0 falhas, 0 skips.
- `TEST_DATABASE_URL="postgresql://stroop_test:stroop_test_password@127.0.0.1:32781/stroop_etapa4_test_m6_session" PYTHONPATH=tests .venv/bin/python -m unittest tests.test_local_auth tests.test_local_auth_http tests.test_web_security_review tests.test_web_proxy_config tests.test_postgres_migrations tests.test_web_database_provision tests.test_web_administration_provisioned -v`:
  **74 aprovados em 53,840 s**, 0 falhas, 0 skips.
- `.venv/bin/python scripts/verify_web_ci.py sources`:
  **393 fontes versionadas verificadas**, 0 achados.
- `.venv/bin/python scripts/verify_web_ci.py secret-self-test`:
  **aprovado** (fonte inócua aceita e token sintético bloqueado sem expor valor).
- `.venv/bin/python scripts/verify_web_ci.py frontend`:
  **300/300 testes Vitest aprovados em 19 arquivos** (3,23 s), `tsc --noEmit` e
  `vite build` (541 ms) aprovados.
- `.venv/bin/python scripts/verify_web_ci.py audit`:
  **npm audit (0 vulnerabilidades) e pip-audit (No known vulnerabilities found)** aprovados.
- `TEST_DATABASE_URL="postgresql://stroop_test:stroop_test_password@127.0.0.1:32781/stroop_etapa4_test_m6_session" .venv/bin/python scripts/verify_web_ci.py python`:
  **429 aprovados em 184,083 s**, 0 falhas, 0 erros, 0 skips.
- `TEST_DATABASE_URL="postgresql://stroop_test:stroop_test_password@127.0.0.1:32781/stroop_etapa4_test_m6_session" .venv/bin/python scripts/verify_web_ci.py integration`:
  **40/40 aprovados em 12,3 min** (`playwright.integration.config.ts`, Chromium e
  Firefox) + **10/10 aprovados em 34,5 s** (`playwright.local-auth.config.ts`,
  Chromium e Firefox), 0 falhas, 0 skips.
- `.venv/bin/python scripts/verify_web_ci.py browser`:
  **104/104 aprovados em 2,5 min** (casos gerais) + **4/4 aprovados em 3,6 min**
  (`@timing` serial), totalizando **108/108 em Chromium e Firefox**, 0 skips.
- `.venv/bin/python scripts/smoke_web_compose.py --build-images --api-image stroop-web-api:m6-final --proxy-image stroop-web-proxy:m6-final`:
  **aprovado** (build das imagens, PostgreSQL/migrations/provisionamento,
  bootstrap local, login/sessão/CSRF, corte OIDC 404, 9 caminhos sensíveis
  negados no proxy, coleta sintética completa e limpeza da pilha).
- `.venv/bin/python scripts/smoke_local_auth_restore.py --api-image stroop-web-api:m6-final --proxy-image stroop-web-proxy:m6-final`:
  **aprovado** (`status=passed`, `old_token_rejected=true`,
  `old_passwords_rejected=true`, `new_login_status=200`,
  `principal_and_project_grant_preserved=true`, `credential_version=3`,
  `assessment_preserved=true`, `trials_preserved=16`, `metrics_preserved=12`,
  `observations_preserved=16`, `restore_closed_until_operator_recovery=true`).
  Imagens temporárias `stroop-web-api:m6-final` e `stroop-web-proxy:m6-final`
  removidas ao final.

Falhas intermediárias preservadas nesta sessão:
- Invocação combinada `.venv/bin/python scripts/verify_web_ci.py sources secret-self-test frontend audit`
  retornou `exit 2` porque `scripts/verify_web_ci.py` aceita apenas uma etapa
  posicional por chamada; corrigido executando cada etapa separadamente.
- Primeira execução de `.venv/bin/python scripts/verify_web_ci.py browser` teve
  **102 aprovados e 2 falhas** (Chromium e Firefox em `e2e/administration.spec.ts:11`,
  aguardando o rótulo antigo `sub verificado` / `Cadastrar conta` removido de
  `AdministrationPanel.tsx` por CHG-004, enquanto `e2e/integrated/administration.spec.ts`
  já refletia o contrato local). Atualizado `web/e2e/administration.spec.ts` para
  testar o contrato local (ausência de `Cadastrar conta`, criação de projeto,
  vínculo/revogação de membro, `Encerrar sessões` e `PATCH` de conta), após o
  que a etapa `browser` passou integralmente (**104 + 4 aprovados, 0 falhas**).

Conferência de todos os critérios de `WEB-021`, `WEB-024` e do marco `M6`:
todos comprovados. `WEB-021` e `WEB-024` passam a `CONCLUIDA`, encerrando **M6
(4/4)** e elevando o progresso global para **22/45 (48,9%)**. Limites mantidos:
autenticação local técnica não resolve `DEC-03`/`WEB-033` (adequação institucional
da conta compartilhada e risco `R12`), não substitui réplica externa `WEB-031`,
release candidata `WEB-032`, integração de produto `M4`/`M5` nem validação
física/metodológica `M9`. Git, envio e CI no fechamento da Retomada vigente.

### EV-M6-022/023 — autorização e sessões reais sintéticas, 2026-11-06

Autorização excepcional desta sessão permite M6 após M2 aceito, sem dispensar
conta/cliente externo para WEB-021. Base ensaiada `851ac3a`; novo teste HTTPS
na branch `test/m6-m8-validacao-isolada`. Nenhuma alteração no runtime, grants,
cookies, políticas, schema, método ou dependências. Novo teste
`web/e2e/integrated/sessions-security.spec.ts` cobre lacuna de integração.

Critérios conferidos: perfis consulta/importacao/admin em consulta, importação,
convites e administração; administrador sem vínculo e acesso cruzado recebem
404; consulta não escreve; bloqueio, expiração e revogação revalidados; papéis
restritos de leitura/escrita provisionados no harness. Sessão participante usa
cookie Secure/HttpOnly/SameSite=Lax, invisível ao JS; troca de tokens entre
nomes de cookie falha. Origin ausente/divergente, CSRF ausente/divergente ou da
outra sessão negam escrita/logout. Logout profissional invalida replay e
mantém participante; logout participante remove cookie e invalida replay.
Expiração participante não gera avaliação, armazenamento local permanece vazio.
Cookie profissional de produção emitido pelo callback é conferido em teste
HTTP com exchange OIDC double; no browser sua sessão é provisionada localmente.
Isso não comprova login Google interativo, que continua bloqueado em WEB-021.

Ambiente: Python 3.12.3, Node 24.15.0, PostgreSQL 17.6 em container exclusivo
`stroop-session-m6-20261106`, tmpfs, porta aleatória loopback, banco
`stroop_etapa4_test_m6`. HTTPS certificado efêmero, API real/papéis restritos e
React build atual; Chromium/Firefox do Playwright 1.64.1. Sem dados reais,
secrets operacionais, produção, PR/merge/deploy. Contagens/fixtures sintéticas.

Comandos/resultados locais:

- `PYTHONPATH=tests TEST_DATABASE_URL=<PG sintético> .venv/bin/python -m unittest
  tests.test_web_auth tests.test_web_assessments tests.test_web_sessions
  tests.test_authentication tests.test_web_oidc_callback tests.test_google_oidc -q`:
  **76 aprovados**, sem skips; `tests.test_web_imports -q`: **4 aprovados**, sem skips.
- `npm --prefix web test`: **292 aprovados**, 18 arquivos, sem skips.
- `npm --prefix web run build`: tipos/build aprovados.
- Em web: `TEST_DATABASE_URL=<PG sintético> npx playwright test --config
  playwright.integration.config.ts sessions-security.spec.ts participant.spec.ts
  dashboard.spec.ts --grep 'separa credenciais|cookie HttpOnly|painel HTTPS'`:
  **10/10 aprovados**, cinco por navegador, sem retries/skip, 29,8 s. Inclui
  leitura/detalhe/CSV e revogação por três perfis, sem aceitar antecipadamente M5.

Falhas preservadas: primeira invocação Python por módulo não definiu PYTHONPATH
exigido pelo import legado de test_web_oidc_callback: 72 executados, um erro de
importação. Repetição com `PYTHONPATH=tests` passou os 76; nenhum teste enfraquecido.
Primeira tipagem do novo E2E recusou união de headers opcionais; array recebeu
tipo `Record<string,string>[]` e build passou. Aviso legado depreciação TestClient
não motivou instalação/upgrade. Mensagem negativa de break-glass é esperada em
teste de CLI; não foi recuperação operacional. Nenhuma falha funcional observada.

WEB-022/023 aceitas; M6 permanece incompleto por WEB-021/024. WEB-024 mantém
PENDENTE por dependência, sem review final artificial. Git/envio/CI consolidados
no fechamento desta sessão; hash do próprio registro consultável no Git.

## M7 — Integração, compatibilidade histórica e transição

- Objetivo: Retirar a importação manual de CSV do produto WEB (`CHG-005`), comprovar compatibilidade histórica de exportação e vínculos legados verificáveis, e preparar a substituição operacional sem retirar legado nem modificar coletas.
- Justificativa: Dados operacionais passam a ser cadastrados e produzidos diretamente na plataforma WEB; CSV permanece exclusivamente como funcionalidade de exportação para o usuário.
- Inclui: Retirada de `CsvImportPanel` e de rotas de upload CSV do modo produto (`WEB-025`), roundtrip dos CSVs exportados com pipeline/CLIs (`WEB-026`), vínculo explícito legado e associação verificável de registros pseudonimizados anteriores a cadastros centrais (`WEB-027`), e matriz de cobertura operacional e paridade do fluxo unificado em 3 eixos (`WEB-028`).
- Exclui: Remoção física de PsychoPy/Streamlit/CLIs, migração automática por coincidência de nome/código ou acesso a banco de coleta real.
- Pré-requisitos: M5 e M6 aceitos.
- Dependências: M5, M6.
- Entregáveis: Produto WEB sem upload CSV de usuário, intercâmbio sintético de exportação e cobertura funcional revisada pelo proprietário.
- Componentes afetados: `web/src/components/ProfessionalDashboard.tsx, CsvImportPanel.tsx, api/imports.py, stroop/ingestion/, CLIs, docs/operacao/`.
- Testes necessários: Ausência de upload CSV no modo produto, roundtrip de exportação, legado e associação de entidades por mapa explícito auditado; CLIs/launchers e consultas preservados (EXP-CSV-01).
- Critérios de aceite: Retirada de importação CSV no produto comprovada, cobertura necessária validada e sem concessão de acesso ou fusão cadastral por coincidência textual.
- Riscos: R06, R07, R08, R13.
- Decisões externas: Revisão do proprietário da cobertura (`WEB-028`); retirada física de Streamlit/legado é autorização futura independente.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-025 — Revalidar importação minimizada e status idempotente

- Marco: M7. Prioridade: P0. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-020, WEB-024.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: CHG-005 (`REQ-CSV-004`): retirar a tela de importação CSV (`CsvImportPanel.tsx`), comandos visíveis de importação no dashboard e bloquear/retirar os endpoints de upload CSV (`POST/GET /api/v1/projects/{project_id}/imports/{operation_id}` retornando `404`/`410`) no modo operacional do produto WEB, garantindo que dados operacionais entrem apenas pelo fluxo de cadastro e execução da plataforma. Preservar isoladamente os módulos internos `stroop/ingestion/` e validadores para compatibilidade técnica/CLI e testes unitários sintéticos, mantendo o escopo histórico documentado.
- Testes/verificação: `tests/test_web_imports.py; Vitest e Playwright em HTTPS real comprovando ausência de upload CSV na UI e bloqueio no modo produto (EXP-CSV-01)`. 5 testes unitários backend aprovados; 4 testes Playwright em Chromium e Firefox aprovados; verificação integrada comprovando retorno 410 Gone (`csv_import_disabled`). Ver EV-M7-025.
- Evidências: EV-M7-025, 2026-11-08; `CsvImportPanel.tsx` e comandos de importação retirados de `ProfessionalDashboard.tsx`; endpoints `POST/GET /api/v1/projects/{project_id}/imports/{operation_id}` retornam 410 Gone no modo produto; ingestão isolada preservada para testes sintéticos e CLI.
- Riscos/bloqueios: R06, R07 superados no escopo do produto; dados operacionais entram exclusivamente pela plataforma WEB.
- Referências: REQ-CSV-002, REQ-CSV-004; [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md), [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `feat/m7-transicao-e-compatibilidade-historica`; commits e PR integrados na conclusão de M7.

### WEB-026 — Comprovar intercâmbio histórico por fixtures sintéticas

- Marco: M7. Prioridade: P1. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-025.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: CSV 21 campos exportado pela plataforma WEB (`stroop_21_colunas`) e demais granularidades aplicáveis compatíveis em roundtrip com os validadores Python/SQLite e CLIs preservados; unidades e 16 tentativas `main` íntegras; sem depender de upload CSV na interface WEB e sem leitura/migração de coletas existentes.
- Testes/verificação: `tests/test_csv_unificado.py, test_importar_csv_sqlite.py, test_web_export.py, test_web_multi_export.py`. Todos os 27 testes de roundtrip e regressão aprovados, mais 9 testes de exportação multi-granularidade aprovados. Ver EV-M7-026.
- Evidências: EV-M7-026, 2026-11-08; roundtrip de CSV canônico 21 colunas com `analisar_stroop.py` (0 erros de validação, 12 métricas oficiais calculadas) e SQLite `import_csv` (1 avaliação, 16 tentativas e 12 métricas importadas); roundtrip das 5 granularidades avançadas em SQLite aprovado.
- Riscos/bloqueios: R04, R06 superados; intercâmbio sintético comprovado sem acesso ou modificação de coletas reais.
- Referências: REQ-CSV-001; [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md), [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `feat/m7-transicao-e-compatibilidade-historica`; commits e PR integrados na conclusão de M7.

### WEB-027 — Revalidar vínculo explícito de dados legados

- Marco: M7. Prioridade: P1. Complexidade: M. Estado: CONCLUIDA.
- Dependências: WEB-026, WEB-047.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Projeto de rótulo coincidente sem mapa não acessa (`web_legacy_project_links`); mapa autorizado e desativação cobertos; reader somente leitura; sem provisionar mapa real. CHG-005: validar procedimento autorizado, verificável e auditado (`web_legacy_entity_links` e `web_registry_audit_events`) para associar registros pseudonimizados anteriores (`web_project_participants` / `evaluator` textual histórico) aos cadastros centrais `web_patients` e `web_evaluators`, proibindo reconciliação ou fusão automática por coincidência de nome ou código.
- Testes/verificação: `tests/test_web_assessments.py, test_web_database_provision.py, tests/test_web_evaluators.py`. 3 testes em `test_web_evaluators.py` e 19 testes em `test_web_assessments.py` aprovados no PostgreSQL real descartável. Ver EV-M7-027.
- Evidências: EV-M7-027, 2026-11-08; `link_legacy_entity`, `deactivate_legacy_entity_link` e `list_legacy_entity_links` implementados em `web_registry.py` e expostos em `api/administration.py`; testes reais comprovam vínculo explícito com reason_code, gravação em `web_registry_audit_events`, desativação reversível e recusa categórica de merge automático por coincidência de strings.
- Riscos/bloqueios: R06, R13 superados; auditoria completa sem fusão automática de participantes legados.
- Referências: REQ-AUD-002, REQ-PAR-005; [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md), [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `feat/m7-transicao-e-compatibilidade-historica`; commits e PR integrados na conclusão de M7.

### WEB-028 — Revisar cobertura e plano de substituição operacional

- Marco: M7. Prioridade: P1. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-027.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Matriz Streamlit/React com capacidades requeridas testadas, incluindo o fluxo completo `CHG-005` e o modelo unificado de 3 eixos `CHG-006` / `ADR-008` (análise unificada com filtros reativos e exportação CSV, aplicação direta em etapa única com modalidades presencial "Iniciar Agora" e remota "Link / QR Code", e gestão cadastral secundária), paridade operacional frente ao Streamlit e ao PsychoPy Runner, lacunas tratadas e proprietário aprova transição; Streamlit e CLIs legados permanecem preservados sem remoção física; M7 aceito.
- Testes/verificação: Revisão documental e formalização da [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md); atualização da matriz de recursos e continuidade em `docs/operacao/TRANSICAO_WEB.md`; execução das suítes de testes unitários, integração e browser. Ver EV-M7-028.
- Evidências: EV-M7-028, 2026-11-08; consolidação do fluxo em 3 eixos (aplicação direta presencial/remota em 1 etapa, análise reativa estilo Streamlit e exportação avançada multi-granularidade); preservação integral de launchers (`abrir_dashboard.sh/bat`), CLIs (`analisar_stroop.py`, `importar_csv_sqlite.py`) e código Streamlit; marco M7 integralmente aceito (4/4).
- Riscos/bloqueios: R08, R10 superados na transição operacional; Streamlit e ferramentas locais mantidos sem quebra de suporte histórico.
- Referências: requisitos transversais do marco, ADR-004, ADR-007 e [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md); [TRANSICAO_WEB.md](operacao/TRANSICAO_WEB.md).
- Git da entrega: branch `feat/m7-transicao-e-compatibilidade-historica`; commits e PR integrados na conclusão de M7.
- CHG-004: Paridade deve comparar capacidades autorizadas Streamlit/React, incluindo login local, logout/sessões e limitação de autoria individual (AUTH-L07). Aprovação do proprietário continua necessária; nenhuma remoção Streamlit autorizada.
- CHG-005: Comprovar que a plataforma WEB substitui controles externos de cadastro e upload CSV, mantendo CSV exclusivamente como exportação.
- CHG-006: Comprovar a experiência de uso unificada em 3 eixos e o fluxo direto de sessões (REQ-INT-004, REQ-INT-005, REQ-SESS-001, REQ-SESS-002, REQ-SESS-003) na matriz de transição operacional.

## M8 — CI, infraestrutura e preparação operacional

- Objetivo: Consolidar experiência profissional e integridade analítica antes da candidata, além de pipeline/empacotamento/recuperação existentes.
- Justificativa: CI e restauração já implementadas não podem ser tratadas como só futuras.
- Inclui: Build isolado, pipeline por SHA, HTTPS, backup, réplica/agenda, restauração sintética e WEB-048..055 (CHG-007).
- Exclui: Deploy, alteração de VPS/DNS/certificado operacional ou gatilho nesta fase documental.
- Pré-requisitos: M1 aceito; integração final com M7 antes de M9.
- Dependências: M1; WEB-032 exige M7.
- Entregáveis: Experiência profissional integrada CHG-007, release candidata reproduzível e retorno compatível com schema.
- Componentes afetados: `Dockerfiles, compose.web.yaml, web/deploy/, deploy/, scripts/verify_web_ci.py, .github/workflows/`; CHG-007 inclui também `web/src/`, `api/`, `stroop/application/`, `stroop/domain/`, `stroop/persistence/`.
- Testes necessários: Build/smoke isolados, pipeline local e Actions autorizado, recuperação e benchmark limitados ao ambiente medido; casos COMP7/NAV7/QUERY7/DATA7/ANALYTICS7/EXPORT7/PREP7/UX7-AA e jornadas UX7-J1..J3.
- Critérios de aceite: Sem skip obrigatório; WEB-048..055 aceitas; consulta, gráficos, prévia e CSV consistentes; restauração íntegra e runbooks executáveis por SHA no escopo autorizado.
- Riscos: R08, R09, R14, R15.
- Decisões externas: Destino de réplica e chaves sob custódia; teste externo só com autorização específica; CI verify em PR conforme workflow vigente, sem mudar proteções.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-029 — Revalidar imagens e Compose isolado em HTTPS

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-004.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Build e saúde reais, proxy único público, limites/headers e rejeição de fontes aprovados; pilha temporária separada dos volumes operacionais.
- Testes/verificação: `scripts/smoke_web_compose.py, tests/test_web_runtime.py, test_web_proxy_config.py`. 17 testes runtime/proxy aprovados; build e smoke Compose/HTTPS reais aprovados, incluindo nove rotas de fonte/configuração recusadas. Ver EV-M8-029/031.
- Evidências: EV-M8-029/031, 2026-11-06; imagens com tags exclusivas, proxy/API/PG reais, recursos descartáveis e fluxo sintético persistido.
- Riscos/bloqueios: R08/R09 preservados para release/operação; nenhum impedimento do ensaio local. Não aceita VPS/produção ou OIDC externo.
- Referências: REQ-INF-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m6-m8-validacao-isolada`; hash/envio/CI no fechamento desta sessão.
- CHG-004: Aceite histórico preservado; reexecução local de imagens/configuração sem Google exigida em WEB-032 (AUTH-L08/L09), sem transferência de CI anterior.

### WEB-030 — Reproduzir pipeline e definir validação formal sem PR automático

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: CONCLUIDA.
- Dependências: WEB-029.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Runner local passa testes/PG, frontend/build, scanner/auditoria, browsers e integração; verificação Actions por SHA quando autorizada, sem alterar proteções/gatilhos por conveniência.
- Testes/verificação: `scripts/verify_web_ci.py all`, doze testes do runner e workflow_dispatch existente na mesma SHA: todos estágios locais/remotos aprovados, sem skips. Ver EV-M8-030.
- Evidências: EV-M8-030, 2026-11-06; SHA `0d79fd297f169ad25c63402dbd11c535694a0b98`, pipeline integral local e Actions 42159898317 aprovados. Procedimento formal sem PR em CI_WEB.
- Riscos/bloqueios: R09 preservado para recursos/gates operacionais; nenhum impedimento nos critérios do pipeline. Primeira falha scanner preservada na evidência.
- Referências: REQ-EXT-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch `test/m6-m8-validacao-isolada`; candidato `0d79fd2` enviado e Actions por SHA aprovado. Fechamento documental posterior sem transferir CI ao novo HEAD.
- CHG-004: Aceite histórico por SHA preservado; WEB-021/032 devem integrar testes locais e revisar locks/harnesses/fixtures OIDC e scanners sem alterar gatilhos/proteções nem remover regressões para obter passe.

### WEB-031 — Ensaiar restauração, réplica e retorno compatível

- Marco: M8. Prioridade: P0. Complexidade: G. Estado: BLOQUEADA.
- Dependências: WEB-029; destino externo de teste autorizado se necessário.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Massa sintética restaurada isoladamente, schema/dados/recibo conferidos; réplica+agenda+alerta e retorno de imagem ensaiados, RPO/RTO medidos e limites aceitos.
- Testes/verificação: `scripts/smoke_web_recovery.py`, `scripts/smoke_web_replication.py`, `scripts/smoke_local_auth_restore.py`, `tests/test_web_backup_replication.py`, `tests/test_vps_rollback.py`. EV-M8-031-MINT comprova restauração positiva/negativa, conteúdo em 21 tabelas, cadastros/vínculos/auditoria, SSH local/idempotência/hostkey incorreta, timer com cópia/atraso/indisponibilidade e rollback. Réplica VPS→notebook ainda não ensaiada.
- Evidências: EV-M8-029/031 histórica preservada; EV-M8-031-MINT, 2026-11-12: receptor Mint instalado, 36 testes locais, 14 migrations/uma avaliação/16 tentativas/12 métricas restauradas. Cópia 2,079 s/118.821 bytes; restore da cópia 9,285 s, exclusivamente locais. Sem RPO/RTO externo comprovado.
- Riscos/bloqueios: R08/R09. Notebook autorizado como destino temporário e identidade SSH exclusiva preparada. Proprietário/operador deve fornecer host/porta/usuário e fingerprint confiável, aprovar instalação restrita da chave/exportador na VPS e comprovar custódia AES separada. Depois medir ensaio externo e recuperação ponta a ponta. Notebook intermitente não garante RPO 24 h em desligamentos prolongados; RTO 4 h não presumido nem limite dispensado. Procedimento concreto no runbook; nenhuma alteração/conexão à VPS nesta execução. WEB-032 permanece dependente.
- Referências: REQ-INF-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega parcial: branch `test/m6-m8-validacao-isolada`; commit/envio/CI no fechamento desta sessão.
- CHG-004: Réplica externa independente continua obrigatória; após evolução de schema local, WEB-032 revalida restauração de hashes/sessões com custódia e invalidação de sessões restauradas para não ressuscitar acessos. RPO/RTO externo requer medição e aceite, não conta Google.
- CHG-005: Como o backup PostgreSQL passará a incluir tabelas cadastrais nominais (`web_patients` e `web_evaluators` da migration `0014`), o ensaio de restauração e réplica criptografada deve comprovar integridade dos cadastros, vínculos e trilhas de auditoria sem expor nomes em logs operacionais.

### EV-M8-031-MINT — receptor temporário e ensaios sintéticos, 2026-11-12

Autorização explícita do proprietário para preparar Linux Mint como receptor,
automação local e ensaios sintéticos. Exclui modificações na VPS sem nova
aprovação. A sessão abriu no Ambulatório CPS; localizada a árvore correta do
Stroop sem alteração naquele repositório. Base `d6d9dbb57310cc517f81e4d6a7d32a0b1fc4f0c3`,
branch `feat/web031-receptor-mint`; preservados `.deploy-hostgator/`, commits
preexistentes e proibição de integrar a ancestralidade do PR #18. Sem commit,
push, PR, merge, deploy ou acesso à VPS nesta entrega. CI não executada para
esta árvore de trabalho; não transferir resultados remotos de outro SHA.

Após pedido de desfazer e posterior pedido explícito de recuperar na mesma
data, arquivos e recursos privados foram recuperados de
`/tmp/stroop-web031-undo-skz33sb2`. Patch integral, instalador, conteúdo da
release e permissões conferidos; branch original da entrega recriada, timer
enabled/active e Linger=yes restabelecidos. Origem SSH continua ausente,
sem acesso à VPS. Ensaios funcionais abaixo são os da execução anterior,
não reexecutados nesta recuperação. A imagem de teste foi reconstruída com
camadas em cache: manifesto de runtime
`sha256:cbb236e086379e678007c78cdb30b33e72bab282c40ba1e593dbd2ec1b84a6e2`
e configuração idênticos aos originais; a nova atestação mudou o índice da
tag para `sha256:0fa1ea4db088e76a7602cb4d28051294b827a8eb5b63bbd71437fe34ca59ff1f`.
O identificador anterior abaixo é evidência histórica da rodada ensaiada.

Receptor instalado pelo `scripts/install_web_backup_receiver.py`, Python 3.12
do Mint 22.2 com `cryptography` existente, sem instalar pacotes no host:

- Ciphertext em `/home/raposo/.local/share/stroop-web-replica/backups`, 0700;
  configuração/SSH exclusivos em `/home/raposo/.config/stroop-web-replica`, 0700,
  chave Ed25519 0600. Chave AES operacional não lida/copiada nem colocada nesse
  diretório de backups. AES sintética em `synthetic-recovery.key`, na pasta
  privada de configuração, separada do ciphertext de qualificação.
- Release local por conteúdo
  `648beff840f5ccad3a991159a2d9fa3f1344b42696d101e9800681f247045e81`,
  arquivos 0400/diretórios 0500. Timer `stroop-web-backup-pull.timer`
  **enabled/active**, agenda horária + até 5 min aleatórios, disparo de startup
  em 2 min e `Persistent=true`; `Linger=yes` conferido após habilitação.
  Units aprovadas por `systemd-analyze --user verify`; reinício físico não feito.
- Serviço com CPUQuota 10%, MemoryMax 128 MiB, Nice 19, IO idle, UMask 0077,
  NoNewPrivileges e timeout 420 s, sem restauração periódica. Último JSON
  sanitizado atômico em `status/last-result.json`; journal/exit 1 identificam
  falha sem canal externo. Status antigo deve ser identificado por `checked_at`.
- `pull.json` **ausente** e `known_hosts` vazio até verificação da origem;
  `pull.json.pending` é somente exemplo privado. Disparo real do serviço
  terminou com `ExecMainStatus=1`, `alert=true`, `status=unavailable`, conforme
  esperado nesta preparação. Não declarar automação operacional a partir disso.

Comandos de integração, na raiz, usando `--api-image
stroop-web-api:web031-20261112 --proxy-image stroop-web-proxy:deploy-6196c39`:

1. `.venv/bin/python scripts/smoke_web_replication.py` com esses argumentos e
   `--synthetic-backup-directory /home/raposo/.local/share/stroop-web-replica/qualification
   --synthetic-key-file /home/raposo/.config/stroop-web-replica/synthetic-recovery.key`:
   **passed**. SSH real somente em loopback, chave/hostkey efêmeras, forced
   command rejeitou shell e hostkey errada foi recusada. SHA-256/bytes exatos,
   repetição sem novo download/substituição, timers reais de cópia positiva,
   geração de 25 h (`stale`, saída 1) e servidor parado (`unavailable`, saída 1).
   Cópia restaurada em PG tmpfs sem portas; nenhum banco existente usado.
2. `.venv/bin/python scripts/smoke_web_recovery.py` com os mesmos argumentos:
   **passed**, backup+restore **10,004 s**, conteúdo divergente com mesma
   contagem rejeitado, recibo desvinculado rejeitado, outage detectado e imagem
   candidata inválida revertida para a imagem anterior, contagens preservadas.
3. `.venv/bin/python scripts/smoke_local_auth_restore.py` com os mesmos
   argumentos: **passed**, snapshot restaurado fechado até recuperação,
   senha/token antigos recusados e login novo 200; conta/vínculo do projeto,
   16 tentativas/12 métricas/16 observações/recibo preservados. API restaurada
   testada por TestClient após recuperação; não confundir com tráfego na VPS.

Comparação origem→restore usa contagem + SHA-256 ordenado do conteúdo em
**21 tabelas**, inclusive schema_migrations, resultados, hashes/sessões locais,
cadastros e auditorias. Massa nova contém 14 migrations, um paciente, um
avaliador, um projeto/membro/participante/visita/convite/sessão/avaliação, 16
tentativas/observações, 12 métricas, dois eventos cadastrais e sete de auditoria
profissional. Vínculos paciente/avaliador/convidado e códigos científicos
conferidos na origem e conteúdo integral preservado no restore. Nenhum nome,
cookie, hash de credencial ou dado de participante é impresso nos relatórios.

Imagem API construída localmente do código da base com allowlist, sem novos
locks/migrations: `sha256:46b8ab6b66d693c42a6b7d41c1edda7e3215f17d7473a97b815ae54cfe0f1fbd`.
Identificação completa é consultável por `docker image inspect
stroop-web-api:web031-20261112`; proxy preexistente
`sha256:fad12ab57fae24a7f3da5ebe0eb44d0e188d2e218751b8178da72654f62be366`.
SSH foi instalado exclusivamente na imagem descartável do harness. Containers,
volumes, timers transitórios, imagem SSH e chaves efêmeras próprios removidos;
mantidos somente cliente/timer locais e ciphertext/AES **sintéticos** separados
para futuro ensaio externo autorizado.

Consumo do cliente medido com `/usr/bin/time`: cópia **2,079 s**, **0,49 s CPU
usuário + 0,05 s sistema**, pico **25.420 KiB RSS**, payload **118.821 bytes**;
repetição **1,22 s**, **0,38 + 0,03 s CPU**, **25.224 KiB RSS**, sem novo download
de ciphertext. Inclui cliente Python/SSH, não soma todos containers Docker;
overhead de rede SSH não medido. Restore da réplica **9,285 s**; idade pontual
**6,725 s**, não RPO externo. Ausência de configuração: **0,21 s**, CPU
**0,17 + 0,02 s**, **21.840 KiB RSS**, sem rede. Não extrapolar fixture para
volume real: retenção atual verifica hashes locais e seu custo cresce com
tamanho/número de gerações. Política preservada em 30 gerações recebidas;
cliente atual consulta só a última geração, sem recompor dias intermediários
perdidos enquanto desligado. Disco local alocado observado por `du -sk`:
48 KiB de cliente, 20 KiB de configuração/chaves e 204 KiB de estado,
ciphertext sintético e proposta para a VPS; **272 KiB** no total, sem somar
imagens Docker de teste. Diretório de backups operacionais recebidos vazio.
Ver orçamento máximo de disco no runbook.

Regressão: **36 testes, zero falhas/skips**, com `.venv/bin/python -m unittest
tests.test_backup_web tests.test_web_backup_replication tests.test_vps_rollback
tests.test_monitor_web tests.test_hardening_producao.BackupEncryptionTests
tests.test_hardening_producao.ProductionConfigurationTests -v`. Integração real
está nos três harnesses, não inferida desses testes unitários. Documentação
aprovada: 90 documentos/729 links/114 âncoras, grafo sem ciclos; sete testes
do verificador aprovados sem skips e `git diff --check` limpo. Units validadas
e `git status --short` revisado; somente arquivos da unidade e o diretório
preexistente preservado aparecem. Nenhum backup/credencial adicionado ao Git.

Falhas anteriores preservadas: duas tentativas ao montar massa via correção
posterior de vínculos falharam na asserção de resposta de `relink`; HTTP/corpo
não registrados. Inspeção indica possível falta de grants UPDATE no runtime
para essa rota, fora desta unidade; não houve diagnóstico conclusivo nem
correção de produção. Responsável técnico deve reproduzir isoladamente antes
de alterar provisionamento/WEB-047. Aceite histórico não reaberto por inferência.
O harness final cria os vínculos pelo convite cadastral canônico e os verifica,
sem dispensar integridade para obter passe.

Próxima dependência externa concreta: pacote local de proposta
`/home/raposo/.local/share/stroop-web-replica/server-proposal/f64df30748913afd14e4e1d3a2d4c5091d8e61b2f1e609d37f3bc457267f6674.tar.gz`,
com hashes, wrapper de origem exclusivamente sintética e linha de chave SSH
restrita preparada. **Não enviado/instalado**. Procedimento para aprovação no
[runbook](operacao/WEB_RECUPERACAO.md#procedimento-proposto-para-aprovação-específica-na-vps).
Bloqueio/responsável/condição: proprietário deve conferir origem/hostkey e
aprovar instalação restrita; operador depois mede réplica/restore externos e
custódia. Intermitência impede garantir 24 h em longos desligamentos; RTO 4 h
depende de medição ponta a ponta. **WEB-031 permanece BLOQUEADA**, sem dispensa
de critério, sem conclusão de M8/WEB-032 nem autorização de publicação.

### WEB-032 — Fechar release candidata e runbooks reproduzíveis

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-028, WEB-030, WEB-031, WEB-024, WEB-055.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Manifesto por SHA/imagens/schema, capacidade no ambiente medido, runbooks backup/retorno/incidente e custódia revisados; M8 aceito sem publicação.
- Testes/verificação: `scripts/benchmark_web.py; PLANEJADO: revisão de release e CI real aplicável`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R08, R09; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.
- CHG-004: Candidata deve incluir WEB-024 local aceita, AUTH-L08/L09, manifesto/schema/locks novos, runbooks sem cliente Google obrigatório, provisionamento/recuperação e invalidação de sessões no restore/rollback. Réplica externa WEB-031 e M7 continuam impeditivos; nenhuma publicação.
- CHG-005: Candidata deve incluir schema aditivo `0014`, suítes `CAD-01..03`, `PREP-01`, `DASH-01`, `EXP-CSV-01` e `E2E-FLOW-01` verdes no pipeline por SHA, e smoke Compose atualizado para o fluxo com cadastro central de pacientes/avaliadores e sem upload CSV de produto.

- CHG-007: Candidata só após WEB-048..055 aceitas, com evidência de igualdade consulta→prévia→CSV, UX integrada, acessibilidade e CI verify na SHA candidata. Aceites WEB-029/030 preservados; nenhuma tag/release/deploy implícitos.

### WEB-048 — Padronizar identidade pública e componentes visuais

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PRONTA.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Converter a marca Cores e a UI heterogênea em uma fundação reutilizável para os três eixos.
- Inclui: Marca Stroop Test Web no cabeçalho, início, área profissional, título da aba, metadados, navegação e textos institucionais; inventário de referências públicas; tokens e catálogo completo de componentes da decisão UX7-VIS.
- Exclui: Renomear test_code/instrumento/protocolo, texto experimental aprovado, schema/CSV; motor, Streamlit, dependências por estética.
- Dependências: WEB-028, WEB-024.
- Requisitos relacionados: REQ-UX-013, REQ-UX-014, REQ-UX-016.
- Componentes afetados: `web/index.html, web/src/App.tsx, web/src/styles.css, web/src/components/; referências públicas vigentes em docs/`.
- Contratos envolvidos: Nenhuma mudança de payload; modelo científico e contrato HTTP preservados.
- Critérios de aceite: Busca auditada de ocorrências públicas de Cores/Correspondência distingue marca substituída de nome científico/histórico preservado; títulos contextuais usam Stroop Test Web. Todos os componentes UX7-VIS possuem contrato de uso e estados exercitados; módulos migram aos componentes ao serem integrados nas fichas seguintes.
- Critérios de UI/UX: Tokens delimitados ao shell administrativo; nenhuma cascata modifica estímulo/HUD. Escalas, hierarquia e ações primária/secundária/destrutiva obedecem UX7-VIS; sem caixas aninhadas para simples separação de texto.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: COMP7: Vitest por comportamento (teclado, erro preservando dados, foco e diálogo), TypeScript, build; regressão DOM de apresentação experimental; comparação de tokens usados.
- Testes manuais/visuais exigidos: Revisão visual do catálogo em Chromium/Firefox, dez cores experimentais preservadas por regressão quando CSS compartilhado for tocado; larguras/zoom de UX7-AA.
- Evidências: PLANEJADAS. Exigir data/SHA, comandos/resultados/ambiente e casos com dados inequivocamente sintéticos; confrontar cada critério, vínculos e contratos; screenshots não substituem comportamento. Registrar branch/commits/push/PR/verify/merge reais na execução.
- Riscos/bloqueios: R15: CSS global e troca indevida de nome científico. Sem bloqueio técnico conhecido.
- Decisões externas necessárias: Nenhuma para marca/direção visual autorizadas nesta missão; mudança científica exige decisão separada.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### WEB-049 — Consolidar sidebar responsiva nos três eixos profissionais

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Materializar ADR-008 sem copiar as oito abas para um menu lateral.
- Inclui: Shell dos três eixos, títulos e navegação contextual, perfil/conta/logout, sidebar expandida/recolhida e drawer móvel; Gestão com pacientes/avaliadores/projetos/conta e operações existentes autorizadas; preservação do contexto em RAM.
- Exclui: Novos privilégios, editor genérico de auditoria, oito módulos como destinos principais, credenciais/dados na URL, fluxo experimental dentro da sidebar.
- Dependências: WEB-048.
- Requisitos relacionados: REQ-INT-004, REQ-UX-015, REQ-UX-016, REQ-UX-012.
- Componentes afetados: `web/src/App.tsx, ProfessionalDashboard.tsx, componentes de navegação e painéis cadastrais/administrativos existentes`.
- Contratos envolvidos: Cookies, CSRF, perfis e projetos do contrato HTTP/autenticação; rotas internas sem dados sensíveis.
- Critérios de aceite: Exatamente três destinos de primeiro nível por capacidade autorizada; overview/resultados/histórico/exportação compõem Eixo 1. Abrir detalhe e voltar mantém recorte aplicado, ordenação/página válidas e posição; logout/401/403 limpa dados e previews. Menus não concedem acesso negado pelo servidor.
- Critérios de UI/UX: Desktop expandido/recolhido, rótulo acessível em ambos, ativo/hover/focus/disabled, atalhos para conteúdo e conta em posição estável; drawer fecha com Escape e restaura foco. Sem formulário de emissão dominando a abertura analítica.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: NAV7: Vitest de rotas/perfis/transições; Playwright teclado, voltar/avançar, logout, viewport e ausência de dados/segredos em URLs; tipos/build.
- Testes manuais/visuais exigidos: Percorrer três eixos sem mouse; transição de análise→Gestão→análise sem reaplicar consulta; perfil sem acesso não vê ação e requisição direta também nega.
- Evidências: PLANEJADAS. Exigir data/SHA, comandos/resultados/ambiente e casos com dados inequivocamente sintéticos; confrontar cada critério, vínculos e contratos; screenshots não substituem comportamento. Registrar branch/commits/push/PR/verify/merge reais na execução.
- Riscos/bloqueios: R15: fragmentação reaparece em submenus. Ajustes dependentes da consulta única completam-se em WEB-050/052.
- Decisões externas necessárias: Nenhuma para navegação; expansão de operações administrativas exige novo escopo.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### WEB-050 — Unificar estado aplicado de consulta e descartar respostas obsoletas

- Marco: M8. Prioridade: P0. Complexidade: G. Estado: EM_ANDAMENTO.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Impedir que KPIs, gráficos, histórico e exportação representem consultas distintas.
- Inclui: Objeto de consulta normalizado, rascunho/aplicada, Aplicar explícito, chips/remover/limpar, dimensões REQ-REL-004, seleção de instrumento/versão/plataforma incorporada; geração de consulta e cancelamento; contexto único para todos os consumidores.
- Exclui: Persistência de resultados/consulta nominal no cliente, filtros só locais como controle de acesso, novo cálculo científico, aplicação automática a cada tecla.
- Dependências: WEB-017, WEB-019, WEB-020, WEB-024.
- Requisitos relacionados: REQ-REL-004, REQ-REL-006, REQ-INT-005.
- Componentes afetados: `web/src/dashboard/, ResearchFilters.tsx, ProfessionalDashboard.tsx, web/src/api/assessments.ts, aggregate.ts, exports.ts`.
- Contratos envolvidos: Contrato alvo CHG-007 de consulta no HTTP, sem duplicar catálogo REQ-REL-004.
- Critérios de aceite: Aplicar publica uma única geração; editar mostra alterações pendentes e bloqueia download até aplicar ou descartar; todos os consumidores usam mesma chave. Remover chip/limpar edita rascunho com ação de aplicar visível. Resposta fora de ordem não substitui contexto novo; erro de página/snapshot expira conjunto inteiro, sem total parcial. Detalhe fora do recorte exige retorno/ação explícita.
- Critérios de UI/UX: Combobox/MultiSelect com busca e labels; filtros principais e avançados sob expansão; resumo aplicado legível; alteração pendente não se confunde com carregamento ou recorte vazio.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: QUERY7: Vitest de estado puro e consumidor; fake HTTP controlado fora de ordem/projeto/instrumento; Playwright voltar/avançar, erro de paginação, snapshot expirado, revogação e logout; tipos/build.
- Testes manuais/visuais exigidos: Aplicar filtros combinados, navegar em detalhes e exportação; inspecionar que todos exibem chave/contexto coerentes e nenhuma resposta antiga reaparece após troca rápida de projeto.
- Evidências: núcleo, seleção no servidor e React pelo POST único em EV-M8-050, 2026-11-11/12; ver comandos, falhas intermediárias, evidência real e limites abaixo. Sem aceite integral de WEB-050 ou antecipação dos gates WEB-051/053/055.
- Riscos/bloqueios: R14: catálogo residual e agregações/CSV v2 ainda exigem capacidades próprias. Busca/faixas/RT ausente e ordenação migrados ao servidor; campos sem suporte são recusados. UX7-AA e integração WEB-051/053/055 permanecem gates próprios.
- Decisões externas necessárias: Nenhuma: aplicação explícita formalizada como complemento à reatividade da ADR-008.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### EV-M8-050 — núcleo da consulta aplicada compartilhada, 2026-11-11

Execução posterior de M8 autorizada pelo responsável com `continue o projeto`.
Unidade técnica: `dashboard/query.ts` normaliza dimensões, defaults e identidade
local (não é fingerprint de conteúdo/autorização); formulário único controlado
em RAM mantém rascunho/aplicada entre visão geral, histórico, análises e
exportação. Aplicar publica uma geração e cancela lista/detalhe/downloads
anteriores; chips/limpar somente editam, descartar restaura a consulta aplicada.
Instrumento/versão/plataforma não têm seletores paralelos de efeito imediato.
Projeto de preparação é independente da consulta analítica; nenhum storage/URL.

Busca em multisseleções mantém selecionados visíveis. Catálogo de instrumentos
é obtido sem restringi-lo ao instrumento aplicado, permitindo troca direta;
opções são autorizadas pelo mesmo endpoint. Carregamento/erro das opções não
substitui validação/autorização da consulta no servidor, nem impede reaplicar
um recorte conhecido; atualização da consulta também atualiza opções. Página
com erro/cursor repetido/mais de 5.000/snapshot inconsistente não publica totais
parciais. HTTP 401/403 nas consultas encerra a visualização profissional;
409 em detalhe/download invalida o conjunto. Revogação mascarada como 404
continua negada pelo servidor, conforme integrações existentes.

Caminho agregado existente só é habilitado com snapshot completo e filtros
básicos suportados; edição pendente cancela download, e qualquer filtro avançado
não suportado impede CSV sem o recorte. UI da exportação avançada permanece
**desabilitada** no dashboard até vínculo de seleção/token no servidor em
WEB-051/053; código/backend das exportações anteriores preservado. Isso é uma
restrição temporária explícita de integridade, não aceite de EXPORT7.
Tabela mista identifica instrumento e apresenta somente colunas comuns,
sem desalinhamento entre linhas Stroop e instrumentos genéricos.

Estado: **EM_ANDAMENTO**, sem novo aceite. Ainda faltam multisseleção completa
de instrumento/condição/resposta e integração ao contrato alvo normalizado
(tipos atuais reutilizam o catálogo anterior); busca, status e faixas avançadas ainda usam
seleção local histórica até WEB-051. Condição/resposta foram migradas para seleção
no servidor na continuação registrada abaixo; esta descrição inicial é histórica. Nenhum aceite de população A/T, nova
cardinalidade, fórmula, snapshot/fingerprint servidor ou CSV avançado é alegado.
Matriz UX7-AA integral (cinco larguras, zoom/reflow, contrastes e revisão com
leitor de tela) não foi concluída. Verificações de 390 px/zoom 200% e árvores/DOM
existentes são evidência limitada, não conformidade AA. Não avançar WEB-051 como
CONCLUIDA por implicação. WEB-048 continua PRONTA; WEB-031 bloqueada externamente.

Ambiente local: Linux 7.0.0-42-generic, Node 24.15.0, npm 11.16.0, Python
3.12.3; Playwright 1.64.1, Chromium 156.0.8078.4/Firefox 157.0. Sem instalar/atualizar dependências, sem CSS experimental, migrations,
produção ou acesso a fontes protegidas. PG 17.6 em container **exclusivamente
sintético** `stroop-m8-query7-synthetic-20261111`, tmpfs e porta efêmera local,
banco `stroop_etapa4_test_query7`; harness HTTPS existente usa API/grants reais.

Validação e Git: resultados finais registrados no fechamento desta evidência;
branch `feat/m8-consulta-aplicada-unica`, base `67dfbf7`. PR #18 aberto sem
merge (verify histórico aprovado em `67dfbf7`, não transferido à nova entrega),
auto-merge desabilitado. A branch contém ancestralidade documental desse PR;
não integrar à main por outra via enquanto a instrução específica vigorar.
Material `.deploy-hostgator/`, PRs #16/#17 e main preservados.

#### Validação local desta unidade

- `npm --prefix web test -- --reporter=dot`: **336/336**, 28 arquivos, sem
  skips; inclui duas verificações puras de normalização/exportação, quatro
  casos de consumidor com promessas que ignoram cancelamento e formulário.
- `npm --prefix web run build`: TypeScript e Vite aprovados; mantém aviso de
  chunk JS acima de 500 kB (540,15–540,17 kB conforme build). Sem alteração de
  dependências/limite para esconder o aviso.
- Em `web/`: `WEB_TEST_PORT=4289 npx playwright test
  e2e/applied-query.spec.ts e2e/research-filters.spec.ts
  e2e/aggregate-export.spec.ts e2e/dashboard.spec.ts
  e2e/complete-results.spec.ts e2e/invitations.spec.ts
  e2e/presentation.spec.ts --workers=2 --trace=off
  --output=test-results/query7-final`: **76/76**, Chromium 156.0.8078.4 e Firefox
  157.0. Inclui dez cores/centro/HUD, teclado, consultas fora de ordem,
  rascunho/aplicada, expiração, logout e voltar/avançar após encerramento.
  API double HTTP local; não prova autorização PG. Houve aviso React de
  `flushSync` no encerramento durante lifecycle em uma fixture negativa Firefox.
  Experimento local separou o handler de sessão encerrada do pagehide, mas a
  regressão adicional manteve o aviso: tentativa revertida integralmente, App
  permanece idêntico à base. Causa do aviso não determinada; nenhum teste
  funcional falhou por ele. Não foi suprimido nem considerado resolvido.
- Em `web/`, `TEST_DATABASE_URL` aponta somente para o banco descartável acima:
  `npx playwright test --config playwright.integration.config.ts
  e2e/integrated/dashboard.spec.ts e2e/integrated/filters.spec.ts
  e2e/integrated/complete-results.spec.ts e2e/integrated/aggregate-export.spec.ts
  --output=test-results/query7-https-final`: **14/14**, sem skips,
  **2,4 minutos**. HTTPS/proxy, React compilado, API e PG/grants reais; perfis,
  todos os projetos/páginas, 105 registros, filtro reduzido, RT nulo, outros
  instrumentos, detalhe e CSV confrontados com dados sintéticos. API/PG não
  modificados; não testa ainda o futuro POST analysis/query ou EXPORT7 avançado.
- `python3 scripts/verify_web_docs.py`, sete testes
  `python3 -m unittest tests.test_verify_web_docs -q` e `git diff --check`:
  aprovados, 11 marcos/56 tarefas/75 requisitos/15 riscos/cinco decisões,
  **37 aceitos**, 90 documentos, 727 links/112 âncoras, grafo acíclico.
  Nova evidência não aumenta o numerador. Inspeção visual de screenshot sintético
  390 px realizada; sem alegar campanha UX7-AA ou aprovação visual do proprietário.

Regressão adicional após investigar o aviso: em `web/`,
`WEB_TEST_PORT=4290 npx playwright test e2e/applied-query.spec.ts
 e2e/navigation.spec.ts e2e/administration.spec.ts e2e/research-filters.spec.ts
 --workers=2 --trace=off --output=test-results/query7-auth-final`: **42/42**;
mesmo aviso Firefox preservado. Não altera os 76 passes da campanha anterior.
Scanner `.venv/bin/python scripts/verify_web_ci.py sources`: **426 fontes
versionadas verificadas**, sem achado; dados/histórico fora do escopo. Container
PG sintético criado nesta sessão removido após a integração, sem tocar qualquer
outro container/volume. Artefatos de teste permanecem ignorados.

Falhas intermediárias preservadas: 328/329 Vitest antes de revisar o teste que
aplicava Limpar automaticamente; 331/332 por Response única reutilizada na
fixture de opções (corrigida para resposta nova por fetch); dois dos quatro
novos testes de consumidor falharam por seletores que supunham aria-label na
tabela/texto do botão (corrigidos para classe/label reais). Primeira campanha
filtros/exportação falhou por nomes de busca/listbox ambíguos e expectativa
antiga após 403; corrigidas as receitas sem reduzir isolamento, 26/26 aprovados.
Regressão intermediária 31/34 detectou seletor de preparação omitido em três
perfis/estados; restaurado em todos, preservando sua independência do recorte.
Campanha seguinte 42/44 falhou no seletor exato implícito de precisão; corrigido
para nome/papel acessível real, dez novos casos passaram nos dois navegadores.

Primeira integração: **seis passes, três falhas, um interrompido e quatro não
executados**, parada por SIGINT no processo de teste da sessão após confirmar
causas corrigíveis. Instrumento era retirado do próprio catálogo ao selecioná-lo
(corrigido fetch de opções); erro de opções desabilitava Aplicar indefinidamente
(corrigido sem burlar autorização servidor); alerta de opções e alerta da consulta
exigiam escopo explícito na assertiva. Um diagnóstico isolado com trace sintético
ignorando servidor novo localizou a primeira falha; não é aceite. Campanha
final integral dos 14 casos passou após correções, sem aumentar timeouts/gates.
Duas tentativas de comando usaram prefixo web/ duplicado dentro de web e falharam
antes de criar o arquivo temporário pretendido; corrigidos os caminhos, sem
alterar ambiente operacional. Artefatos/traces sintéticos somente ignorados ou
em /tmp; nenhum log/export/coleta versionado. Suíte Python funcional completa e
auditorias de dependência não reexecutadas localmente (sem alteração backend/locks);
Actions verify da entrega tem estado próprio, registrado no fechamento Git.

#### Fechamento Git desta unidade

Entrega em **`07473b906f75982cb37f53ee778b33fd99fcdba5`**, branch
`feat/m8-consulta-aplicada-unica`, push com upstream confirmado por igualdade
HEAD/upstream/ls-remote. **20 arquivos da tarefa**, sem App (experimento
revertido), dependências, dados ou material de deploy. Build/tipos e 336 testes
Vitest reexecutados após o commit, todos aprovados; CSS emitido preserva mesmo
hash `index-mVgr7SNY.css` e bundle `index-6EHd1uPz.js` da campanha HTTPS final.

[PR #19](https://github.com/thiagorraposo/stroop-test-web/pull/19) **draft aberto**
para main; auto-merge desabilitado. `verify` em **IN_PROGRESS** na SHA 07473b9
na consulta desta sessão, execução [43124268881](https://github.com/thiagorraposo/stroop-test-web/actions/runs/43124268881).
Não é CI aprovada, e o fechamento documental posterior recebe seu próprio check.
PR #18 conferido aberto em `67dfbf7`, sem auto-merge; nenhum merge por esta
branch, para não integrar indiretamente sua ancestralidade. Sem deploy/tag/release.

WEB-050 continua **EM_ANDAMENTO**, progresso 37/56 e M8 2/12 preservados.
Próxima ação técnica: completar catálogo de seleção e serialização normalizada
conforme contrato alvo, com capacidades/rejeição explícita dos recortes ainda
não suportados; conferir UX7-AA da ficha antes do aceite. Não declarar WEB-051
pronta por código parcial. WEB-048 continua independente e PRONTA; WEB-031
continua bloqueada por recursos/autorização externos, impedindo WEB-032.
Fechamento documental identificável por `git log -1 --format=%H
--grep='docs(web): registra unidade parcial de WEB-050 e PR de revisão'`;
confirmar envio por HEAD/upstream/remoto, sem commit artificial de autorreferência.

#### Continuação — multisseleção de instrumentos, 2026-11-11

Novo `continue o projeto` mantém o escopo em M8 e retoma WEB-050 na mesma
branch, inicialmente em `b4382e6`, alinhada ao upstream após fetch. Main e
origin/main em `b5fccbb`; `.deploy-hostgator/` preexistente preservado sem leitura
ou staging. PR #19 permanece draft: a proibição de integrar a ancestralidade
do PR #18 continua vigente e impede merge mesmo se os checks passarem.

Entrega **`7f43295423e994d2bca9684187391a5723c2a95a`**:

- Instrumento passa a listbox múltiplo pesquisável, com selecionados preservados
  durante busca, chip removível e publicação somente ao aplicar. A identidade
  local normaliza ordem/duplicatas e torna string única/lista unitária equivalentes.
- API/listagem e persistência SELECT recebem até 100 instrumentos como OR no
  mesmo recorte. Não são consultas paralelas nem filtro posterior local.
  Cursor e snapshot vinculam a seleção completa; reordenação é equivalente,
  troca de instrumento recusa reaproveitamento. Valores inválidos e excesso
  retornam 422. Facetas mantêm contrato anterior com instrumento único.
- CSV agregado recebe a mesma seleção integral e revalida todos os vínculos;
  clientes antigos com `test_code` string continuam compatíveis. A projeção
  existente segue por instrumento; a UI não habilita CSV agregado de instrumentos
  mistos. Sem mudança de fórmulas, 21 colunas, motor, CSS, dependências ou schema.

Verificações locais, ambiente de EV-M8-050 preservado, sem instalações:

- `npm --prefix web test -- --reporter=dot`: **340/340**, 28 arquivos, sem skips;
  `npm --prefix web run build`: tipos e Vite aprovados, aviso de chunk >500 kB
  preservado (540,07 kB), CSS mantém `index-mVgr7SNY.css`.
- `TEST_DATABASE_URL` exclusivamente sintético,
  `.venv/bin/python -m unittest tests.test_web_assessments -q`: **21/21**, sem
  skips, em 22,768 s. Inclui união de dois instrumentos, paginação reordenada,
  recorte/cursor incompatível, snapshot/CSV, compatibilidade string/lista,
  limites e revogação; demais contratos de consulta regressados.
- Em `web/`, `WEB_TEST_PORT=4291 npx playwright test
  e2e/applied-query.spec.ts e2e/research-filters.spec.ts
  e2e/aggregate-export.spec.ts e2e/dashboard.spec.ts e2e/complete-results.spec.ts
  --workers=2 --trace=off --output=test-results/m8-multi-instrument`:
  **50/50**, Chromium/Firefox, 32,2 s; HTTP double, sem alegar integração real.
- Em `web/`, `TEST_DATABASE_URL` sintético, `npx playwright test
  --config playwright.integration.config.ts e2e/integrated/complete-results.spec.ts
  e2e/integrated/filters.spec.ts e2e/integrated/aggregate-export.spec.ts
  --output=test-results/m8-multi-instrument-https`: **8/8**, Chromium/Firefox,
  58,5 s; HTTPS/API/PG e grants reais. Confere seis avaliações de dois instrumentos
  na mesma consulta, rascunho/busca/seleção preservada, separação das tabelas e
  downloads incompatíveis desabilitados; regressa CSV, múltiplos projetos e
  revogação. PG 17.6 descartável em tmpfs no container próprio
  `stroop_etapa4_test_m8_continue`, banco homônimo, loopback porta efêmera 32769.
- Validador documental, sete testes do validador e `git diff --check` aprovados;
  scanner de secrets: **426 fontes versionadas**, sem achados. Somente fixtures
  sintéticas; nenhum dado operacional, secret ou material de deploy lido.

CI anterior conferida nesta sessão: `verify` da SHA **b4382e6** falhou na execução
[43124371410](https://github.com/thiagorraposo/stroop-test-web/actions/runs/43124371410),
com **45/46** integrações aprovadas. O caso CSP Chromium não encontrou o estímulo
principal em 8 s; Python, frontend, auditorias e navegadores isolados passaram
naquele run. Isso não prova regressão CSP nem explica a causa. Diagnóstico local
na base b4382e6: `npx playwright test --config playwright.integration.config.ts
e2e/integrated/security.spec.ts --repeat-each=3
--output=test-results/m8-csp-diagnostic`: **12/12**, 2,5 min, sem retries/skips,
nos dois navegadores, com HTTPS/API/PG reais. Nenhum timeout, gate científico,
CSP ou teste afrouxado; falha remota e ausência de causa comprovada preservadas.

WEB-050 permanece **EM_ANDAMENTO**, sem novo aceite e sem promover WEB-051.
Esta unidade resolve a multisseleção de instrumentos, mas ainda faltam condição/
resposta, serialização/integração ao POST normalizado do contrato alvo e UX7-AA
integral. WEB-048 continua PRONTA, WEB-031 bloqueada externamente; global 37/56,
M8 2/12.

Regressão integral: `TEST_DATABASE_URL` no banco descartável acima,
`.venv/bin/python scripts/verify_web_ci.py python`: **449/449**, sem skips,
141,875 s, exit 0. Inclui API base, auth, sessões, resultados, domínio, grants,
exportações e migrações sintéticas; não aplica migrações operacionais. O runner
rejeita skips; mensagens internas de auditoria sintética recusada pertencem aos
testes negativos do próprio runner, não a uma auditoria de dependências desta
sessão. Auditoria de dependências não reexecutada localmente (locks intactos).
Container descartável próprio removido ao final; demais containers preservados.

Fechamento desta continuação: commit funcional `7f43295`; commit documental
identificável por `git log -1 --format=%H
--grep='docs(web): registra multisseleção validada e continuidade de M8'`.
Envio e estado do check da SHA final devem ser conferidos por
HEAD/upstream/`git ls-remote` e PR #19, sem commit artificial de autorreferência.
O novo `verify` permanece pendente até seu resultado por SHA; não transferir
os passes locais nem o diagnóstico CSP para aceite de Actions. PR #19 e PR #18
continuam abertos sem merge, auto-merge desabilitado. Sem deploy/tag/release.


#### Continuação — condição/resposta e reflow da consulta, 2026-11-11

Autorização renovada por `continue o projeto`; WEB-050 continua no marco M8 e
na branch `feat/m8-consulta-aplicada-unica`, base inicial `fc487cb`, alinhada ao
upstream após fetch. Main/origin/main `b5fccbb`. `.deploy-hostgator/` preexistente
preservada sem leitura/staging. Proibição específica de integrar PR #18 mantida,
inclusive pela ancestralidade do PR #19, que continua draft sem merge.

Entrega desta unidade:

- Catálogo pesquisável passa a usar multisseleções de condições congruente/
  incongruente e respostas canônicas hit/omission/commission/correct_rejection.
  Rascunho, chips, limpar, descartar e publicação explícita mantêm a mesma
  geração; normalização ordena/deduplica as duas dimensões. Resumo aplicado
  identifica ambas. Erro de capacidade é anunciado e associado ao formulário.
- GET de listagem aceita esses dois campos com allowlists e teto de 100 valores;
  exige instrumento Stroop explícito/exclusivo, recusando capacidade ausente ou
  mista com 422. Não cria suporte fictício em outros instrumentos nem nominal
  em URL. Cursor/snapshot vinculam o recorte integral com reautorização SELECT.
- PostgreSQL aplica **um único EXISTS main**: condição E resposta devem ocorrer
  na mesma tentativa, OR dentro de cada campo. Alternativas de classificação
  derivam de `stroop.domain.stroop.expected_outcome`, sem nova fórmula ou
  dependência de flags redundantes de acerto/erro. Prática excluída. Hidratação
  preserva métricas oficiais da avaliação inteira. Removida a aproximação React
  por totais de Go/No-Go/respostas, que não comprovava a conjunção em tentativa.
- Agregado legado recusa condição/resposta no servidor (422) e continua
  desabilitado na UI para esse recorte; não produz arquivo com filtros ignorados.
  Individual continua explicitamente o CSV oficial completo da avaliação.
- Corrigido reflow: grade de filtros permite coluna menor que 280 px, controles
  administrativos não impõem largura intrínseca e cabeçalho profissional quebra
  linha quando necessário. Seletores delimitados à administração; nenhuma
  alteração de DOM/tempos/HUD/estímulos do motor. Sem schema, migration,
  dependência, dados reais, configuração operacional, deploy, tag ou release.

Ambiente observado: Linux `7.0.0-42-generic`, Python 3.12.3, Node 24.15.0,
npm 11.16.0, Chromium 156.0.8078.4 e Firefox 157.0; dependências existentes.
PG 17.6 em container próprio `stroop_etapa4_test_m8_trials`, tmpfs, banco
homônimo, loopback porta efêmera 32770; somente fixtures sintéticas.

Validações desta unidade:

- `npm --prefix web test -- --reporter=dot`: **342/342**, 28 arquivos, sem skips;
  inclui equivalência de conjuntos, transporte integral, capacidade, seleção
  preservada na busca e rascunho/aplicação/descarte. `npm --prefix web run build`:
  TypeScript/Vite aprovados. Aviso de chunk >500 kB preservado (540,27 kB), sem
  alterar dependência/limite para ocultá-lo.
- `TEST_DATABASE_URL` exclusivamente no PG descartável acima,
  `.venv/bin/python scripts/verify_web_ci.py python`: **452/452**, sem skips,
  159,569 s, exit 0. Inclui três novos casos PG: oito combinações confrontadas
  com detalhe canônico, OR, mesma tentativa, prática excluída, flags redundantes
  inconsistentes, métricas completas, cursor reordenado/incompatível, mutação
  com mesma cardinalidade, exportação recusada, capacidade inválida e revogação.
  Regressão integral de API/auth/sessões/resultados/domínio/grants/CSV preservada.
- Em `web/`, `WEB_TEST_PORT=4292 npx playwright test e2e/applied-query.spec.ts
  e2e/research-filters.spec.ts e2e/aggregate-export.spec.ts e2e/dashboard.spec.ts
  e2e/complete-results.spec.ts e2e/presentation.spec.ts --workers=2 --trace=off
  --output=test-results/m8-trial-filters-browser`: **56/56**, 38,8 s, dois
  navegadores, HTTP double. Campanha anterior à correção CSS; não prova PG.
- Após CSS, em `web/`, `WEB_TEST_PORT=4293 npx playwright test
  e2e/research-filters.spec.ts e2e/presentation.spec.ts --workers=2 --trace=off
  --output=test-results/m8-trial-filters-layout-corrected`: **20/20**, 18,3 s.
  Inclui cinco larguras 360/768/1024/1366/1920, viewport de reflow 320, ampliação
  CSS 200% em 1366/1920 e 400% em 1280, foco/seleção e erro associado. Ampliação
  CSS é evidência automatizada limitada, não revisão manual de zoom nativo.
  Dez cores/centro/contorno e prática sem precisão regressados nos dois browsers.
  Quatro screenshots sintéticos de filtros (360 e 1366, por navegador) em
  diretório ignorado; inspeção visual de Chromium 360 e Firefox 1366 realizada.
  Não concede revisão visual do proprietário nem conformidade WCAG integral.
- Em `web/`, `TEST_DATABASE_URL` no banco descartável acima, `npx playwright
  test --config playwright.integration.config.ts e2e/integrated/trial-filters.spec.ts
  e2e/integrated/filters.spec.ts e2e/integrated/aggregate-export.spec.ts
  --output=test-results/m8-trial-filters-https-final`: **8/8**, sem skips, 50,3 s,
  HTTPS/proxy/React compilado/API/PG/grants reais em Chromium/Firefox. Confere
  recorte impossível vazio, OR, seleção conservada, métricas completas, contexto
  aplicado, exportação bloqueada, múltiplos projetos/páginas e revogação.
  Build final usa CSS `index-Cd1eQ5rm.css` e JS `index-8UK2m2v9.js`.
- `python3 scripts/verify_web_docs.py`, sete testes do validador e
  `git diff --check`: aprovados; 11 marcos/56 tarefas/75 requisitos/15 riscos/
  cinco decisões, 37 aceitos, 90 documentos/727 links/112 âncoras, sem ciclos.
  Scanner `.venv/bin/python scripts/verify_web_ci.py sources`: **427 fontes
  versionadas**, sem achados. Auditorias de dependências não reexecutadas
  localmente; locks intactos. Só artefatos sintéticos ignorados, sem export/coleta
  versionados. Container descartável próprio removido após os ensaios, sem tocar
  containers/volumes preexistentes.

Falhas intermediárias preservadas: primeira execução focada PG teve **23 passes
e um erro** na fixture que tentava gravar error_type fora da constraint. Ajustada
para valor válido porém incoerente (`omission`), sem alterar constraints/domínio;
regressão integral acima passou. Primeira matriz de layout falhou **2/2** em 320
nos dois browsers; diagnóstico Chromium confirmou coluna mínima 280 maior que
espaço do formulário. Após correção da grade, outra execução falhou **2/2** na
ampliação CSS 400%; diagnóstico Chromium localizou overflow no cabeçalho público
profissional. Correção delimitada de flex-wrap e campanha final 20/20, sem remover
asserções, ocultar overflow global ou reduzir requisitos. Aviso React histórico
`flushSync` reapareceu em cenários negativos Firefox; na campanha CSS houve
também `Cannot update ProfessionalAccess while rendering ResultsTable`. Causa
não comprovada, não suprimida nem declarada resolvida; testes passaram, mas isso
permanece limite de lifecycle a investigar na homologação integrada.

WEB-050 segue **EM_ANDAMENTO**. Multisseleção de instrumento/condição/resposta
está materializada, porém ainda faltam integração ao POST normalizado alvo,
capacidades/agregação integral servidor e UX7-AA completa (revisão critério a
critério, contraste, espaçamento/estados e leitor de tela efetivamente utilizado).
Orca 46.1 disponível localmente; sua versão consultada não equivale a ensaio com
leitor de tela. Não antecipar WEB-051/053 ou aceite integrado. Próxima ação exata:
materializar contrato normalizado do POST e sua capacidade explícita para os
recortes restantes, mantendo os gates de WEB-051 e revisão UX7-AA. WEB-048 segue
independente e PRONTA; WEB-031 bloqueada externamente. Global **37/56**, M8
**2/12**, sem novo aceite.

Git desta unidade identificável por `git log -1 --format=%H
--grep='feat(web): filtra condição e resposta na mesma tentativa'`.
Commit/push/PR/check por SHA no fechamento posterior; não inferir CI de testes
locais. Na consulta anterior ao novo envio, `verify` de **fc487cb** ainda estava
IN_PROGRESS na execução 43131698618 (integração HTTPS), sem aprovação atribuída.
PR #19 draft e PR #18 abertos, sem auto-merge/merge. Nenhum deploy/tag/release.

Fechamento Git da unidade de condição/resposta: entrega funcional/documental em
**`9c6c9dfb70486ab2d3b37dd9e54d1906746651f1`**, **18 arquivos**, push confirmado
por HEAD/upstream/ls-remote na mesma SHA. [PR #19](https://github.com/thiagorraposo/stroop-test-web/pull/19)
permanece draft aberto, descrição atualizada, auto-merge desabilitado; sem merge
pela restrição do PR #18. `verify` da entrega **QUEUED** na consulta, execução
[43134541360](https://github.com/thiagorraposo/stroop-test-web/actions/runs/43134541360),
sem atribuir aprovação. Fechamento documental posterior tem check próprio,
identificável por `git log -1 --format=%H
--grep='docs(web): registra seleção por tentativa e limites de M8'`;
conferir envio por HEAD/upstream/remoto, sem commit artificial de autorreferência.
Worktree final só conserva `.deploy-hostgator/` preexistente fora de escopo.
Sem deploy/tag/release; estado e próxima ação de WEB-050 preservados acima.

#### Continuação — entrada POST normalizada com capacidades parciais, 2026-11-11

Novo `continue o projeto` mantém autorização em M8. Base `ca8a114`, branch
`feat/m8-consulta-aplicada-unica`, inicialmente alinhada ao upstream após fetch;
main/origin/main `b5fccbb`. Material `.deploy-hostgator/` preservado sem leitura
ou staging. PR #18 aberto sem merge; a mesma restrição alcança PR #19 por
ancestralidade, independentemente do resultado de CI.

Implementado `POST /api/v1/analysis/query` com RequestModel estrito em todos os
níveis, Origin/CSRF, sessão profissional e DSN SELECT sem fallback. Normaliza
aliases de datas/código/plataforma, ordena/deduplica seleções e recusa aliases
contraditórios. O contexto público inclui consulta canônica, capacidades,
identificadores, prazo, fingerprints, contagens completas e página. Suporte
inicial: categorias/datas existentes, status valid, seleção explícita,
condição/resposta Stroop, quatro ordenações e agrupamento assessment/project
somente com contagens operacionais. Busca, faixas métricas, status operacionais,
IDs cadastrais, plataforma legacy sem proveniência própria e demais agrupamentos
retornam 422 sanitizado. Não são aceitos/ignorados.

A seleção ocorre em uma única transação REPEATABLE READ/READ ONLY: reautoriza
todos os projetos, limita A a 5.000, aplica seleção explícita antes do limite e
recusa IDs fora do recorte. Ambiguidade de legado em dois projetos falha fechada.
Condição/resposta mantém EXISTS na mesma tentativa; T conta somente main que
passam ambos. Métricas em items continuam da avaliação completa, pelo domínio
oficial. Participantes/visitas são contados por projeto/código, com definição
explícita; não é deduplicação cadastral ou união nominal entre projetos.
Fingerprints incluem conteúdo pseudonimizado relevante, inclusive estímulo;
cursor assinado vincula identidade, consulta, ordenação, conteúdo e prazo de
15 minutos. Alteração de mesma cardinalidade/expiração recusa paginação com 409;
limite/erro nunca produz 200 com prefixo parcial. Sem novo cálculo científico.

**Limites:** o React ainda consome GET e os filtros avançados locais históricos.
Não há integração ao POST da consulta aplicada na UI, catálogo integral ou
contexto de busca/exportação v2. A resposta informa exports=false; query_id
não autoriza downloads. Esta unidade não conclui WEB-050/051 e não concede
aceite AA ou funcional integrado. Avisos históricos de lifecycle permanecem
sem diagnóstico; frontend de produto/motor/CSS/bundle preservados.

Ambiente de EV-M8-050 preservado: Linux 7.0.0-42-generic, Python 3.12.3,
Node 24.15.0/npm 11.16.0, Chromium 156.0.8078.4/Firefox 157.0. PG 17.6 no
container próprio `stroop_etapa4_test_m8_post`, tmpfs, banco homônimo, porta
loopback efêmera 32771. Só fixtures sintéticas; sem dependências instaladas,
schema/migration novos, acesso operacional, deploy, tag ou release.

Validações:

- `TEST_DATABASE_URL` exclusivamente no PG descartável acima,
  `.venv/bin/python scripts/verify_web_ci.py python`: **456/456**, sem skips,
  168,138 s, exit 0. Inclui esquema fechado, aliases/capacidades, seleção vazia,
  subconjunto explícito em universo maior que 5.000, rejeição de 5.001 sem
  truncamento, paginação, identidade, expiração, conteúdo mutado, projetos
  inacessíveis/revogação, CSRF e ausência de DSN SELECT. Mensagens de auditoria
  sintética recusada e pipeline aborted pertencem aos testes negativos; o
  runner concluiu com todos os testes aprovados.
- Foco anterior `.venv/bin/python -m unittest tests.test_web_assessments -q`:
  **27/27**, 37,035 s; teste de normalização puro adicional aprovado. Primeira
  rodada focada teve **26 passes/um erro** por atributo inexistente no helper
  de revogação; corrigido para opaque_user_id e PUT real com active=false,
  sem alterar autorização. Nenhuma falha funcional omitida.
- `npm --prefix web run build`: tipos e Vite aprovados; bundle de produto
  idêntico à base (`index-Cd1eQ5rm.css`, `index-8UK2m2v9.js`). Aviso de chunk
  >500 kB preservado (540,27 kB). Vitest/browser double não reexecutados:
  nenhum fonte React/runtime experimental mudou.
- Em `web/`, `TEST_DATABASE_URL` sintético, `npx playwright test --config
  playwright.integration.config.ts e2e/integrated/analysis-query.spec.ts
  e2e/integrated/trial-filters.spec.ts
  --output=test-results/m8-normalized-post-https`: **4/4**, sem skips, 16,7 s.
  HTTPS/proxy/API/PG/grants reais em Chromium/Firefox; POST executado no browser
  autenticado, sem interceptação. Confere aliases, métricas completas, T,
  capacidades, recusa nominal/CSRF, revogação e storage vazio; regressa filtros
  React existentes. Não comprova migração da UI ao POST ou campanha UX7-AA.
- Verificação documental, sete testes do validador e diff check aprovados;
  scanner e Git registrados no fechamento abaixo. Auditorias de dependências
  não reexecutadas localmente; locks intactos. Artefatos/log temporário de teste
  somente ignorados ou em /tmp, nenhum export/coleta versionado.

WEB-050 permanece **EM_ANDAMENTO**; global **37/56**, M8 **2/12**. Próxima ação:
ampliar capacidades de seleção e migrar consumidores React ao POST único,
eliminando filtros locais históricos com capacidades explícitas e verificando
UX7-AA; WEB-048 continua PRONTA. WEB-031 bloqueada externamente impede WEB-032,
sem impedir esse ramo. Nenhum avanço a M9.

Entrega identificável por `git log -1 --format=%H
--grep='feat(web): adiciona entrada analítica normalizada com capacidades explícitas'`.
Conferir SHA/envio/check no fechamento desta unidade e HEAD/upstream/remoto;
PR #19 continua draft, auto-merge desabilitado e nenhum merge autorizado.

Fechamento desta unidade: entrega **`ee852f11f482af97ef0f4c460e8fcea9547957e3`**,
11 arquivos da tarefa; push com upstream confirmado por HEAD/upstream/ls-remote
na mesma SHA. Scanner: **430 fontes versionadas**, sem achados. Foco final de
contrato/reautorização após ajustar a adulteração do cursor para byte significativo:
**2/2 aprovados**, 1,642 s; evita dependência dos bits de padding base64 na fixture.
Container descartável próprio removido após os testes, demais recursos preservados.

[PR #19](https://github.com/thiagorraposo/stroop-test-web/pull/19) atualizado,
draft, auto-merge desabilitado. `verify` da SHA ee852f1 **IN_PROGRESS** na consulta
final, execução [43136318278](https://github.com/thiagorraposo/stroop-test-web/actions/runs/43136318278).
Não é CI aprovada. O fechamento documental posterior recebe seu próprio check;
consultar o SHA final, sem transferir aprovação local ou de outro commit.
Nenhum merge, publicação, tag ou release. Registro de fechamento identificável
por `git log -1 --format=%H
--grep='docs(web): registra POST analítico validado e continuidade de M8'`;
confirmar seu envio por HEAD/upstream/remoto, sem commit artificial de autorreferência.

#### Continuação — React na consulta POST única e seleção no servidor, 2026-11-12

Novo `continue o projeto` autoriza continuidade de M8 deixando WEB-031 pendente.
Base `d6d9dbb57310cc517f81e4d6a7d32a0b1fc4f0c3`; fetch confirmou main/origin/main
`b5fccbb` e branch/upstream sem divergência. Reutilizada
`feat/m8-consulta-aplicada-unica`, inicialmente no mesmo HEAD da branch
`feat/web031-receptor-mint`. Alterações locais da WEB-031 e `.deploy-hostgator/`
preservadas; somente hunks desta unidade entram no commit. Nenhum acesso à VPS,
backup operacional, secret ou dado real. A restrição específica de merge do
PR #18 continua alcançando a ancestralidade do PR #19.

O dashboard agora aplica e pagina exclusivamente pelo POST analysis/query.
Busca por substring literal do código do participante, precisão geral, faixas
de RT mediano, exclusão explícita de RT ausente e ordenação são executadas no
servidor, sobre métricas oficiais da avaliação completa hidratadas pelo domínio.
Precisão e RT requerem instrumento Stroop exclusivo; limites inferiores são
inclusivos, superiores exclusivos. RT nulo não vira zero; include_null_rt=true
inclui essa população explicitamente, false exclui inclusive sem faixa. Busca
não lê nome/iniciais e não faz pesquisa nominal, mesmo para administração.
Status operacionais estão desabilitados na UI e seguem recusados pela API.
Nenhuma mudança no motor, fórmulas, CSV científico, schema ou dependências.

Cliente normaliza aliases e confere resposta fechada, consulta canônica,
capacidades, contagens, IDs e metadados comuns entre páginas. Não publica totais
até concluir todo conjunto. Fingerprint/query_id/prazo divergente, cursor
repetido, duplicata, falha/limite ou expiração descartam o contexto completo;
resposta atrasada não substitui outra geração. A expiração local também cancela
detalhe/downloads e exige reaplicação, sem refresh silencioso. Navegar entre
análise/histórico/exportação preserva contexto e rascunho somente em RAM.
O consumidor deixou de aplicar filterAssessments/sortAssessments localmente;
helpers antigos foram preservados para compatibilidade, sem uso nessa seleção.

CSV básico preservado com legacy_export_context, tokens assinados das fontes de
resumo obtidas na MESMA transação RO da consulta. Somente dimensões já suportadas
pelo CSV v1 recebem esse contexto; busca/faixas/tentativas/exclusão de RT/seleção
explícita não recebem token. Exports=false ainda identifica ausência de prévia/
download v2. Não buscar snapshots por GET nem retirar filtros para exportar um
conjunto maior. A rota antiga reautoriza e verifica suas fontes a cada download.

Ambiente: Linux 7.0.0-42-generic, Python 3.12.3, Node 24.15.0/npm 11.16.0,
Playwright 1.64.1, Chromium 156.0.8078.4/Firefox 157.0. PG 17.6 em container próprio
`stroop_etapa4_test_m8_client`, tmpfs/porta loopback efêmera 32770, bancos
`stroop_etapa4_test_m8_client` (HTTPS) e `stroop_etapa4_test_m8_regression` (Python).
Todos exclusivamente sintéticos. Recursos temporários próprios serão removidos
após a conferência; não instalar/atualizar pacotes nem acessar produção.

Validações desta unidade:

- `npm --prefix web test -- --reporter=dot`: **356/356**, 29 arquivos, zero skips.
  Inclui parser fechado, transporte, ausência de fallback, faixas/aliases,
  expiração e consumidores com respostas que ignoram cancelamento.
- `npm --prefix web run build`: tipos/Vite aprovados; bundle
  `index-B6iIW6SI.js`, CSS `index-Cd1eQ5rm.css`. Aviso histórico de chunk >500 kB
  preservado (544,08 kB), sem mudar limites/dependências para escondê-lo.
- Em web/, `WEB_TEST_PORT=4289 npx playwright test e2e/applied-query.spec.ts
  e2e/research-filters.spec.ts e2e/dashboard.spec.ts e2e/aggregate-export.spec.ts
  e2e/complete-results.spec.ts e2e/invitations.spec.ts e2e/imports.spec.ts
  --workers=2 --trace=off --output=test-results/m8-post-query`: **78/78**, zero
  skips, 1,6 min. Doubles HTTP; não são prova de autorização PG. Inclui larguras
  360/768/1024/1366/1920, reflow 320, zoom 200%/400% nos filtros, sem constituir
  checklist AA integral. Aviso histórico flushSync em Firefox persiste; também
  observado aviso de atualização de ProfessionalAccess durante renderização em
  fixture de sessão. Nenhum foi suprimido ou declarado corrigido nesta unidade.
- `TEST_DATABASE_URL` no banco sintético de regressão,
  `.venv/bin/python scripts/verify_web_ci.py python`: **461/461**, zero skips,
  369,496 s. Resultado da árvore de trabalho com os arquivos locais preexistentes
  da WEB-031; validação da versão exata enviada tem registro próprio no fechamento.
- Em web/, `TEST_DATABASE_URL` no banco sintético HTTPS, `npx playwright test
  --config playwright.integration.config.ts e2e/integrated/analysis-query.spec.ts
  e2e/integrated/filters.spec.ts e2e/integrated/trial-filters.spec.ts
  e2e/integrated/dashboard.spec.ts e2e/integrated/complete-results.spec.ts
  e2e/integrated/aggregate-export.spec.ts
  --output=test-results/m8-post-query-https-confirmed`: **20/20**, zero skips,
  3,5 min, Chromium/Firefox. React compilado, HTTPS/proxy/API/PG/grants reais;
  105 registros, projetos/páginas, alias, recorte misto, busca por código/faixas/
  RT ausente, mesma tentativa, métricas completas, navegação sem reconsulta,
  CSRF/revogação e CSV básico confrontados. Sem interceptar respostas.
- Scanner `.venv/bin/python scripts/verify_web_ci.py sources`: **433 fontes
  versionadas**, sem achados. Documentação/links/grafo, sete testes do verificador
  e git diff --check: aprovados na árvore de trabalho; conferência do índice e fechamento abaixo.

Falhas intermediárias preservadas: testes antigos ainda esperavam rejeição de
patient_search/accuracy_min/include_null_rt no schema; agora verificam capacidades
atuais e recusas residuais, além de novos casos de fronteira reais. Vitest inicial
teve 337/342 por mocks GET antigos, seletor de placeholder e prazo sintético 2099
que excedia timeout do browser; fixtures migradas ao POST e prazo de 15 min,
342/342 antes dos novos testes e 356/356 na campanha final. Build seguinte recusou
tipos platform inferidos como string nos doubles novos; fixadas as fixtures com
literais, sem afrouxar tipos do produto. Primeiro teste de conflito do CSV alterava
word, fora das fontes do resumo; corrigido para alterar RT que afeta o CSV.
Foco API/schema final: **4/4**, 7,925 s, sem skips.
Primeira integração interrompida após identificar espera antiga pelo GET:
6 passes, timeout em complete-results e preparação de filters interrompida por
SIGINT (10 não executados). Campanha seguinte teve 18 passes/2 falhas no teste
novo que procurava a tabela de dashboard dentro de resultados; o módulo usa
cartão de contagem próprio. Corrigida a assertiva por superfície, preservando
contagens e exigência de não emitir nova consulta ao navegar. Sem aumentar
limites/timeouts ou reduzir gates.

Limites: catálogo residual inclui status operacionais, Go/No-Go, precisão Go/No-Go,
RT médio e IDs cadastrais; campos sem capacidade são recusados, não ignorados.
Busca nominal depende de seus gates próprios. Limite de 5.000 também vale para
candidatos antes das faixas métricas: servidor recusa universo maior, não trunca.
Não há novo dicionário/agregação científica ou exportação v2. Checklist UX7-AA,
contraste e revisão com leitor de tela ainda não executados integralmente;
Orca 46.1 disponível não significa revisão realizada. WEB-050 continua
**EM_ANDAMENTO**, WEB-051 permanece PENDENTE e nenhum aceite é antecipado.
Global **37/56**, M8 **2/12**. Próxima ação: completar catálogo/capacidades da
WEB-050 e seu checklist UX7-AA antes do aceite; WEB-048 permanece independente
PRONTA. WEB-031 segue bloqueada externamente e impede WEB-032; não avançar M9.

#### Fechamento Git e conferência da entrega isolada — 2026-11-12

Entrega **`7cc3562e4daef7220000b160121105bba45a509c`**, 32 arquivos, na branch
`feat/m8-consulta-aplicada-unica`; push com upstream confirmado por igualdade
HEAD/upstream/ls-remote. Nenhum arquivo/hunk da WEB-031, material de deploy,
backup, credencial ou coleta entrou no commit. A evidência local anterior da
WEB-031 permanece na árvore de trabalho; somente as atualizações desta unidade
foram extraídas para o índice nos documentos compartilhados.

Conferência adicional em checkout separado, exatamente **7cc3562**, sem os
arquivos alterados da WEB-031: `TEST_DATABASE_URL` no banco descartável de
regressão, `.venv/bin/python scripts/verify_web_ci.py python`: **459/459**,
zero falhas/skips, **356,455 s**. Os **461/461** acima pertencem à árvore com
trabalho preexistente; não são a contagem desse commit. Documentação do checkout:
**88 documentos/727 links/112 âncoras**, sete testes do validador aprovados,
diff check limpo. No índice antes do commit, catálogo/links também conferidos
por leitura dos blobs indexados; a árvore com material local adicional contou
90 documentos/729 links/114 âncoras, sem transferir esses arquivos à entrega.
Fontes api/stroop/web e os testes desta unidade permaneceram idênticos ao commit
após os testes frontend/HTTPS. Capturas sintéticas de filtros em Chromium 360 e
Firefox 1366 inspecionadas; não equivalem ao checklist AA integral. Nenhuma
baseline visual atualizada para esconder achado.

Container PG, seus dois bancos sintéticos e checkout temporário próprios
removidos após a validação. Cliente/timer/arquivos locais da WEB-031 e demais
recursos preexistentes preservados. Sem deploy, tag, release, dados reais ou M9.

[PR #19](https://github.com/thiagorraposo/stroop-test-web/pull/19) atualizado,
**draft aberto**, auto-merge desabilitado. `verify` de **7cc3562** estava
**IN_PROGRESS** na consulta de fechamento, execução
[43300961985](https://github.com/thiagorraposo/stroop-test-web/actions/runs/43300961985).
Não é CI aprovada. O commit documental de fechamento recebe check próprio;
consultar o SHA final sem transferir aprovação de outra revisão. PR #18 continua
aberto sem merge; sua ancestralidade não foi integrada indiretamente. A base
d6d9dbb teve verify SUCCESS (run 43136417744), preservado apenas historicamente.

Registro de fechamento identificável por `git log -1 --format=%H
--grep='docs(web): registra validação isolada da consulta POST'`; confirmar
HEAD/upstream/remoto sem commit artificial de autorreferência. WEB-050 segue
EM_ANDAMENTO, global 37/56 e M8 2/12. Próxima ação funcional preservada: catálogo
residual/capacidades e UX7-AA antes do aceite; WEB-048 independente PRONTA e
WEB-031 BLOQUEADA externamente.

### WEB-051 — Consolidar seleção analítica autorizada e agregações no servidor

- Marco: M8. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Base comum de integridade para análise multigranular e extração; limitar volume sem truncamento silencioso.
- Inclui: Parser fechado da consulta, seletor de avaliações/tentativas elegíveis, metadados/fingerprint, dicionário de indicadores UX7-DADOS, totais por identidade autorizada, qualidade de dados e agregações descritivas paginadas; plano de volume e índices só com evidência.
- Exclui: Fórmula científica nova/React, inferência clínica, infraestrutura distribuída/cache externo, schema/migration operacional; não inferir vínculo legado por texto.
- Dependências: WEB-050.
- Requisitos relacionados: REQ-REL-004, REQ-REL-007, REQ-REL-009, REQ-REL-010, REQ-AUT-002, REQ-MET-001, REQ-MET-002.
- Componentes afetados: `api/assessments.py, stroop/application/, stroop/persistence/web_assessments.py, stroop/domain/ e registry existentes`.
- Contratos envolvidos: Consulta CHG-007 no HTTP, MODELO_DE_DADOS, auth/grants, ADR-003/007; revisão de grants se leitura exigir colunas autorizadas, sem fallback writer.
- Critérios de aceite: AND entre dimensões/OR dentro; projetos reautorizados integralmente; status operacionais separados do conjunto científico. Quatro contagens de pacientes distinguidas; RT ausente não vira zero. Cada indicador referencia código oficial/fonte, denominador, exclusões, unidade e versão. Fixtures com avaliações repetidas, homônimos e legados não fundem identidades. 5.001 avaliações não produzem total de 5.000: caminho servidor completo ou recusa explícita conforme volume declarado no contrato.
- Critérios de UI/UX: API retorna unidades, disponibilidade, completude e incompatibilidade para UI; mensagens sanitizadas identificam ação de reduzir recorte/atualizar sem expor SQL/nomes.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: DATA7: unittest domínio/aplicação e API/PG sintético stroop_etapa4_test*, paridade oficial, filtros combinados, mapas de legado, isolamento/revogação, cardinalidades, todos os status, paginação e 5.000/5.001; EXPLAIN e medição sintética com volume/ambiente; regressão grants.
- Testes manuais/visuais exigidos: Confrontar dicionário com domínio Python e tabela analítica/fixture; revisar plano medido antes de escolher índices/cache; conferir contagens sem confundir cadastros e participantes.
- Evidências: PLANEJADAS. Exigir data/SHA, comandos/resultados/ambiente e casos com dados inequivocamente sintéticos; confrontar cada critério, vínculos e contratos; screenshots não substituem comportamento. Registrar branch/commits/push/PR/verify/merge reais na execução.
- Riscos/bloqueios: R14/R13; índices novos dependem de evidência e migration aditiva revisada na tarefa, jamais alterar migrations existentes. Não reduzir gates por custo de consulta.
- Decisões externas necessárias: DEC-03 para uso nominal real; nenhuma para testes sintéticos desidentificados. Incompatibilidade científica sem regra existente exige decisão metodológica antes de comparação.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### WEB-052 — Integrar dashboard multigranular com exploração e tabelas acessíveis

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Converter visualizações existentes em exploração contínua reproduzível e multigranular.
- Inclui: Hierarquia contexto→filtros→KPIs→tempo→distribuições→longitudinal→tabela→exportação; níveis projeto/institucional autorizado, instrumento/versão, participante/visita, avaliação, tentativa; interações e tabelas UX7-DADOS.
- Exclui: Normas/escores/diagnóstico, tratar repetidas como amostras independentes, misturar versões incompatíveis, recalcular métricas oficiais em TS, modificar jsPsych.
- Dependências: WEB-048, WEB-049, WEB-050, WEB-051.
- Requisitos relacionados: REQ-REL-005, REQ-REL-007, REQ-REL-008, REQ-REL-010, REQ-UX-016, REQ-INT-005.
- Componentes afetados: `ProfessionalDashboard.tsx, ResearchVisualizations.tsx, InstrumentVisualizations.tsx, ResultsTable.tsx, web/src/dashboard/, web/src/api/`.
- Contratos envolvidos: Respostas analíticas CHG-007/WEB-051 e contrato científico existente; navegação usa consulta de WEB-050.
- Critérios de aceite: Cada gráfico tem unidade/população/nulos, tabela equivalente e drill-down que mantém seleção; dia/semana/mês, grupo e métrica explícitos; tooltip e legenda não alteram denominador. Longitudinal identifica visitas repetidas e versões, sem unir legados por código. Tabela ordena/pagina/busca/ajusta colunas e densidade; detalhe mostra proveniência e tentativas. Seleção local torna-se filtro aplicado antes de exportar, nunca CSV da página por engano.
- Critérios de UI/UX: Gráficos de tempo, barras por projeto/avaliador/condição/resposta, histograma RT com faixas identificadas, completude e longitudinal acessíveis; nenhuma visualização decorativa. UUID em detalhe técnico; nomes/códigos amigáveis na lista; rolagem horizontal apenas na tabela.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: ANALYTICS7: Vitest de mapeamento/unidades/ausência e contratos, Playwright Chromium/Firefox com tabelas equivalentes, drill-down, agrupamento e mudança de contexto; tipos/build e paridade de valores com fixture oficial.
- Testes manuais/visuais exigidos: Comparar gráficos, tabela e KPIs com fixture conhecida em cada nível; testar teclado/zoom/tamanhos UX7-AA e UX7-J1; aferir a definição exibida de média por avaliação versus proporção por tentativa.
- Evidências: PLANEJADAS. Exigir data/SHA, comandos/resultados/ambiente e casos com dados inequivocamente sintéticos; confrontar cada critério, vínculos e contratos; screenshots não substituem comportamento. Registrar branch/commits/push/PR/verify/merge reais na execução.
- Riscos/bloqueios: R14/R15: gráficos podem comunicar agregação errada. Biblioteca futura só após avaliação documentada de licença/manutenção/peso/acessibilidade/testes; ausência de biblioteca não dispensa interações exigidas.
- Decisões externas necessárias: Nenhuma para exploração descritiva existente; comparação metodologicamente incompatível é bloqueada e exige responsável.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### WEB-053 — Vincular filtros prévia e CSV à mesma seleção validada

- Marco: M8. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Corrigir lacunas reproduzidas no router e integrar as cinco granularidades à mesma população analítica.
- Inclui: Reutilizar catálogos/serializadores, parser/seletor autorizado, ExportDialog, colunas, amostra mascarada/projetada, token integral e fingerprint, multi-projeto, auditoria, nome/manifesto seguro e compatibilidade individual/agregado; contrato CHG-007.
- Exclui: Alterar 21 colunas/fórmulas, download sem prévia válida, nominal por papel isolado, autorizar pelo frontend, exportar tudo quando um filtro não é suportado.
- Dependências: WEB-048, WEB-049, WEB-050, WEB-051.
- Requisitos relacionados: REQ-CSV-005, REQ-CSV-006, REQ-CSV-007, REQ-AUT-002, REQ-SEG-002, REQ-SEG-003.
- Componentes afetados: `ExportHubPanel.tsx, web/src/api/exports.ts e aggregate.ts, api/exports.py, stroop/application/, stroop/persistence/web_multi_export.py, stroop/domain/web_multi_export.py`.
- Contratos envolvidos: Contrato HTTP CHG-007 (única semântica de filtros/granularidades/token), CSV canônico/modelo e ADR-007; sessão/CSRF/DEC-03.
- Critérios de aceite: Para cada granularidade, conjunto de IDs e contagens lógicas coincide com consulta aplicada; linhas seguem regras da projeção, não contagem da página. Filtros/colunas/modo/projetos/versão mudados invalidam prévia; mutação/expiração retorna 409; revogação entre prévia/download nega tudo. Amostra não expõe colunas omitidas/nominais. Filtro desconhecido/inaplicável retorna 422, nunca é ignorado. CSV21 só completo e compatível, recusa filtros de tentativa conforme contrato.
- Critérios de UI/UX: Prévia exibe recorte, quantidade de avaliações/participantes/tentativas e linhas com unidades de cardinalidade; download desabilitado se rascunho pendente ou token inválido. Estados indisponível/processando/arquivo preparado claros; não afirmar gravação no computador.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: EXPORT7: API/PG real sintético combinando filtros/cinco granularidades, conteúdo/ordem/ausência/paridade, concorrência e revogação; token adulterado/reutilizado com colunas diferentes; pacientes sem vínculo; projeção nominal e deidentified; CSV injection incluindo delimitadores/aspas/controles; roundtrip CSV21 com consumidores; Vitest e Playwright HTTPS Chromium/Firefox da jornada completa.
- Testes manuais/visuais exigidos: UX7-J1 com arquivo parseado e conjuntos comparados; testar prévia sem nominal, CSV individual e agregado preservados, troca rápida de projeto/colunas, erro 409 e nova prévia explícita.
- Evidências: PLANEJADAS. Exigir data/SHA, comandos/resultados/ambiente e casos com dados inequivocamente sintéticos; confrontar cada critério, vínculos e contratos; screenshots não substituem comportamento. Registrar branch/commits/push/PR/verify/merge reais na execução.
- Riscos/bloqueios: R14 P0; riscos adicionais de pacientes globais, reader fallback, amostra nominal e DEC-03 por verificar com PG. Corrigir por esta ficha sem reabrir WEB-020; nenhum aceite de segurança com doubles.
- Decisões externas necessárias: DEC-03/WEB-041 para habilitação nominal real; testes negativos e positivos institucionais somente sintéticos e configuração de teste explícita, sem habilitar research real.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### WEB-054 — Materializar preparação contextual e modalidades seguras da ADR-008

- Marco: M8. Prioridade: P1. Complexidade: G. Estado: PENDENTE.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Vincular capacidades apenas documentadas da CHG-006 a um entregável futuro sem reabrir M4/M7.
- Inclui: Tela única com revisão inline; busca/cadastro contextual autorizado e confirmação de homônimos; orquestração atômica/idempotente, seleção paciente/avaliador/projeto/instrumento/visita; iniciar no dispositivo com isolamento real e convite/link/QR em RAM; Gestão/correção de vínculo com componentes compartilhados.
- Exclui: Novo paradigma, modo offline/retomada, enviar convite a terceiros automaticamente, suportar celular como motor por renderizar QR, criar conta de avaliador, promessa de início em 10 segundos sem medida.
- Dependências: WEB-049, WEB-045, WEB-046, WEB-023.
- Requisitos relacionados: REQ-SESS-001, REQ-SESS-002, REQ-SESS-003, REQ-AVA-005, REQ-PAR-005, REQ-UX-016.
- Componentes afetados: `SessionInvitation.tsx, PatientsPanel.tsx, EvaluatorsPanel.tsx, web/src/api/sessions.ts, App.tsx, api/sessions.py, stroop/application/web_sessions.py e persistência cadastral`.
- Contratos envolvidos: Complemento operacional CHG-007 da ADR-008 no contrato HTTP; ADR-005/D2, sessão e identidade científica inalteradas.
- Critérios de aceite: Cadastro é explícito após verificar candidatos, nunca por digitação isolada. Uma operação idempotente resolve vínculo/visita/convite, falha faz rollback sem paciente/convite órfão; retry após resposta desconhecida consulta operação antes de nova emissão. Presencial não permite voltar ao painel por histórico/cache/BFCache/URL após handoff, exige reautenticação servidor; modo remoto copia/QR sem tokens em URL. Revisão permite corrigir sem perder dados; revinculação confirmada audita antes/depois preservando resultados.
- Critérios de UI/UX: Pré-seleções são conferíveis, cadastro secundário sob expansão, erros preservam preenchimento recuperável; foco restaura após diálogo; estado desconhecido não informa falha/sucesso falso; convites duplicados/concurrentes testados.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: PREP7: unidade/idempotência/rollback/concorrência em API/PG real; Vitest formulário/homônimos; Playwright HTTPS Chromium/Firefox handoff/logout/voltar/avançar/BFCache/reautenticação, QR sem segredo URL e regresso após recibo/interrupção; regressão prática/principal/checkpoints/CSV.
- Testes manuais/visuais exigidos: UX7-J2 e UX7-J3, busca/homônimos e emissão duplicada; medir passos e tempo observado sem requisito universal de 10 s; retomar equipe com conta autorizada após teste.
- Evidências: PLANEJADAS. Exigir data/SHA, comandos/resultados/ambiente e casos com dados inequivocamente sintéticos; confrontar cada critério, vínculos e contratos; screenshots não substituem comportamento. Registrar branch/commits/push/PR/verify/merge reais na execução.
- Riscos/bloqueios: R13/R15; ocultar DOM não garante isolamento. Se fluxo seguro conflitar com cookie/protocolo, bloquear modalidade dependente e registrar decisão, sem improvisar URL com token ou relaxar sessão.
- Decisões externas necessárias: Nenhuma para direção aprovada e ensaios sintéticos; mudança de política D2/modos científicos exige responsável. Evolução de schema eventualmente necessária só aditiva, revisada nesta tarefa, nunca aplicada operacionalmente por implicação.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### WEB-055 — Homologar experiência profissional integrada antes da candidata

- Marco: M8. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Responsável: Codex na implementação e testes; proprietário no aceite de produto e decisões externas; operador somente em ação especificamente autorizada.
- Justificativa: Impedir RC baseada apenas em build/screenshot quando os recortes, jornadas ou permissões divergem.
- Inclui: Campanha UX7-AA/COMP7/NAV7/QUERY7/DATA7/ANALYTICS7/EXPORT7/PREP7, três jornadas reais sintéticas UX7-J1/J2/J3, regressão visual/funcional/científica e volume; evidências por SHA.
- Exclui: Conceder aceite institucional/metodológico M9, publicar/deploy/tag/release, usar coletas reais, alterar workflow/verify ou afrouxar teste para obter passe.
- Dependências: WEB-052, WEB-053, WEB-054.
- Requisitos relacionados: REQ-UX-016, REQ-REL-006, REQ-REL-007, REQ-REL-008, REQ-REL-009, REQ-CSV-006, REQ-CSV-007.
- Componentes afetados: `web/e2e/integrated/, testes existentes de UI/API/PG, docs/VALIDACAO_WEB.md e evidências neste backlog`.
- Contratos envolvidos: Todos os contratos preservados e alvos CHG-007 materializados em WEB-050/051/053/054.
- Critérios de aceite: Zero divergência inexplicada entre consulta, gráficos, tabela, prévia e CSV em todas as cinco granularidades; três jornadas concluídas com assertivas de persistência/arquivo/auditoria; bloqueios de segurança/dados/acessibilidade AA resolvidos antes do aceite. Perfil/ambiente/volume/SHA registrados; Actions verify real na SHA de integração exigido na candidata WEB-032.
- Critérios de UI/UX: Revisão humana documentada das jornadas e matriz visual nas cinco larguras e zoom 200%; nenhuma sobreposição/corte/rolagem global; estados de interface contextualizados. Screenshot prova layout apenas; erros funcionais não recebem aceite visual.
- Acessibilidade: UX7-AA em [validação](VALIDACAO_WEB.md#homologação-profissional-integrada--chg-007); componentes/rotas desta ficha cumprem WCAG 2.2 AA aplicável; gráficos têm tabela equivalente; foco, labels e anúncio de estado testados. Em backend, contrato transmite estados/erros necessários à apresentação acessível.
- Segurança e privacidade: servidor revalida perfil e todos os projetos; mesma origem/cookies seguros/CSRF; somente RAM; nenhum nominal/credencial em URL/log/manifesto; deidentified padrão e nominal condicionado a DEC-03/WEB-041. Nenhuma alteração científica por redesign.
- Testes automatizados exigidos: Vitest completo, typecheck/build, Python focado e regressão científica/CSV/auth, PG sintético real sem skips obrigatórios, Playwright Chromium/Firefox HTTPS com cenários negativos e responsividade; performance segundo UX7-PERF.
- Testes manuais/visuais exigidos: Executar UX7-J1/J2/J3 e checklist WCAG 2.2 AA aplicável com teclado/leitor de tela e contraste; registrar navegador/versão/SO/viewports, achados e correções; revalidar o que mudou.
- Evidências: PLANEJADAS. Exigir data/SHA, comandos/resultados/ambiente e casos com dados inequivocamente sintéticos; confrontar cada critério, vínculos e contratos; screenshots não substituem comportamento. Registrar branch/commits/push/PR/verify/merge reais na execução.
- Riscos/bloqueios: R14/R15 e WEB-031 externa independente: pode concluir homologação local sem resolver réplica, mas WEB-032 não fecha sem WEB-031. Ferramenta/ambiente obrigatório indisponível mantém aceite pendente.
- Decisões externas necessárias: Proprietário confere jornadas/limites; DEC-03/04/05 e autorizações M9/M10 seguem separadas.
- Condições de conclusão: todos os critérios desta ficha e casos aplicáveis de validação comprovados, dependências aceitas, sem skip obrigatório ou divergência silenciosa; atualizar evidência, matriz e painel neste backlog. Nenhum aceite concedido por este planejamento.
- Referências: CHG-007; [UX](experimento/UX_DECISIONS.md#interface-profissional-integrada--chg-007); [contrato](desenvolvimento/CONTRATO_API_WEB.md#consulta-e-exportação-integradas--alvo-chg-007); [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md).

### EV-M8-029/031 — imagens e recuperação isoladas, 2026-11-06

Escopo autorizado nesta sessão após M1: revalidar infraestrutura existente sem
VPS, DNS, certificados operacionais ou dados reais. Base `851ac3a` preservada;
branch `test/m6-m8-validacao-isolada`. Build serial usa allowlists Dockerfile
*.dockerignore; dados/secrets não entram no contexto. Tag exclusiva `web029-20261106-851ac3a` nos repositórios locais
`stroop-web-api` e `stroop-web-proxy`; essas imagens não foram publicadas.

WEB-029: 17 testes de `tests.test_web_runtime tests.test_web_proxy_config`
aprovados sem skips. Wrapper Python chamou `WebComposeSmoke(tempdir, True, api_image=...,
proxy_image=...)`, `run()` e `cleanup()` com as tags acima; passou build/saúde API/PG/Nginx, proxy único público em portas loopback
aleatórias, limites/headers/Host inválido, grants de leitura, coleta sintética,
consulta/detalhe/CSV e reinício com persistência. Acrescentadas requisições reais
que exigem 404 para nove caminhos de fontes/config/secret; não abrem arquivos
operacionais: são URLs na pilha sintética. Smoke final com `build_images=False` também passou. IDs locais das imagens:
API `sha256:117f2e999c8cc67d8e8c81e969a0e8142426b684eebe2361df77068863182dfd`;
proxy `sha256:bd45523682e6337e29be89ceb1c14cf8779cab38861bbbb815ff05f838c7db1e`.
Comando reproduzível equivalente: `.venv/bin/python scripts/smoke_web_compose.py
--build-images --api-image IMAGEM_API_LOCAL --proxy-image IMAGEM_PROXY_LOCAL`,
substituindo os dois nomes pelos repositórios e tag identificados acima.

Correções de isolamento/validação: nomes de bancos sintéticos agora seguem
`stroop_etapa4_test_*`; projeto Compose de restore ganhou sufixo aleatório para
não colidir com outra execução. Verificação pós-restauração confere vínculos,
state/platform/session_id/assessment_id no recibo, além de schema, tentativas,
métricas e estado. Nenhuma migration, dado real ou configuração operacional
alterada. Primeiro smoke usou nome legado `stroop_w19`, mas em pilha nova
exclusiva; repetição final usou prefixo correto. Sem falha de produto observada.

WEB-031 parcial: `scripts/smoke_web_recovery.py` com as mesmas tags passou em
três rodadas progressivas. Última: **6,305 s** backup+restore, **11 migrations,
uma avaliação**, detecção de outage, candidato inválido/retorno da imagem e
contagens preservadas. Novo caso negativo real altera somente o assessment_id
do recibo da fixture temporária, cria backup e exige rejeição estrutural do
restore; repara a fonte no finally. Última rodada confirmou
`invalid_receipt_rejected=true`. Isso não mede RPO externo ou RTO da VPS.
Rodadas anteriores positivas: 6,487 s e 6,261 s, sem descartar falhas.

Regressão: 39 testes runtime/proxy/backup/replicação/monitor/rollback aprovados;
`tests.test_hardening_producao` com PG descartável M6: **21 aprovados**, sem skips.
Rodada ampliada inicial sem TEST_DATABASE_URL teve 56 passes e quatro skips de
integração; não usada como aceite. A repetição PG acima comprova os quatro casos.
Réplica em `tests.test_web_backup_replication` usa fetch double; timer é modelo
estático nesses testes, portanto não comprova SSH/agenda real. Nenhum sshd local
nos caminhos padrão nem imagem SSH disponível; não instalada dependência nova,
nenhum destino externo/credencial foi presumido autorizado. WEB-031 permanece
BLOQUEADA para réplica positiva real e limites operacionais; WEB-032 preserva
suas dependências M7/WEB-030/031. Ambiente Docker 29.9.3, PostgreSQL 17.6,
Python 3.12.3; cada harness encerra somente pilhas/volumes temporários próprios.
Agenda/alerta negativo real: `systemd-run --user` criou unit transitório
exclusivo com `--on-active=1s --timer-property=AccuracySec=100ms`, executando
`replicate_web_backup.py --config` de fixture temporária 0600 e chave ed25519
sintética. SSH real só para 127.0.0.1/porta aleatória reservada sem listener:
falha esperada gerou `status=unavailable`, `alert=true`,
`error=replication_failed`, ExecMainStatus=1; nenhum ciphertext publicado.
Stop/reset-failed somente do timer/service próprio e artefatos removidos.
Esse caminho comprova disparo/alerta negativo, não réplica positiva.
Git diff --check aprovado. Código em `357e28f39b132b0213998b5066051bdd7b2fa04d`,
enviado e confirmado por HEAD/upstream/ls-remote. Hashes/envio/CI adicionais no
fechamento desta execução.

Continuação independente — réplica real local, 2026-11-06:

A ausência de sshd no host foi superada com ferramenta de teste em imagem Docker
descartável derivada da API aceita. Instala openssh-server somente nessa imagem,
sem mudar host, serviços existentes, locks ou dependências da aplicação. Novo
`scripts/smoke_web_replication.py`: gera massa PostgreSQL sintética nova, usa
create_backup, SSH real/forced-command canônico, cópia/idempotência e restaura
cópia com restore_isolated/verify_web. Chaves efêmeras/known_hosts fixo, somente
loopback/porta aleatória, usuário restrito sem senha/forwarding/root; StrictModes
preservado. Chave AES separada não é montada no servidor/exportador.

Comando: `.venv/bin/python scripts/smoke_web_replication.py --api-image
IMAGEM_API_LOCAL --proxy-image IMAGEM_PROXY_LOCAL`, usando repositórios/tag/IDs
locais documentados acima. Resultado final **passed**, **86.649 bytes**, bytes e
checksum exatos, idempotência sem substituir arquivo, comando livre recusado.
Cópia SSH restaurou **11 migrations/uma avaliação/recibo válido**. Timer transitório
real executou CLI para copiar e confirmou arquivo; depois servidor parado gerou
alerta fechado e exit 1. Imagem/container SSH, timers, chaves/configs e massa
sintética próprios removidos; nenhuma conexão externa ou backup operacional.

Medidas observadas: idade do backup **3,689 s**, tempo da cópia **0,909 s**;
backup+restore anterior **6,305 s**. São menores que os objetivos históricos
RPO 24 h/RTO 4 h, mas idade/cópia/restore pontuais não medem disponibilidade ou
recuperação ponta a ponta do destino externo. Saída explicita
`external_rpo_not_measured=true`. WEB-031 **não concluída**: REQ-INF-003 mantém
réplica externa e comparação/aceite dos limites operacionais por responsável.
Nenhum objetivo/garantia foi redefinido para aceitar o ensaio local.

Duas tentativas anteriores falharam na cópia por StrictModes: authorized_keys
montada tinha UID do host, diferente do usuário do container. Diagnóstico
sanitizado confirmou causa. Correção somente no harness copia chave pública
efêmera ao contexto de build e instala arquivo de root; não desabilita
StrictModes nem relaxa SSH. Primeiro diagnóstico usou ciphertext de transporte;
rodada final usou dump PG real conforme descrito. Falhas preservadas, sem
conversão artificial em passes. Código novo revisado pelo principal; execução
real positiva/negativa serve como validação do harness, sem testes espelho.

### EV-M8-030 — pipeline por SHA em execução, 2026-11-06

Worktree sparse exclusiva `/tmp/stroop-web030-20261106`, exclusões de dados e
secrets antes checkout; venv nova com locks exatos e pip check aprovado, npm ci
somente isolado. PostgreSQL tmpfs exclusivo, banco `stroop_etapa4_test_web030`.
Runner `verify_web_ci.py all` exige scanner/self-test, Python sem skips,
frontend/build, auditorias, browsers gerais/temporais e HTTPS real. Doze testes
do runner aprovados na preparação. Nenhuma mudança de proteção/gatilho ou PR.

Primeira tentativa local em `357e28f` bloqueou em sources: dois achados
`generic-api-key` nas linhas de documentação das tags de imagens locais,
sem segredo real. Confirmado por inspeção somente dessas fontes sintéticas;
reescrita da representação documental separa repositório/tag e preserva IDs
reproduzíveis. Scanner/configuração/asserts intactos, sem allowlist/bypass.
Verificação sources local subsequente passou 366 fontes. Demais estágios da
primeira tentativa não executados; não há aceite parcial de pipeline.

Actions inicial [42159772439](https://github.com/thiagorraposo/stroop-go-nogo-psychopy/actions/runs/42159772439)
disparado pelo workflow_dispatch existente sobre `357e28f`, com headSha
conferido; concluiu **failure** no Scanner oficial de secrets, preservada.
Reexecução local/remota na SHA **`0d79fd297f169ad25c63402dbd11c535694a0b98`**:
[Actions 42159898317](https://github.com/thiagorraposo/stroop-go-nogo-psychopy/actions/runs/42159898317),
headSha conferido. Não transferir sucesso entre SHAs por inferência.

Resultados locais já concluídos na reexecução: sources **366 fontes** e
secret-self-test aprovados; **397 Python aprovados em 99,884 s**, sem skips;
frontend `npm ci`, **292 Vitest/18 arquivos**, tipos/build aprovados; npm audit
zero e pip-audit sem vulnerabilidades conhecidas. Browsers gerais **104/104** (1,7 min), temporais seriais **4/4** (3,5 min)
e integração HTTPS/API/PG **40/40** (10,7 min, vinte por navegador) aprovados,
sem falhas/skips/retries. Runner integral terminou exit 0; worktree sparse
permaneceu limpa e seu PG exclusivo foi removido. Actions **42159898317** concluiu **success** na mesma SHA, todos estágios
obrigatórios aprovados. WEB-030 aceita; não é campanha metodológica ou deploy.
Commits posteriores documentais têm verificação de fontes/links/consistência,
sem alegar Actions no novo HEAD. Logs sintéticos locais preservados em
`/tmp/stroop-web030-local-pipeline.log` (tentativa bloqueada) e
`/tmp/stroop-web030-local-pipeline-0d79fd2.log` (aprovação). Ambiente Python
3.12.3, Node 24.15.0/npm 11.16.0, PG 17.6, OpenSSL 3.0.13, Playwright 1.64.1,
Chromium 156.0.8078.4 e Firefox 157.0, locks exatos sem upgrade.

## M9 — Validação técnica e metodológica

- Objetivo: Separar aceitação de software da autorização de pesquisa.
- Justificativa: Aceite reduzido histórico W16 não equivale a equivalência nem matriz física atual.
- Inclui: Política institucional, campanha aprovada, integração/capacidade, homologação da experiência profissional final CHG-007 em WEB-035, revisão metodológica e barreira de coleta.
- Exclui: Declarar equivalência automaticamente ou realizar estudo com pessoas nesta tarefa técnica.
- Pré-requisitos: M7, M8 e M3 aceitos; responsável/equipamento disponíveis.
- Dependências: M7, M8, M3.
- Entregáveis: Relatório técnico com limites e decisão metodológica assinada/registrada pelo responsável.
- Componentes afetados: `docs/VALIDACAO_WEB.md, homologação, segurança, protocolo e gates existentes`.
- Testes necessários: Campanha de engenharia e física conforme DEC-04; paridade matemática, dados e limites de capacidade; sem dados reais implícitos.
- Critérios de aceite: Falhas resolvidas ou escopo de suporte explicitamente reduzido com aprovação; nenhuma alegação além das evidências; prontidão real decidida.
- Riscos: R01, R02, R07, R12, R13.
- Decisões externas: DEC-03/04 para prontidão; DEC-05 é autorização posterior a M9; se estudo científico necessário, planejar protocolo separado e não fabricar resultados.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

### WEB-033 — Registrar prontidão institucional e privacidade

- Marco: M9. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-028; DEC-03.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Responsável registra política, finalidades, minimização/retenção, informação aplicável, responsabilidades e eventual autorização institucional; sem inferir consentimento legal.
- Testes/verificação: `PLANEJADO: revisão institucional/documental DEC-03`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R07, R12, R13; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-SEG-002; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.
- CHG-004: DEC-03 deve avaliar expressamente uso compartilhado, ausência de atribuição individual, custódia/distribuição/troca na saída de profissional e adequação a dados reais; rejeição exige contas individuais em mudança futura antes do uso, sem aprovação presumida. REQ-AUT-006, R07/R12; evidência institucional ainda ausente.
- CHG-005: Com a revisão de `DEC-01` ([ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md)), `DEC-03` e `WEB-033` devem aprovar formalmente a base legal/institucional para coleta e armazenamento de nome completo (`participant_name`) e iniciais no cadastro central de pacientes e avaliadores, critérios de confirmação diante de homônimos, regras de exportação nominal vs. desidentificada e política de inativação lógica/retenção antes de qualquer uso real.

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
- CHG-004: Arquitetura local não altera campanha/metodologia. Manter DEC-04 e obter aprovação específica do protocolo/equipamento físico quando exigido em M9; aceite de engenharia local não o substitui.

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
- CHG-004: Homologar candidata local por SHA: AUTH-L01–L09, segurança/privacidade, provisão sintética e recuperação; nenhum resultado OIDC histórico aprova login local ou ambiente VPS.
- CHG-005: Homologar o fluxo completo `E2E-FLOW-01` (login → dashboard → pacientes/avaliadores → preparar avaliação → executar teste → armazenar resultado → consultar, analisar e exportar CSV) e concorrência na criação de cadastros/convites no ambiente autorizado.

- CHG-007: Homologar novamente a experiência profissional final e as três jornadas UX7-J1/J2/J3 em HTTPS/API/PG reais, por SHA da candidata, incluindo responsividade, teclado, segurança e consistência de exportação. Evidência WEB-055 é entrada, não substitui homologação M9.

### WEB-036 — Obter aceite técnico e decisão explícita de liberação

- Marco: M9. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-033, WEB-034, WEB-035.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Responsável aceita prontidão técnica/metodológica e limites de suporte após 033/034/035; não concede deploy/coleta real. Barreira synthetic preservada; pedido concreto de DEC-05 pode ser preparado depois de M9.
- Testes/verificação: `PLANEJADO: ata de aceite por responsável e revisão das barreiras de operação`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R01, R07, R12, R13; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: REQ-SEG-003; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.
- CHG-004: Aceite técnico inclui riscos residuais R05/R07/R12 e decisão de adequação de conta compartilhada em WEB-033; DEC-05, deploy e coleta permanecem separados.
- CHG-005: Inclui revisão dos riscos R13 (homônimos e proteção de cadastros nominais) e confirmação das barreiras contra exportação nominal não autorizada antes de `DEC-05`.

## M10 — Implantação controlada e documentação operacional

CHG-007: documentação/handoff devem corresponder à interface final aceita (marca, três eixos, consulta e exportação), conforme WEB-037/039/040; nenhuma publicação autorizada por este replanejamento.

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
- Riscos: R07, R08, R09, R12, R13.
- Decisões externas: Autorização de deploy somente antes de WEB-038, após plano concreto; credenciais/recursos; integração main se desejada exige autorização separada; coleta e retirada legado independentes.
- Encerramento: todas as tarefas do marco CONCLUIDAS, critérios acima comprovados e evidência consolidada por SHA; sem aceite presumido por documentação ou código existente.

- CHG-007: Exigir homologação profissional WEB-035 com CHG-007, integridade dos recortes e riscos R14/R15 explicitados, além dos gates institucionais/metodológicos anteriores.

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
- CHG-004: Plano concreto identifica provisionamento local protegido, custódia, rotação/revogação, schema compatível e rollback sem reabrir OIDC/sessões antigas; nenhum segredo no manifesto.
- CHG-005: Plano identifica aplicação controlada da migration aditiva `0014` (`web_patients`, `web_evaluators`, `web_registry_audit_events`, `web_legacy_entity_links`) e proteção de backups contendo cadastros nominais.

- CHG-007: Runbooks e materiais de operação devem corresponder à marca Stroop Test Web, sidebar de três eixos, consulta aplicada e exportação final; revisar screenshots exclusivamente sintéticos, perfis, falhas e recuperação.

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
- CHG-004: Somente após autorização específica: provisionar/verificar conta local no ambiente alvo por procedimento protegido, smoke HTTPS/login/logout/negações, sem publicar senha/segredos; deploy não autoriza coleta.
- CHG-005: Smoke pós-deploy exercita exclusivamente registros sintéticos de paciente/avaliador (inativados após o ensaio), confirma ausência de upload CSV de usuário e verifica exportação desidentificada padrão.

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
- CHG-004: Handoff inclui recuperação administrativa, rotação na alteração da equipe, revogação de todas as sessões e restore sem ressuscitar acesso; demonstrar custódia e recuperação externa/RPO/RTO.
- CHG-005: Handoff operacional inclui procedimentos de inativação lógica de pacientes/avaliadores, correção auditada de vínculos e custódia de exportações nominais autorizadas.

- CHG-007: Handoff ensaia busca/correção auditada, preparação e consulta→prévia→download na interface final; limites de volume, nominal/DEC-03 e estado desconhecido documentados.

### WEB-040 — Encerrar transição com aceite do proprietário

- Marco: M10. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-039, WEB-041; DEC-05 para uso real.
- Responsável: Codex na execução; responsável do produto/metodológico nas aprovações externas indicadas.
- Critérios de aceite: Aceite final identifica limites, suporte, política de uso e incidentes; legado preservado salvo autorização específica; liberação real, se concedida, rastreada e verificada; M10 aceito.
- Testes/verificação: `PLANEJADO: aceite operacional e revisão final de rastreabilidade`. Arquivos citados existem; verificações PLANEJADAS não têm resultado.
- Evidências: PLANEJADAS; nenhum teste desta tarefa reexecutado nesta fase. Ao executar registrar comando, resultado, data e SHA.
- Riscos/bloqueios: R07, R10, R12, R13; decisões externas nas dependências/ficha do marco. Dependências pendentes não são falha observada.
- Referências: requisitos transversais do marco e ADR-004; [arquitetura](ARQUITETURA_WEB.md).
- Git da entrega: branch/commit/push/CI ainda não aplicáveis; registrar evidência real na execução.
- CHG-004: Aceite operacional explicita conta compartilhada, limites de auditoria e política institucional; transição, uso real e eventual retirada Streamlit exigem aprovações próprias.

- CHG-007: Aceite operacional confronta documentação e interface final da CHG-007; não aceitar instruções dos oito módulos como fluxo atual.

### WEB-041 — Implementar configuração controlada para pesquisa real após aprovação

- Marco: M10. Prioridade: P0. Complexidade: G. Estado: PENDENTE.
- Dependências: WEB-036, DEC-03 e autorização DEC-05 específica para a implementação/configuração de pesquisa; nenhuma ação sobre dados reais por implicação.
- Responsável: Codex no código e testes; proprietário/instituição nas regras e autorização; operador na ativação real separada.
- Critérios de aceite: especificar e implementar o contrato já previsto em seguranca/ACESSO_WEB.md para modo research, aviso versionado, elegibilidade/informação aplicáveis, confirmação datada por responsável e habilitação administrativa explícita por projeto. Default continua synthetic; ausência/incompletude/revogação da configuração bloqueia emissão/resgate research. Não alterar D1–D6 nem métricas. Qualquer schema novo é aditivo e testado apenas em banco sintético. Revalidar autorização, integração e critérios M9 afetados na nova SHA candidata antes de WEB-037; registrar se requisito metodológico novo exigir replanejamento em vez de implementar por inferência.
- Testes/verificação: PLANEJADOS, novos testes de configuração completa/incompleta, modos, papéis, revisão/retirada da habilitação e aviso no fluxo real com participantes inequivocamente sintéticos; regressão Python/PG, frontend e HTTPS real. Arquivos/testes novos só serão nomeados quando implementados.
- Evidências: PLANEJADAS; nenhuma configuração/código de coleta real implementado nesta sessão.
- Riscos/bloqueios: R05/R07/R12/R13; sem DEC-03/05 permanece PENDENTE/BLOQUEADA conforme impedimento observado. Não há tarefa independente que permita declarar operação real concluída sem esta entrega.
- Referências: REQ-SEG-003, REQ-SEG-002, REQ-PAR-003, REQ-AVA-001; ARQUITETURA_WEB e seguranca/ACESSO_WEB.md.
- Git: branch/commit/push/CI a registrar na execução autorizada; não habilitar produção por commit ou teste.
- CHG-004: Configuração research exige DEC-03/05, política de conta local e privilégios/vínculos explícitos, proteção de credenciais e autoria limitada; testar barreiras com conta sintética antes da ativação real separada.
- CHG-005: A habilitação `research` controla também a permissão para exportação CSV em modo `nominal` (`identification_mode = "nominal"`), mantendo bloqueada a exportação nominal enquanto o projeto estiver em `synthetic` ou sem `DEC-03` configurada.

## Registro de riscos

Probabilidade qualitativa é hipótese de planejamento, não estatística. Severidade
considera integridade, validade e continuidade. R01–R10 ABERTOS desde 2026-11-04; R11 registrado em 2026-11-05; R12 em 2026-11-06; R13 em 2026-11-07. A presença
de mitigação no código não elimina risco sem ensaio. Atualizar somente aqui.

| ID | Descrição e causa | Impacto | Probabilidade | Severidade | Mitigação e evidência exigida | Marco | Responsável | Estado |
|---|---|---|---|---|---|---|---|---|
| R01 | Timing de navegador varia com hardware, SO, carga e compositor | RT/onset incompatíveis com uso pretendido | Alta | Crítica | M3 cedo, trilhas/gates, matriz medida e campanha aprovada; não inferir latência física; CHG-003 mede layout final/HUD com transporte ativo, custo de stroke e browsers sem relaxar D5 | M3/M9 | Técnico + metodológico | ABERTO |
| R02 | Confundir PsychoPy, variante WEB e aceites históricos | Conclusões científicas indevidas | Alta | Crítica | D1–D6 e versões separadas, preservar falhas W16, validação metodológica distinta; identificar apresentação antes/depois e variante aprovada frente a D3/D4 | M2/M3/M9 | Metodológico | ABERTO |
| R03 | RAM até envio final, falha/reload/expiração e corrida de commit | Perda ou duplicação de tentativas/resultados | Alta | Crítica | CHG-002/ADR-005; validar estratégia incremental e matriz antes de código; ensaiar ACK/replay, perda do sufixo e corridas; final-only rejeitado | M2/M4 | Backend + produto | ABERTO |
| R04 | Diferenças de sentinela RT, unidade, mediana/arredondamento entre consumidores | Regressão nos cálculos/análises | Média | Alta | Golden fixtures sintéticas e paridade núcleo/API/CSV/UI, sem mudança silenciosa | M1/M2/M5 | Técnico | ABERTO |
| R05 | Substituir OIDC por senha local ou alterar perfis/vínculos/cadastros sem revalidar negações | Acesso cruzado a pacientes, avaliações ou exportações nominais, sessão indevida, perda de administração | Média | Crítica | WEB-021/024 aceitas; CHG-005 exige revalidar escopo por projeto em `/api/v1/patients`, `/api/v1/evaluators` e `/api/v1/exports/*` (CAD-02/03, EXP-CSV-01) | M6/M4/M5 | Segurança/técnico | ABERTO |
| R06 | Novo schema, rótulo de projeto ou associação de legado apropria/muda histórico | Corrupção de coletas ou fusão indevida de participantes legados | Média | Crítica | Migration 0014 aditiva (`ON DELETE RESTRICT`), `web_legacy_project_links` e `web_legacy_entity_links` explícitos e auditados sem fusão automática por coincidência de nome/código (`WEB-045`/`WEB-027`) | M2/M4/M7 | Backend + proprietário | ABERTO |
| R07 | Armazenamento de nomes completos de pacientes/avaliadores e coleta/exportação sem política institucional | Exposição de dados pessoais nominais (LGPD) e uso indevido | Alta | Crítica | Segregação física entre `web_patients`/`web_evaluators` e `assessments`, exportação `deidentified` por padrão, `nominal` restrito a autorização e `DEC-03`/`DEC-05` (`WEB-045`/`020`/`033`/`041`), zero dados nominais em logs/URLs/bootstrap participante | M4/M5/M9/M10 | Proprietário/instituição | ABERTO |
| R08 | Publicação interrompe aplicação; backup não restaurável/retorno incompatível | Indisponibilidade/perda | Média | Crítica | Ensaio isolado schema/dados/imagens, réplica/agenda/alerta, deploy autorizado e retorno | M7/M8/M10 | Operador/proprietário | ABERTO |
| R09 | Dependências de VPS/DNS/TLS/provisionamento local/chaves/destino externo ou CI sem PR | Bloqueio de homologação/recuperação e falsa prontidão | Média | Alta | Preparar local independente; inventário de recursos e validação por SHA, sem mudar proteção para contornar bloqueio | M1/M8/M10 | Operador + técnico | ABERTO |
| R10 | Reescrever o que existe, ampliar instrumentos e manter backlogs concorrentes | Retrabalho e escopo sem controle | Alta | Alta | Auditoria, backlog único, critérios pequenos, IDs e controle de mudança; sem crédito histórico automático | Todos | Coordenador técnico | ABERTO |
| R11 | Contorno/retirada da caixa e precisão, HUD e diferenças de renderização alteram percepção/saliência/atenção | Versões experimentais incompatíveis e evidência anterior insuficiente | Média | Alta | Aprovação visual D3/D4 pelo proprietário registrada; conferir dez cores/screenshots sintéticos Chromium/Firefox, versão/SHA distinta, WEB-044/011 e revisão WEB-034 com DEC-04. Não inferir melhoria de desempenho/validade pela redução de informação potencialmente distrativa | M3/M4/M9 | Técnico + metodológico | ABERTO |
| R12 | Conta administrativa compartilhada: vazamento/reuso da senha, saída de integrante e autoria técnica indistinguível da identificação declarada do avaliador | Sem atribuição individual por credencial, revogação por pessoa impossível, seleção de `evaluator_id` depende de declaração operacional | Alta | Crítica | Proprietário/operador: custódia protegida, senha exclusiva, troca na alteração da equipe e revogação global; `CHG-005` separa `issued_by` (conta autenticada) de `evaluator_uuid` (avaliador responsável cadastrado em `web_evaluators`); adequação institucional avaliada em `DEC-03`/`WEB-033` | M6/M4/M5/M9/M10 | Proprietário + segurança + instituição | ABERTO |
| R13 | Homônimos, duplicidade de cadastro por concorrência ou erro humano de vinculação paciente/avaliador sem documento civil no formulário original | Criação duplicada do mesmo paciente ou associação de sessão à pessoa errada | Média | Alta | Busca prévia obrigatória por `normalized_name`/iniciais/código, bloqueio `409 duplicate_candidate_found` exigindo `confirm_homonym=true`, etapa de resumo/conferência antes do convite (`WEB-046`), inativação lógica sem exclusão destrutiva e revinculação administrativa auditada (`WEB-047`) | M4/M5/M7/M9 | Produto + técnico + metodológico | ABERTO |
| R14 | Recortes divergentes entre dashboard, prévia e CSV; token sem vínculo integral | Resultados/arquivos de pesquisa incorretos e exposição indevida | Alta | Crítica | WEB-050/051/053/055: seleção autorizada comum, fingerprint de conteúdo e reautorização; filtro cliente não autoriza | M8/M9 | Técnico + segurança | ABERTO |
| R15 | Redesign mantém fragmentação ou CSS administrativo afeta apresentação experimental | Experiência divergente e regressão visual/científica | Média | Alta | WEB-048/049/052/054/055: três eixos reais, estilos delimitados e regressão experimental; sem biblioteca incidental | M8/M9/M10 | Produto + técnico | ABERTO |

Risco mais importante: R01, com R02 como limite de interpretação. R03 é o
principal risco de integridade do fluxo experimental; R07, R12 e R13 concentram
a governança de dados nominais, homônimos e conta compartilhada introduzida por
`CHG-004` e `CHG-005`.

## Decisões externas e condições de desbloqueio

As hipóteses não são autorização. Uma decisão deve registrar autor/data, opção,
justificativa, requisito/contrato, tarefas/testes e necessidade de novo ADR ou
versão experimental. Somente bloquear tarefa dependente, sem paralisar documentação.

| ID | Questão / hipótese preservada | Responsável | Condição objetiva / impacto | Tarefas relacionadas | Estado |
|---|---|---|---|---|---|
| DEC-01 | Histórico (2026-11-05): participante pseudonimizado por projeto sem cadastro central. **Revisão formal CHG-005 (2026-11-07, ADR-007):** cadastro central de pacientes (`web_patients`) e avaliadores (`web_evaluators`) com IDs e códigos gerados automaticamente, nome completo e iniciais do formulário original do PsychoPy, reutilização entre projetos/visitas/instrumentos e separação entre tabela nominal e resultados científicos | Proprietário; decisão inicial em 2026-11-05 e revisão formal em 2026-11-07 (`CHG-005`) | APROVADA a revisão formal ([ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md)). Aceites históricos `WEB-005`/`006`/`007`/`013` preservados. Expansão aditiva autorizada para especificação e implementação sintética em `WEB-045`, `WEB-046`, `WEB-047` e `WEB-027`. Caso o estudo exija atributo adicional de desambiguação civil além de nome/iniciais/código/histórico, definir em `DEC-03` antes de coleta real | WEB-005/006/007/013/045/046/047/027 | APROVADA |
| DEC-02 | Final-only rejeitado; persistência incremental com recibo/idempotência e preservação de incompletas/ inválidas, sem retomada; nova sessão com prática | Proprietário + metodológico; diretriz e validação explícitas em 2026-11-05 | Resposta “valido” à proposta `270377b` aprova ADR-005, contrato alvo, matriz D2/D5 e perda residual; gate documental WEB-005 satisfeito. Receptor aceito em M2, worker/campanha local em EV-M3-011 e integração real aceita em EV-M4-013/016 | WEB-005/006/007/011/012/015 | APROVADA |
| DEC-03 | Regras institucionais de informação, consentimento aplicável, base legal para dados nominais de pacientes/avaliadores (`CHG-005`), exportação nominal, conta compartilhada (`R12`), retenção e incidentes | Proprietário/instituição | Documento aprovado e responsabilidades/canal definidos antes de habilitar projetos `research` (`WEB-033`/`WEB-041`); nenhuma base legal ou regra de identificação civil inventada pelo Codex | WEB-033/036/041 | PENDENTE |
| DEC-04 | Matriz local e alcance de engenharia; validação física/metodológica permanece gate M9 | Proprietário/responsável metodológico; aprovação explícita em 2026-11-05 | Resposta “eu aprovo esse alcance para DEC-04” aprova proposta de dez sessões sintéticas por ambiente local Chromium/Firefox visíveis, layout final e transporte/falhas ativos. Equipamento observado em EV-M3-011; D1/D5 intactos. Não aprova suporte por antecipação nem validação física/metodológica WEB-034 | WEB-011/012/034 | APROVADA |
| DEC-05 | Após prontidão M9, autorizar separadamente configuração research, deploy e eventual uso real | Proprietário + metodológico/operador | WEB-036 comprovada; registrar autorização específica antes de WEB-041 e, para produção/uso, de WEB-038/040; mudanças da candidata passam revalidação dos gates afetados; não retirar synthetic apenas por aprovação técnica | WEB-041/038/040 | PENDENTE |

WEB-021 alvo não exige recurso Google; provisionamento local futuro deve ser protegido.
Recursos externos não decisórios: destino de
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

### CHG-003 — revisão D3 e liberação visual, 2026-11-05

Nova solicitação explícita do proprietário aprova apresentação/HUD e substitui
requisitos visuais incompatíveis da D3 anterior. A fonte metodológica já registra
o proprietário como responsável pela pesquisa/validação/operação; não exige
aprovação de terceiro para este gate. Aprovação atribuída somente ao proprietário.
D3 revisada e D4 complementada no protocolo: variante `stroop-web-outline`, versão
visual `1.0.0`, identificada também pelo sufixo `+visual.1.0.0` no app_version já
persistido. Protocolo cognitivo/test_version preservados; comparabilidade não
comprovada, dados antigos não recebem identificação retroativa. Não cria CHG,
requisito, tarefa ou denominador redundante; é aprovação da mudança já registrada.

WEB-042/043: BLOQUEADA → PRONTA → EM_ANDAMENTO, dependências WEB-009/010 aceitas;
esta missão autoriza implementação após validação documental. Sem aprovação de
DEC-04, estudo psicométrico, coleta real, produção ou encerramento de M3. Campanha
WEB-011 exige a variante revisada, transporte ativo e D5 intacto; WEB-044 e
WEB-034 mantêm critérios próprios. Histórico inicial CHG-003 acima preservado.

- Revisão futura: usar ID CHG novo com motivo, requisito alterado, componentes,
  testes a revisar, dependências afetadas e aprovação externa quando exigida.
  Não reabrir tarefa concluída sem regressão comprovada ou novo escopo registrado.

### CHG-004 — Substituição do Google OIDC por autenticação local com conta administrativa única

- Origem/data: missão explícita do proprietário, 2026-11-06. Mudança de produto,
  arquitetura e segurança; retirar dependência Google para profissionais. Autoriza
  somente análise, integração documental, validação e versionamento nesta sessão.
- Anterior: Google OIDC com cadastro `iss/sub`, callback/PKCE/state/nonce e sessão
  profissional limitada pela identidade. Alvo: login/senha no backend, uma conta
  administrativa local sem cadastro público/autenticação externa obrigatória;
  interface profissional e sessão opaca segura. [ADR-006](arquitetura/ADR-006-autenticacao-local.md)
  registra a decisão durável ainda não coberta pelos ADRs anteriores, sem duplicar
  política/HTTP/DDL. Possibilidade futura de várias contas não implementada agora.
- Requisitos alterados: REQ-AUT-001/002/003, REQ-AUD-001, REQ-SEG-001/002/003,
  REQ-INF-001/002/003, REQ-EXT-002, REQ-AVA-001 e REQ-REL-001/003. Novos REQ-AUT-004 (credenciais/ciclo),
  REQ-AUT-005 (antiabuso) e REQ-AUT-006 (conta compartilhada). Demais requisitos
  mantêm conteúdo e recebem integração pela dependência de M6 nas fichas;
  matriz passa de 47 para 50 requisitos sem alegar implementação.
- Marcos: M0–M2 aceitos intactos; M3 mantém WEB-012/EV-M3-012 e gates científicos;
  M6 substitui mecanismo em WEB-021 e agrega regressões de WEB-022/023 em
  WEB-021/024, preservando seus aceites históricos. M4 integra convite/persistência
  por conta local; M5 login/admin sem redesign; M7 paridade/transição sem retirar
  Streamlit; M8 configuração/CI/release/restore sem Google obrigatório; M9 revisão
  institucional/metodológica/homologação; M10 provisionamento e operação protegidos.
- Dependências: WEB-021 depende de WEB-008 aceita e fica PRONTA tecnicamente;
  bloqueio antigo do cliente Google deixa de ser dependência da solução alvo.
  Falta implementação e teste locais; WEB-024 continua dependente de WEB-021/023.
  WEB-032 explicita WEB-024 além de WEB-028/030/031, sem ciclos; restante do grafo
  e regras de entrada por marco preservados. Sem avanço excepcional entre marcos.
- Segurança: hash Argon2id, bootstrap/recuperação protegidos, antiabuso/erros
  genéricos, CSRF/Origin, cookies, expiração inativa/absoluta e revogação após
  senha; grants/último admin/vínculos por projeto preservados. Sem credencial
  default/hardcode/plaintext/versionada, nem token em storage. Schema aditivo e
  compatibilidade exigem execução futura; nenhuma migration alterada/aplicada.
- Privacidade/riscos: R05/R07 revistos, R09 ajustado ao recurso alvo e R12 novo.
  Conta compartilhada perde atribuição individual, sofre vazamento/reuso e exige
  troca global ao mudar equipe; não permite revogar só uma pessoa. Hash/HTTPS
  não eliminam esse risco. Proprietário/operador custodiam; instituição decide
  adequação em DEC-03/WEB-033. Produto aprovado não presume autorização com dados reais.
- Operação: provisionamento seguro, rotação, recuperação e restore sem ressuscitar
  sessões/credenciais; replica externa independente, RPO/RTO e custódia permanecem
  WEB-031. Não acessar/reconfigurar VPS, Google ou qualquer serviço nesta missão.
- Testes/aceite futuros: AUTH-L01–L09 em [validação](VALIDACAO_WEB.md#autenticação-local--plano-de-verificação-chg-004),
  vinculados à matriz e fichas: unidade/hash/CLI, API/PG reais, React/tipos/build,
  E2E HTTPS Chromium/Firefox, segurança, schema/grants/restore e operação.
  OIDC sintético não aceita alternativa local; WEB-021 não concluída. Todos os
  critérios completos em WEB-021/024 e revisão de candidata por SHA.
- Condições de implementação: autorização posterior do marco M6 pelo workflow,
  WEB-008 aceita, contratos alvo disponíveis; schema/testes sintéticos primeiro.
  Alterações reais de dados/migrations e credenciais sensíveis exigem autorização
  específica. M6 antecede M4; nenhum comando novo nem continuidade excepcional.
- Condições de uso real: WEB-033/034/035/036 e DEC-03; DEC-05/WEB-041 para research,
  autorização de deploy antes de WEB-038, coleta e transição operacional separadas.
  Caso conta compartilhada seja inadequada, nova mudança para contas individuais
  antes do uso. Não há aprovação institucional ou recurso externo novo nesta revisão.
- Contagem: nenhum WEB novo/renumerado/retirado; denominador **45** e numerador
  **19** preservados (**42,2%**, 26 sem aceite). Requisitos/riscos novos detalham
  escopo de tarefas existentes e não criam entregável ou crédito documental extra.

### EV-CHG-004 — auditoria direcionada e revisão integral, 2026-11-06

Base auditada `bdd2631f6d6e7981b6c92c1d77471e4deeb45df8`, branch inicial
`test/m6-m8-validacao-isolada` limpa e alinhada ao upstream após fetch;
main local `fe8f24f`, origin/main `db56b40` preservados sem integração.
Nova branch documental `docs/autenticacao-local-roadmap` parte dessa base para
preservar M2/M3/M6/M8 não integrados. Auditoria por leitura de código e manifests,
sem abrir .env operacional, backups, secrets ou coletas, nem executar login/teste
funcional. Fontes: AGENTS aplicáveis, workflow, fichas, matriz, arquitetura,
ADRs 001–005, segurança/dados/API/testes/CI/infraestrutura. Registro técnico:

| Classificação | Componentes observados | Direção futura / limite |
|---|---|---|
| Reutilizáveis, com regressão | `api/auth.py`: cookies __Host separados, hash de token, HMAC CSRF, Origin exato, require_professional, me/logout e limite profissional; `api/transport.py` RequestBoundary montado em `api/main.py`; erros seguros/headers | Preservar sem reduzir proteção; autenticação local troca contexto e prazos. Rate limit atual de login é por IP, não basta para senha local |
| Reutilizáveis, com adaptação de identidade | `stroop/domain/auth.py` ROLES/PERMISSIONS, `stroop/application/auth.py`, `api/sessions.py`, `api/administration.py`, persistência auth/web_sessions, grants `scripts/provision_web_database.py` | Guards e permissões por projeto/último admin/emissor permanecem; parse_identity e parse_opaque_user_id restringem Google e precisam adaptação explícita. Admin não herda dados |
| Substituir na WEB alvo | `api/auth.py` GET login e callback/alias em main; `api/google_oidc.py` discovery/token/JWKS, verificação assinatura/aud/iss/nonce; `api/config.py` OIDC obrigatório; `web/src/App.tsx` link Google/guard e `web/src/api/client.ts` mensagens Google | POST local/validação de senha e formulário; sem retorno de claims/cadastro, sem fallback externo obrigatório. Nenhuma implementação feita |
| Substituir estruturas acopladas | `stroop/persistence/web_auth.py` sessão com oidc_expires_at; CHECK/FKs de 0002/0004 e referências 0005/0008/0009/0010; CLI `scripts/gerenciar_usuarios.py` bootstrap/recover por issuer/subject | Nova evolução aditiva de identidade/credencial/sessão local e funções/grants; não reutilizar identidade Google fictícia, não reassociar dados. CLI atual não provisiona senha |
| Removíveis futuramente da WEB após corte validado | `api/google_oidc.py`, transações/state/nonce/PKCE e configuração cliente/callback, google-auth/httpx/requests onde só servirem ao provedor | Remoção só por necessidade demonstrada e autorização/escopo futuro; httpx também é ferramenta de testes, requests pode ter outros consumidores. Nenhuma dependência/rota/configuração removida nesta missão |
| Configuração a substituir/revalidar | `compose.web.yaml` secrets OIDC obrigatórios/callback, api requirements/lock, scripts de smoke/fixtures; `.github/workflows/web.yml` e `scripts/verify_web_ci.py` | Alvo não exige Google; testar imagens/schema/login local e atualizar fixtures/locks quando implementar. Manter scanners, gatilhos PR/main/manual e CI por SHA |
| Históricos preservados | Streamlit `dashboard/app.py` login google e `dashboard/auth.py`, `compose.production.yaml`, `dashboard/requirements.lock` Authlib==1.9.4; migrations existentes, testes/relatórios e SHAs OIDC | Authlib está no lock do dashboard/stack Streamlit, sem import direto no cliente FastAPI (usa google-auth==2.62.0, httpx/requests). Não apagar Authlib/Google do legado nem assumir retirada autorizada do Streamlit |
| Testes reutilizáveis ou substituídos por escopo | test_web_auth.py/test_web_sessions.py/test_web_administration_provisioned.py/test_web_assessments.py, E2E integrated e fixtures de sessão provisionada; test_web_oidc_callback.py/test_google_oidc.py/test_web_security_review.py | Negativos de autorização/CSRF persistem e ganham login real local. Fixtures e criptografia OIDC são histórico/regressão do código preservado, sem comprovar senha, bootstrap, inatividade ou recuperação locais |

Revisão de **todas as 26 fichas sem aceite** feita contra seus requisitos,
pré-requisitos de marco, dependências locais e evidências; inventário abaixo
explica a revisão, enquanto estado/critério executável continuam nas fichas:

- WEB-012 EM_VALIDACAO: REQ-EXP-003 e gate M3, WEB-011 aceita/EV-M3-012 disponível;
  proprietário deve aceitar resultados/limites ou bloquear motor. Nada no login
  resolve timing físico ou transfere DEC-04 para suporte.
- WEB-013/014/015/016 PENDENTES: REQ-PAR/AVA/INT/UX do fluxo, dependências
  sequenciais preservadas e gates M2/M3/M6. Evidências de receptor/campanha são
  parciais para integração; ensaios reais e estados/recibos ainda PLANEJADOS.
- WEB-017/018/019/020 PENDENTES: REQ-REL/MET/CSV/UX e gate M4, dependências
  preservadas; login/admin local integrado sem redesign, gráficos/12 métricas/
  exportações preservados. Ensaios finais de cada ficha ainda sem aceite.
- WEB-021 PRONTA e WEB-024 PENDENTE: requisitos AUT/AUD/SEG e novas regressões,
  WEB-008 aceita; 024 aguarda 021/023. OIDC histórico é parcial para mecanismo
  retirado do alvo. Implementar/testar local e revisar segurança; uso sintético
  não exige DEC-03, uso real exige. Nenhum bloqueio Google remanescente no alvo.
- WEB-025/026/027/028 CONCLUÍDAS em EV-M7-025..028: importação CSV retirada da UI do produto e bloqueada com 410 Gone; roundtrip de exportação comprovado com analisador Python e SQLite; vínculo explícito auditado de legados via web_legacy_entity_links e web_registry_audit_events sem merge automático; paridade operacional em 3 eixos formalizada em ADR-008 e TRANSICAO_WEB.md. Streamlit, CLIs e launchers preservados 100% sem remoção física.
- WEB-031 BLOQUEADA: REQ-INF-003, WEB-029 aceita e evidência parcial EV-M8-029/031;
  proprietário/operador devem prover destino externo independente autorizado,
  custódia, ensaio medido RPO/RTO e aceite dos limites; duas cópias locais não bastam.
- WEB-032 PENDENTE: REQ-INF/EXT, WEB-028/030/031/024 e M7; candidata/runbooks
  PLANEJADOS. Consolidar SHA/imagens/schema local, CI nova e recuperação sem
  credenciais/sessões ressuscitadas; não transferir Actions 0d79fd2 ao futuro SHA.
- WEB-033 PENDENTE: REQ-SEG-002/AUT-006 e WEB-028/DEC-03; política/aprovação
  institucional e conta compartilhada a decidir pelo proprietário/instituição.
- WEB-034 PENDENTE: requisitos experimentais/UX, WEB-012/DEC-04 e gates M9;
  campanha local existe, validação metodológica/física aprovada ainda não.
- WEB-035/036 PENDENTES: requisitos transversais/SEG e gates M9; 035 aguarda
  candidata/segurança, 036 converge 033/034/035. Homologação técnica e aceite do
  responsável ainda sem evidência, não concedem deploy/coleta.
- WEB-041 PENDENTE: REQ-SEG-003, WEB-036/DEC-03/05; proprietário deve autorizar
  configuração research após M9. Conta local e barreiras exigem testes futuros.
- WEB-037/038/039/040 PENDENTES: requisitos INF/SEG/operação e gate M9/041;
  plano → autorização específica de deploy → smoke → recuperação/handoff →
  aceite operacional do proprietário, conforme fichas. Destino/custódia e uso
  compartilhado não aprovados; retirada legado e coleta têm autorização própria.

WEB-000…011, WEB-022/023/029/030/042/043/044 mantêm aceites/evidências anteriores;
regressões novas ficam nas tarefas abertas, sem reabrir aceite por planejamento.
DEC-01…05 e CHG-001…003 preservadas integralmente. Nenhuma decisão externa foi
resolvida documentalmente. Resultado desta missão é integração de especificação;
nenhum requisito de autenticação local declarado IMPLEMENTADO/TESTADO/ACEITO.

#### Validação e aceite documental de CHG-004 — 2026-11-06

Critérios desta missão conferidos: decisão/arquitetura local, credenciais e
segurança, WEB-021 e regressões WEB-022/023/024, marcos afetados e 26 pendências,
grafo/gates, R12 e decisões externas, testes futuros e matriz, workflow/progresso,
preservação de histórico e próxima ação. Aceite restrito à integração documental;
nenhum aceite funcional local ou aprovação externa concedido.

Verificações locais, Python 3.12.3, sem instalação:

- `python3 scripts/verify_web_docs.py`: aprovado; **11 marcos, 45 tarefas,
  50 requisitos/matriz, 12 riscos, cinco decisões, 19 aceitos, 85 documentos,
  611 links locais e 69 âncoras**, dependências sem ciclos e IDs preservados.
- `python3 -m unittest tests.test_verify_web_docs -v` e rodada final `-q`:
  **7/7 aprovados**, sem skips; não são testes funcionais de autenticação.
- Conferência adicional contra base `bdd2631`: bloco CHG-001–003 integralmente
  preservado, linhas DEC-01–05 idênticas, todos os 19 estados CONCLUIDA mantidos;
  referências de requisito resolvem e escopo contém somente Markdown em docs/.
  Distribuição: 19 CONCLUIDAS, 23 PENDENTES, uma EM_VALIDACAO, uma PRONTA e uma
  BLOQUEADA. Workflow permanente/AGENTS sem diff; denominador/progresso intactos.
- `git diff --check`: aprovado. Não houve alteração de validador ou critério
  para permitir passe. Uma conferência intermediária rejeitou a matriz após
  ajuste de células sem espaço após `|`; corrigida formatação, com nova validação
  integral e sete testes aprovados, sem alterar conteúdo/asserções do validador.

Escopo: 21 documentos Markdown (incluindo novo ADR-006); runtime, dependências,
DDL, dados e configurações CI/infraestrutura não alterados. Suites funcionais,
PG/React/build/Playwright, scanners e Actions **não executados nesta missão**;
nenhum ensaio OIDC/local, serviço remoto, PR/merge/deploy ou coleta. Testes futuros
explicitamente PLANEJADOS. Versionamento/envio conferidos no fechamento Git.

### CHG-005 — Replanejamento funcional e UX: cadastros centrais de pacientes e avaliadores, preparação completa, exportação CSV avançada e retirada de upload CSV

- Data: `2026-11-07`.
- Origem: solicitação explícita do responsável pelo repositório para incorporar o novo fluxo profissional (`Login da equipe → Dashboard → Pacientes/Avaliadores → Preparar avaliação → Executar teste → Armazenar resultados → Consultar, analisar e exportar`), cadastros centralizados de pacientes e avaliadores com IDs automáticos (`PAT-...`/`EVA-...`) e nome completo, formulário completo de preparação da sessão alinhado ao PsychoPy Builder (`stroop_go_nogo_ptbr.psyexp`), revisão formal de `DEC-01` (`ADR-007`), retirada de importação CSV do produto (`REQ-CSV-004`), exportação CSV avançada multi-granularidade (`REQ-CSV-005`) e reformulação modular e acessível da interface administrativa (`REQ-REL-004/005`, `REQ-UX-012`), em escopo exclusivamente documental.
- Racional: concentrar na plataforma WEB o cadastro reutilizável de pacientes e avaliadores entre múltiplos testes, projetos e visitas, eliminando digitação manual de IDs internos e upload operacional de CSV pelo usuário, ampliando a capacidade analítica e de exportação multi-granularidade sem alterar o motor experimental jsPsych (`WEB-042/043/044`).
- Requisitos impactados: revisão de `REQ-PAR-001`..`003`, `REQ-AVA-001`..`003`, `REQ-REL-001`..`003`, `REQ-CSV-001`..`003`, `REQ-AUD-001`..`002`, `REQ-SEG-002`..`003`; criação de nove novos requisitos sequenciais (`REQ-PAR-004`, `REQ-PAR-005`, `REQ-AVA-004`, `REQ-AVA-005`, `REQ-REL-004`, `REQ-REL-005`, `REQ-CSV-004`, `REQ-CSV-005`, `REQ-UX-012`), totalizando `59` requisitos na matriz de rastreabilidade.
- Tarefas impactadas: criação de `WEB-045` (`PRONTA`, backend/schema de cadastros centrais em `M4`), `WEB-046` (`PENDENTE`, formulário completo de preparação em `M4`) e `WEB-047` (`PENDENTE`, UI React de cadastros e reformulação de oito módulos em `M5`); atualização de `WEB-017`..`WEB-020` (`M5`), `WEB-025`..`WEB-028` (`M7`), `WEB-031`..`WEB-032` (`M8`), `WEB-033`..`WEB-036` (`M9`) e `WEB-037`..`WEB-041` (`M10`). Os `26` entregáveis já `CONCLUIDA` (`M0`, `M1`, `M2`, `M3`, `WEB-013`..`016` em `M4` e `M6`) preservam integralmente seus aceites e evidências históricas (`54,2%`, `26/48`).
- Decisões e riscos impactados: revisão formal de `DEC-01` (substituída por `ADR-007` com preservação do texto histórico), atualização de `DEC-03` (conta local compartilhada + proteção de dados nominais e exportação `deidentified` vs. `nominal`), atualização de `R05`, `R06`, `R07`, `R12` e inclusão de `R13` (exposição nominal, homônimos e exclusão indevida nos cadastros centrais).
- Documentos sincronizados: [Projeto Stroop Test.md](Projeto%20Stroop%20Test.md), [REQUISITOS_E_RASTREABILIDADE.md](REQUISITOS_E_RASTREABILIDADE.md), [ARQUITETURA_WEB.md](ARQUITETURA_WEB.md), [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), [MODELO_DE_DADOS.md](dados/MODELO_DE_DADOS.md), [CONTRATO_API_WEB.md](desenvolvimento/CONTRATO_API_WEB.md), [UX_DECISIONS.md](experimento/UX_DECISIONS.md), [ACESSO_WEB.md](seguranca/ACESSO_WEB.md), [TRATAMENTO_DE_DADOS.md](seguranca/TRATAMENTO_DE_DADOS.md) e [VALIDACAO_WEB.md](VALIDACAO_WEB.md).

### EV-CHG-005 — auditoria de cobertura, correspondência PsychoPy e validação documental, 2026-11-07

#### Matriz compacta de auditoria de cobertura pré-replanejamento

| Requisito da solicitação (`CHG-005`) | Classificação | Evidência auditada no código e docs | Lacuna identificada | Marco / Tarefa | Ação documental executada |
| --- | --- | --- | --- | --- | --- |
| **3.1. Autenticação por conta local compartilhada (`username` + `password`) sem Google OIDC** | `IMPLEMENTADO E VALIDADO` | `ADR-006`, `CHG-004`, `WEB-021`/`022`/`023`/`024` (`CONCLUIDA` em `EV-M6-021/024`, commit `7e77ef8`), `web/backend/auth.py`, `LoginForm.tsx` | Identificação do avaliador na sessão ainda era texto livre sem vínculo a cadastro central (`web_evaluators`); governança `DEC-03` segue pendente para dados reais | `M6` (`WEB-021`..`024` mantidas `CONCLUIDA`), `M4` (`WEB-045`/`046`), `M9` (`WEB-033`) | Reutilizados requisitos/aceites de `CHG-004`; documentada separação entre conta local compartilhada e `evaluator_id` cadastrado (`R12`, `DEC-03`, `ACESSO_WEB.md`) |
| **4. Cadastro centralizado de pacientes (CRUD, UUID + `PAT-...`, nome completo, reutilização entre projetos/visitas/instrumentos, homônimos e inativação lógica)** | `INCOMPATÍVEL COM DECISÃO ANTERIOR` / `NÃO PREVISTO` | `DEC-01` anterior vedava nome civil e cadastro global; `web/backend/db.py` (`web_participants`) armazenava apenas `(project_id, participant_code)` sem tabela nominal central nem endpoints `/patients` | Inexistência de tabela `web_patients`, detecção de homônimos (`409 duplicate_candidate_found`), auditoria de edição (`web_registry_audit_events`), bloqueio `ON DELETE RESTRICT` e UI CRUD | `M4` (`WEB-045`, `WEB-046`), `M5` (`WEB-047`), `M7` (`WEB-027`, `WEB-028`) | Revisada formalmente `DEC-01` via `ADR-007`; criados `REQ-PAR-004`/`005`, `WEB-045` (`PRONTA`) e `WEB-047`; especificados schema em `MODELO_DE_DADOS.md` e endpoints `/api/v1/patients` em `CONTRATO_API_WEB.md` |
| **5. Cadastro centralizado de avaliadores (CRUD, UUID + `EVA-...`, nome completo, histórico, sem login individual automático)** | `NÃO PREVISTO` | Em `InvitationCreateRequest` (`web/backend/schemas.py`) e `assessments`, `evaluator` era string livre (`1..64` chars), sem tabela `web_evaluators` nem CRUD dedicado | Inexistência de cadastro reutilizável de avaliadores, código estável `EVA-...`, vínculo `evaluator_id` e tela administrativa de avaliadores | `M4` (`WEB-045`, `WEB-046`), `M5` (`WEB-047`) | Criados `REQ-AVA-004`, `WEB-045` e `WEB-047`; especificados `web_evaluators` em `MODELO_DE_DADOS.md` e `/api/v1/evaluators` em `CONTRATO_API_WEB.md` |
| **6. Formulário completo de preparação da sessão alinhado ao PsychoPy Builder (`project`, paciente, `initials`, `visit`, avaliador, `instrument_code`, resumo pré-emissão)** | `PARCIALMENTE IMPLEMENTADO` | `InvitationPreparationPanel.tsx` e `POST /api/v1/projects/{project_id}/invitations` (`WEB-013`/`016`) já exigiam `participant_id`, `initials`, `visit`, `evaluator` e `instrument_code`, porém com digitação manual a cada teste | Exigia digitação manual de `participant_id` e `evaluator`, sem seleção/cadastro inline de paciente/avaliador, sem auto-preenchimento e sem etapa explícita de resumo pré-emissão | `M4` (`WEB-046`) | Produzida tabela de correspondência com `stroop_go_nogo_ptbr.psyexp` em `MODELO_DE_DADOS.md`; criados `REQ-AVA-005` e `WEB-046` preservando `WEB-013`..`016` |
| **7. Separação entre identidade nominal e resultados experimentais + associação auditável de legados sem merge automático** | `PARCIALMENTE IMPLEMENTADO` / `INCOMPATÍVEL COM DECISÃO ANTERIOR` | `assessments` e `trials` já são isolados em `stroop/persistence/` (`001_initial_stroop_schema.sql`), mas `DEC-01` proibia tabelas nominais e `WEB-027` previa apenas migração de CSVs legados | Faltava modelar segregação física `web_patients`/`web_evaluators` vs. `assessments` e tabela `web_legacy_entity_links` para reconciliação humana assistida | `M4` (`WEB-045`), `M7` (`WEB-027`, `WEB-028`), `M8` (`WEB-032`) | Especificados `ADR-007`, `web_legacy_entity_links` em `MODELO_DE_DADOS.md`, proteção em `TRATAMENTO_DE_DADOS.md` e reconciliação assistida em `WEB-027` |
| **8. Retirar importação CSV do produto (upload/painel), mantendo CSV exclusivamente para exportação do usuário** | `PARCIALMENTE IMPLEMENTADO` (em direção oposta no protótipo de importação) | `CsvImportPanel.tsx`, `POST /api/v1/projects/{project_id}/imports` (`web/backend/app.py`) e `REQ-CSV-001`/`WEB-025` previam upload CSV no dashboard | Necessidade de retirar `CsvImportPanel.tsx` e endpoints de upload de avaliações do produto, mantendo `stroop/ingestion/` apenas para CLI/testes internos (`WEB-026`) | `M7` (`WEB-025`, `WEB-026`), `M5` (`WEB-047`) | Criado `REQ-CSV-004`; redefinida `WEB-025` para remoção do upload CSV do produto e atualizado `CONTRATO_API_WEB.md` |
| **9. Exportação CSV avançada multi-granularidade (`pacientes`, `avaliacoes`, `tentativas`, `metricas`, `stroop_21_colunas`), seleção de colunas, prévia e controle `deidentified` vs. `nominal`** | `PARCIALMENTE IMPLEMENTADO` / `PLANEJADO E NÃO IMPLEMENTADO` | `ExportToolbar.tsx` e `/api/v1/exports/{trials,summary}.csv` existiam no protótipo e estavam planejados para revalidação em `WEB-020` (`M5`), mas restritos a 2 formatos fixos por projeto | Faltavam 5 granularidades, seleção de colunas, endpoint `/api/v1/exports/preview`, escopo por avaliação/paciente/filtro, modo `deidentified` padrão vs. `nominal` restrito e sanitização CSV injection | `M5` (`WEB-017`, `WEB-020`), `M7` (`WEB-026`) | Criados `REQ-REL-004` e `REQ-CSV-005`; atualizadas fichas `WEB-017`, `WEB-020` e especificados `/api/v1/exports/preview` e `/api/v1/exports/download` em `CONTRATO_API_WEB.md` |
| **10. Reformulação da interface administrativa em 8 módulos, KPIs documentados, gráficos interativos e design system acessível (preservando motor jsPsych)** | `PARCIALMENTE IMPLEMENTADO` / `PLANEJADO E NÃO IMPLEMENTADO` | `DashboardShell.tsx`, `AnalyticsFilterBar.tsx`, `AssessmentTable.tsx`, `MetricsCharts.tsx`, `AccountLinksAdminPanel.tsx` existiam e estavam planejados em `WEB-017`/`018`/`019` (`M5`); motor jsPsych já aceito em `WEB-007`..`010` e `WEB-042`..`044` | Faltavam arquitetura de navegação em 8 módulos (incluindo `Pacientes` e `Avaliadores`), catálogo explícito de KPIs sem normas clínicas e requisitos de acessibilidade/estados visuais | `M5` (`WEB-047`, `WEB-017`, `WEB-018`, `WEB-019`) | Criados `REQ-REL-005`, `REQ-UX-012` e `WEB-047`; atualizadas `WEB-017`/`018`/`019`, `UX_DECISIONS.md` e `ARQUITETURA_WEB.md`, preservando intactas `WEB-042`/`043`/`044` |

#### Validação e aceite documental de CHG-005 — 2026-11-07

Verificações locais executadas nesta missão documental (`Python 3.12.3`, sem instalação de pacotes):

- `python3 scripts/verify_web_docs.py`: aprovado; **11 marcos, 48 tarefas, 59 requisitos/matriz, 13 riscos, cinco decisões, 26 aceitos, 87 documentos, 665 links locais e 78 âncoras**, dependências sem ciclos e IDs preservados.
- `python3 -m unittest tests.test_verify_web_docs -v`: **7/7 aprovados**, sem skips.
- `.venv/bin/python scripts/verify_web_ci.py sources`: aprovado (`OK [sources] Fronteiras de importação e ausência de artefatos sensíveis verificadas`).
- `git diff --check`: aprovado sem erros de whitespace ou formatação.
- Conferência de escopo (`git status --short`): exclusivamente arquivos Markdown sob `docs/` (`10` documentos: `ADR-007` novo e `9` documentos canônicos atualizados); nenhum arquivo de código-fonte, migration SQL, configuração ou teste funcional alterado.

### CHG-006 — Replanejamento operacional e simplificação estrutural em 3 eixos fundamentais e fluxo direto de avaliação

- Data: `2026-11-08`.
- Origem: instrução explícita do responsável pelo repositório / produto e infraestrutura para replanejar a arquitetura operacional e a experiência de uso da equipe (`CHG-006`), superando a sobrecarga cognitiva e a fragmentação em 8 abas independentes introduzidas em `CHG-005` e viabilizando a aplicação clínica direta e sem atrito no consultório.
- Diagnóstico do produto:
  1. O marco M5 concluiu com sucesso todas as capacidades funcionais unitárias (`WEB-017` a `WEB-020` e `WEB-047`), incluindo CRUDs de pacientes e avaliadores, catálogo de filtros combinados, métricas descritivas, gráficos interativos e exportação CSV multi-granularidade.
  2. A distribuição dessas ferramentas em 8 módulos/abas isolados gerou, contudo, fricção operacional severa: para analisar dados, o pesquisador precisava alternar entre três abas reaplicando filtros; para aplicar uma avaliação presencial no consultório/laboratório, o operador precisava cadastrar o paciente em uma aba, navegar para outra para preparar o convite, copiar o link e executá-lo em janela externa.
  3. Essa burocracia afasta a solução da agilidade do **Streamlit** (análise reativa em tela única) e da facilidade do **PsychoPy Runner** (diálogo direto de 1 formulário com início imediato no dispositivo).
- Decisões arquiteturais ([ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md)):
  1. **Redução estrutural para 3 eixos fundamentais:**
     - **Eixo 1: Resultados e Análise Unificada** (`REQ-INT-005`): unificação em tela única reativa de KPIs executivos, catálogo de filtros combinados (`REQ-REL-004`), visualizações gráficas descritivas (`REQ-REL-005`), tabela completa de tentativas e hub de exportação CSV multi-granularidade (`REQ-CSV-005`).
     - **Eixo 2: Aplicação Direta / Nova Avaliação** (`REQ-SESS-001`, `REQ-SESS-002`): formulário unificado de 1 etapa (Participante + Visita + Projeto) com seleção imediata de modalidade: *"Iniciar Agora neste Dispositivo"* (aplicação presencial com isolamento seguro pós-teste) ou *"Gerar Link / QR Code"* (aplicação remota/assistida com QR Code dinâmico).
     - **Eixo 3: Gestão Cadastral e Acessos**: área secundária de governança e retificação auditada (`relink`), fichas detalhadas e controle de contas locais.
  2. **Orquestração relacional atômica e transparente** (`REQ-SESS-003`): backend e frontend coordenam a resolução de `web_patients`, `web_evaluators`, `web_project_participants`, `web_participant_visits`, `web_participant_sessions` e `web_invitations` em uma única transação, sem necessidade de múltiplos cadastros prévios manuais.
  3. **Preservação científica e psicométrica estrita**: motor psicométrico jsPsych, estímulos com contorno branco `stroop-web-outline/1.0.0` (`CHG-003`), paleta de dez cores, ausência de precisão no HUD, tempos e gates temporais D5, persistência incremental (`ADR-005`), 12 métricas oficiais e CSV de 21 colunas permanecem 100% inalterados.
- Requisitos impactados: criação de cinco novos requisitos sequenciais: `REQ-INT-004`, `REQ-INT-005`, `REQ-SESS-001`, `REQ-SESS-002` e `REQ-SESS-003`, totalizando `64` requisitos canônicos na matriz de rastreabilidade. Atualizados impactos em `REQ-AVA-001`, `REQ-AVA-002`, `REQ-AVA-005`, `REQ-REL-004`, `REQ-REL-005` e `REQ-UX-012`.
- Tarefas e marcos impactados:
  - M4 e M5: mantêm todos os entregáveis `CONCLUIDA` (6/6 e 5/5 aceitos); nenhuma tarefa é desmarcada. As capacidades já implementadas constituem os blocos construtores dos 3 eixos.
  - M7: ficha `WEB-028` revisada para incluir a comprovação de paridade operacional e fluidez do novo fluxo frente ao Streamlit e ao PsychoPy Runner.
  - Progresso global: preservado em **33/48 entregáveis aceitos (68,8%)**.
- Documentos sincronizados: [Projeto Stroop Test.md](Projeto%20Stroop%20Test.md), [ARQUITETURA_WEB.md](ARQUITETURA_WEB.md), [ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md), [REQUISITOS_E_RASTREABILIDADE.md](REQUISITOS_E_RASTREABILIDADE.md) e [REGISTRO_DE_ALTERACOES.md](REGISTRO_DE_ALTERACOES.md).

### EV-CHG-006 — auditoria arquitetural, modelo mental Streamlit/PsychoPy e validação documental, 2026-11-08

#### Matriz compacta de replanejamento funcional CHG-006

| Dimensão da simplificação (`CHG-006`) | Arranjo anterior (`CHG-005`) | Novo arranjo consolidado (`ADR-008`) | Racional e benefício operacional | Requisitos vinculados | Tarefas / Marcos |
|---|---|---|---|---|---|
| **Arquitetura de informação da equipe** | 8 módulos dispersos em abas independentes | **3 eixos fundamentais**: Resultados e Análise Unificada; Aplicação Direta; Gestão Cadastral e Acessos | Elimina a sobrecarga cognitiva e alternância constante de contexto | `REQ-INT-004` | `M5` (`WEB-047`, `WEB-017`), `M7` (`WEB-028`) |
| **Fluxo analítico e extração de dados** | Visão geral, Análises, Histórico e Exportações em abas separadas | **Tela única reativa estilo Streamlit**: KPIs + Filtros reativos + Gráficos + Tentativas + Exportação CSV sobre o mesmo recorte | Fluidez analítica imediata; filtros refletem simultaneamente em KPIs, gráficos e arquivos CSV | `REQ-INT-005`, `REQ-REL-004`, `REQ-REL-005`, `REQ-CSV-005` | `M5` (`WEB-017`, `WEB-019`, `WEB-020`), `M7` (`WEB-028`) |
| **Preparação e início de avaliação** | Cadastramento prévio obrigatório de paciente, seleção de avaliador e emissão de link em múltiplas etapas | **Formulário de 1 etapa estilo PsychoPy Runner**: Participante + Visita + Projeto em tela limpa com pré-seleção inteligente | Início de teste clínico em menos de 10 segundos no consultório | `REQ-SESS-001`, `REQ-AVA-005` | `M4` (`WEB-046`), `M7` (`WEB-028`) |
| **Modalidades de aplicação** | Apenas geração de convite por token com URL copiada | **Modalidades duais imediatas**: "Iniciar Agora neste Dispositivo" (presencial) vs "Gerar Link / QR Code" (remoto/assistido) | Atendimento presencial sem fricção com isolamento seguro pós-teste; QR Code dinâmico para smartphones/tablets | `REQ-SESS-002`, `REQ-AVA-001` | `M4` (`WEB-046`, `WEB-013`, `WEB-015`), `M7` (`WEB-028`) |
| **Orquestração relacional de dados** | Criação manual sequencial de registros nas tabelas relacionais | **Orquestração atômica transparente no backend/frontend**: resolução/criação automática de paciente, visita, convite e sessão em 1 transação | Preserva integralmente o PostgreSQL sem sobrecarregar o operador com passos intermediários | `REQ-SESS-003`, `REQ-PAR-004`, `REQ-AVA-004` | `M4` (`WEB-045`, `WEB-046`), `M7` (`WEB-027`, `WEB-028`) |
| **Rigor científico e psicométrico** | jsPsych, contorno branco, tempos D5, 12 métricas, persistência incremental | **100% inalterado e preservado**: motor jsPsych, estímulos, HUD, D5, 12 métricas, ADR-005 e CSV de 21 colunas intactos | Garantia de validade metodológica e paridade experimental sem regressão | `REQ-EXP-001`..`003`, `REQ-MET-001`..`003`, `REQ-INT-001`..`003`, `REQ-CSV-001` | `M2`, `M3`, `M4`, `M5`, `M9` |

#### Validação e aceite documental de CHG-006 — 2026-11-08

Verificações locais executadas nesta missão documental (`Python 3.12.3`, sem instalação de pacotes):

- `python3 scripts/verify_web_docs.py`: aprovado; **11 marcos, 48 tarefas, 64 requisitos/matriz, 13 riscos, cinco decisões, 33 aceitos, 88 documentos, 671 links locais e 83 âncoras**, dependências sem ciclos e IDs preservados.
- `python3 -m unittest tests.test_verify_web_docs -v`: **7/7 aprovados**, sem skips.
- `python3 scripts/verify_web_ci.py sources`: aprovado (`Secrets: 420 fontes versionadas verificadas; dados/historico fora do escopo`).
- `git diff --check`: aprovado sem erros de whitespace ou formatação.
- Conferência de escopo (`git status --short`): exclusivamente arquivos Markdown sob `docs/` (`ADR-008` novo e documentos canônicos atualizados); nenhum arquivo de código-fonte, migration SQL, configuração ou teste funcional alterado.

### CHG-007 — Replanejamento integrado da experiência profissional e integridade analítica

- Data: **2026-11-11**. Origem/autorização: missão explícita `replanejar` do proprietário, exclusivamente documental; implementação somente por `continue o projeto` posterior no marco autorizado.
- Motivo: materializar a CHG-006/ADR-008 sem arquitetura concorrente, padronizar identidade pública **Stroop Test Web**, reconstruir fundação visual profissional e integrar análise multigranular/CSV com o mesmo conjunto lógico validado. Integridade e autorização precedem visual.
- Fontes: AGENTS raiz/aplicáveis e workflow lidos; backlog, matriz, arquitetura, UX, ADR-007/008, contratos HTTP/dados/autenticação e código/testes dirigidos. Nenhuma coleta, .env operacional, backup ou credencial inspecionados.
- Base histórica preservada no Git: `b5fccbbd5e199e0312467b26486a7734448e20c8` contém versão anterior integral dos documentos (`git show SHA:caminho`). Esse arquivo imutável no Git é a fonte anterior arquivada; sem cópia de backlog/roadmap concorrente. Texto/evidências CHG-001..006 e aceites das 37 tarefas permanecem. M0–M10 mantidos, nenhum WEB renumerado/retirado/reaberto.
- Novos entregáveis: **WEB-048..055**, oito fichas em **M8**, cada uma com escopo/fronteiras/dependências/componentes/contratos, critérios funcionais/UX/AA/segurança, testes automatizados/manuais, evidências, riscos/decisões e conclusão. M8 passa de 4 para 12 tarefas, com WEB-029/030 aceitas preservadas; WEB-031 bloqueada e WEB-032 pendente preservadas. Justificativa: são integração/reparação pré-candidata da plataforma existente; M5/M7 não são reabertos, nenhum marco de redesign é criado.
- Requisitos: 11 novos (REQ-UX-013..016, REQ-REL-006..010, REQ-CSV-006/007), **64→75**. REQ-INT-004/005 e REQ-SESS-001..003 recebem vínculo futuro executável em M8, conservando referências aos blocos aceitos M4/M5/M7. Extensões de REQ-UX-012, REL-004/005, CSV-005 e transversais constam das relações complementares da matriz.
- Decisões: complemento da ADR-008 torna aplicação de filtros **explícita**, define sidebar nos mesmos três eixos, revisão inline e handoff presencial seguro. Não é nova ADR: mesma arquitetura/entidades da ADR-007. Ilustração anterior de token em URL é rejeitada; QR/código em RAM com resgate aprovado, sem ampliar suporte experimental. Meta antiga universal de 10 segundos é hipótese a medir, não aceite herdado. D1–D6, DEC-01 revisada/02, 12 métricas/protocolo/jsPsych/CSV canônico permanecem. DEC-03/04/05 não são resolvidas por planejamento.
- Contrato: alvo CHG-007 claramente não implementado no HTTP define normalização/seleção A/T, semântica e rejeição de filtros, projeções existentes, token integral/fingerprint, amostra protegida, concorrência/reautorização e compatibilidade. Não duplicar fórmulas ou schema científico em UI. Nominal continua dependente de gate institucional e configuração WEB-041, sem uso real implícito.
- Gates: WEB-055 depende WEB-052/053/054; WEB-032 recebe WEB-055 além de WEB-028/030/031/024; WEB-035 rehomologa a experiência profissional da candidata e WEB-036 exige esse aceite. M10/WEB-037/039/040 exigem documentação/handoff da interface final. WEB-031 pode bloquear RC sem impedir tarefas independentes autorizadas em M8. Caminho detalhado na seção de ordem, sem ciclo.
- Prioridade/risco: novo R14 P0 para recortes/autorização; R15 para fragmentação/CSS. WEB-050/051/053 P0 antes do aceite visual integrado. Nenhuma dependência de gráficos/UI selecionada ou instalada.
- Progresso: **37/48 (77,1%) → 37/56 (66,1%)**; sem aceite novo/retirado, sem crédito documental adicional. 19 sem aceite. Redução de 11,0 pontos percentuais é ampliação do denominador, não regressão. Os valores antigos nas evidências datadas continuam históricos.
- Documentos alterados: este backlog, requisitos/matriz, arquitetura, UX, ADR-008, contrato HTTP, validação e registro de alterações. ADR-007 e workflow/AGENTS não precisam de mudança; contratos científicos, código, testes, migrations e infraestrutura intactos nesta missão.

### EV-CHG-007 — diagnóstico direcionado e limites da evidência

Git inicial: worktree limpa, branch `feat/deploy-vps-github-flow`, HEAD
`6196c397f8575a8fd85cb7d435974914fcd12ac4`, alinhada ao próprio upstream; fetch
origin concluído. `origin/main` e main local em `b5fccbb`, dez commits atrás da
branch inicial (nenhum exclusivo de main nessa comparação). PRs #16 e #17 abertos
na consulta desta sessão. Esses commits/PRs preexistentes são preservados, sem
integração nesta missão. Nova branch documental `docs/chg-007-replanejamento-integrado`
parte de origin/main para PR exclusivamente documental; cinco arquivos de
exportação (hub, cliente exports.ts, router, persistência e domínio) têm mesmo
conteúdo nas duas bases; ProfessionalDashboard difere por refinamentos de UI.
As observações de oito módulos, contagem global, filtros locais, teto/snapshots
e ExportHub com apenas project/profile foram conferidas nas duas versões. Mudanças de UI/deploy
da branch inicial são contexto adicional observado, não funcionalidade aceita
por este replanejamento. Após troca, `.deploy-hostgator/` ficou visível como
não rastreado por diferença de ignore: preservado, não aberto nem staged.

Classificações abaixo se aplicam **ao requisito solicitado completo**, não ao
mérito histórico de um componente. “Comprovado” indica evidência anterior citada,
sem afirmar reexecução. Hipóteses estáticas e reproduções isoladas estão separadas.

| Solicitação / componente | Classificação | Evidência e lacuna/impacto | Requisitos / prioridade | Futuro entregável |
|---|---|---|---|---|
| React/TS/Vite, FastAPI/PG, jsPsych e login local | Implementado e comprovado no escopo histórico | EV-M1, EV-M2, EV-M3, EV-M4 e EV-M6; reutilizar camadas/métricas/grants. Não prova nova UX nem todos caminhos avançados de CSV | REQ-EXT-001, REQ-AUT-001..003, REQ-MET-001/002; P0 regressão | WEB-051/055 |
| Cadastros centrais, homônimos, avaliador separado e relink | Implementado e comprovado na base aceita; experiência contextual parcialmente implementada | WEB-045/046/047 e EV-M7-027, SessionInvitation/PatientsPanel/EvaluatorsPanel; melhorar busca/revisão/feedback, sem duplicar CRUD | REQ-PAR-004/005, REQ-AVA-004/005; P1 | WEB-049/054 |
| Marca Stroop Test Web | Não implementado como identidade pública consistente | App.tsx mostra Cores e título Correspondência de Cores; index.html e mensagens mantêm título antigo. Inventário deve distinguir marca de instrumento/texto científico | REQ-UX-013; P1 | WEB-048 |
| Design system integral e estados padronizados | Parcialmente implementado | styles.css, botões/cards e painéis existem; falta catálogo consolidado, revisão de densidade/hierarquia/controles/diálogos/estados. Não houve inspeção visual atual | REQ-UX-014/016; P1 | WEB-048/055 |
| Sidebar expandida/recolhida/móvel | Não implementado | ProfessionalDashboard.tsx usa nav modular horizontal; três eixos são alvo aprovado, não evidência de sidebar | REQ-UX-015; P1 | WEB-049 |
| Três eixos com fluxo analítico sem reaplicar | Documentado e não materializado integralmente | CHG-006/ADR-008/EV-M7-028 aceitam direção/cobertura; runtime mantém oito activeModule e ExportHub separado. Aceite M7 não prova experiência integrada | REQ-INT-004/005; P0/P1 | WEB-049/050/052/053 |
| Catálogo de filtros e rascunho/aplicada | Parcialmente implementado | ResearchFilters, filterAssessments local, query e instrument/platform separados, snapshots agregados existentes; central avançada só recebe project/profile. Recortes podem divergir, sem prova E2E atual | REQ-REL-004/006, REQ-CSV-006; P0 | WEB-050/051/053 |
| KPIs/contagem de pacientes | Parcialmente implementado | ProfessionalDashboard chama listPatients({page_size:1}) sem project e usa total sob rótulo “no projeto”; origem global vs recorte exige fixture/PG para reproduzir divergência, não foi comprovado erro de contagem real | REQ-REL-007; P0 | WEB-051/052 |
| Gráficos/descritivos/histórico | Parcialmente implementado | ResearchVisualizations, InstrumentVisualizations, analysis.ts e detalhes existem (EV-M5-019). Interações/níveis/catálogo de agregação e tabelas equivalentes completos não comprovados | REQ-REL-005/007/008; P1 | WEB-051/052 |
| Volume, snapshots e resposta obsoleta | Parcialmente implementado | ProfessionalDashboard usa AbortController e conjunto completo até 5.000; api/assessments e persistence verificam snapshots. ExportHub não usa AbortSignal/generation; teto e falhas não equivalem a escala maior | REQ-REL-006/009; P0 | WEB-050/051/053/055 |
| CSV individual/agregado e cinco catálogos/colunas | Implementado e comprovado para componentes históricos; integração parcial | EV-M5-020/EV-M7-026; api/assessments.py e aggregate.ts usam filtros básicos/snapshots. test_web_multi_export testa serialização/roundtrip, não vínculo integral de prévia avançada | REQ-CSV-001/003/005; P0 | WEB-053 |
| Filtros→prévia→download avançado | Parcialmente implementado, lacunas reproduzidas no router isolado | api/exports.py aceita filters mas não os passa a query_multi_export_rows; token só modo/granularidade/projeto/prazo; download reconsulta sem fingerprint/colunas. Probe abaixo confirma alcance isolado, sem PG | REQ-CSV-006; P0 | WEB-050/051/053 |
| Privacidade da amostra e autorização avançada | Parcialmente implementado; riscos adicionais por verificar | Amostra é rows[:5] crua, serializer mascara só CSV. SQL pacientes não usa project_id; consulta avançada não recebe actor e router usa reader ou writer fallback; nominal verifica papel sem gate institucional visível. Probe confirma amostra crua; isolamento/negações precisam HTTP/PG reais | REQ-CSV-007, REQ-AUT-002; P0 | WEB-051/053/055 |
| Qualidade de dados e quatro contagens distintas | Parcialmente implementado | Invalidadores/exclusões e RT ausente já existem; painel completo de bases, proveniência, avaliador ausente e compatibilidade não comprovado | REQ-REL-007/010; P1 | WEB-051/052 |
| Aplicação direta, QR e orquestração única segura | Documentado e não materializado integralmente | ADR-008 prevê DirectSessionLauncher/QrCodeModal/direct-evaluations; busca rg desses nomes não encontrou runtime; convite/revisão base existem. Ficha nova evita atribuir alvo a WEB-046 já aceita | REQ-SESS-001..003; P1 | WEB-054 |
| Token em URL, criação por nome sem confirmação, confirmação visual como isolamento | Incompatível com decisões/restrições vigentes | Ilustrações da ADR-008 precisam limite formal; complemento rejeita segredo URL/fusão, exige revisão e reautenticação servidor. Não altera D2 ou autoriza modo móvel | REQ-AUT-003, REQ-SESS-002/003; P0 | WEB-054/055 |
| Responsividade/AA/testes visuais e jornadas completas novas | Documentado e parcialmente implementado nos controles existentes; conformidade não comprovada | UX anterior prevê teclado/contraste; nenhuma campanha atual de cinco larguras/zoom/AA executada. Build/render não valida usabilidade | REQ-UX-016; P0 | WEB-048..055 e WEB-035 |
| Nominal real / uso research / deploy | Incompatível sem autorização externa vigente | DEC-03/04/05, WEB-031/033/034/041 e produção continuam gates. Nenhuma missão de redesign os resolve | REQ-SEG-002/003; P0 | WEB-033/034/041, gates M8–M10 |

#### Reprodução isolada da exportação

2026-11-11, Python do `.venv`, runtime de `b5fccbb`, sem alteração no repositório.
Script temporário `/tmp/stroop_chg007_probe.py`, executado com
`PYTHONPATH=. .venv/bin/python /tmp/stroop_chg007_probe.py`: quatro observações
confirmadas por assertivas. Chamada inicial sem PYTHONPATH falhou apenas no import
`api`; corrigido comando, não runtime. Guards/consulta substituídos por doubles
sintéticos: **não prova HTTP/auth/PG, exploração real ou perda de dados reais**.
Receita reproduzível equivalente (nenhum secret operacional):

```python
import asyncio
from types import SimpleNamespace as N
from unittest.mock import patch
import api.exports as ex

async def run():
    config = N(session_secret='synthetic-only-secret',
               read_database_url='synthetic', database_url='synthetic')
    req = N(app=N(state=N(config=config)))
    actor = N(role='consulta', issuer='synthetic', subject='synthetic')
    pid = '00000000-0000-0000-0000-000000000001'
    with patch.object(ex, '_reject_query'), patch.object(
        ex, '_professional_write', return_value=actor
    ), patch.object(ex, 'query_multi_export_rows', return_value=[{
        'assessment_id': 'synthetic-A', 'participant_name': 'Pessoa Sintetica'
    }]) as query:
        preview = await ex.preview_export(req, ex.ExportPreviewRequest(
            project_id=pid, granularity='avaliacoes', columns=['assessment_id'],
            filters={'visit': ['V1']}))
        assert 'filters' not in query.call_args.kwargs
        assert preview['sample_rows'][0]['participant_name'] == 'Pessoa Sintetica'
        query.return_value = [{'assessment_id': 'synthetic-B', 'visit': 'V2'}]
        response = await ex.download_export(req, ex.ExportDownloadRequest(
            project_id=pid, granularity='avaliacoes', columns=['visit'],
            filters={'visit': ['V2']}, export_token=preview['export_token']))
        assert response.status_code == 200 and b'V2' in response.body
        assert 'filters' not in query.call_args.kwargs
asyncio.run(run())
```

Essas assertivas caracterizam lacunas locais de seleção/token/amostra, sem
declarar que todos os caminhos CSV têm defeito. Testes API/PG negativos de
isolamento por projeto/cadastro/nominal e CSV21 são obrigatórios em WEB-053;
não inferir ausência de problema por falta de reprodução PG nesta missão.

#### Validação documental e fechamento Git de CHG-007 — 2026-11-11

- `python3 scripts/verify_web_docs.py`: aprovado; 11 marcos, 56 tarefas, 75 requisitos/matriz, 15 riscos, cinco decisões, 37 aceitos; 90 documentos, 727 links e 112 âncoras na rodada anterior ao fechamento; grafo sem ciclos. Contagens de links podem crescer pelo próprio fechamento.
- `python3 -m unittest tests.test_verify_web_docs -v`: sete testes aprovados, zero falhas/erros/skips; validador e testes não alterados.
- `.venv/bin/python -m unittest tests.test_web_multi_export -v`: nove testes existentes aprovados, zero falhas/erros/skips, incluindo serialização, mascaramento do CSV e roundtrip Python/SQLite. Não testa autorização HTTP/PG ou corrige as lacunas da prévia.
- Probe sintético isolado acima: assertivas aprovadas; falha inicial de import sem PYTHONPATH corrigida no comando. Nenhuma suite PG, frontend/Vitest/typecheck/build ou Playwright/AA executada nesta missão documental; verificações futuras explicitamente PLANEJADAS.
- `git diff --check`: aprovado. Inspeção estrutural adicional comparou as 37 fichas CONCLUIDA e todo o registro anterior de CHG à base b5fccbb: conteúdo integral preservado. Primeira tentativa dessa inspeção procurava heading CHG-001 (que é linha histórica de tabela) e falhou no seletor; corrigida para seção de registro, passou sem modificar o histórico.
- Matriz requisito→tarefa→marco, IDs sequenciais/únicos, grafo e painel conferidos pelo validador; revisão semântica conferiu caminho crítico, gates externos, distinção de população A/T e cardinalidades. Somente oito Markdown canônicos em docs/ alterados. Código/testes/configurações/workflow/AGENTS/ADR-007 intactos; nenhum novo roadmap/arquivo de progresso. Histórico anterior arquivado na base Git imutável, sem fonte concorrente.
- Git da missão: branch `docs/chg-007-replanejamento-integrado` sobre `b5fccbb`; unidade documental `2d982d7bf7cdd40f7bf9ff9bfc27430cb7d76add`, commit/push com upstream concluídos. [PR #18](https://github.com/thiagorraposo/stroop-test-web/pull/18) aberto para main, somente oito Markdown; auto-merge desabilitado. No fechamento documental, verify aguardando execução/conclusão na SHA final; merge não realizado. **Instrução posterior explícita do proprietário nesta sessão: deixar o PR aberto, sem merge.** Auto-merge permanece desabilitado; CI aprovada não autoriza integração nesta missão. Não executar merge, deploy, tag ou release. O SHA do fechamento é consultável por `git log -1 --format=%H --grep='docs(planejamento): registra envio da CHG-007'`; resultado remoto final é consultável no PR/check correspondente, sem autorreferência artificial de commit. Nenhum aceite funcional de WEB-048..055.

## Retomada

### Retomada vigente — continuidade M8 e consulta POST integrada, 2026-11-12

Encerramento explícito solicitado pelo proprietário após a entrega: encerrar a
execução sem aguardar CI; deixar o GitHub executar e conferir os resultados em
outra sessão. Commits `7cc3562` (implementação) e `b10015e` (validação/fechamento)
enviados, HEAD/upstream/remoto conferidos em b10015e antes deste registro.
PR #19 permanece draft e sem merge; auto-merge desabilitado. CI final não
reconsultada neste encerramento, sem alegar aprovação. Na próxima retomada,
conferir os checks da revisão enviada antes de decidir qualquer integração.
Este registro será enviado na mesma branch; a CI correspondente segue no GitHub,
sem monitoramento ou execução local mantida aberta. WEB-031 local preservada.

Novo `continue o projeto` retoma M8 pela WEB-050 e mantém WEB-031 pendente.
React passou a aplicar/paginar pelo POST único; filtros disponíveis e ordenação
executados no servidor, com expiração e integridade entre páginas. CSV básico
preservado por snapshots da mesma leitura; recortes avançados sem fallback.
Evidências, comandos, falhas e limites na continuação EV-M8-050 de 2026-11-12.
WEB-050 EM_ANDAMENTO: completar catálogo residual/capacidades e UX7-AA antes de
aceitar. WEB-048 continua PRONTA e independente; WEB-031 BLOQUEADA por origem,
autorização, custódia e medição externas, sem impedir esse ramo. WEB-032 pendente.
37/56 aceitos, M8 2/12; nenhuma autorização de M9, deploy ou dados reais.

Branch reutilizada feat/m8-consulta-aplicada-unica, base d6d9dbb; alterações locais
da WEB-031 preservadas sem staging/commit/envio e .deploy-hostgator/ intacto.
PR #18 permanece aberto sem merge; PR #19 draft, sem integrar essa ancestralidade.
Consultar fechamento da evidência para SHA/push/check próprios da entrega.

### Retomada anterior — WEB-031 local autorizada, 2026-11-12

Proprietário autorizou notebook Mint como receptor temporário, configuração
local e ensaios exclusivamente sintéticos; vedou mudanças na VPS sem aprovação
específica. Preparação e provas em EV-M8-031-MINT. Timer local habilitado com
Linger; origem ainda não configurada, alerta esperado de indisponibilidade.
**WEB-031 BLOQUEADA** por origem/hostkey, instalação SSH restrita a aprovar,
custódia e medição externas. Notebook intermitente não comprova RPO 24 h;
RTO 4 h não presumido. Procedimento/pacote concretos prontos para aprovação.
Não conectar/alterar a VPS nem promover configuração sintética a operacional
por inferência. Próxima ação dependente: proprietário fornece dados públicos
da conexão/fingerprint e aprova os passos do runbook; continuar o ensaio
sintético externo somente após isso. Reinício real do notebook não ensaiado.

Branch `feat/web031-receptor-mint`, base `d6d9dbb`; sem commit/push/PR/CI/merge
nesta unidade, alterações disponíveis para revisão. Mantidos PR #18 sem merge,
PR #19 draft e `.deploy-hostgator/`; Ambulatório CPS intacto. WEB-050 conserva
seu trabalho e próximo passo da retomada anterior; WEB-048 independente.
37/56 aceitos e M8 2/12 preservados, sem autorização de M9/deploy/dados reais.

### Retomada anterior — execução M8 autorizada, 2026-11-11

Novo `continue o projeto` autoriza M8 e suas tarefas prontas e sucessoras,
sem avançar M9 ou autorizar operações externas. WEB-050 EM_ANDAMENTO: núcleo de
consulta aplicada/cancelamento, multisseleção de instrumentos e condição/resposta
na mesma tentativa implementados; entrada POST com capacidades parciais disponível.
Completar migração React, catálogo integral e UX7-AA antes do aceite.
Evidências e fechamento em EV-M8-050; próximo trabalho exato é ampliar as
capacidades do seletor e migrar consumidores React ao POST único, preservando
rejeição explícita dos recortes sem suporte; completar UX7-AA da ficha.
WEB-048 continua disponível independentemente.
Unidades `07473b9`, `7f43295`, condição/resposta e entrada POST normalizada; evidência atual em EV-M8-050. PR #19 draft aberto,
sem merge; verify anterior b4382e6 falhou no caso CSP Chromium (diagnóstico local
12/12 não explica a causa). Consultar fechamento atual para push/check por SHA.
Não integrar indiretamente a ancestralidade do PR #18.
WEB-048 permanece PRONTA; WEB-031 BLOQUEADA pelo destino externo/custódia.
37/56 aceitos preservados; nenhum aceite concedido no início da execução.
Branch `feat/m8-consulta-aplicada-unica` deriva de `67dfbf7` (CHG-007), pois
as fichas/contratos ainda não estão em main. PR #18 permanece aberto **sem
merge**, conforme instrução específica preservada; não integrar indiretamente
sua ancestralidade por outro PR. PRs #16/#17 e `.deploy-hostgator/` preservados.


### Retomada anterior — replanejamento integrado CHG-007, 2026-11-11

Missão atual: `replanejar`, **somente documentação**. M0–M7 mantêm aceites;
M8 passa a 2/12, M9 0/4 e M10 0/5. Global 37/56 (66,1%), 19 sem aceite,
por ampliação de oito tarefas; nenhuma conclusão funcional nova. WEB-048 e
WEB-050 PRONTAS tecnicamente; WEB-049/051..055 e WEB-032 PENDENTES conforme
grafo; WEB-031 BLOQUEADA por destino externo/custódia/medição autorizados.

Próxima ação exata: **`continue o projeto`**, em instrução posterior do
proprietário, autoriza **M8** e permite WEB-048/050 e sucessoras dentro de M8.
Não avançar M9 automaticamente. WEB-031 continua ramo externo: sua autorização
específica e recursos não decorrem desse comando; sua falta não impede tarefas
independentes da CHG-007, mas impede WEB-032/fechamento de M8. Priorizar seleção,
autorização e consistência de CSV antes de aceitar o visual integrado.

Git/validação documental desta missão: fechamento na seção EV-CHG-007;
nenhuma implantação/migration/tag/release, implementação ou operação em dados reais.
Branch inicial/PRs #16/#17 e material local não rastreado preservados.
Instrução final do proprietário: **manter PR #18 aberto, sem merge**, mesmo se
verify aprovar. Retomada da implementação depende da autorização posterior já
indicada; integração deste PR requer nova instrução explícita.


### Retomada anterior — conclusão do marco M7: Integração, compatibilidade histórica e transição (WEB-025 a WEB-028), 2026-11-09

Marco vigente **M7 integralmente concluído com 4 de 4 entregáveis aceitos**
(`WEB-025`, `WEB-026`, `WEB-027` e `WEB-028` **CONCLUIDAS**).
Entregue via Pull Request #14 (`feat/m7-transicao-e-compatibilidade-historica`),
aprovado na CI (`verify`, Run `42559837206`, 24m30s) e integrado à `main` via
Merge Commit tradicional (`e2bc001`).

Progresso global do projeto: **37/48 entregáveis aceitos (77,1%)**, 11 sem aceite:
marco **M7 com 4/4 aceitos**, encerrado sem pendências funcionais.
`WEB-031` permanece **BLOQUEADA** aguardando definição de destino externo.

Próxima ação exata: autorização formal do responsável pelo repositório para início do
marco **M8 (CI, infraestrutura e preparação operacional: WEB-031 e WEB-032)**,
especialmente a definição de destino e credenciais de teste para réplica externa (`WEB-031`).

Git da entrega: branch `feat/m7-transicao-e-compatibilidade-historica`, commit `1b7da61`,
PR #14, Run de CI `42559837206` e Merge Commit tradicional `e2bc001` na `main`.
Fast-forward local na `main` concluído e confirmado.

### Retomada anterior — replanejamento operacional e simplificação estrutural (CHG-006), 2026-11-08

Replanejamento documental **CHG-006** concluído e validado em escopo estritamente documental. Foram integrados ao planejamento canônico: a consolidação da interface profissional em **3 eixos fundamentais** ([ADR-008](arquitetura/ADR-008-simplificacao-estrutural-e-fluxo-direto-sessao.md)) inspirados no modelo mental do Streamlit (Resultados e Análise Unificada; Aplicação Direta / Nova Avaliação; Gestão Cadastral e Acessos), o formulário sem atrito em etapa única estilo PsychoPy Runner com modalidades duais ("Iniciar Agora neste Dispositivo" presencial e "Gerar Link / QR Code" remoto), a orquestração relacional atômica e transparente (`REQ-SESS-003`) e a preservação metodológica/psicométrica absoluta do motor jsPsych e das 12 métricas oficiais.

Progresso global do projeto: **33/48 entregáveis aceitos (68,8%)**, 15 sem aceite:
marco **M5 integralmente concluído com 5/5 aceitos**, e escopo de transição de **M7** (`WEB-028`) alinhado à paridade de experiência de uso dos 3 eixos.
`WEB-031` permanece **BLOQUEADA** aguardando definição de destino externo.

Próxima ação exata: obter aprovação do responsável pelo repositório sobre as decisões da CHG-006 antes de iniciar qualquer implementação de código; com autorização, iniciar o marco **M7 (Migração, paridade e retirada do Streamlit)** ou os refinamentos operacionais correspondentes.

### Retomada anterior — conclusão do marco M5 e exportações CSV (WEB-020), 2026-11-08

Marco vigente **M5 integralmente concluído com 5 de 5 entregáveis aceitos**
(`WEB-017`, `WEB-018`, `WEB-047`, `WEB-019` e `WEB-020` **CONCLUIDAS**).
Tarefa final `WEB-020` entregue via Pull Request #10 (`feat/m5-exportacoes-csv-filtradas`)
aprovado na CI (Run `42522885308`) e integrado à `main` via Merge Commit tradicional (`ff45b7a`).

Progresso global do projeto: **33/48 entregáveis aceitos (68,8%)**, 15 sem aceite:
marco **M5 com 5/5 aceitos**, encerrado sem pendências funcionais.
`WEB-031` permanece **BLOQUEADA** aguardando definição de destino externo.

Próximo marco: **M7 (Migração, paridade e retirada do Streamlit)**, dependente de
autorização expressa do responsável para início da execução técnica.

Git da entrega: branch `feat/m5-exportacoes-csv-filtradas`, commit `f6cc03b`,
PR #10, Run de CI `42522885308` e Merge Commit tradicional `ff45b7a` na `main`.
Fast-forward local na `main` concluído e confirmado.

### Retomada anterior — validação de detalhe, histórico e análises descritivas (WEB-019), 2026-11-08

Tarefa pronta `WEB-019` concluída em M5, entregue via Pull Request #8
(`feat/m5-detalhes-resultados-metricas`) aprovado na CI (Run `42517336016`) e
integrado à `main` via Merge Commit tradicional (`6be3042`).

Progresso global do projeto: **32/48 entregáveis aceitos (66,7%)**, 16 sem aceite:
marco **M5 com 4 de 5 entregáveis aceitos** (`WEB-017`, `WEB-018`, `WEB-047` e `WEB-019` **CONCLUIDAS**),
`WEB-020` **PRONTA** e `WEB-031` **BLOQUEADA** por destino externo autorizado indisponível.

Próxima ação exata: prosseguir no marco vigente **M5** executando a próxima tarefa
pronta `WEB-020` ("Conferir exportação do conjunto filtrado no React"), implementando
o módulo `Exportações` (`REQ-CSV-005`) com 5 granularidades (`pacientes`, `avaliacoes`,
`tentativas`, `metricas`, `stroop_21_colunas`), seleção de colunas, pré-visualização de contagem,
controle `deidentified` vs. `nominal` e neutralização de CSV formula injection.

Git da entrega: branch `feat/m5-detalhes-resultados-metricas`, commit `48839a2`,
PR #8, Run de CI `42517336016` e Merge Commit tradicional `6be3042` na `main`.
Fast-forward local na `main` concluído e confirmado.

### Retomada anterior — conclusão de WEB-047 (CRUD administrativo de pacientes, avaliadores e correção de vínculos), 2026-11-08

Comando `continue o projeto` no marco vigente **M5** avançou com a conclusão da tarefa
`WEB-047` ("Implementar CRUD administrativo completo de pacientes e avaliadores,
histórico longitudinal e correção auditada de vínculos"), integrada via Pull Request #6
(`feat/m5-crud-pacientes-avaliadores-vinculos`) aprovado na CI (Run `42508601295`) e
unido à `main` via Merge Commit tradicional (`b050e4c`).

Progresso global do projeto: **31/48 entregáveis aceitos (64,6%)**, 17 sem aceite:
marco **M5 com 3 de 5 entregáveis aceitos** (`WEB-017`, `WEB-018` e `WEB-047` **CONCLUIDAS**),
`WEB-019` **PRONTA**, `WEB-020` **PENDENTE** e `WEB-031` **BLOQUEADA** por destino
externo autorizado indisponível.

Próxima ação exata: prosseguir no marco vigente **M5** executando a próxima tarefa
pronta `WEB-019` ("Validar detalhe, tentativas, métricas e proveniência"), consolidando
os módulos `Avaliações e histórico` (acompanhamento operacional de sessões e checkpoints)
e `Resultados e análises` (`REQ-REL-005`: detalhe completo com vínculos, visualizações
longitudinais e gráficos interativos sem normas clínicas).

Git da entrega: branch `feat/m5-crud-pacientes-avaliadores-vinculos`, commit `93bb8f1`,
PR #6, Run de CI `42508601295` e Merge Commit tradicional `b050e4c` na `main`.
Fast-forward local na `main` concluído e confirmado.

### Retomada anterior — catálogo de filtros combinados, KPIs e administração React (WEB-017 e WEB-018), 2026-11-08

Tarefas `WEB-017` e `WEB-018` concluídas em M5, entregues via Pull Request #5
(`feat/m5-filtros-kpis-administracao`) aprovado na CI (Run `42501325270`) e
integrado à `main` via Merge Commit tradicional (`b625ab6`). Progresso avançou
para 30/48 aceitos (62,5%).

### Retomada anterior — adoção de Pull Request, Push e Merge tradicional e autorização de M5, 2026-11-07

Por instrução explícita do responsável em 2026-11-07 ("continue o projeto e adicione
pullresquest merge e push ao workflow do projeto"), foram formalizados no workflow
canônico os comandos e ciclo de GitHub Flow com commits e pushes autônomos
(`git push -u origin BRANCH`), abertura/atualização de Pull Request para `main`
(`gh pr create`) e integração exclusivamente via Merge Commit tradicional
(`gh pr merge --merge`), preservando commits originais (sem Squash Merge, sem Rebase
Merge e sem push direto em `main`).

Comando `continue o projeto` autoriza o marco **M5 — Interface administrativa e analítica React**,
com `WEB-017` ("Revalidar filtros, lista e agregações autorizadas") e `WEB-018` ("Revalidar
administração React de contas e vínculos") prontas para execução em branch dedicada
de M5 (`feat/m5-interface-administrativa-react`). Progresso global mantido em
**28/48 entregáveis aceitos (58,3%)**, 20 sem aceite: `WEB-017` e `WEB-018` **PRONTAS**,
17 **PENDENTES** e `WEB-031` **BLOQUEADA** por destino externo autorizado indisponível.

Próxima ação exata: integrar esta atualização de governança documental via PR #2
(`docs(git): adota Merge Commit tradicional com PR obrigatório`) em `main` com
Merge Commit tradicional após CI aprovada, e iniciar o desenvolvimento de M5
(`WEB-017` e `WEB-018`) a partir de `main` na branch de feature dedicada.

### Retomada anterior — conclusão de M4 expandido (WEB-045 e WEB-046), 2026-11-07

Comando `continue o projeto` no marco vigente **M4** concluído até o limite do
marco, sem avançar implicitamente para outro marco. `WEB-045` e `WEB-046`
**CONCLUIDAS**, encerrando integralmente **M4 (6/6)** (`EV-M4-045/046`). Progresso
global: **28/48 entregáveis aceitos (58,3%)**, 20 sem aceite: `WEB-017` e `WEB-018`
**PRONTAS** (aguardando autorização do marco M5), 17 **PENDENTES** e `WEB-031`
**BLOQUEADA** por destino externo autorizado indisponível.

Próxima ação exata: emitir nova instrução explícita (`continue o projeto`) para
autorizar o marco **M5 — Interface administrativa e analítica React**, iniciando
por `WEB-017` ("Revalidar filtros, lista e agregações autorizadas") e `WEB-018`
("Revalidar administração React de contas e vínculos"), seguidas por `WEB-047`,
`WEB-019` e `WEB-020`. `WEB-031` permanece aguardando destino externo autorizado;
`DEC-03` (`WEB-033`) e `DEC-05` (`WEB-041`/`WEB-038`/`WEB-040`) mantêm seus gates
próprios.

Git: branch `feat/m4-fluxo-avaliacoes`, sincronizada com fast-forward seguro a
partir de `cdbd195a191fb4d042665c8bf3ba79ea693f1c3c` (`CHG-005`); `main` (`fe8f24f`)
e `origin/main` (`db56b40`) preservadas sem integração. Evidências funcionais e
integradas completas em `EV-M4-045/046`. Entrega identificável por
`git log -1 --format=%H --grep='feat(web): implementa cadastros centrais e preparação completa em M4'`.
Validação documental, scanner e `git diff --check` aprovados antes do commit;
envio e consulta de Actions por SHA registrados no fechamento abaixo. Sem PR, merge,
tag, deploy, migração real ou acesso a dados/secrets operacionais.

#### Fechamento Git de M4 expandido (WEB-045 e WEB-046) — 2026-11-07

Entrega **`1844ca2c3d13c1a0eacab60f3ca45e9400708b24`**, enviada com upstream na
branch `feat/m4-fluxo-avaliacoes`; igualdade `HEAD`, `origin/feat/m4-fluxo-avaliacoes`
e `git ls-remote --heads origin feat/m4-fluxo-avaliacoes` confirmada nessa SHA.
`gh run list --branch feat/m4-fluxo-avaliacoes --limit 5 --json headSha,status,conclusion,url`
retornou `[]`: nenhuma execução Actions encontrada para `1844ca2` (o workflow
existente dispara em `push` para `main`, `pull_request` e `workflow_dispatch`);
CI remota **não executada** para esta SHA, sem transferir aprovação de outra SHA.

Validador documental final (`python3 scripts/verify_web_docs.py`): **11 marcos,
48 tarefas, 59 requisitos, 13 riscos, cinco decisões, 28 aceitos, 87 documentos,
666 links e 81 âncoras**, grafo sem ciclos; `python3 -m unittest tests.test_verify_web_docs -v`
(**7/7 aprovados**, sem skips), `.venv/bin/python scripts/verify_web_ci.py sources`
(**405 fontes versionadas verificadas**, zero achados) e `git diff --check`
aprovados. Este fechamento documental é identificável por
`git log -1 --format=%H --grep='docs: registra envio e fechamento de WEB-045/046 em M4'`;
conferir seu envio por `HEAD`/upstream/remoto, sem commit artificial de
autorreferência. Próxima ação preservada: autorizar explicitamente **M5/WEB-017 e WEB-018**
com novo `continue o projeto`. Nenhum PR, merge, tag, deploy ou acesso a dados reais executado.

### Retomada anterior — replanejamento funcional e UX (CHG-005), 2026-11-07

Replanejamento documental **CHG-005** concluído e validado em escopo estritamente documental. Foram integrados ao planejamento canônico: o novo fluxo profissional (`Login da equipe → Dashboard → Pacientes/Avaliadores → Preparar avaliação → Executar teste → Armazenar resultados → Consultar, analisar e exportar`), a revisão formal de `DEC-01` via [ADR-007](arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md), os cadastros centrais de pacientes (`web_patients`, `PAT-...`) e avaliadores (`web_evaluators`, `EVA-...`), o formulário completo de preparação da sessão alinhado ao PsychoPy Builder (`stroop_go_nogo_ptbr.psyexp`), a retirada de importação CSV do produto (`REQ-CSV-004`), a exportação CSV avançada em cinco granularidades (`REQ-CSV-005`) e a reformulação modular da interface administrativa (`REQ-REL-004/005`, `REQ-UX-012`).

Progresso global recalculado com a inclusão de `WEB-045`, `WEB-046` (em `M4`) e `WEB-047` (em `M5`): **26/48 entregáveis aceitos (54,2%)**, preservando integralmente os 26 aceites históricos (`M0`, `M1`, `M2`, `M3`, `WEB-013`..`016` em `M4` e `M6`), e **22 entregáveis sem aceite**: `1` **PRONTA** (`WEB-045`), `20` **PENDENTES** e `1` **BLOQUEADA** (`WEB-031`, aguardando destino externo autorizado).

Próxima ação exata: emitir instrução explícita (`continue o projeto`) para retomar o marco vigente **M4 — Fluxo completo de avaliações e cadastros centrais**, iniciando por `WEB-045` ("Implementar cadastros centrais de pacientes e avaliadores no backend e schema"), cuja dependência técnica (`WEB-016` e `WEB-024`) e revisão de `DEC-01` (`CHG-005` / `ADR-007`) já estão satisfeitas, seguida por `WEB-046` ("Reformular preparação da sessão com seleção cadastral, campos originais e resumo") para concluir `M4 (6/6)` antes de avançar para `M5` (`WEB-047`, `WEB-017`..`020`).

#### Fechamento Git de CHG-005 — 2026-11-07

Entrega documental **`cdbd195a191fb4d042665c8bf3ba79ea693f1c3c`** (`docs: replaneja cadastros centrais, preparação, exportação e UX em CHG-005`), criada na branch `docs/chg-005-replanejamento-funcional-ux` (base `7a35a09fb32cecd1a408340ddfc1ac5f9cc3557c`) e enviada com upstream para `origin/docs/chg-005-replanejamento-funcional-ux`. `gh run list --branch docs/chg-005-replanejamento-funcional-ux --limit 5 --json headSha,status,conclusion,url` retornou `[]` (o workflow existente dispara em `push` para `main`, `pull_request` e `workflow_dispatch`, não para push em branch documental sem PR). Nenhum PR ou merge automático foi executado.

### Retomada anterior — conclusão de M4 (WEB-013 a WEB-016), 2026-11-06

Comando `continue o projeto` no marco vigente **M4** concluído até o limite do
marco, sem avançar implicitamente para outro marco. `WEB-013`, `WEB-014`,
`WEB-015` e `WEB-016` **CONCLUIDAS**, encerrando **M4 (4/4)**. Progresso global:
**26/45 entregáveis aceitos (57,8%)**, 19 sem aceite: `WEB-017` e `WEB-018`
**PRONTAS** (aguardando autorização do marco M5), 16 **PENDENTES** e `WEB-031`
**BLOQUEADA** por destino externo autorizado indisponível.

Próxima ação exata: emitir nova instrução explícita (`continue o projeto`) para
autorizar o marco **M5 — Interface administrativa e analítica React**, iniciando
por `WEB-017` ("Revalidar filtros, lista e agregações autorizadas") e `WEB-018`
("Revalidar administração React de contas e vínculos"), cujas dependências
(`WEB-016` e marcos `M4`, `M6`) estão integralmente aceitas. `WEB-031` permanece
aguardando destino externo autorizado; `DEC-03` (`WEB-033`) e `DEC-05`
(`WEB-041`/`WEB-038`/`WEB-040`) mantêm seus gates próprios.

Git: branch `feat/m4-fluxo-avaliacoes`, base `7e77ef8127c20d5af255969d93a20d4116f8a247`
(`feat/m6-autenticacao-local`), `main` (`fe8f24f`) e `origin/main` (`db56b40`)
preservadas sem integração. Evidências funcionais e integradas completas em
`EV-M4-013/016`. Entrega identificável por
`git log -1 --format=%H --grep='feat(web): conclui fluxo ponta a ponta de avaliações em M4'`.
Validação documental, scanner e `git diff --check` aprovados antes do commit;
envio e consulta de Actions por SHA registrados no fechamento abaixo. Sem PR,
merge, tag, deploy, migração real ou acesso a dados/secrets operacionais.

#### Fechamento Git de M4 — 2026-11-06

Entrega **`0cf71b6ecdfd14edda090ba2bb7d8bdad7bcccbb`**, enviada com upstream na
branch `feat/m4-fluxo-avaliacoes`; igualdade `HEAD`, `origin/feat/m4-fluxo-avaliacoes`
e `git ls-remote --heads origin feat/m4-fluxo-avaliacoes` confirmada nessa SHA.
`gh run list --branch feat/m4-fluxo-avaliacoes --limit 5 --json headSha,status,conclusion,url`
retornou `[]`: nenhuma execução Actions encontrada para `0cf71b6` (o workflow
existente dispara em `push` para `main`, `pull_request` e `workflow_dispatch`);
CI remota **não executada** para esta SHA, sem transferir aprovação de outra SHA.

Validador documental final (`python3 scripts/verify_web_docs.py`): **11 marcos,
45 tarefas, 50 requisitos, 12 riscos, cinco decisões, 26 aceitos, 86 documentos,
626 links e 76 âncoras**, grafo sem ciclos; `python3 -m unittest tests.test_verify_web_docs -v`
(**7/7 aprovados**, sem skips), `.venv/bin/python scripts/verify_web_ci.py sources`
(**393 fontes versionadas verificadas**, zero achados) e `git diff --check`
aprovados. Este fechamento documental é identificável por
`git log -1 --format=%H --grep='docs: registra envio e fechamento de M4'`;
conferir seu envio por `HEAD`/upstream/remoto, sem commit artificial de
autorreferência. Próxima ação preservada: autorizar explicitamente **M5/WEB-017 e WEB-018**.
Nenhum PR, merge, tag, deploy ou acesso a dados reais executado.

### Retomada anterior — conclusão de M6 (WEB-021 e WEB-024), 2026-11-06

Comando `continue o projeto` no marco vigente **M6** concluído até o limite do
marco, sem avançar implicitamente para outro marco. `WEB-021` e `WEB-024`
**CONCLUIDAS**, encerrando **M6 (4/4)**. Progresso global: **22/45 entregáveis
aceitos (48,9%)**, 23 sem aceite: `WEB-013` **PRONTA** (aguardando autorização
do marco M4), 21 **PENDENTES** e `WEB-031` **BLOQUEADA** por destino externo
autorizado indisponível.

Próxima ação exata: emitir nova instrução explícita (`continue o projeto`) para
autorizar o marco **M4 — Fluxo ponta a ponta de avaliações**, iniciando por
`WEB-013` ("Integrar preparação profissional e identificação por convite"), cujas
dependências (`WEB-008`, `WEB-012`, `WEB-024` e marcos `M2`, `M3`, `M6`) estão
integralmente aceitas. `WEB-031` permanece aguardando destino externo autorizado;
`DEC-03` (`WEB-033`) e `DEC-05` (`WEB-041`/`WEB-038`/`WEB-040`) mantêm seus gates
próprios.

Git: branch `feat/m6-autenticacao-local`, base `7872863` (`EV-M6-021-BASE` em
`188eef5`), `main` (`fe8f24f`) e `origin/main` (`db56b40`) preservadas sem
integração. Evidências funcionais e negativas completas em `EV-M6-021/024`.
Entrega identificável por `git log -1 --format=%H --grep='feat(auth): conclui autenticação local e revisão de segurança em M6'`.
Validação documental, scanner e `git diff --check` aprovados antes do commit;
envio e consulta de Actions por SHA registrados no fechamento abaixo. Sem PR,
merge, tag, deploy, migração real ou acesso a dados/secrets operacionais.

#### Fechamento Git de M6 — 2026-11-06

Entrega **`09f444ce1132fdc0db643d3028c30f1612a2cd66`**, enviada com upstream na
branch `feat/m6-autenticacao-local`; igualdade `HEAD`, `origin/feat/m6-autenticacao-local`
e `git ls-remote --heads origin feat/m6-autenticacao-local` confirmada nessa SHA.
`gh run list --branch feat/m6-autenticacao-local --limit 5 --json headSha,status,conclusion,url`
retornou `[]`: nenhuma execução Actions encontrada para `09f444c` (o workflow
existente dispara em `push` para `main`, `pull_request` e `workflow_dispatch`);
CI remota **não executada** para esta SHA, sem transferir aprovação de outra SHA.

Validador documental final (`python3 scripts/verify_web_docs.py`): **11 marcos,
45 tarefas, 50 requisitos, 12 riscos, cinco decisões, 22 aceitos, 86 documentos,
622 links e 72 âncoras**, grafo sem ciclos; `python3 -m unittest tests.test_verify_web_docs -v`
(**7/7 aprovados**, sem skips), `.venv/bin/python scripts/verify_web_ci.py sources`
(**393 fontes versionadas verificadas**, zero achados) e `git diff --check`
aprovados. Este fechamento documental é identificável por
`git log -1 --format=%H --grep='docs: registra envio e fechamento de M6'`;
conferir seu envio por `HEAD`/upstream/remoto, sem commit artificial de
autorreferência. Próxima ação preservada: autorizar explicitamente **M4/WEB-013**.
Nenhum PR, merge, tag, deploy ou acesso a dados reais executado.

### Retomada anterior — aceite de suporte e encerramento M3, 2026-11-06

O responsável respondeu **“aceito”** à proposta concreta de suporte restrito e
limites de EV-M3-012 apresentada nesta sessão. WEB-012 CONCLUIDA e **M3 7/7
concluído**, com conferência em EV-M3-012-ACEITE. **20/45 aceitos (44,4%)**,
25 sem aceite: 23 PENDENTES, WEB-021 PRONTA e WEB-031 BLOQUEADA.
R01/R02/R11 permanecem abertos; aceite local não elimina falhas históricas,
perda de pendências, integração M4 ou validação física/metodológica M9.

Próxima ação exata: autorização posterior explícita de **M6/WEB-021**, próxima
implementação tecnicamente pronta no caminho de integração (autenticação local).
O aceite encerra M3, sem autorizar outro marco. M4 mantém dependência de M6;
WEB-031 aguarda destino externo autorizado. Nenhuma continuidade excepcional.

Git: branch `docs/m3-aceite-suporte`, criada da base `9979b64` limpa e alinhada
a origin após fetch; main/origin/main preservadas, sem integração. Evidências
funcionais históricas não reexecutadas; esta unidade registra decisão e valida
somente documentação. Entrega identificável por `git log -1 --format=%H
--grep='docs: registra aceite de suporte e encerra M3'`; fechamento de envio abaixo.
Sem PR/merge/tag/deploy, migrations ou dados reais.

Validação local desta unidade: `python3 scripts/verify_web_docs.py` aprovado
(11 marcos, 45 tarefas, 50 requisitos, 12 riscos, cinco decisões, 20 aceitos,
85 documentos, 612 links e 70 âncoras, sem ciclos); `python3 -m unittest
tests.test_verify_web_docs -v`: sete testes aprovados, sem skips; `git diff
--check` aprovado. Revisão do diff restrita aos três documentos desta entrega.
Campanha, Vitest, browsers e testes Python funcionais não reexecutados: nenhum
runtime mudou. CI desta branch será consultada por SHA após envio.

#### Fechamento Git do aceite M3 — 2026-11-06

Entrega **`0730f37ba476340ec96e22cc5263c525a06f9ded`**, enviada com upstream
na branch `docs/m3-aceite-suporte`; igualdade HEAD/upstream/ls-remote confirmada.
`gh run list --branch docs/m3-aceite-suporte --limit 5 --json
headSha,status,conclusion,url` retornou `[]`: nenhuma execução Actions encontrada;
CI não executada, sem aprovação transferida de outra SHA. Não houve dispatch.
Fechamento documental identificável por `git log -1 --format=%H
--grep='docs: registra envio do aceite M3'`; conferir envio por HEAD/upstream/remoto.
Próxima ação preservada: autorizar explicitamente M6/WEB-021. Nenhum outro marco
iniciado, PR/merge ou deploy executado.

### Retomada anterior — integração documental CHG-004, 2026-11-06

Missão exclusivamente documental encerrada após validação/versionamento.
**19/45 aceitos (42,2%)**, 26 sem aceite: 23 PENDENTES, WEB-012 EM_VALIDACAO,
WEB-021 PRONTA e WEB-031 BLOQUEADA. M3 **6/7** permanece vigente; M6 **2/4** e
M8 **2/4** parciais, demais marcos/aceites preservados. Local login PLANEJADO,
nenhuma implementação nesta sessão. R05/R07/R09 atualizados e R12 ABERTO.

Próxima ação pelo workflow permanente: responsável aceitar suporte restrito dos
resultados EV-M3-012 ou bloquear motor; `validar marco atual` pode conferir esses
critérios sem conceder aceite pelo responsável. **Não há tarefa funcional PRONTA
em M3** para `continue o projeto` implementar antes desse gate. WEB-021 é a
próxima implementação tecnicamente pronta no caminho de integração, **em M6**,
exigindo autorização posterior explícita desse marco; não é selecionada por um
`continue o projeto` ainda restrito a M3. Nenhuma continuidade excepcional ativa.
M6/WEB-024 antecedem M4. WEB-031 continua dependendo de destino externo autorizado;
WEB-028/032, DEC-03/033, WEB-034/035/036, DEC-05/041 e WEB-037–040 mantêm seus
pré-requisitos e aprovações separados. Não repetir campanha/baseline sem divergência.

Git: branch `docs/autenticacao-local-roadmap`, base auditada `bdd2631`, main e
origin/main preservadas. Entrega identificável por `git log -1 --format=%H
--grep='docs: integra autenticação local e revisa pendências canônicas'`;
seu envio deve ser conferido por HEAD/upstream/ls-remote, sem commit artificial
de autorreferência. Resultado da validação e envio no fechamento desta missão.
CI histórica aprovada apenas em 0d79fd2/EV-M8-030; CI desta revisão não executada,
sem transferência de aprovação. Nenhum PR/merge/tag/deploy/migration ou dado real.


#### Fechamento Git de CHG-004 — 2026-11-06

Entrega documental **`be014bb71c3d3bf3fe8953624090d3fa101f59d0`**, branch
`docs/autenticacao-local-roadmap`, enviada com upstream. Push bem sucedido e
igualdade HEAD/upstream/`git ls-remote --heads origin docs/autenticacao-local-roadmap`
confirmada nessa SHA. Validador reexecutado após commit: mesmos 11 marcos,
45 tarefas, 50 requisitos, 12 riscos, cinco decisões e 19 aceitos; 85 documentos,
611 links/69 âncoras válidos e grafo sem ciclos. Python observado 3.12.3.
`gh run list --branch docs/autenticacao-local-roadmap --limit 5 --json
headSha,status,conclusion,url` retornou `[]`: nenhuma execução Actions dessa
branch; sem aprovação CI alegada. Nenhum workflow_dispatch solicitado/executado.

Este fechamento registra resultados de envio/validação e limites da missão;
é identificável por `git log -1 --format=%H --grep='docs: registra validação e envio da CHG-004'`.
Seu envio é verificável por HEAD/upstream/remoto, sem autorreferência de SHA.
A missão encerra documentalmente; próxima ação permanece aceite WEB-012 em M3,
com WEB-021 pronta tecnicamente apenas para futura sessão autorizada de M6.
Sem implementação, novo marco, PR, merge, tag, deploy ou dados reais.

### Retomada anterior — execução excepcional encerrada, 2026-11-06

**19/45 aceitos (42,2%)**, 26 sem aceite; M3 6/7, M6 2/4, M8 2/4.
Autorização temporária desta sessão permitiu atravessar marcos com dependências
satisfeitas. WEB-022/023/029/030 CONCLUIDAS; WEB-021/031 BLOQUEADAS; WEB-012
EM_VALIDACAO. Nenhum marco adicional encerrado. Regras de AGENTS/workflow e
semântica permanente de continue o projeto não foram alteradas; a exceção
termina nesta execução.

Base limpa `851ac3a`, fetch concluído; main `fe8f24f`, origin/main `db56b40`
preservadas sem integração. Branch `test/m6-m8-validacao-isolada` mantém base
M2/M3 ainda não integrada. Commits enviados e conferidos por upstream/remoto:
`d10fa376349f948fef82adcda43521db003b5411` (M6),
`357e28f39b132b0213998b5066051bdd7b2fa04d` (infra),
`0d79fd297f169ad25c63402dbd11c535694a0b98` (documentação do scanner).
Entrega/fechamento da réplica identificável por `git log -1 --format=%H
--grep='test(infra): ensaia réplica SSH e agenda em ambiente sintético'`;
conferir seu envio por HEAD/upstream/ls-remote, sem autorreferência artificial.

Pipeline integral local e Actions aprovados em **0d79fd2**, URL/SHA/resultados
em EV-M8-030; falha inicial 357e28f preservada. Novo harness SSH posterior tem
validação real própria em EV-M8-029/031, sem alegar Actions nesse novo HEAD.
Documentação final: validador, sete testes documentais, scanner de fontes e
`git diff --check` aprovados. Evidências M6 em EV-M6-022/023. Sem PR/merge/tag,
VPS/deploy ou dados reais. Worktree sparse e imagens API/proxy sintéticas
preservadas; PG e recursos transitórios criados para os ensaios removidos.

Seleção global final e próxima ação:

- WEB-012: responsável aceitar limites de suporte de EV-M3-012 ou bloquear motor;
  aprovação do alcance DEC-04 não aprova resultados por antecipação.
- WEB-021: disponibilizar conta/cliente/ambiente OIDC de teste autorizado;
  não solicitar secrets pela conversa nem abrir .env operacional. WEB-024 depende dela.
- WEB-031: entrega técnica local pronta e ensaiada, inclusive SSH/agenda/alerta.
  Responsável deve disponibilizar destino externo/custódia de teste autorizados
  e revisar limites; REQ-INF-003 não é comprovado por duas cópias no mesmo host.
- M4 aguarda M3/M6; M5/M7 aguardam seus gates; WEB-032 aguarda M7/WEB-031;
  M9/M10 preservam pré-requisitos, DEC-03/05 e validação física/metodológica.

**Nenhuma tarefa elegível sem recurso/aceite adicional**. Próxima ação:
aceite WEB-012; para execução técnica independente, WEB-021 com ambiente
OIDC autorizado ou continuação WEB-031 com destino externo de teste autorizado.
Não repetir baseline global/campanha concluída sem divergência concreta.

### Retomada anterior — campanha local concluída; suporte em revisão, 2026-11-06

Marco autorizado M3, **15/45 aceitos (33,3%)**, 30 sem aceite; M3 **6/7**.
WEB-011 CONCLUIDA: dez capturas completas válidas por navegador com transporte
ativo e falhas de rede. A campanha original teve 19 passes e uma falha de
preparação sem trilha; uma sessão Chromium adicional explícita passou, sem
apagar nem converter a falha original em sucesso. Nenhuma falha D5 nas vinte
capturas completas, todas validadas no domínio Python. Relatório em EV-M3-011.

WEB-012 EM_VALIDACAO: proposta concreta em EV-M3-012. Próxima ação exata:
responsável aceitar a viabilidade técnica restrita aos ambientes/fixture
ensaiados ou bloquear motor para investigação adicional. A aprovação anterior
DEC-04 autorizou alcance da campanha; não aprova antecipadamente seus resultados.
M3 não encerrado. Não iniciar outro marco; M6 antecede o fluxo M4 e exige
posterior autorização própria. Validação física/metodológica segue M9; sem
pesquisa real, produção, PR, merge ou deploy.

### EV-M3-011 — aprovação do alcance e campanha local, 2026-11-05

Aprovação explícita pelo proprietário/responsável de pesquisa e operação:
“eu aprovo esse alcance para DEC-04”. Proposta aprovada: equipamento local,
Chromium e Firefox visíveis, dez sessões sintéticas por ambiente, apresentação
final, transporte incremental ativo e falhas de rede, D5 e todas falhas
preservados; validação física/metodológica pendente. Não aprova equivalência,
suporte universal, uso real ou deploy. DEC-03/05 independentes.

Matriz identificada por inspeção somente técnica: Intel Core i5-1334U,
12 CPUs lógicas, cerca de 16 GiB RAM (15 GiB exibidos por free), Linux
7.0.0-42-generic x86_64, X11 DISPLAY :0; xrandr confirma tela eDP-1 primária
1920×1080 a 60,00 Hz. Viewport da campanha 1280×720; browsers/versões e período
real de quadro serão registrados por execução. Não é medição física de tela.
Sem carga artificial concorrente; carga normal do desktop não é controlada.

Git inicial limpo, branch feat/m3-motor-experimental, HEAD/upstream a32b896,
main fe8f24f e origin/main db56b40; fetch acessível, base M2/M3 preservada sem
merge/rebase. Não repetida baseline global. Preparação autorizada inclui worker
ADR-005 e ponto de entrega de tentativa completa no motor; fluxo produto/UX
integrado e HTTPS/API/PG continuam M4. Campanha usa fixture sintética com motores
jsPsych e Dedicated Worker reais e receptor HTTP double, sem alegar banco real.
App da fixture identifica transporte como web-0.1.0+visual.1.0.0.transport.1;
app de produto continua na versão visual anterior até integração em M4.

Preparação local: 292/292 Vitest aprovados, typecheck/build aprovados; cobre
cópia imutável após fim observado e próxima fixação, fila contígua/um voo,
ACK lento/perdido, replay original, 1/2/4/8 s e Retry-After, expiração e erros
401/403/409/410. Inicialmente uma asserção do teste assumiu atributo de tentativa
na fixação (só existe no estímulo); corrigida para verificar o sinal de fixação,
sem mudar o runtime. Duas tipagens iniciais corrigidas (assinaturas distintas
onerror/onmessageerror e parâmetro não utilizado). Na preparação a campanha
ainda era PLANEJADA; o aceite abaixo deriva dos ensaios, não da aprovação documental.

#### Execução e conferência de WEB-011 — 2026-11-05/06

Implementação e primeira série: **78f8120bd40869cdbb9d234cd9e4600ad91dcb96**.
Suplemento: **4d5ab56bec47a9d4885e48a20e3871f9e036e925**, somente melhoria do
harness para preservar diagnóstico quando a página perde a fixture, registrar
navegações e não mascarar falha original com erro de cleanup. `git diff 78f8120
4d5ab56 --exit-code -- web/src condicoes stroop` aprovado: mesmo motor, worker,
condições e gates. Hash do diff web vazio nas vinte capturas, sem fonte local
não versionada durante cada ensaio. Sem dependências instaladas/atualizadas.

Ambiente: matriz local descrita acima; Node 24.15.0, npm 11.16.0, Python 3.12.3,
Playwright 1.64.1. Chromium **156.0.8078.4**, Firefox **157.0**, ambos visíveis,
viewport efetivo 1280×720 e foco/visibilidade conferidos. Screen reportado pelo
browser é metadado de automação, distinto da configuração física xrandr: não é
medição física. Prática jsPsych completa antes de cada principal, relógio real,
ordem canônica sintética e uma pressão automatizada durante estímulo; não é
resposta de participante nem teste do fluxo profissional/convite/API real.

| Campanha com transporte ativo | Chromium | Firefox |
|---|---|---|
| Capturas completas válidas / tentativas totais | **10 / 11** | **10 / 10** |
| Transições em capturas completas | 640 | 640 |
| Período de quadro medido | 16,700 ms | 16,340–16,680 ms |
| Maior erro absoluto de transição | **2,0 ms** | **4,0 ms** |
| Maior erro absoluto do principal de 60 s | **1,8 ms** | **3,0 ms** |
| Maior custo observado de enqueue/postMessage | 2,4 ms | 1,0 ms |
| Observações completas recebidas pelo double | 160 | 160 |
| Requests de checkpoint por bloco | 12–16 | 11–16 |

Por navegador: três sessões saudáveis, três com ACK atrasado **4,5 s**, duas
com primeiro ACK perdido **após commit simulado** e recuperação por consulta,
duas com **503 durante todo o principal** e recuperação somente após término.
Fila/JSON/HTTP/retries executam no Dedicated Worker; motor apenas copia após
fim observado e início da próxima fixação. Um voo, agrupamento, replay do mesmo
lote e fila de até 16 sem descarte. Comparados os 320 registros recebidos pelo
double com os resultados em RAM: igualdade integral. ACK/hash do double é
sintético; canonização/durabilidade/replay transacional reais permanecem
comprovados em M2 e voltam à integração HTTPS/API/PG de M4, não neste ensaio.

D5 conferido em cada uma das 1.280 transições contra o quadro da própria sessão;
duração de cada bloco dentro de ±100 ms. As vinte conclusões foram submetidas
sem ajuste de timestamps a `stroop.domain.web_results.validate_result` com
CSV-fonte e ordem observada: **20/20 aprovadas**, 320 tentativas. Cópia/postMessage
medido com performance.now; desvio combinado inclui renderização, contorno/HUD,
callbacks, transporte e compositor. Não isola custo causal de cada componente.
Retries/progresso são observados em trilhas, sem render React por quadro.

Referência antes/depois: EV-M3-044 sem transporte tinha Firefox 157.0 com máximo
2 ms de erro de transição e 2 ms de duração, uma captura; agora máximo 4/3 ms
em dez. Ambas séries dentro de D5. Chrome preparatório era **157.0.8103.38**,
distinto do Chromium atual: não comparar como ensaio causal pareado. Não
alegar diferença estatística, ausência de custo ou melhoria científica.

Falha preservada: réplica Chromium original 3/10, cenário lost, **26,663 s**,
`window.web011` ausente ao tentar preservar captura. Snapshot mostra página
inicial; não há trilha principal recuperável. O cleanup mascarou o erro anterior;
a causa da perda de fixture/navegação não foi determinada. Resultado original
continua **falhou**, sem atribuir gate D5 nem inventar timestamps. Horários civis
mostram descontinuidade: réplica 3 iniciou 2026-11-05T23:46:16Z e a próxima
2026-11-06T02:51:12Z; duração monotônica total do runner foi 27,9 min. Inspeção
posterior: NTP ativo/sincronizado. Não atribuir causalidade à mudança de relógio
nem usar data civil para RT. Preservados results.json e error-context originais.
Suplemento explícito do mesmo cenário completou e confirmou 16 registros;
não substitui a falha, não demonstra sua causa nem estabilidade universal.

Investigação histórica: confrontadas transições atuais, foco e gates com
EV-M3-009/010 e sua observação de intervalos rAF de até 50 ms. Nova campanha
não reproduziu invalidação D5 nas vinte capturas; não há trace causal suficiente
para atribuir as falhas antigas a código/CPU/compositor. R01/R02/R11 continuam
abertos. Não alterados agendamento nominal, limites, suporte aprovado ou histórico.

Comandos executados e resultados:

- Em web: `npx playwright test --config playwright.web011.config.ts`:
  **19 aprovados, 1 falha, zero skips/retries**, 27,9 min; série original intacta.
- Em web: `npx playwright test --config playwright.web011.config.ts
  --project chromium-local --grep 'replica 3/10 lost'
  --output=test-results/web011-supplement --reporter=list`: **1 aprovado**,
  1,4 min, suplemento separado; não sobrescreveu o relatório JSON original.
- `npm --prefix web test`: **292/292**, 18 arquivos; `npm --prefix web run build`:
  typecheck e Vite aprovados, sem skips. Worker foi ensaiado via Vite de teste;
  integração/bundle de produto com transporte permanece M4.
- `.venv/bin/python -m unittest tests.test_fase3_condicoes_tempos
  tests.test_nucleo_compartilhado tests.test_web_export tests.test_web_results
  tests.test_verify_web_docs -q`: **51 aprovados**, sem skips.
- Em web: `WEB_TEST_PORT=4273 npx playwright test e2e/presentation.spec.ts
  --workers=1 --trace=off --output=test-results/web011-visual`: **6 aprovados**,
  29,9 s, dez cores/DOM/árvore acessível/HUD/feedback e 40 screenshots sintéticos;
  relógio controlado/headless, distintos da campanha de relógio real acima.
- Verificação Python inline das vinte engineering.json: montar payload com
  resultado original, PROTOCOL_ID/TEST_VERSION, app_version da captura e frame;
  chamar validate_result com CSV-fonte/ordem capturada, conferir igualdade dos
  registros recebidos, limites D5 e SHA-256 do diff vazio. **20/20 aprovadas**.

Artefatos exclusivamente sintéticos e ignorados: `web/test-results/web011/`
(results.json original, 19 engineering.json, attachments, erro/contexto da falha),
`web/test-results/web011-supplement/` (uma captura adicional),
`web/test-results/web011-manifest.json` (20 caminhos/hashes/SHA de fonte) e
`web/test-results/web011-visual/`. Sem logs/exportações/coletas versionados.
Critérios WEB-011 conferidos; aceite de campanha de engenharia, não de suporte.
Envio/CI e fechamento documental registrados após validação abaixo.

#### Fechamento Git e validação — 2026-11-06

Branch `feat/m3-motor-experimental`. Implementação `78f8120bd40869cdbb9d234cd9e4600ad91dcb96`,
diagnóstico `4d5ab56bec47a9d4885e48a20e3871f9e036e925`, relatório/aceite WEB-011
**`f9e94461cb23ec868658021734c9d94348694a5f`**. Push dos três confirmado por
HEAD/upstream/ls-remote nessa SHA, árvore limpa; nenhuma integração de main.
Consulta `gh run list --branch feat/m3-motor-experimental --limit 5
--json headSha,status,conclusion,url` retornou **[]** após envio: nenhuma execução
Actions encontrada, não é CI aprovada. Evidências acima são locais.

Validador documental: **11 marcos, 45 tarefas, 47 requisitos, 11 riscos, cinco
decisões, 15 aceitos, 84 documentos, 569 links e 49 âncoras**, grafo sem ciclos;
sete testes do validador e git diff --check aprovados. Históricos preservados,
sem artifacts/exports/dados/segredos no staging. Nenhuma migration, produção,
PR, merge, tag ou deploy. Git da implementação e SHA ensaiada distintos do
fechamento documental, sem promover push a aceite funcional.

Relatório EV-M3-012 apresentado ao responsável por pergunta nesta sessão;
resposta de aceite de suporte ainda não recebida neste fechamento. WEB-012
EM_VALIDACAO, M3 6/7; não avançar outro marco. O fechamento é identificável por
`git log -1 --format=%H --grep='docs: registra envio da campanha DEC-04'`;
conferir seu próprio envio por HEAD/upstream/remoto, sem commit artificial
para autorreferenciar SHA. Se houver resposta posterior, registrar decisão
explícita antes de concluir WEB-012/M3.

### EV-M3-012 — proposta de viabilidade e limites para revisão, 2026-11-06

**Histórico da proposta:** aceite posterior registrado em EV-M3-012-ACEITE;
o texto abaixo preserva os limites apresentados e o estado anterior à resposta.

Relatório técnico pronto, **aceite do responsável ainda pendente**. A aprovação
DEC-04 autorizou executar a campanha; não é aceitação de resultados futuros.

Proposta: aceitar **viabilidade técnica local do motor/jsPsych com Dedicated
Worker** na apresentação stroop-web-outline/1.0.0 e app da fixture
web-0.1.0+visual.1.0.0.transport.1, nas versões Chromium/Firefox e equipamento
medidos, viewport 1280×720, em primeiro plano, sem carga artificial concorrente.
Vinte capturas completas passaram D5, incluindo os cenários de rede descritos;
a falha adicional de preparação e as invalidações históricas permanecem abertas.
Não afirmar suporte sem falhas; os gates devem continuar invalidando violações.

Janela de perda: no cenário saudável cada tentativa foi confirmada; no ensaio
503 as **16 observações ficaram sem confirmação durante o bloco** e chegaram
após recuperação. ACK lento agrupou tentativas; ACK perdido foi reconciliado
por consulta. Uma queda antes de confirmação pode perder a tentativa em curso
e todo sufixo pendente, inclusive o bloco inteiro. Não há limite garantido de
uma tentativa nem promessa de perda zero; recibo parcial não é conclusão oficial.

Limites: teclado automatizado, receptor HTTP double, sem HTTPS/API/PG integrado
nesta campanha; nenhuma latência física de monitor/teclado medida, equivalência
PsychoPy, avaliação psicométrica, pesquisa real ou produção. Outros equipamentos,
SO, browsers/versões, dispositivos móveis, cargas e resoluções de timing não
medidos. Screenshots em 1920×1080 validam apresentação, não campanha temporal
nessa resolução. Falhas antigas não tiveram causa comprovada. M4 deve integrar
worker, prontidão/start, expiração, entrega parcial/aborto e recibo oficial com
HTTPS/API/PG; M9 mantém validação física/metodológica. Não antecipar esses aceites.

Responsável deve aceitar explicitamente estes limites ou bloquear o motor para
investigação adicional. Sem essa decisão, WEB-012 EM_VALIDACAO e M3 não encerrado.

### EV-M3-012-ACEITE — decisão do responsável e fechamento M3, 2026-11-06

Após apresentação do relatório EV-M3-012 e pergunta explícita sobre aceitar o
suporte restrito e seus limites para concluir WEB-012/M3, o proprietário respondeu
**“aceito”**. Trata-se do aceite dos resultados observados, distinto da aprovação
prévia de alcance DEC-04. Nenhuma ampliação da matriz foi solicitada.

Conferência dos critérios de WEB-012 e do gate M3:

| Critério | Evidência e alcance aceitos |
|---|---|
| Condições, regras, plugins e lifecycle | WEB-009/010, EV-M3-009/010; condições/tempos preservados e falhas históricas mantidas. |
| Apresentação e HUD aprovados | WEB-042/043/044, EV-M3-042/043 e EV-M3-044; stroop-web-outline/1.0.0, sem caixa/precisão agregada, feedback individual preservado. |
| Campanha final com transporte ativo e D5 | WEB-011/EV-M3-011; implementação 78f8120bd40869cdbb9d234cd9e4600ad91dcb96, diagnóstico 4d5ab56bec47a9d4885e48a20e3871f9e036e925 e relatório f9e94461cb23ec868658021734c9d94348694a5f; dez capturas completas por navegador, falha adicional de preparação preservada. |
| Ambientes e suporte delimitados | EV-M3-012: viabilidade técnica local com Dedicated Worker, fixture web-0.1.0+visual.1.0.0.transport.1, equipamento/versões Chromium e Firefox medidos, 1280×720, primeiro plano e sem carga artificial concorrente. |
| Transporte e janela de perda | Worker real/receptor HTTP double; ACK lento/perdido e 503 medidos. As 16 observações podem ficar pendentes durante o bloco; interrupção pode perder todo o sufixo, inclusive bloco inteiro. Sem garantia de perda zero. |
| Aceite explícito e limites posteriores | Resposta “aceito” nesta sessão. Sem medição de latência física, equivalência PsychoPy/psicométrica, suporte móvel/outros ambientes, autorização de pesquisa real ou produção. Integração HTTPS/API/PG permanece M4; validação física/metodológica, M9. |

Todos os critérios de WEB-012 e as sete tarefas de M3 estão comprovados dentro
desse alcance; M3 encerrado. R01/R02/R11 e falhas sem causa determinada permanecem
abertos para seus gates posteriores. Evidências funcionais acima são históricas,
não reexecuções desta sessão. Nenhum runtime, protocolo, métrica/CSV ou gate
alterado. Verificações documentais e Git desta unidade na Retomada vigente.

### Retomada anterior — regressão WEB-044 aceita, 2026-11-05

Marco autorizado **M3**, ainda não encerrado. WEB-044 **CONCLUIDA** em EV-M3-044;
**14/45 entregáveis aceitos (31,1%)**, 31 sem aceite; M3 **5/7**.
WEB-011 continua **BLOQUEADA** por DEC-04; WEB-012 **PENDENTE**. Nenhuma tarefa
pronta restante no marco; M4 não autorizado por esta sessão.

Próxima ação exata: responsável metodológico aprovar a matriz DEC-04 para a
apresentação `stroop-web-outline/1.0.0`: combinações de hardware/SO/browser e
versões, recursos disponíveis e alcance de engenharia/físico/metodológico.
Depois executar WEB-011: dez execuções sintéticas por ambiente aprovado com
transporte incremental ativo, ACKs lentos/perdidos/retries/falhas e D5 inalterado;
preservar falhas e investigar invalidações históricas. WEB-012 depende da
campanha e da aceitação explícita dos limites de suporte. R01/R02/R11 abertos.
Capturas preparatórias não medem latência física nem comprovam estabilidade,
equivalência psicométrica ou autorização para pesquisa real/deploy.

### EV-M3-044 — regressão consolidada, 2026-11-05

Autorização: novo `continue o projeto`, limitado ao marco vigente M3 e tarefas
prontas. WEB-042/043 concluídas, apresentação D3/D4 aprovada; WEB-044 iniciada
nesta sessão. Branch `feat/m3-motor-experimental`, worktree inicialmente limpa,
HEAD/upstream `5c355f7fa3c53997dde0cdd9cc8a5655ffd09a78` após fetch.
main local `fe8f24f` e origin/main `db56b40` preservadas; base M2/M3 ainda não
integrada. Nenhuma divergência que exigisse repetir baseline/auditoria global.

SHA ensaiada: **`5c355f7fa3c53997dde0cdd9cc8a5655ffd09a78`**. Comparação
`git diff e17a7b9 HEAD --exit-code -- web stroop condicoes tests` passou:
runtime, fixtures e testes idênticos à entrega visual de EV-M3-042/043.
Reutilizados explicitamente seus quatro fluxos completos headed aprovados
(principal e quatro feedbacks da prática em Chromium/Firefox), sem declará-los
reexecutados nesta sessão. As regressões abaixo são novas e complementam essa
evidência; nenhum aceite deriva apenas da identidade de código.

| Critério WEB-044 | Evidência conferida |
|---|---|
| Dez cores, tinta, contorno uniforme, ausência de caixa e centro/fonte/escala | presentation.spec.ts: quatro combinações Chromium/Firefox × 1280×720/1920×1080; 40 PNGs novos. Inspecionadas as dez cores nas quatro combinações por folhas de contato e screenshot integral do HUD. DOM/CSS verificam tinta, centro geométrico, fonte/peso, fundo transparente e stroke uniforme. |
| Sem precisão em prática/principal, sem substituto ou resíduo | DOM e árvore acessível em presentation.spec.ts; estrutura HUD unitária e inspeção integral. Progresso periférico sem deslocar estímulo; nenhuma animação ou espaço de precisão. |
| Progresso, cronômetro e lifecycle | presentation.test.ts testa total recebido, avanço após conclusão, ausência de relógio na prática e MutationObserver sem escrita no mesmo segundo. main/practice/Host testam origem monotônica, cleanup idempotente, cancelamento, StrictMode e ausência de callbacks residuais. Sem timers novos. |
| Feedback, Go/No-Go, congruência, janelas e sequência | Motores unitários e plugins reais jsPsych verificam quatro classificações, primeira pressão nova, RT positivo/fim exclusivo, tecla mantida, todas as condições e interrupções. Fluxos completos previamente aprovados na mesma fonte reutilizados conforme acima; captura real preparatória nova descrita abaixo. |
| Versão e métricas/CSV | presentation.test.ts confere stroop-web-outline/1.0.0 e web-0.1.0+visual.1.0.0; summary.test.ts compara fixtures compartilhadas Python. test_web_export confere 21 colunas, importação sintética SQLite e 12 métricas com unidades; precisão permanece calculada. Integração real WEB-016/019/020 não antecipada. |

Ambiente observado: Linux `7.0.0-42-generic`, Python **3.12.3**, Node
**24.15.0**, npm **11.16.0**, Playwright **1.64.1**. Visual: Chromium
**156.0.8078.4**, Firefox **157.0**. Captura temporal: Google Chrome
**157.0.8103.38** e Firefox Playwright **157.0**, janela visível, teclado
automatizado, API double HTTP/Vite, captura sintética W16 habilitada.
Sem instalação/atualização de dependência, produção ou dados reais.

Comandos/resultados executados nesta sessão:

- `npm --prefix web test`: **281 aprovados/17 arquivos**, sem skips.
- `npm --prefix web run build`: typecheck TypeScript e build Vite aprovados.
- `.venv/bin/python -m unittest tests.test_fase3_condicoes_tempos
  tests.test_nucleo_compartilhado tests.test_web_export -q`: **25 aprovados**,
  sem falhas/erros/skips; fixtures exclusivamente sintéticas.
- Em web: `WEB_TEST_PORT=4273 npx playwright test e2e/presentation.spec.ts
  --workers=1 --trace=off --output=test-results/web044-visual`: **6 aprovados**,
  sem falhas/skips/retries; relógio controlado/headless. 40 screenshots e quatro
  folhas de contato ignorados em `web/test-results/web044-visual/`.
- Em web: `npx playwright test --config playwright.w16.config.ts
  --grep 'replica local 1 de 10' --output=test-results/web044-timing`:
  **2 aprovados**, zero falhas/skips/retries, 2,8 min, execução serial visível.
  O filtro seleciona apenas uma execução preparatória por navegador; não são
  dez execuções nem campanha WEB-011. Trilhas brutas e summaries preservados em
  `web/test-results/web044-timing/`, artefatos sintéticos ignorados pelo Git.

| Observação preparatória | Chrome local | Firefox Playwright |
|---|---|---|
| Execuções completas / transições | 1 / 64 | 1 / 64 |
| Período de quadro medido | 16,700 ms | 16,310 ms |
| Maior desvio absoluto de transição | 1,5 ms | 2,0 ms |
| Duração observada / desvio absoluto de 60 s | 59.998,5 ms / 1,5 ms | 59.998,0 ms / 2,0 ms |
| Viewport / screen reportados | 1440×901 / 1440×900 | 1440×900 / 1760×990 |

Ambas dentro de um quadro por transição e de 100 ms no total nessas execuções.
Viewport Chrome reportado com 901 px de altura pelo ambiente, apesar da
configuração 1440×900; diferença preservada, sem presumir matriz homologada.
Esses valores não isolam o custo do HUD/renderização nem avaliam impacto do
transporte incremental, ACKs/retries ou falha real de servidor. API double
registra um start/complete por execução; nenhum ensaio HTTPS/API/PG ou latência
física nesta tarefa. As falhas Firefox/Chromium anteriores continuam preservadas
em EV-M3-009/010; dois passes não determinam causa nem estabilidade.

Todos os critérios próprios WEB-044 conferidos na tabela acima; nenhum runtime,
schema, protocolo, CSV ou cálculo alterado. REQ-UX-001…007 recebem a evidência
consolidada na matriz; REQ-UX-011 apenas na parcela experimental M3, mantendo
escopo M5 pendente. Persistência/relatórios/admin seguem WEB-016/019/020.
DEC-04 e WEB-011/012 continuam sem aceite; sem PR, merge ou deploy.

Validação documental: `python3 scripts/verify_web_docs.py`,
`python3 -m unittest tests.test_verify_web_docs -v` e `git diff --check`;
sete testes documentais aprovados. Contagens finais e Git no fechamento abaixo.
Entrega identificável por `git log -1 --format=%H
--grep='docs: consolida regressão experimental de WEB-044'`; SHA ensaiada acima
não é o commit documental. Conferir envio por HEAD/upstream/remoto e Actions por
SHA; push de branch não implica execução de CI.

### Fechamento EV-M3-044 — 2026-11-05

Entrega documental em **`21891431e64a1ef3e3eb5659246946019837e747`**, branch
`feat/m3-motor-experimental`, enviada: HEAD, upstream e `git ls-remote --heads
origin feat/m3-motor-experimental` conferidos na mesma SHA. Consulta
`gh run list --branch feat/m3-motor-experimental --limit 5
--json headSha,status,conclusion,url` retornou `[]`: nenhuma execução Actions
na branch; CI não executada para essa SHA, sem alegar aprovação remota.

Validador final: **11 marcos, 45 tarefas, 47 requisitos, 11 riscos, cinco decisões,
14 aceitos, 84 documentos, 566 links e 46 âncoras**, grafo sem ciclos.
Sete testes do validador e `git diff --check` aprovados. Revisão Git restrita a
três documentos; screenshots/trilhas sintéticos permanecem ignorados. Nenhuma
falha/skips nesta sessão; falhas históricas explicitamente mantidas acima.
WEB-044 concluída; próxima ação é aprovação DEC-04, sem tarefa pronta adicional
em M3. Nenhum avanço M4, PR, merge ou deploy.

Este fechamento é identificável por `git log -1 --format=%H
--grep='docs: registra envio e limites da regressão WEB-044'`; conferir seu
próprio envio por HEAD/upstream/remoto, sem commit artificial de autorreferência.

### Retomada anterior — D3 visual implementada, 2026-11-05

Marco autorizado M3; missão atual limitada à revisão D3 e WEB-042/043, agora
CONCLUIDAS. Variante `stroop-web-outline/1.0.0`, snapshot identificado e
`app_version=web-0.1.0+visual.1.0.0`. Progresso **13/45 (28,9%)**, 32 sem aceite;
M3 **4/7**, ainda não encerrado. WEB-044 **PRONTA**, próxima tarefa executável
pelo futuro `continue o projeto`; não antecipada como aceite nesta missão.
WEB-011 continua BLOQUEADA por DEC-04 e dependente de WEB-044/layout final com
transporte incremental ativo; WEB-012 PENDENTE. R01/R02/R11 continuam abertos.
Nenhuma validação física, equivalência psicométrica, pesquisa real ou deploy.

### EV-M3-042/043 — revisão D3 e apresentação visual, 2026-11-05

Autorização: esta missão aprova explicitamente a apresentação pelo proprietário
e permite implementar WEB-042/043 se o gate for satisfeito. Fonte científica
registra o proprietário como responsável por pesquisa/validação/operação desde
2026-10-16; nenhuma exigência vigente de aprovador distinto foi encontrada, nem
aprovação atribuída a terceiro. Histórico D3 anterior transcrito/preservado;
D3 revisada e D4 complementada por versão visual. DEC-04 continua PENDENTE.

Inicialização: branch `feat/m3-motor-experimental`, worktree limpa, HEAD/upstream
`3d9d515c1f3269b418d5416cd0f4d55005c212dd` após fetch; main local `fe8f24f`,
origin/main `db56b40`, base M2/M3 não integrada preservada sem merge/rebase.
Auditoria direcionada: D3/D4, fichas WEB-042/043, snapshot/HUD, motores, Host,
metadados app_version, contratos e testes. Documentação validada **antes** do
runtime: 45 tarefas/47 requisitos/11 riscos/cinco decisões/11 marcos; links e
grafo válidos, diff check aprovado. Não foi repetida auditoria global M0/M1.

Critérios conferidos:

| Entrega | Evidência atual e limite |
|---|---|
| WEB-042: sem retângulo/caixa, contorno fino e tinta preservada | CSS `--experiment-outline-width:.02em`, stroke branco e paint-order stroke fill; nenhum tratamento por cor. Unidade verifica palavras/tintas; Playwright confere dez cores, fonte/peso, fundo transparente, contorno uniforme e centro geométrico em 1280×720/1920×1080, Chromium/Firefox. 40 screenshots sintéticos, amostras inspecionadas incluindo todas as dez cores entre os dois navegadores. Não é validação perceptiva/psicométrica. |
| WEB-042: geometria/escala/tempos preservados | Dimensões/fonte/fundo geral originais mantidos; HUD absoluto periférico; sem scroll na fixture isolada. Testes de tempos/condições e motores passam; nenhuma mudança em agendamento, condição, teclado ou ordem. |
| WEB-043: retirada real da precisão | Motores deixam de criar nós/rótulos/barras/percentuais; DOM/árvore acessível de prática e principal não contêm agregados/substitutos. Removidos apenas contadores/formatadores que desenhavam o HUD principal; cálculo oficial em summary/domínio, exportações e métricas administrativas intactos. Contador de treino/feedback individual preservado. |
| WEB-043: progresso/tempo | HUD imperativo compartilhado presentation.ts recebe total do order validado e número de concluídas; sem total fixo no indicador. Barra 3px sem transição/animação; relógio principal MM:SS com números tabulares/largura estável e origem monotônica existente. Teste de MutationObserver confirma ausência de escrita por quadro no mesmo segundo. Sem novo timer/relógio de prática ou render React por quadro. |
| WEB-043: feedback e lifecycle | Prática mantém os quatro resultados/feedbacks, repetição e sem limiar; testes reais Chromium/Firefox concluem 16 principais sem encurtar resposta. Suite Vitest cobre Host/cleanup, métricas, relatórios e janelas já existentes. Esses ensaios não substituem integração real M4/M5 ou campanha DEC-04. |

Ambiente: Linux `7.0.0-42-generic`, Node `24.15.0`, npm `11.16.0`, Python
`3.12.3`, Playwright `1.64.1`; Chromium **156.0.8078.4**, Firefox **157.0**.
Sem instalação/atualização de dependências; apenas fontes/fixtures sintéticas.

Comandos e resultados desta sessão:

- `npm --prefix web test`: **281/281 aprovados**, 17 arquivos, incluindo novo
  presentation.test.ts e regressões de cálculos/painel. Sem skips.
- `npm --prefix web run typecheck` e `npm --prefix web run build`: aprovados.
- Em web: `WEB_TEST_PORT=4273 npx playwright test e2e/presentation.spec.ts
  --workers=1 --trace=off --output=test-results/d3-visual-final`: **6/6 aprovados**,
  headless, motores reais com relógio controlado. Confere DOM/árvore acessível,
  dez cores, centro, contorno, progresso, fonte tabular/largura, ausência de
  animações e feedback da prática. Artefatos sintéticos ignorados em
  `web/test-results/d3-visual-final/` (40 PNGs); não são coletas nem exportações.
- Em web: `WEB_TEST_PORT=4273 npx playwright test e2e/main.spec.ts
  e2e/practice.spec.ts --grep 'principal executa|rodada real' --workers=1
  --trace=off --headed --output=test-results/d3-flow`: **4/4 aprovados**, prática
  e principal completos por navegador com relógio real. API double em HTTP/Vite;
  não é integração HTTPS/API/PG, ensaio de latência física ou campanha D5 de
  dez execuções por ambiente com transporte incremental ativo.
- `.venv/bin/python -m unittest tests.test_fase3_condicoes_tempos
  tests.test_nucleo_compartilhado tests.test_web_export tests.test_verify_web_docs
  -q`: **32 aprovados**, sem skips; fontes locais/cores/tempos, métricas e CSV
  preservados. Nenhuma migration ou suíte PG necessária para este escopo.
- Validador documental e `git diff --check`: aprovados; **45 tarefas, 47 requisitos,
  11 riscos, cinco decisões, 11 marcos, 13 aceitos, 84 documentos, 565 links e
  45 âncoras**, sem ciclos. Documentação não valida experimento.

Falhas preservadas: primeira tipagem acusou chamada residual updateHud; rodada
focada subsequente teve 34 falhas/57 aprovações pelo mesmo ReferenceError.
Corrigida a chamada no tick, seguida da suite completa aprovada. Primeira rodada
visual headed: 3 falhas/3 aprovações, por fixture que mantinha página com scroll
(deslocando centro em 1280) e timeout/fechamento Firefox no setViewportSize antes
da execução. Fixture passou a isolar DOM e fixar viewport no contexto. Rodada
headless intermediária: 6 aprovados, mas listener remanescente gerou mensagem de
interrupção ao fechar página; acrescentado cleanup explícito afterEach. Rodada
final acima: 6 aprovados sem aquela mensagem; sem afrouxar tolerância geométrica,
interrupções ou limites D5. Falhas históricas Firefox de EV-M3-009/010 permanecem
abertas para campanha; estes novos passes não determinam sua causa/estabilidade.

Aceites restritos às fichas WEB-042/043; WEB-044 mantém regressão consolidada e
WEB-011/012 os gates científicos/técnicos. M4/M5 não antecipados. Sem alteração
de regras, fórmulas, schema, persistência, CSV, produção ou recursos externos.
Sem PR/merge/deploy. Entrega em **`e17a7b90d88f14acfb9707e3636ea05faa388832`**,
push confirmado por HEAD/upstream/ls-remote na mesma SHA. Consulta `gh run list
--branch feat/m3-motor-experimental --limit 5 --json headSha,status,conclusion,url`
retornou `[]`: nenhuma execução Actions, não é CI aprovada. Fechamento documental
identificável por `git log -1 --format=%H
--grep='docs: registra aceite visual de WEB-042 e WEB-043'`; conferir seu envio
por HEAD/upstream/remoto. Validador final preserva IDs/aceites contra a HEAD nova.
A implementação é identificável por `git log -1 --format=%H
--grep='feat(web): aplica apresentação visual aprovada na revisão D3'`.

### Retomada anterior — integração CHG-003 (histórico)

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
Entrega documental e validador em **`85f95ac971a489da8e570ef58151ba9d32a68975`**;
push confirmado por igualdade HEAD/upstream/`git ls-remote --heads origin
feat/m3-motor-experimental` na mesma SHA. `gh run list --branch
feat/m3-motor-experimental --limit 5 --json headSha,status,conclusion,url` retornou
`[]`: nenhuma execução Actions encontrada, não equivale a CI aprovada.
Validador reexecutado após o commit para conferir preservação dos novos IDs
contra HEAD. Registro de fechamento identificável por `git log -1 --format=%H
--grep='docs: registra evidências da integração UX'`; seu envio deve ser conferido
por HEAD/upstream/remoto, sem commit artificial de autorreferência.
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
