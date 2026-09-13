# Workflow de evolucao — referencia substituida

Este documento deixou de governar o planejamento em 2026-09-13. A unica fonte
canonica de etapas, pesos, dependencias, escopo, criterios de aceite, estado,
progresso, proxima etapa e decisoes externas pendentes e
[Projeto Stroop Test.md](Projeto%20Stroop%20Test.md).

O processo operacional esta em [WORKFLOW_CODEX_CLI.md](WORKFLOW_CODEX_CLI.md).
Nao gerar prompts externos por etapa. A distribuicao anterior de entregas e a
regra antiga de contratacao de VPS foram substituidas pela decisao registrada no
[historico de alteracoes](REGISTRO_DE_ALTERACOES.md). O conteudo anterior
permanece no historico Git; este arquivo foi preservado como redirecionamento.

A [baseline](BASELINE_ETAPA_1.md) preserva evidencias datadas. Contratos de
experimento e dados permanecem nos documentos tecnicos citados pelo backlog.

## Riscos tecnicos herdados da baseline

Estes riscos descrevem o contexto tecnico; nao constituem backlog independente.

- Dados locais potencialmente identificaveis exigem minimizacao, controle de
  acesso e proibicao de logs, fixtures e commits.
- O schema SQLite atual depende do importador para varios dominios e unicidades.
- Datas estao em texto e `source_file` nao possui hash de conteudo.
- O importador aceita `practice`, enquanto o CSV oficial atual contem `main`.
- A migracao deve provar paridade de metricas, contagens e rastreabilidade.
- Upload, API e autenticacao ampliam a superficie de ataque e exigem decisoes
  explicitas antes da implementacao.
- O dashboard pode exibir dados pessoais locais; exports e screenshots continuam
  sendo risco operacional.
