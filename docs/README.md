# Índice documental

Leitura inicial: [README do produto](../README.md) → [auditoria](AUDITORIA_REPLANEJAMENTO.md)
→ [arquitetura](ARQUITETURA_WEB.md) → [requisitos/matriz](REQUISITOS_E_RASTREABILIDADE.md).

| Fonte | Papel exclusivo |
|---|---|
| [Projeto Stroop Test](Projeto%20Stroop%20Test.md) | Único backlog: marcos/tarefas/estados/progresso/aceite/riscos/decisões/retomada |
| [Acompanhamento visual](PROGRESS.md) | Acesso ao painel de marcos e aceites no backlog, sem contagem paralela |
| [WORKFLOW_CODEX_CLI](WORKFLOW_CODEX_CLI.md) | Protocolo dos quatro comandos e Git autônomo sem PR/merge automático |
| [AGENTS raiz](../AGENTS.md) e [docs](AGENTS.md) | Instruções estáveis e limites |
| [ARQUITETURA_WEB](ARQUITETURA_WEB.md), [ADRs](arquitetura/) | Visão atual/alvo e decisões; [ADR-004](arquitetura/ADR-004-replanejamento-plataforma.md) consolida a direção; [ADR-006](arquitetura/ADR-006-autenticacao-local.md) define autenticação local alvo |
| [REQUISITOS_E_RASTREABILIDADE](REQUISITOS_E_RASTREABILIDADE.md) | Catálogo A–L, origem e vínculos; não mantém progresso |
| [Decisões metodológicas](experimento/DECISOES_DO_EXPERIMENTO.md), [protocolo](experimento/PROTOCOLO_WEB.md), [CSV](experimento/CSV_UNIFICADO.md) | Regras científicas, limites e intercâmbio |
| [Modelo](dados/MODELO_DE_DADOS.md), [migrations](dados/MIGRACOES_POSTGRESQL.md), [HTTP](desenvolvimento/CONTRATO_API_WEB.md) | Contratos técnicos canônicos, sem cópias |
| [Segurança](seguranca/), [acesso WEB](seguranca/ACESSO_WEB.md) | Autorização, privacidade, ameaças e incidentes |
| [Operação](operacao/), [WEB Docker](operacao/WEB_DOCKER.md), [VPS](operacao/DEPLOY_WEB_VPS.md), [recuperação](operacao/WEB_RECUPERACAO.md) | Runbooks existentes; não autorizam execução |
| [CI](desenvolvimento/CI_WEB.md), [validação](VALIDACAO_WEB.md), [homologação](operacao/HOMOLOGACAO_WEB.md) | Reprodução e evidências históricas datadas, não reexecução atual |
| [Registro de alterações](REGISTRO_DE_ALTERACOES.md) | Fatos datados, sem contabilidade paralela |
| [Estrutura](ESTRUTURA_DO_PROJETO.md), [API](../api/README.md), [Web](../web/README.md), [scripts](../scripts/README.md) | Mapa e comandos existentes |
| [Legado](legado/), [etapas 1–12](legado/Projeto%20Stroop%20Test.md), [Wxx](legado/ROADMAP_WEB_2026-11-04.md), [retomada anterior](legado/RETOMADA_2026-11-04.md) | Arquivos congelados, histórico e aceites anteriores; não executar como backlog |

ROADMAP_WEB.md, PROGRESS.md e desenvolvimento/WORKFLOW_CODEX_CLI.md são pontes de
compatibilidade. DECISOES_DO_EXPERIMENTO.md e MODELO_DE_DADOS.md nesta raiz apontam
para suas fontes científicas nas subpastas; não duplicam contratos.
