# Validacao WEB — evidencias e piloto

Este relatorio registra evidencias observadas e o procedimento de piloto W16.
Estado e aceite permanecem no [roadmap](ROADMAP_WEB.md); tempos e tolerancias
sao definidos somente em [D5 do protocolo](experimento/PROTOCOLO_WEB.md#verificacao-temporal-aprovada-d5).
Nao constitui homologacao para coleta real ou equivalencia com PsychoPy.

## Ambiente observado em 2026-10-16

| Sistema/navegador | Modo observado | Evidencia | Pendencia de referencia |
|---|---|---|---|
| Linux Mint 22.2 / Chromium 156.0.8078.4 | Playwright 1.64.1, headless, teclado sintetico | Principal real de 60 s, 16 tentativas, gates e Escape aprovados; HTTPS/API/PostgreSQL e reenvio aprovados | Equipamento, monitor fisico 60 Hz, teclado, dez pilotos e medicoes |
| Linux Mint 22.2 / Firefox 157.0 | Playwright 1.64.1, headless, teclado sintetico | Mesmos cenarios e gates aprovados | Mesmas pendencias |
| Linux / Chrome e Edge distribuidos ao publico | Nao medido | Nenhuma homologacao inferida do Chromium embarcado | Versao estavel, equipamento e dez pilotos por ambiente |
| Windows / Chrome, Edge e Firefox | Nao medido | Nenhuma evidencia neste ambiente | Matriz de equipamentos e dez pilotos por ambiente |

Versoes observadas nas validacoes W11–W15; uma atualizacao requer nova
identificacao do ambiente. Viewports automatizados nao identificam monitor,
frequencia fisica, teclado, GPU ou atraso de apresentacao. Celular/macOS/Safari
permanecem fora do MVP experimental conforme D1; o painel profissional responsivo
nao amplia o suporte do motor experimental.

## Evidencias existentes

- W11: 42 testes do motor principal, incluindo limites de quadro, origem unica,
  janela exclusiva, pressao repetida/mantida e tarefas atrasadas. Registros
  observados nao sao corrigidos retrospectivamente para passar gates.
- W13: quatro ensaios `@timing` Chromium/Firefox aprovados em serie/3,5 minutos;
  26 casos gerais e oito HTTPS reais, incluindo conclusao de principal completo,
  falha antes/depois do commit, refresh, expiracao, descarte e logout.
- W15: 187 testes frontend, 40 casos gerais e seis HTTPS de consulta/exportacao
  por perfil; formulas compartilhadas com fixtures Python e ausencia de hits.
- Logs temporais brutos das execucoes antigas nao foram preservados. Os testes
  comprovam seus asserts, mas nao fornecem medias, desvios ou dez replicas por
  equipamento. Nao reconstruir esses numeros a partir de um resultado verde.

Comandos reproduziveis: `npm test`, `npm run test:browser` e
`npm run test:integration` em `web/`; requisitos do ultimo no
[README WEB](../web/README.md). Nao executar outra carga de testes/build durante
um ensaio temporal de referencia. Relogio controlado de testes da area
profissional nao e evidencia temporal do experimento.

## Procedimento de piloto de referencia

1. Usar somente participantes/codigos inequivocamente sinteticos, ambiente
   isolado e versao de aplicativo identificada por commit. Registrar SO,
   navegador/versao, monitor/modelo/resolucao/60 Hz e teclado/modelo/conexao,
   escala/zoom, GPU quando disponivel e condicoes de carga. Nao registrar
   nomes, cookies, convites, credenciais ou dados de pesquisa.
2. Em primeiro plano, sem carga artificial concorrente, executar dez sessoes
   completas independentes por combinacao navegador/SO/equipamento. Cada sessao
   exige convite proprio e pratica; nao retomar uma execucao interrompida.
3. Preservar em artefato local sintetico os instantes planejados e observados,
   periodo de quadro e eventos de teclado no relogio monotono. Calcular os
   desvios absolutos de cada transicao e duracao total, conforme D5. Conservar
   todas as dez tentativas de piloto, inclusive invalidas; nao escolher somente
   as que passaram. Sem artefato bruto nao conceder aceite da replica.
4. Separadamente exercitar tecla mantida/repeat, fronteiras da janela, perda de
   foco, aba oculta, Escape, recarga, fechamento e longa tarefa na thread.
   Confirmar descarte/novo convite e nenhuma avaliacao parcial. Carga artificial
   desses cenarios nao integra as dez replicas de referencia sem carga.
5. Registrar resultado individual, causa de invalidez e resumo de variabilidade
   por ambiente; conferir recebimento e metricas no servidor. Somente atribuir
   aceite ao ambiente cujos criterios aprovados foram demonstrados.
6. Se o estudo exigir equivalencia temporal com o legado, definir com o
   responsavel o protocolo comparativo e instrumentacao fisica de monitor e
   teclado. Nenhum timestamp JavaScript identifica sozinho o instante fisico.

Modelo de registro por replica (sem valores preenchidos artificialmente):

| Ambiente/commit | Replica 1–10 | Periodo de quadro | Maior desvio de transicao | Duracao principal | Artefato bruto | Resultado/causa |
|---|---|---|---|---|---|---|
| A preencher no equipamento de referencia | — | — | — | — | — | Nao executado |

## Limite atual

Faltam inventario do equipamento de referencia, execucao presencial das dez
replicas por ambiente e evidencias fisicas/comparativas quando exigidas pelo
estudo. O Codex pode preparar software e analisar artefatos sinteticos, mas nao
atestar monitor/teclado fisicos a partir de um navegador headless. W16 continua
pendente de aceite; essa pendencia localizada nao impede W17/W18.

A [documentacao primaria de temporizacao do jsPsych](https://www.jspsych.org/v8/overview/timing-accuracy/)
distingue limitacoes de apresentacao em navegador e alerta que resultados de
estudos anteriores podem nao se aplicar a versoes atuais. Ela nao concede
homologacao automatica a este motor ou ao equipamento do estudo.
