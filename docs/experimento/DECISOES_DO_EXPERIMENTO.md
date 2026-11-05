# Decisoes do experimento

Revisão documental em 2026-11-04: regras científicas preservadas. A direção de
produto/infraestrutura está em [ARQUITETURA_WEB](../ARQUITETURA_WEB.md) e
[ADR-004](../arquitetura/ADR-004-replanejamento-plataforma.md), sem decidir
validade científica. Estado e validação atuais somente no [backlog](../Projeto%20Stroop%20Test.md).
A aprovação histórica D1–D6 permanece; não é evidência de equivalência ou coleta real.

## Decisoes estabelecidas

- O paradigma e Stroop Go/No-Go.
- A resposta esperada e pressionar `Espaco` apenas quando palavra e cor coincidirem.
- Tentativas incongruentes devem ser inibidas, sem resposta.
- A pratica e separada do bloco principal.
- As cores previstas para o experimento sao verde, amarelo, rosa, preto, vermelho, laranja, marrom, roxo, azul e cinza.
- A lista oficial de palavras e `VERDE`, `AMARELO`, `ROSA`, `PRETO`, `VERMELHO`, `LARANJA`, `MARROM`, `ROXO`, `AZUL` e `CINZA`.
- O bloco principal deve permanecer sem feedback por tentativa.
- No Builder local, a pratica tem uma unica rodada. A variante WEB aprovada
  permite repetir rodadas completas antes do principal conforme o protocolo abaixo.
- A versao `0.2.2` usa protocolo curto com 4 tentativas de pratica e 16 tentativas principais.
- A pratica tem 2 tentativas Go/congruentes e 2 tentativas No-Go/incongruentes.
- O bloco principal tem 8 tentativas Go/congruentes e 8 tentativas No-Go/incongruentes.
- Cada tentativa de pratica dura 2,8 segundos: 300 ms de fixacao, 2000 ms de estimulo/resposta e 500 ms de intervalo vazio.
- A pratica mantem feedback automatico de 500 ms apos cada tentativa.
- Cada tentativa principal dura 3,75 segundos: 300 ms de fixacao, 2500 ms de estimulo/resposta e 950 ms de intervalo vazio.
- O bloco principal dura aproximadamente 60 segundos; o fluxo completo e maior por incluir formulario, instrucoes, contagens, pratica e feedbacks.
- A versao `0.2.2` usa HUD discreto de precisao acumulada durante pratica e bloco principal.
- O cronometro visual inicia apenas no comeco da primeira tentativa principal e segue continuamente ate o fim do intervalo da ultima tentativa principal.
- A precisao ao vivo pode influenciar o comportamento do participante e e uma decisao de UX, nao uma configuracao metodologicamente neutra.
- O bloco principal deve exibir apenas estimulo central, cronometro, precisao e progresso durante as tentativas, sem texto instrucional ou navegacional.
- A interface usa tema escuro original com cartao claro para contraste dos estimulos.
- A primeira fase visual pre-pratica usa o fluxo `boas_vindas` -> `tutorial_regra` -> `pratica_inicio` -> `regra_rapida` antes da contagem da pratica.
- As telas de navegacao pre-pratica aceitam clique, `Espaco` e `Enter`; cliques nao contam como respostas experimentais.
- Resultados exibidos ao participante devem ser apenas descritivos.
- Idade e sexo nao devem ser usados para pontuacao, classificacao ou comparacao normativa.
- Decisão histórica de 2026-07-06: SQLite como armazenamento inicial local; preservado no legado, superado como alvo operacional pelo ADR-004.
- Decisão histórica de 2026-07-06: dashboard local Streamlit; preservado na transição, substituído como interface final por React conforme ADR-004.
- `participant_id` sera o identificador principal da pessoa.
- `initials` serao opcionais e tratadas como dado potencialmente identificavel.
- `assessment_date` sera gerada automaticamente pelo sistema.
- Campos obrigatorios de sessao: `project`, `participant_id`, `visit` e `evaluator`.
- O experimento usa formulario local de sessao antes da primeira tela.
- `participant_id` e o identificador canonico da pessoa no CSV.
- Nomes de arquivo de dados nao devem usar `participant_id`, `participant_name`, iniciais, visita ou avaliador.
- O CSV oficial deve seguir `stroop_go_nogo_ptbr_YYYY-MM-DD_HHhMMmSSs_trials.csv`, permitindo descoberta por `data/*_trials.csv`; metadados pessoais ficam somente no conteudo local.
- `test_version` local e `0.2.2`; a variante WEB aprovada usa `0.2.2-web.1`.
- Cada execucao concluida normalmente deve gerar um unico CSV oficial contendo apenas tentativas do bloco principal.
- A pratica continua sendo usada para feedback e HUD, mas nao e exportada no CSV oficial.
- O CSV oficial usa `block` com valor canonico `main` nas execucoes atuais; `practice` permanece aceito apenas para compatibilidade historica de validacao.
- O CSV oficial usa `condition` com valores canonicos `congruent` e `incongruent`, mesmo que os CSVs de condicoes usem nomes em portugues.
- O CSV oficial usa `error_type` com valores canonicos `hit`, `omission`, `correct_rejection` e `commission`.
- Dados estruturalmente incoerentes devem bloquear a exportacao oficial em vez de gerar CSV ambiguo.
- Execucao abortada antes do encerramento normal nao gera CSV oficial parcial nesta fase.
- Dados clinicos, normativos e diagnosticos permanecem proibidos.
- `response_time` sera definido como mediana dos tempos de reacao dos hits validos.
- A tela final `resultados` deve calcular metricas apenas a partir do registro canonico em memoria das tentativas `main`, sem ler CSV e sem adicionar linhas ao CSV.
- A precisao total exibida em `resultados` e `(hits + correct_rejections) / total_main_trials * 100`, arredondada para percentual inteiro.
- O tempo de reacao exibido em `resultados` e a mediana dos `reaction_time` dos hits do bloco principal, com 3 casas decimais e sufixo `s`; quando nao houver hits, exibe `—`.
- O projeto nao faz alegacoes clinicas, normativas, diagnosticas ou de equivalencia psicometrica.
- Dados locais de execucao e coleta ficam em `data/` e nao devem ser versionados.
- A pasta `condicoes/` e mantida como pasta existente de CSVs de condicoes, equivalente funcional ao nome `conditions/` solicitado para estrutura.

## Regras de classificacao de resposta

- Congruente + Espaco = `hit`.
- Congruente sem resposta = `omission`.
- Incongruente sem resposta = `correct_rejection`.
- Incongruente + Espaco = `commission`.

## Variante WEB aprovada em 2026-10-16

O usuario aprovou explicitamente os itens 1–19 apresentados na sessao, incluindo
as decisoes D1–D6 detalhadas no [protocolo WEB](PROTOCOLO_WEB.md). A finalidade e
coleta de dados pelo grupo de pesquisa ao qual pertence; o publico sao os
participantes da pesquisa, podendo ser qualquer pessoa. O usuario assumiu a
responsabilidade pelo protocolo, elegibilidade, informacao/consentimento
aplicaveis, validacao e operacao antes de uso real. Nao criar filtros demograficos
nem coletar idade ou sexo na WEB. Permanecem o carater exploratorio e os
resultados descritivos, sem alegacoes clinicas ou de equivalencia psicometrica.

- **D1:** MVP em desktop/notebook com teclado fisico, Windows/Linux e
  Chrome/Edge Chromium ou Firefox; celulares, tablets, toque, Safari e macOS
  ficam fora do MVP. Homologacao deve enumerar as combinacoes e versoes medidas.
- **D2:** perda de foco, troca de aba, recarga, fechamento ou Escape durante o
  principal invalida a execucao, sem resultado oficial parcial; recomeco exige
  nova sessao e pratica. Na pratica, descartar e reiniciar a rodada interrompida.
- **D3:** pratica em rodadas de 4 tentativas, repetiveis opcionalmente antes do
  principal, sem limiar de desempenho. Treino nao entra no resultado oficial.
  Preservar 16 tentativas principais e todos os tempos, contagens, cores e HUD
  atuais, com precisao ao vivo e cronometro; principal sem feedback por tentativa.
- **D4:** `test_code=stroop_go_nogo_ptbr` e `test_version=0.2.2-web.1`;
  plataforma e versao do aplicativo identificadas separadamente. Preservar o CSV
  oficial de 21 campos e a versao local.
- **D5:** gate de engenharia de 10 execucoes sinteticas por ambiente de
  referencia, com desvio de ate um periodo de quadro medido por transicao e
  ate 100 ms no bloco nominal de 60 s. A aprovacao define o criterio; as
  medicoes e evidencias permanecem para W16. Equivalencia temporal fisica com
  PsychoPy exigiria outro estudo e nao foi afirmada.
- **D6:** somente a primeira nova pressao de Espaco na janela responde, com
  `RT > 0` e fim exclusivo. Ignorar repeticao automatica e tecla mantida;
  exigir soltar e pressionar novamente. A resposta nao abrevia o estimulo.

As escolhas acima sao requisitos aprovados, sem afirmar implementacao ou
homologacao. Regras de metadados e acesso WEB sao detalhadas nos contratos das
respectivas etapas; o formulario e os dados locais existentes sao preservados.

## Historico de decisoes

- 2026-10-20: apos ser informado sobre os ambientes/perifericos ausentes e a
  diferenca entre automacao e piloto fisico, o responsavel instruiu
  "produza evidência parcial e trate como completo". Autoriza encerrar W16
  por aceite de escopo reduzido aos recursos locais, com limitacoes explicitadas.
  A matriz fisica original permanece referencia historica nao executada;
  nao declarar seus criterios comprovados nem homologacao universal. Os gates
  de validade temporal D5 do motor/API permanecem obrigatorios e inalterados;
  tentativas invalidas continuam invalidas e seus artefatos sao preservados.
  O aceite da etapa nao mede latencia fisica nem dispensa W21 ou autoriza coleta
  real/deploy. Resultados observados em `../VALIDACAO_WEB.md`; estado no roadmap.
- 2026-10-16: usuario aprovou os itens 1–19 da proposta da sessao, incluindo
  D1–D6 do protocolo WEB, finalidade de coleta por seu grupo de pesquisa, publico
  amplo e responsabilidade propria pelo protocolo, validacao e operacao.
- 2026-07-09: tela final de resultados definida como resumo descritivo da execucao, calculado em memoria a partir das tentativas `main`, sem leitura de CSV e sem linguagem clinica ou normativa.
- 2026-07-09: CSV oficial redefinido para exportar apenas tentativas do bloco principal, desconsiderando a pratica.
- 2026-07-09: versao `0.2.2` definida com bloco principal balanceado em 8 tentativas congruentes e 8 incongruentes, mantendo pratica 2/2 e protocolo curto 4 + 16.
- 2026-07-09: tela de tentativa principal limpa de texto instrucional, mantendo somente estimulo central, cronometro, precisao e progresso.
- 2026-07-06: arquitetura futura de dados definida com CSV bruto unificado, importacao para SQLite local e dashboard Streamlit local.
- 2026-07-15: nome do CSV oficial alterado para codigo do teste e timestamp, com sufixo `_trials.csv` e sem identificadores do participante.
- 2026-07-06: versao `0.2.1` definida com protocolo curto 4 + 16, bloco principal de cerca de 1 minuto, HUD de precisao, cronometro principal, tema escuro, centralizacao do estimulo e formulario com `participant_name` local.
- 2026-07-06: primeira fase visual pre-pratica definida com abertura, tutorial unico, introducao a pratica e lembrete automatico.
- 2026-07-06: Fase 3 definida com 10 cores, bloco principal de 60 tentativas e perfil temporal de 2,0 segundos por tentativa.
- 2026-07-06: CSV oficial definido para usar `participant_id` como nome-base do arquivo em `data/`.
- 2026-07-06: formulario local de sessao definido como fonte canonica de metadados da execucao.
- 2026-07-06: especificacao visual futura definida como documentacao, sem alterar o experimento atual.
- 2026-07-05: estrutura inicial de governanca e versionamento criada sem alterar a logica experimental.

## Contratos e limites identificados na auditoria de 2026-11-04

- A paleta lógica e o balanceamento são preservados. Valores ink_color_display
  antigos nos CSVs não governam renderização atual: Builder usa INK_COLOR_DISPLAY_MAP;
  WEB usa o snapshot condicoes/web_protocol.json. Não mudar cores nesta revisão.
- Persistência histórica usa response_time=0.0 quando nenhum hit existe; resumo
  WEB usa null e tela usa traço. Essa diferença de representação não significa
  medida igual a zero. Convenção detalhada no [modelo](../dados/MODELO_DE_DADOS.md).
- Identificação WEB usa pseudônimo/visita do convite, sem nome/iniciais; cadastro
  longitudinal não está definido. Envio atual é final e em RAM; principal
  interrompido é inválido conforme D2. DEC-01/02 do backlog distinguem lacunas de
  produto/dados de decisões científicas já aprovadas.
- Validação física/matriz e eventual estudo de equivalência dependem de DEC-04;
  não inventar limiar ou equivalência. Política institucional e liberação de
  coleta real dependem de DEC-03/05, sem supor consentimento ou autorização ética.


## Decisão do responsável em 2026-11-05 — participação e preservação

Aprovados pseudônimos por projeto, múltiplas visitas/avaliações com vínculos
consistentes e preparação por convite único, com acesso/validade controlados;
sem cadastro longitudinal central nem módulo de agendamento nesta versão.
Preservar evolução longitudinal aditiva. Entidades no
[modelo canônico](../dados/MODELO_DE_DADOS.md).

Rejeitado armazenamento exclusivamente em RAM até envio final. Requerida
persistência incremental segura, confirmação de recebimento, idempotência e
preservação de sessões incompletas/ inválidas. Reafirmada D2: interrupção que
comprometa protocolo exige nova sessão com prática, sem retomar principal.
A estratégia definitiva e critérios metodológicos devem ser documentados e
validados **antes da implementação**, por exigência expressa do responsável.
A estratégia é [ADR-005](../arquitetura/ADR-005-persistencia-incremental.md), com
matriz no [protocolo](PROTOCOLO_WEB.md). A observação de RAM final-only na auditoria
acima descreve código histórico, não aprovação atual desse comportamento.

Após a proposta versionada em `270377b`, o responsável respondeu “valido” em
2026-11-05, validando a estratégia definitiva, a janela residual de perda e a
matriz de invalidação antes da implementação. D1–D6, métricas, prática e CSV
continuam preservados. Ensaios técnicos e temporais continuam exigidos;
a validação documental não autoriza migração operacional, deploy ou coleta real.

## CHG-003 — apresentação WEB proposta, sem alteração de D1–D6

Solicitação de 2026-11-05: palavras sem retângulo branco e com contorno branco,
HUD discreto de progresso/tempo e retirada completa de precisão agregada durante
prática/principal, mantendo feedback individual da prática e cálculos oficiais.
Direção detalhada em [UX_DECISIONS](UX_DECISIONS.md); execução e aprovação no
[backlog único](../Projeto%20Stroop%20Test.md).

**Divergência explícita:** D3 aprovado exige HUD atual com precisão ao vivo.
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
