# ADR-004 — Consolidação da plataforma modular e governança única

Data: 2026-11-04. Estado: ACEITA como direção técnica/documental nesta missão;
aceite técnico de software e liberação científica permanecem separados.

## Contexto

A missão agora abrange aplicação, gestão e análise de avaliações cognitivas,
iniciando por Stroop Go/No-Go. A [auditoria](../AUDITORIA_REPLANEJAMENTO.md) encontrou
React/Vite/jsPsych/FastAPI já implementados, além de PsychoPy/Streamlit.
Reconstruir do zero descartaria contratos, testes e autorização existentes.

## Decisão

Consolidar monólito modular Python/FastAPI + React/TypeScript/Vite, PostgreSQL,
Compose/Nginx/HTTPS; reutilizar núcleo de métricas, ingestão e persistência.
PsychoPy é referência metodológica histórica; Streamlit permanece compatível
na transição, deixando de ser interface operacional final. Não remover agora.
Outros instrumentos terão contratos/versionamento próprios; não implementá-los
antecipadamente, nem promover a demonstração sintética a instrumento real.

Manter jsPsych hospedado em componente React, com plugins temporais existentes
que controlam DOM/teclado/relógio. Comparação para M3:

| Alternativa | Compatibilidade e precisão | Manutenção e integração | Custo / decisão |
|---|---|---|---|
| jsPsych + plugins existentes | Preserva quadro, HUD, janela e interrupção já codificados; requer medição real | Host React com ciclo de montagem/limpeza explícito; pacote especializado e testes atuais | Menor migração; escolhida para revalidação |
| Plugins padrão jsPsych | Exigiriam provar mesma janela fixa, HUD e semântica de tecla mantida | Menos código próprio, mas composição e adaptação ainda necessárias | Investigar só se M3 mostrar ganho; não substituir por preferência |
| Motor próprio sem jsPsych | Nenhuma garantia temporal adicional; reproduziria infraestrutura/testes | Todo teclado, lifecycle e dados sob manutenção local | Rejeitado por custo sem benefício comprovado |
| React dirigindo cada quadro | Renderizações não constituem relógio experimental | Acopla apresentação administrativa ao motor | Rejeitado para o caminho temporal |

A escolha não certifica precisão. A documentação oficial de
[jsPsych sobre timing](https://www.jspsych.org/v8/overview/timing-accuracy/)
explica dependência de ambiente; sua documentação de
[execução e armazenamento](https://www.jspsych.org/v8/overview/running-experiments/)
separa tarefa no navegador de persistência no servidor. FastAPI suporta
[organização modular](https://fastapi.tiangolo.com/tutorial/bigger-applications/).
Fontes consultadas em 2026-11-04; não se decidiu atualizar versões/locks.

## Governança e consequências

Único backlog executável: `docs/Projeto Stroop Test.md`, IDs WEB imutáveis.
Roadmap Wxx e etapas 1–12 são arquivos históricos congelados. ADR-001 continua
referência das fronteiras; ADR-002 mantém VPS existente e objetivos operacionais;
ADR-003 mantém vínculo explícito de legado. Esta decisão substitui apenas as
orientações antigas de backlog/comandos/Git e a ideia de interfaces ainda futuras.
Decisões D1–D6 e fórmulas não são alteradas.

GitHub Flow adaptado: branches coesas, commits e pushes autônomos validados;
sem PR automático, sem merge automático, sem force push/bypass. Integração à main,
produção e dados reais dependem de autorização específica. Proteções existentes
podem exigir revisão/procedimento futuro; não serão reduzidas por esta decisão.

Alternativas rejeitadas: dois backlogs ativos (divergência); reaproveitar 87%
(progresso enganoso); microserviços (complexidade sem necessidade); reescrita total
(risco de perda de semântica). Custo aceito: coexistência temporária e nova
revalidação sem invalidar aceites históricos. Próximas mudanças metodológicas
exigem responsável científico, registro de impacto e novo versionamento aplicável.
