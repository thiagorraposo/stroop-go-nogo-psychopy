# Protocolo experimental WEB

Referencia factual conferida e decisoes D1–D6 aprovadas explicitamente pelo
usuario em 2026-10-16, ao aprovar os itens 1–19 apresentados na sessao. Este
documento distingue o experimento local existente do protocolo aprovado para
sua variante web. A aprovacao define requisitos; nao comprova implementacao,
medicao temporal ou homologacao. Escopo, dependencias e estado de W01
permanecem exclusivamente no [roadmap WEB](../ROADMAP_WEB.md).

## Fontes e limites

- [Decisoes do experimento](DECISOES_DO_EXPERIMENTO.md): paradigma e regras
  metodologicas canonicas, incluindo as decisoes aprovadas para a variante web.
- [Validacao de condicoes e tempos](VALIDACAO_CONDICOES.md): balanceamento,
  paleta, duracoes e HUD da versao local `0.2.2`.
- [Fonte Builder](../../stroop_go_nogo_ptbr.psyexp) e CSVs de
  [pratica](../../condicoes/pratica_stroop_go_nogo_ptbr.csv),
  [principal](../../condicoes/bloco_principal_stroop_go_nogo_ptbr.csv) e
  [contagem](../../condicoes/contagem_regressiva.csv): comportamento configurado
  efetivamente, conferido por leitura do XML e das condicoes versionadas.
- [CSV unificado](CSV_UNIFICADO.md) e [modelo de dados](../dados/MODELO_DE_DADOS.md):
  contratos de exportacao e formulas; exemplos antigos sao discutidos abaixo.
- [ADR-001](../arquitetura/ADR-001-evolucao-web.md): limites de medicao no
  navegador e arquitetura; paridade funcional nao comprova equivalencia de RT.
- [Especificacao visual e fluxo](../legado/ESPECIFICACAO_VISUAL_E_FLUXO.md): proposta
  historica de 2026-07-06, sem precedencia sobre a fonte atual.

A finalidade WEB aprovada e a coleta de dados pelo grupo de pesquisa do qual
o usuario faz parte. O publico sao participantes da pesquisa, podendo ser
qualquer pessoa, sem introduzir filtro demografico no produto. O usuario e o
responsavel pelo protocolo, elegibilidade, informacao/consentimento aplicaveis,
validacao e operacao antes do uso real. Publico amplo nao dispensa as regras
especificas de cada pesquisa. Idade e sexo nao serao coletados pela versao WEB.

A tarefa permanece original e de pesquisa exploratoria, com resultados somente
descritivos, sem diagnostico, norma, percentil clinico ou equivalencia
psicometrica. As validacoes deste documento usam somente fontes versionadas;
nao incluem coletas locais, Pilot grafico ou medicao fisica de latencia.

## Comportamento local observado

### Fluxo e navegacao

| Trecho do Flow atual | Acao ou duracao | Efeito experimental |
|---|---|---|
| `formulario_sessao` | Formulario visual local; avanco apos validacao | Define metadados; nao gera tentativa |
| `boas_vindas` -> `tutorial_regra` -> `pratica_inicio` | Clique no botao, Espaco ou Enter | Navegacao; cliques e teclas destas telas nao sao respostas experimentais |
| `regra_rapida` | Automatico, 1,5 s | Lembrete antes da pratica |
| `contagem_pratica_loop` / `contagem` | Prepare-se, 3, 2, 1, Comecar; 0,55 s cada | Contagem de 2,75 s; nenhuma resposta experimental |
| `pratica_loop` | Uma passagem aleatoria pelas 4 condicoes; `trial_pratica` seguido de `feedback_pratica` | 2 Go e 2 No-Go; feedback de 0,5 s apos cada tentativa |
| `resumo_pratica` | Espaco | Avanca ao principal; nao existe opcao atual de repetir a pratica |
| `contagem_principal_loop` / `contagem` | Mesmas 5 telas e duracoes | Prepara principal; cronometro principal ainda nao iniciou |
| `principal_loop` | Uma passagem aleatoria pelas 16 condicoes | 8 Go e 8 No-Go, sem feedback por tentativa; aproximadamente 60 s |
| `resultados` | Clique em Finalizar, Espaco ou Enter | Resumo em memoria; ao sair, grava CSV oficial uma vez |

Os dois loops experimentais usam `random`, `nReps=1`, sem semente fixa na
fonte. A ordem apresentada determina o `trial_number` sequencial exportado;
o numero da linha original da condicao nao e a ordem sorteada. Todas as dez
cores oficiais aparecem no principal, sem garantir igual frequencia em apenas
16 tentativas. A rotina `fim` existe no XML, mas **nao esta no Flow atual**.

O formulario local exige `project`, `participant_id`, `participant_name`,
`visit` e `evaluator`; `initials` e opcional. Na WEB, o usuario aprovou receber
somente codigo pseudonimizado, projeto, visita e identificacao tecnica do
avaliador, sem nome, iniciais, CPF, contato, idade ou sexo. A correspondencia
entre codigo e pessoa fica fora do sistema. O CSV WEB preservara os 21 campos,
com `participant_name=NAO_COLETADO` e `initials` vazio. W02/W03 detalham os
contratos e os controles de dados, sem modificar a coleta local existente.

### Tempos, resposta e HUD

| Segmento relativo ao inicio da tentativa | Pratica | Principal |
|---|---|---|
| Fixacao | 0 a 0,300 s | 0 a 0,300 s |
| Estimulo / resposta | 0,300 a 2,300 s; duracao 2,000 s | 0,300 a 2,800 s; duracao 2,500 s |
| Intervalo sem estimulo | 2,300 a 2,800 s; duracao 0,500 s | 2,800 a 3,750 s; duracao 0,950 s |
| Feedback posterior | 0,500 s, fora dos 2,800 s da tentativa | Ausente |

No Builder, `stopType=duration (s)`: o `stopVal` de 2,0/2,5 representa
**duracao**, nao instante final absoluto. Os componentes de resposta comecam
aos 300 ms, aceitam somente Espaco, registram a primeira tecla pressionada,
descartam eventos anteriores e usam sincronizacao de tela. `forceEndRoutine`
e falso: responder nao abrevia estimulo nem tentativa. Os limites reais de
apresentacao sao sujeitos a quadros do ambiente local; nao foi provada aqui
precisao fisica de fronteira em milissegundos.

O tema atual e escuro, com cartao claro para o estimulo. O HUD usa precisao
acumulada e barra textual de dez posicoes, inicialmente `Precisao: —`; pratica
e principal possuem contadores independentes. A atualizacao ocorre ao terminar
a tentativa, nao imediatamente apos pressionar a tecla. A pratica exibe um
lembrete da regra e `Tempo: --:--`. O principal mostra estimulo, precisao,
cronometro e progresso, com fixacao/intervalo nos respectivos segmentos e sem
texto instrucional ou navegacional durante as tentativas.

O cronometro inicia no comeco da primeira tentativa principal, incluindo sua
fixacao; segue continuamente pelos intervalos, e nao inicia no tutorial ou
pratica. `format_main_time()` mostra minutos/segundos inteiros e limita o valor
a 60 s. As 16 tentativas de 3,75 s somam 60 s nominais; o fluxo completo inclui
tempos de navegacao variaveis, contagens, pratica e feedbacks. Preservar o HUD
inclui preservar a precisao ao vivo, que pode influenciar o comportamento.

### Matriz de respostas e resultados

As quatro classificacoes seguem as fontes canonicas; aplicam-se a pratica e
principal. RT e o intervalo desde o inicio do estimulo/resposta, em segundos
no CSV, e nao desde a fixacao nem desde uma requisicao de rede.

| Condicao | Espaco na janela | Classificacao | `correct` | RT |
|---|---|---|---|---|
| `congruent` / Go | Sim | `hit` | 1 | Positivo |
| `congruent` / Go | Nao | `omission` | 0 | Vazio |
| `incongruent` / No-Go | Nao | `correct_rejection` | 1 | Vazio |
| `incongruent` / No-Go | Sim | `commission` | 0 | Positivo |

A pratica fornece feedback para os quatro casos e nao entra no CSV oficial.
O resumo final usa somente registros `main` em memoria, com precisao e mediana
dos hits conforme [decisoes](DECISOES_DO_EXPERIMENTO.md). Sem hits, mostra `—`
como RT; nao inventa um RT de zero. Por exemplo, oito omissoes e oito rejeicoes
corretas produzem 50% de precisao e RT ausente. O transporte e a persistencia
web deverao distinguir ausencia de medida de zero sem alterar formulas do legado.

O experimento habilita Escape. O contrato local proibe CSV oficial parcial
antes do encerramento normal. Na fonte, a escrita ocorre ao sair de
`resultados`; atingir a ultima tentativa sozinho nao comprova que o arquivo
foi gravado. Este documento nao valida detalhes do encerramento do processo
PsychoPy nem autoriza recuperar execucoes incompletas.

## Casos de fronteira para a variante web

A configuracao local comprova janela, primeira resposta e descarte do buffer;
ela nao resolve, por si, repeticao automatica do teclado, foco de navegador
ou instantes fisicos de fronteira. A coluna web abaixo registra regras
aprovadas em D2/D6, cuja implementacao e validacao continuam necessarias;
nao comprova equivalencia com o PsychoPy.

| Caso | Evidencia / limite atual | Regra web aprovada |
|---|---|---|
| Espaco durante fixacao, intervalo, feedback ou contagem | Teclado experimental inativo; eventos anteriores descartados | Ignorar como resposta; nao transportar evento para outra tentativa |
| Primeiro Espaco apos inicio e antes do fim da janela | Primeira tecla; RT positivo no exportador | Aceitar se `0 < RT < duracao_da_janela`; ancorar RT ao inicio registrado do estimulo |
| Espaco exatamente no inicio com RT=0 | Exportador rejeita RT nao positivo | Rejeitar o registro como inconsistente; nao arredondar RT positivo para zero |
| Espaco exatamente no fim ou depois | Componente deixa de aceitar respostas no fim | Usar fim exclusivo; resolver por timestamp monotono, nao pela ordem de callbacks |
| Duas ou mais pressoes validas | `store=first key` | Guardar somente a primeira; manter duracao integral |
| Outra tecla, Enter, clique ou toque durante estimulo | Somente Espaco permitido; Escape tem funcao de encerramento | Nao classificar como resposta; preservar Escape como interrupcao |
| Espaco mantido antes do estimulo ou atravessando tentativas | `registerOn=press` e descarte de buffer; sem evidencia suficiente sobre todos os backends/teclados | Exigir soltar e pressionar novamente; ignorar `repeat` e pressionamentos sem nova transicao solta->pressionada |
| Perda de foco, troca de aba, fechamento, recarga ou Escape | Sem politica web na fonte local | Interromper conforme D2; nao concluir/exportar resultado parcial |
| Nenhum hit no principal | Resumo mostra `—` | Preservar ausencia de RT; validar contagens e precisao separadamente |
| Resposta recebida durante atraso da thread principal | Fonte nao especifica fila de eventos web | Conferir timestamp e janela; impedir aceitar evento tardio como se estivesse dentro dela |

## Decisoes aprovadas para o MVP

As decisões originais D1–D6 foram **aprovadas explicitamente pelo usuario em
2026-10-16**, em resposta a proposta de decisoes da sessao. O usuario tambem
confirmou ser o responsavel pela pesquisa, validacao e operacao. A aprovacao
remove a pendencia metodologica; a implementacao e as evidencias dos gates
continuam sob as respectivas etapas do roadmap, que concentra o aceite formal.
D3 visual e identificação complementar D4 foram revisadas pelo proprietário em
2026-11-05, conforme tabela vigente e registro detalhado abaixo.

| ID | Decisao aprovada | Motivo e limite |
|---|---|---|
| D1 — Dispositivos e navegadores | MVP em computador desktop/notebook com teclado fisico, Windows ou Linux, usando Chrome/Edge Chromium ou Firefox estaveis na data da validacao. Verificar ambiente antes de iniciar, sem exigir tela cheia. Celular, tablet, toque, Safari e macOS ficam fora do MVP ate validacao propria | Preserva Espaco como resposta e limita combinacoes de ambiente; versoes e combinacoes efetivamente homologadas devem ser enumeradas a partir dos testes, sem declarar suporte universal |
| D2 — Foco e interrupcao | Antes da pratica, aguardar foco/aba visivel. Durante o principal, perda de foco (`blur`), troca de aba/aba oculta, fechamento, recarga ou Escape invalida a execucao; nao pausar/retomar a mesma serie nem gerar resultado parcial. Novo inicio exige nova sessao e pratica. Durante a pratica, descartar a rodada interrompida e exigir nova rodada completa antes do principal | Evita continuidade silenciosa com exposicao/intervalos alterados; o backend devera representar interrupcao sem metricas finais ou exportacao oficial parcial. Fechamento/recarga nao garantem entrega de aviso ao servidor; W02 devera prever expiracao |
| D3 — Prática e apresentação visual (revisada em 2026-11-05 pelo proprietário) | Manter rodadas de 4 tentativas, sem limiar de desempenho; permitir repetir opcionalmente antes do principal, com nova ordem aleatoria e descarte das tentativas de treino para o resultado oficial. Manter 16 tentativas principais, tempos, contagens e cores. Adotar stroop-web-outline/1.0.0: palavras com contorno branco fino sem retângulo, progresso periférico e cronômetro principal; sem precisão agregada na prática/principal, feedback individual só na prática. Política de visibilidade na revisão visual abaixo | A repeticao opcional altera a dose de treino e foi aprovada metodologicamente para a WEB; sua implementacao nao altera o Builder local |
| D4 — Identificacao | Preservar `test_version=0.2.2-web.1` e identificar também a variante visual/versão via snapshot e app_version conforme revisão D3; manter `test_code=stroop_go_nogo_ptbr`; versao do aplicativo e plataforma `web` ficam em metadados separados a especificar em W02 | Identifica a variante de coleta sem prometer equivalencia. Nao adicionar colunas ao CSV oficial de 21 campos nem reutilizar silenciosamente `0.2.2` para tecnologia de medicao diferente |
| D5 — Criterio temporal | Adotar os ensaios instrumentados e limites abaixo como gate de engenharia: 10 execucoes sinteticas por ambiente de referencia, ate um quadro por transicao e ate 100 ms de desvio no bloco principal de 60 s | RT do navegador nao mede latencia fisica completa; aprovacao do criterio nao comprova seu atendimento nem equivalencia psicometrica |
| D6 — Fronteiras do teclado | Aplicar as regras web da matriz: somente a primeira nova pressao de Espaco, RT estritamente positivo e fim exclusivo; tecla mantida/repeticao automatica nao responde e a resposta nao abrevia estimulo ou tentativa | Torna os casos limite verificaveis e evita transportar respostas de navegacao para estimulos. O XML local sozinho nao comprova paridade de tecla mantida |

### Verificacao temporal aprovada (D5)

Excecao de aceite W16 em 2026-10-20: por decisao explicita do responsavel,
a etapa pode ser encerrada com evidencia local parcial e ressalvas. O alcance
esta registrado no [historico de decisoes](DECISOES_DO_EXPERIMENTO.md#historico-de-decisoes).
Essa excecao modifica o aceite da etapa, sem alterar os limites de validade
abaixo nem transformar medicoes de software em latencia fisica comprovada.

1. Preservar duracoes nominais, contagens e sequencia; HUD segue D3 revisada. Registrar
   instantes planejados e observados de apresentacao/retirada do estimulo com
   relogio monotono no navegador; registrar eventos do teclado no mesmo dominio
   temporal. Data/hora civil identifica a sessao, sem calcular RT.
2. No equipamento de referencia de cada navegador/sistema aprovado, medir o
   periodo de quadro e executar 10 sessoes sinteticas completas em primeiro
   plano. Ambiente de referencia inicial: monitor de 60 Hz, sem carga artificial
   concorrente; registrar navegador/versao, sistema e periodo medido no relatorio.
3. Tolerancia de engenharia aprovada: desvio absoluto de cada transicao
   observado por software de ate um periodo de quadro medido; erro acumulado
   da duracao principal de ate 100 ms em torno dos 60 s nominais. Sessoes fora
   desses limites devem ser sinalizadas como temporalmente invalidas e nao
   publicadas como resultado valido; nao ajustar RT retrospectivamente para
   ocultar desvio. O criterio foi aprovado; seu atendimento ainda depende das
   medicoes e evidencias de W16, sem aceite temporal fisico presumido.
4. Exercitar eventos sinteticos antes, dentro e depois da janela, incluindo
   RT=0, fim exato, pressao repetida, tecla mantida e longas tarefas da thread
   principal. A classificacao deve ser deterministica e o RT deve manter
   precisao suficiente antes de sua conversao de unidade no contrato W02.
5. Testes automatizados verificam logica, fila, tolerancia e registros; execucao
   instrumentada em navegador real verifica apresentacao observavel por software.
   Nenhuma dessas evidencias mede o instante fisico no monitor/teclado. Se for
   exigida equivalencia temporal com PsychoPy, definir e executar outro protocolo
   com instrumentacao fisica antes de afirmar essa equivalencia.

## Divergencias historicas e exemplos CSV

A especificacao visual historica propoe tema claro, fluxo com telas adicionais,
repeticao de pratica e HUD sem feedback de desempenho. A fonte atual usa tema
escuro, precisao ao vivo e Flow descrito acima; dez cores, resultados e CSV
unificado ja existem. Nao executar de novo suas antigas fases nem remover o
HUD por tratar uma proposta de 2026-07-06 como requisito atual.

O bloco **Colunas oficiais** de [CSV unificado](CSV_UNIFICADO.md) tem 21 campos,
coerentes com `OFFICIAL_CSV_COLUMNS` no `.psyexp`. A auditoria inicial encontrou
exemplos antigos com 20 campos: cabecalho sem `participant_name`, versao
`0.2.1` e comando com nome-base de participante. Os exemplos na fonte canonica
foram corrigidos nesta etapa para 21 campos e versao **local** `0.2.2`, usando
somente dados inequivocamente sinteticos. Os quatro exemplos foram reunidos
em CSV temporario e validados com o analisador e o nucleo atuais.

Os exemplos ilustram as quatro classificacoes locais; nao representam uma sessao
completa de 16 tentativas nem evidenciam implementacao de D4 ou coleta WEB.
O nome de arquivo segue codigo do teste e timestamp, sem identificadores
pessoais. Exportacao web, acesso e minimizacao seguem as decisoes aprovadas e
dependem dos contratos e controles de W02/W03; a correcao documental nao altera
o CSV oficial nem autoriza nova coleta real.


## Esclarecimento D2 e critérios para persistência incremental — 2026-11-05

O responsável reafirmou: interrupção que comprometa o protocolo invalida a
execução para resultado final e exige nova sessão com prática aprovada; é
proibida retomada do bloco interrompido. Dados já recebidos devem ser preservados
como incompletos/ inválidos. “Sem resultado parcial” em D2 significa sem métricas
ou exportação **oficiais**, e não descarte obrigatório de observações técnicas.
A aprovação histórica D2 permanece; envio final-only não é mais política aceita.

Matriz validada explicitamente pelo responsável em 2026-11-05, na resposta
“valido” à proposta apresentada em `270377b`, antes da implementação de DEC-02:

| Evento | Validade e ação |
|---|---|
| Blur, aba oculta/trocada, Escape, recarga ou fechamento durante principal | Invalidar sessão; conservar prefixo recebido; não retomar; novo convite/sessão e prática |
| Transição ou duração fora dos gates D5; relógio/ordem incompatível | Invalidar execução, preservar observações seguras e motivo; não corrigir timestamps; nova sessão com prática |
| Interrupção durante prática | Descartar rodada para desempenho e repetir rodada completa conforme D2/D3; não iniciar principal sem prática completa. Recarregar não autoriza reaproveitar treino sem comprovação |
| Rede/ACK indisponível, sem falha D2/D5 | Somente transporte pendente; não pausar/alongar principal. Após término íntegro pode reenviar os mesmos dados dentro do prazo; não executar tentativas novamente na sessão |
| Prazo ou revogação antes da conclusão válida | Sessão sem resultado final, dados recebidos preservados; expiração não prova causa metodológica específica; novo convite/sessão com prática |
| Sessão abandonada sem aviso | Incompleta por ausência de conclusão; motivo desconhecido. Mesmo 16 observações não bastam para declarar sucesso |
| Violação anterior ao fim conhecida após recibo | Preservar dados/recibo histórico e registrar invalidação auditável, excluindo resultado dos conjuntos válidos; não transformar corrida de rede em validade |

Checkpoint não altera duração, estímulos, HUD, prática, métricas ou CSV.
[ADR-005](../arquitetura/ADR-005-persistencia-incremental.md) define a estratégia
validada e seus limites. A validação documental dessa matriz e da estratégia
não comprova ensaios de timing com transporte nem prontidão para coleta real.

## CHG-003 — proposta inicial (histórico anterior à aprovação visual)

Solicitação de 2026-11-05: palavras sem retângulo branco e com contorno branco,
HUD discreto de progresso/tempo e retirada completa de precisão agregada durante
prática/principal, mantendo feedback individual da prática e cálculos oficiais.
Direção detalhada em [UX_DECISIONS](UX_DECISIONS.md); execução e aprovação no
[backlog único](../Projeto%20Stroop%20Test.md).

Registro histórico, superado pela aprovação visual abaixo.

**Divergência explícita à época:** D3 aprovado exige HUD atual com precisão ao vivo.
A solicitação autoriza direção UX, mas não alteração silenciosa de D3. Antes do
runtime, o responsável metodológico deve aprovar a apresentação revisada,
visibilidade de progresso/cronômetro, escopo do feedback e identificação/versionamento
da variante frente a D4, sem misturar evidências anteriores e posteriores.
Até isso ocorrer, os contratos e o código anteriores continuam vigentes.
DEC-04 segue pendente para matriz/equipamento/campanha; não é aprovada por CHG-003.

Tempos, condições, dez cores, resposta, métricas/CSV e D1/D2/D5/D6 permanecem.
A campanha WEB-011 deve usar o layout final aprovado e transporte incremental
ativo (DEC-02/ADR-005), com falhas/retries e limites D5 intactos; medição apenas
na apresentação antiga não comprova esta alteração. WEB-034 avalia percepção,
saliência, atenção e protocolo visual, sem presumir equivalência com PsychoPy.

## Revisão visual D3 — aprovação explícita do proprietário, 2026-11-05

O proprietário aprovou expressamente nesta missão a substituição da apresentação
incompatível anterior: remover retângulo branco, contorno branco fino nas letras
com as dez tintas preservadas, progresso minimalista/periférico e cronômetro
estável, sem precisão acumulada na prática/principal. Feedback individual da
prática, repetição opcional sem limiar e todo o protocolo cognitivo permanecem.
Essa aprovação é atribuída **ao proprietário**, que já se declarou responsável
pela pesquisa, validação e operação em 2026-10-16. Não há requisito documentado
de anuência adicional de um responsável distinto para esse gate; não se atribui
aprovação a terceiro. DEC-04 continua pendente para campanha/suporte; DEC-03/05
continuam independentes, sem autorização de coleta real ou deploy.

### Identificação e comparabilidade da apresentação

- Identificador estável da variante visual: **`stroop-web-outline`**.
- Versão do protocolo visual: **`1.0.0`**; fonte executável:
  `condicoes/web_protocol.json`, seção `visual` (`id`, `version`).
- Identificação cognitiva D4 preservada: `test_code=stroop_go_nogo_ptbr`,
  `test_version=0.2.2-web.1`, `protocol_id=stroop_go_nogo_ptbr/0.2.2-web.1`.
  D4 passa a exigir também identificação visual: não reutilizar isoladamente
  esses campos para inferir a apresentação usada.
- Aplicativo com esta apresentação: `app_version=web-<versão do pacote>+visual.1.0.0`.
  A versão visual fica assim nos metadados já fixados em start/complete/recibo e
  detalhe/exportação técnica, sem coluna nova no CSV de 21 campos ou schema novo.
  Snapshot/SHA complementam a proveniência. Não mudar resultados anteriores.
- Anterior: apresentação com retângulo claro e precisão ao vivo, sem versão visual
  explícita, presente até `3d9d515`. Não atribuir retroativamente `1.0.0` a dados
  antigos. Dados só com test_version ou CSV sem app_version não distinguem os dois
  visuais: exigir proveniência técnica externa; não combinar silenciosamente.
- Incrementar versão visual quando mudar apresentação relevante; nova aprovação
  se afetar percepção/atenção. Testes anteriores continuam históricos, sem provar
  a nova apresentação. Não há comparabilidade/equivalência psicométrica ou
  temporal demonstrada pela revisão documental.

### Política do HUD e apresentação aprovada

| Estado | Estímulo / HUD |
|---|---|
| Prática: fixação, estímulo e intervalo | Progresso discreto de tentativas concluídas/total; sem precisão agregada ou cronômetro novo de prática |
| Prática: lembrete, contagem e feedback individual | HUD oculto; feedback de cada tentativa preservado, sem avaliação agregada |
| Principal: fixação, estímulo e intervalo | Progresso e cronômetro decorrido MM:SS visíveis e periféricos, sem precisão ou feedback individual |
| Principal: contagem | HUD oculto e relógio do principal ainda não iniciado |
| Fim/interrupção | Motor limpa HUD/listeners; fluxo posterior mantém regras de recibo/D2 e protocolo de resultados já existente |

Durante estímulos: palavras sobre o fundo experimental atual, sem caixa; contorno
branco fino/uniforme por token, tinta/fonte/peso/escala/centro preservados. Progresso
real de concluídas, sem valores fixos ou animação. Cronômetro tem números tabulares,
largura estável e usa origem monotônica existente; não mede RT nem usa timer React.
Nenhuma accuracy acumulada, taxa de erros, ranking, tooltip ou conteúdo equivalente
no DOM/árvore acessível. Não altera cálculos, persistência, métricas administrativas
ou exportações. A espessura será conferida nas dez cores em Chromium/Firefox,
sem tratamento por cor ou inferência de equivalência a partir de screenshots.

D1/D2/D5/D6, ordem, Go/No-Go, janelas, durações, condições, feedback individual e
repetição da prática preservados. Campanha WEB-011 deve avaliar esta variante com
transporte incremental ativo e limites D5 inalterados; WEB-034 mantém revisão
metodológica final. Aprovação visual libera implementação autorizada de
WEB-042/043, não os gates de campanha, suporte ou encerramento de M3.


### D3/D4 anteriores — transcrição histórica preservada

| ID | Decisão anterior | Motivo e limite histórico |
|---|---|---|
| D3 — Repeticao da pratica | Manter rodadas de 4 tentativas, sem limiar de desempenho; permitir repetir opcionalmente antes do principal, com nova ordem aleatoria e descarte das tentativas de treino para o resultado oficial. Manter 16 tentativas principais, tempos, contagens, cores e HUD atuais, incluindo precisao ao vivo e cronometro; principal sem feedback por tentativa | A repeticao opcional altera a dose de treino e foi aprovada metodologicamente para a WEB; sua implementacao nao altera o Builder local |
| D4 — Identificacao | Usar `test_version=0.2.2-web.1`, mantendo `test_code=stroop_go_nogo_ptbr`; versao do aplicativo e plataforma `web` ficam em metadados separados a especificar em W02 | Identifica a variante de coleta sem prometer equivalencia. Nao adicionar colunas ao CSV oficial de 21 campos nem reutilizar silenciosamente `0.2.2` para tecnologia de medicao diferente |


### Alcance DEC-04 local — 2026-11-05

A aprovação posterior da campanha local de engenharia pelo proprietário consta
em [DECISOES_DO_EXPERIMENTO](DECISOES_DO_EXPERIMENTO.md#dec-04--alcance-local-de-engenharia-aprovado-em-2026-11-05).
Preserva integralmente D1/D2/D5/D6, sem transportar a exceção histórica W16 para
M3. Matriz, recursos, evidências e limites ficam somente no backlog; aprovação
do alcance não concede aceite dos resultados nem validação física/metodológica.
