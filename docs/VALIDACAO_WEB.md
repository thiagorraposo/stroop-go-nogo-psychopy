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

### Inventario parcial do host atual — 2026-10-17

Leitura local de `/etc/os-release`, `xrandr`, `xinput`, `lsusb` e binarios
instalados identificou Linux Mint 22.2, 12 processadores logicos, cerca de
15 GiB de memoria, painel eDP em 1920x1080/60 Hz e Google Chrome 155.0.8059.84
e Firefox 158.0. O teclado visivel ao sistema e interno AT; nenhum teclado USB
com fio foi identificado. Microsoft Edge e Windows 11 nao estao disponiveis
neste host. Isso torna parcialmente disponivel um ambiente Linux da matriz,
mas nao executa nem aprova qualquer replica W16. Nenhuma sessao fisica foi
realizada; as versoes headless acima permanecem evidencias separadas.

### Captura local de tempos para coleta W16

O motor pode preservar quadros da contagem, transicoes planejadas/observadas e
eventos Space/Escape em execucoes completas ou interrompidas. A captura so e
ativada em build local configurada com `VITE_W16_TIMING_CAPTURE=synthetic-only`
e rota `/pratica?w16=1`; sem ambos o callback e a interface ficam desligados.
Use exclusivamente convite e execucao sinteticos, sem participante. O painel
mantem replicas apenas em memoria da aba e exporta sob acao explicita
`w16_timing_traces.json`; nao envia artefato ao servidor. O JSON inclui agente
de usuario, plataforma, viewport, tela, densidade de pixels e horario de
captura, alem das transicoes. Nao inclui convite, nome, iniciais ou identificador
de sessao. Mantenha os arquivos localmente e revise-os antes de compartilhar.
A captura facilita produzir evidencias brutas e preservar tentativas invalidas,
mas nao aprova replica nem substitui o procedimento fisico, a analise D5 ou os
seis ambientes/60 sessoes exigidos.

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

### Configuracao de referencia aprovada

Pacote aprovado explicitamente pelo responsavel na sessao em 2026-10-16
("eu aprovo este pacote"). Sao alvos de ensaio, nao equipamentos existentes
confirmados nem resultados medidos. Preserva D1/D5 e nao concede aceite W16.

| Item | Configuracao aprovada |
|---|---|
| Equipamento | Computador fisico desktop/notebook, CPU com pelo menos quatro processadores logicos, 8 GB de RAM; registrar modelo/CPU/GPU reais antes do ensaio. Esta configuracao de referencia nao constitui requisito minimo comprovado para participantes |
| Sistemas | Windows 11 e Linux Mint 22.2; equipamento por sistema identificado, preservando o mesmo monitor/teclado quando possivel |
| Navegadores | Chrome, Edge e Firefox estaveis instalados no inicio da campanha, com versoes exatas registradas; atualizar durante a campanha exige nova identificacao e repeticao do ambiente afetado |
| Monitor | Uma tela ativa, 1920x1080 a 60 Hz fixos, sem VRR; zoom do navegador 100%, escala do sistema 100%, notebook conectado a energia e economia de energia desativada |
| Teclado | Teclado fisico USB com fio, Espaco como resposta; registrar modelo e conexao |
| Replicas | Dez sessoes independentes por combinacao sistema/navegador: seis combinacoes, 60 sessoes; treino e bloco principal completos, somente dados sinteticos |
| Criterios | Aplicar D5 sem alterar tolerancias: ate um quadro medido por transicao e ate 100 ms de desvio do bloco de 60 s; preservar tambem replicas invalidas e investigar falhas antes de homologar a combinacao |
| Evidencias e alcance | Artefatos brutos planejados/observados e relatorio por replica, testes de interrupcao separados; homologacao de engenharia por software, sem alegar equivalencia temporal/psicometrica com PsychoPy |

A aprovacao autoriza preparar e executar o plano com recursos disponiveis; nao
substitui acesso ao Windows, monitor/teclado fisicos ou realizacao dos pilotos.
O Codex prepara instrumentacao, automacao e analise; o responsavel disponibiliza
os equipamentos e executa os passos presenciais que nao puderem ser automatizados.
Equipamento indisponivel continua pendente, sem substituicao silenciosa por VM,
emulacao ou navegador headless. Equivalencia fisica, se exigida pelo estudo,
requer protocolo comparativo e instrumentacao separados conforme D5.

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

Faltam teclado USB com fio para o host Linux, Edge, ambiente Windows 11,
execucao presencial das dez replicas por combinacao e evidencias fisicas/
comparativas quando exigidas pelo estudo. O inventario parcial acima nao e
resultado de piloto. O Codex pode preparar software e analisar artefatos
sinteticos, mas nao atestar ensaios fisicos sem os equipamentos. W16 continua
pendente de aceite. A configuracao do pacote esta decidida; a pendencia e a
disponibilidade/verificacao dos equipamentos e a execucao dos ensaios, sem nova
aprovacao tecnica rotineira. W17–W20 ja foram executadas independentemente.

A [documentacao primaria de temporizacao do jsPsych](https://www.jspsych.org/v8/overview/timing-accuracy/)
distingue limitacoes de apresentacao em navegador e alerta que resultados de
estudos anteriores podem nao se aplicar a versoes atuais. Ela nao concede
homologacao automatica a este motor ou ao equipamento do estudo.
