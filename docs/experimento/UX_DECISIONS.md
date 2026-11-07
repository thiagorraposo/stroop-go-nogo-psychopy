# Decisoes de UX

Este experimento usa uma interface original para uma tarefa Stroop Go/No-Go em portugues brasileiro. A experiencia foi desenhada para ser clara, limpa e adequada a uma tarefa cognitiva digital, sem copiar marca, logotipo, paleta proprietaria, textos, layout, assets ou sistema de pontuacao da CogniFit.

## Principios aplicados

- Tela cheia, cursor oculto e unidades relativas (`height`) para reduzir distracoes.
- Tema escuro com texto de alto contraste.
- Instrucoes curtas em telas separadas, evitando paragrafos longos.
- Exemplos visuais reais antes da pratica.
- Contagem regressiva visual antes da pratica e antes do bloco principal.
- Feedback apenas na pratica, com texto explicito e sem depender apenas de cor.
- Bloco principal sem feedback de desempenho, pontos, ranking ou classificacao.
- Indicador de progresso discreto durante o bloco principal.
- HUD discreto de precisao acumulada durante pratica e bloco principal.
- Cronometro visual apenas durante o bloco principal.

## Decisoes para a proxima versao visual

- Criar identidade visual original, propria do projeto, sem copiar interface, textos, logotipos, paletas, graficos, avaliacoes ou composicoes de terceiros.
- Usar layout de referencia 16:9, responsivo por unidades relativas do PsychoPy, preferencialmente `height`.
- Separar tutorial, pratica e tarefa principal com rotulos claros.
- Manter pratica com feedback imediato e bloco principal limpo, sem feedback por tentativa.
- Nao mostrar diagnostico, normas populacionais, recomendacoes clinicas, classificacao individual ou comparacoes como acima/abaixo da media.
- Usar as dez cores definidas para a versao futura: verde, amarelo, rosa, preto, vermelho, laranja, marrom, roxo, azul e cinza.
- Manter foco visual no estimulo central e evitar elementos decorativos durante a tarefa principal.
- Oferecer botoes claros em telas de navegacao, sempre com alternativa por teclado quando aplicavel.

## Fase visual pre-pratica

Implementada em 2026-07-06 como primeira parte da nova interface visual:

- `boas_vindas`: abertura com titulo, explicacao, exemplo visual simples, botao textual e alternativa por teclado.
- `tutorial_regra`: tutorial unico com exemplos Go e No-Go lado a lado.
- `pratica_inicio`: introducao curta a pratica e ao feedback.
- `regra_rapida`: lembrete automatico de aproximadamente 1,5 segundo antes da contagem regressiva.

As telas navegaveis aceitam clique no botao textual, `Espaco` e `Enter`. Cliques sao tratados apenas nessas telas de navegacao e nao entram como resposta experimental nas tentativas Stroop. O `participant_name` e um dado pessoal local, usado apenas no formulario e nunca em nome de arquivo, logs ou screenshots publicos. A identidade visual inicial usava fundo claro, tipografia sans-serif, destaque azul-esverdeado proprio e exemplos simples, sem imagens externas ou assets de terceiros.

## Tema escuro e HUD

Implementado em 2026-07-06 na versao `0.2.1`:

- tema escuro aplicado nas telas de instrucao, contagem, pratica, bloco principal e fim;
- fundo principal `#0B1020`, texto principal `#F8FAFC` e texto auxiliar `#CBD5E1`;
- estimulos exibidos sobre cartao claro aproximado de `#F8FAFC` para preservar contraste;
- palavras centralizadas explicitamente no cartao claro, com alinhamento e ancoras horizontal e vertical no centro;
- cartoes de pratica e bloco principal usam retangulo Builder de `0,82 x 0,24` em unidades `height`, com palavras em altura `0,090`, evitando overflow das palavras mais longas sem prejudicar leitura rapida;
- branco permanece apenas como cor de interface, nao como estimulo;
- HUD mostra `Precisão: —` antes da primeira tentativa concluida e `Precisão: XX%` depois disso;
- barra horizontal textual acompanha a precisao acumulada;
- a pratica calcula precisao apenas da pratica;
- o bloco principal calcula precisao apenas do bloco principal;
- cronometro visual mostra `Tempo: MM:SS`, inicia apenas na primeira tentativa principal e segue ate o fim da ultima tentativa principal.

A precisao ao vivo pode influenciar o comportamento do participante. Essa exibicao e uma decisao de UX e nao uma configuracao metodologicamente neutra. O HUD nao deve ser interpretado como diagnostico, norma, classificacao clinica ou comparacao populacional.

## Paleta visual dos estimulos

Atualizada em 2026-07-15 exclusivamente para renderizacao. As chaves logicas de `ink_color`, condicoes e exportacao permanecem inalteradas:

- `green`: `#40FF00`;
- `yellow`: `#FFF200`;
- `pink`: `#FF5CCB`;
- `black`: `#000000`;
- `red`: `#FF0000`;
- `orange`: `#FF9000`;
- `brown`: `#965000`;
- `purple`: `#9A24FF`;
- `blue`: `#0062FF`;
- `gray`: `#808080`.

A mesma paleta e usada na pratica e no bloco principal por meio de um mapa visual no `.psyexp`, sem exportar hexadecimal, RGB ou campos auxiliares. A verificacao Pilot deve priorizar a legibilidade de amarelo sobre o cartao claro e a distincao entre preto/cinza, vermelho/rosa, laranja/marrom e azul/roxo.

Checklist Pilot visual:

1. Abrir o experimento em Run.
2. Conferir o cartao branco centralizado.
3. Conferir que as dez cores estao mais vivas.
4. Conferir distincao clara entre preto/cinza, vermelho/rosa, laranja/marrom e azul/roxo.
5. Conferir a legibilidade do amarelo.
6. Confirmar que o teste e o CSV continuam normais.

## Tela final de resultados

Implementada em 2026-07-09:

- rotina `resultados` exibida apos o bloco principal como tela final de encerramento;
- mantem o tema escuro atual com painel central claro e alinhado em unidades `height`;
- mostra apenas dados descritivos desta execucao: precisao total do bloco principal, mediana dos tempos de reacao dos hits e contagens de Hits, Omissoes, Rejeicoes corretas e Comissoes;
- usa indicador circular original, sem logotipo, marca, paleta proprietaria, classificacao, ranking, normas ou recomendacoes;
- inclui aviso explicito de que o resumo nao representa diagnostico ou avaliacao clinica;
- aceita clique no botao `Finalizar`, `Espaco` ou `Enter`.

## Limites

O experimento implementa um paradigma experimental de inibicao de resposta. Ele nao fornece diagnostico, escore clinico, classificacao cognitiva ou equivalencia clinica com qualquer produto comercial.

## Formulario visual responsivo

Atualizado em 2026-08-04:

- o cadastro e uma rotina visual interna do PsychoPy, sem `gui.Dlg`, `tkinter` ou janela nativa;
- campos editaveis, labels, mensagem de erro e botao permanecem dentro de um cartao central em unidades `height`;
- fullscreen continua como padrao, mas o layout nao define posicoes ou tamanhos em pixels;
- o cursor fica visivel no formulario e nas telas com botao, sendo ocultado somente durante as tentativas Stroop;
- entradas invalidas mantem a rotina ativa e exibem a orientacao no proprio formulario.

Essa decisao reduz variacoes de layout causadas por DPI scaling, decoracoes de janelas nativas e resolucoes diferentes entre Windows, Linux e macOS, sem mudar o protocolo ou o contrato de dados.

## Registro de dados

A coluna `block` permanece no CSV oficial, mas as execucoes atuais exportam apenas o bloco principal (`main`). A pratica e usada para treinamento, feedback e HUD local, sem gerar linhas no CSV oficial. Os tipos de resposta do bloco principal sao registrados como `hit`, `omission`, `correct_rejection` e `commission`.

## Area de upload local

Em 2026-09-13, autorizada interface separada do dashboard SQLite para envio
local de um CSV sintetico por vez. A pagina apresenta limite e descarte antes
do envio, botao desabilitado durante processamento e resultado textual recebido,
validado, importado ou rejeitado. Nao renderiza conteudo do CSV ou mensagens
internas; a selecao e limpa ao finalizar. Operacao em [UPLOAD_LOCAL.md](../dados/UPLOAD_LOCAL.md).

Atualizado na Etapa 8: a rota HTTP propria foi removida e o comando existente
passou a abrir a area **Importacao** dentro do dashboard autenticado. Perfis sem
permissao nao veem essa area; conta nao cadastrada ve apenas os identificadores
`iss` e `sub` da propria sessao para solicitar cadastro manual. O e-mail e
exibido somente como informacao auxiliar da conta autenticada. Detalhes em
[AUTENTICACAO_E_PERMISSOES.md](../seguranca/AUTENTICACAO_E_PERMISSOES.md).

## WEB — preparacao da sessao pela equipe (W13A)

A area autenticada oferece `Preparar sessao` no projeto ativo para perfis de
coleta/importacao e administracao. Exibe projeto e identificacao tecnica da
conta; o servidor fixa o avaliador. Os dois campos recebem apenas codigo
pseudonimizado e visita, com validacao por campo e foco no primeiro erro.
Nao coleta nome, iniciais ou outros dados pessoais do participante.

A emissao exige acao explicita e bloqueia envio concorrente. A confirmacao
mostra metadados e convite de uso unico somente em RAM, com prazo UTC.
`Abrir pratica em outra aba` usa apenas `/pratica`, sem segredo na URL.
Troca de projeto, recarga, saida ou expiracao da conta descartam a exibicao;
cancelar uma requisicao local nao desfaz uma escrita no servidor.

Timeout, falha de rede ou resposta invalida nao provam que a criacao falhou:
a interface informa resultado desconhecido, nao repete POST nem oferece
revogacao sem identificador confirmado. Nova emissao e uma nova sessao,
explicitamente solicitada. Revogacao so e declarada apos resposta204; uma
falha pede confirmacao novamente e orienta a nao entregar o codigo.

## WEB — importacao de CSV pela equipe (W15E)

O painel de importacao fica no projeto ativo selecionado e somente para perfis
de coleta/importacao ou administracao com vinculo. A pessoa escolhe um CSV
registrado; o navegador cria uma copia em memoria, substitui `participant_name`
por `NAO_COLETADO` e limpa `initials`. O arquivo original nao e alterado, e a
tela mostra destino e limites sem exibir nome ou conteudo do arquivo.

Durante a operacao, a tela informa envio e estado recebido/validado/importado/
rejeitado. Se a resposta se perder, oferece consulta pelo UUID e reenvio
explicitamente solicitado da mesma copia; nunca repete POST automaticamente.
Concluido o upload, limpa selecao e copia e atualiza os resultados do projeto.
O CSV continua sendo dado local de origem; a importacao nao equivale a coleta
WEB nem habilita pesquisa real.

## WEB — consulta combinada da equipe (W15A)

`Projeto` mantem o contexto de preparacao da sessao; `Projetos da consulta`
seleciona os contextos de leitura explicitamente. Filtros usam seletores nativos
com labels, instrucoes de teclado, datas inclusivas e resumo aplicado.
Alteracoes no formulario nao mudam o agregado ate `Aplicar filtros`; limpar
retorna a consulta ao projeto de preparacao. Facetas respeitam projeto,
periodo e instrumento; erro ou excesso de opcoes e indicado sem truncamento.

A lista so publica o conjunto apos completar todas as paginas, com teto explicito
de 20 projetos/5.000 avaliacoes. Durante a espera, contagens recebidas sao progresso,
nao totais de pesquisa. Falha, acesso revogado ou mudanca do conjunto durante
paginacao descartam totais, tabela e graficos; recuperacao e explicita.
Participantes sao identificados por projeto+codigo. A evolucao individual
anterior so aparece num unico projeto, evitando fundir pseudonimos coincidentes.
A tabela mostra projeto e encaminha detalhe/exportacao ao contexto da linha.


## WEB — apresentacao dos resultados por instrumento (W15B)

A tabela mostra metadados e metricas aplicaveis ao instrumento selecionado,
sem colunas Stroop preenchidas ficticiamente para outros instrumentos.
O detalhe identifica avaliacao/sessao/projeto, avaliador tecnico, horarios,
versoes, protocolo, aplicativo e quatro contagens de resposta do principal.
Ausencias legadas ficam explicitas; arquivo fonte e campos nominais nao entram
na apresentacao. Resultados descritivos nao possuem norma, ranking ou score.

A comparacao de erros distingue projetos e oferece tabela alternativa.
A evolucao seleciona projeto+codigo, conserva visitas repetidas e usa ordem
inicio+ID. Precisao e tempo mediano recebem figuras separadas, com unidades
explicitas e ausencia sem barra/zero ficticio. A demonstracao sintetica registrada
recebe cards, figuras e tabela com suas metricas/unidades; codigos desconhecidos
ficam em tabela neutra. Os componentes usam somente o conjunto filtrado carregado,
sem requisicao de detalhe por linha nem mistura entre instrumentos.

## WEB — exportacao agregada manual (W15C)

`Exportar visao filtrada` acompanha os filtros e projetos aplicados e tambem a
selecao local de instrumento/plataforma. O arquivo tem uma linha por avaliacao,
colunas permitidas e unidades explicitas; metadados nominais, nomes de arquivo
fonte e identificadores de sessao nao entram. Texto que possa ser interpretado
como formula e protegido, valores ausentes permanecem vazios e metricas nao sao
arredondadas. O token de consistencia fica apenas em RAM, expira em 15 minutos
e o download so inicia depois da reautorizacao integral no servidor. Este arquivo
agregado nao substitui o CSV oficial individual de tentativas.

## WEB — administracao de contas e projetos (W15D)

A area **Administracao** e exclusiva do perfil correspondente; **Resultados**
continua separado. O cadastro solicita o `sub` que a propria pessoa obteve ao
entrar com Google sem cadastro WEB e encaminha por canal institucional. O
e-mail e opcional, auxiliar e visivel somente a administradores. Antes de
cadastrar, alterar perfil/e-mail/estado ou mudar um vinculo, a interface informa
o alvo e o efeito e pede confirmacao. Projetos nao concedem acesso por criacao:
cada profissional precisa de vinculo explicito. Bloqueio e revogacao preservam
coletas e o servidor revalida cada operacao. Nao ha autocadastro, exclusao nem
edicao de mapa legado nessa tela.

## WEB — percurso do participante (W09A)

A abertura preserva a identidade visual e o titulo da tarefa, com acao
`Iniciar tutorial` e exemplos proprios que distinguem palavra/cor iguais e
diferentes. O tutorial organiza a regra em passos curtos e segue para a pratica.
O indicador de percurso aparece nas telas preparatorias, sem HUD novo durante
tentativas. Preparacao apresenta verificacoes e passos; no resumo da pratica,
`Comecar tarefa` e a acao primaria e repetir fica secundaria.

O resumo principal so declara conclusao/agradecimento quando o recibo foi
confirmado. Envio pendente continua distinguivel e recuperavel; falha ao encerrar
a sessao nao mostra a tela de encerramento e permite tentar novamente. A
confirmacao de encerramento oferece retorno as orientacoes e deixa outro convite
como opcao secundaria. O foco programatico permanece visivel. Essas telas nao
alteram motor, estimulos, condicoes, tempos, feedback cronometrado, teclas,
tratamento de foco/Escape ou CSV.

## WEB — direção UX de CHG-003 (2026-11-05)

Especificação visual aprovada explicitamente pelo proprietário na revisão D3 de
2026-11-05; implementação e aceite por tarefa no backlog. As seções
locais e Wxx acima preservam seu contexto histórico; não governam esta mudança.
Execução, riscos, decisões e evidências somente no
[backlog canônico](../Projeto%20Stroop%20Test.md); vínculos na
[matriz](../REQUISITOS_E_RASTREABILIDADE.md), REQ-UX-001 a REQ-UX-011.

**Durante o teste, a interface do participante deverá apresentar os estímulos
sem a barra de precisão dos acertos ou indicadores agregados de desempenho.
A barra de progresso e o cronômetro poderão permanecer, conforme o protocolo
aprovado.** A apresentação foi aprovada explicitamente pelo proprietário; D3/D4 revisadas
e identificação `stroop-web-outline/1.0.0` no [protocolo](PROTOCOLO_WEB.md).
D1/D2/D5/D6 e protocolo cognitivo preservados. DEC-04 continua pendente.

### Estímulos e hierarquia (UX-01/05)

Retirar o retângulo branco, sem substituir por caixa/cartão. Aplicar contorno
branco diretamente aos caracteres para delimitar a forma das letras sobre o
fundo experimental escuro; essa é uma hipótese de legibilidade, não prova de
percepção equivalente das cores. Preservar o preenchimento das dez cores do
snapshot, fundo geral, família/peso/tamanho experimental e centro geométrico.
Não usar sombra pesada, gradiente ou volume; não ajustar cores automaticamente
nem criar tratamentos por cor. Qualquer ajuste tipográfico exige justificativa.

Avaliar `-webkit-text-stroke` e alternativa de contorno compatível nos navegadores
de D1. Definir token único de espessura após revisão sintética das dez cores,
sem fixar valor experimental por conveniência; comprovar que o contorno não
encobre a tinta. Registrar alternativa, limites de renderização, screenshots
sintéticos e dimensões em Chromium/Firefox. Nenhum suporte inferido de CSS.
Estímulo permanece no centro experimental; HUD periférico não desloca seu centro.
Remover espaços reservados à precisão. Sem menus, sidebar ou controles flutuantes.
Não alterar escala por responsividade, duração, ordem, composição ou intervalos.

### Progresso e cronômetro (UX-02/03)

Progresso minimalista: traço fino, geometria consistente, cantos discretos,
contraste controlado, rótulo legível e alinhado. Derivar etapa e total do contrato
vigente e contar tentativas **concluídas**, sem número fixo ou avanço no início
da tentativa. Exemplo ilustrativo: `Bloco principal · 8 / 16`. Distinguir prática e
principal; sem animação durante estímulos. Visibilidade aprovada na D3 revisada: progresso em prática/principal, cronômetro
somente no principal; HUD oculto em contagens/lembrete/feedback individual.
Conferir localização e impacto na campanha DEC-04.

Cronômetro mantém tempo **decorrido** do principal, iniciado na primeira tentativa
até o fim da última, formato `MM:SS`, algarismos tabulares e largura numérica
estável, alinhamento discreto e sem decoração. O placeholder da prática será retirado, conforme política D3 aprovada, sem criar
relógio de prática. Usar origem monotônica do motor; atualizar DOM somente quando necessário,
sem novo intervalo React, relógio científico paralelo, ticks acumulativos ou
re-render por quadro. RT e registros científicos permanecem independentes.

### Ausência de desempenho agregado (UX-04)

Retirar nós, rótulos, percentuais, barras, tooltips e conteúdo acessível de
precisão, taxa de acertos/erros, classificação, ranking ou equivalentes na prática
e no principal. Não basta ocultar com CSS/aria-hidden; não substituir por outro
indicador de qualidade nem deixar espaço vazio. Feedback **individual** da
prática e repetição sem limiar permanecem conforme protocolo; sem classificação.
Accuracy total/Go/No-Go, omissões, comissões e RT continuam calculados, persistidos
e disponíveis nos relatórios/CSV/dashboard aos profissionais autorizados.

### Instruções e transições (UX-06/07)

Hierarquia clara da regra Go/No-Go, tecla de resposta destacada e confirmação de
início, distinguindo prática e principal. Preservar semântica aprovada, sem dicas
novas de estratégia cognitiva. Reutilizar textos de COPY_DAS_TELAS como fonte de
copy; revisão aprovada antes de mudança semântica. Organizar instruções, prática,
feedback, preparação, execução e encerramento sem tempos adicionais implícitos.

Distinguir execução concluída, dados aguardando envio, envio em andamento,
confirmação do servidor, falha de envio e sessão interrompida/inválida. Somente
recibo válido autoriza afirmar recebimento/sucesso. Preservar ADR-005, idempotência,
ACKs incrementais, observações parciais separadas de resultado oficial e D2:
nenhuma retomada do principal. Resultado individual ao participante somente se
autorizado no protocolo; revisar o resumo agregado existente em WEB-015 sem
supor que removê-lo durante execução autorize mudar a tela final.

### Acessibilidade e regressão (UX-08)

Reutilizar tokens/componentes existentes de styles.css; sem biblioteca nova.
Teclado, foco visível, legibilidade, contraste não experimental, erros/loading,
resoluções permitidas, ausência de scroll e perda de foco devem ser verificados.
Não recolorir estímulos para satisfazer contrastes de UI, não alterar modalidade
de resposta nem restrições de ambiente/fullscreen vigentes em D1 (fullscreen
não obrigatório). Não prometer acessibilidade experimental por ajuste automático.

Regressão planejada em WEB-044: DOM e árvore acessível sem desempenho agregado;
feedback individual preservado; dez cores/centralização/tipografia/contorno sem
caixa em Chromium e Firefox nas resoluções aprovadas; screenshots sintéticos;
progresso real e sem animação; relógio monotônico sem duplicação/deriva; Go/No-Go,
congruência, quatro resultados, janelas, sequência, lifecycle e interrupções
inalterados. WEB-016/019/020 verificam persistência, dashboard e exportações.
WEB-011 mede D5 com o layout final e transporte ativo; WEB-034 avalia saliência,
atenção, protocolo visual e limitações de equivalência com PsychoPy. Testes
CSS/automatizados não comprovam validade psicométrica nem latência física.

### Concretização de D3 visual 1.0.0

O token `--experiment-outline-width: .02em` aplica contorno branco uniforme
com `-webkit-text-stroke`; `paint-order: stroke fill` desenha o preenchimento
sobre o contorno, preservando a tinta e a fonte existentes. Referência técnica:
[WHATWG Compatibility — text stroking](https://compat.spec.whatwg.org/#text-stroke).
A avaliação de alternativa com sombras deslocadas foi descartada por gerar
aproximação direcional do contorno; não há fallback que altere silenciosamente
cores/tipografia. A capacidade stroke/paint-order é verificada nos navegadores
ensaiados, sem prometer compatibilidade com versões não medidas.

HUD imperativo compartilhado entre motores por `presentation.ts`, fora do React;
progresso de 3 px, sem animação, e contador MM:SS com números tabulares e largura
estável. O cronômetro mantém a origem monotônica principal; não há relógio novo
na prática. Nenhum elemento de desempenho agregado é criado. Tokens e centro
experimental independem da quantidade de itens no HUD. Evidências e ambientes
reais dos ensaios, incluindo falhas, ficam apenas no backlog canônico.

## WEB — reformulação funcional e UX da interface administrativa (CHG-005 — 2026-11-07)

Especificação da experiência profissional planejada em `CHG-005` ([ADR-007](../arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md)), integrada às tarefas `WEB-045` e `WEB-046` (`M4`), `WEB-047` e `WEB-017`–`WEB-020` (`M5`) e `WEB-025` (`M7`). As seções históricas `W13A`, `W15A`–`W15E` permanecem acima como registro do baseline anterior. **Esta reformulação aplica-se exclusivamente à área profissional autenticada; o motor experimental jsPsych, estímulos, contorno branco `stroop-web-outline/1.0.0`, HUD, dez cores e temporização D5 permanecem inalterados.**

### 1. Arquitetura de informação e fluxo de trabalho profissional

O percurso principal da equipe segue a sequência integrada:

**Login da equipe → Dashboard (Visão geral) → Pacientes / Avaliadores → Preparar avaliação → Executar teste → Armazenar resultados → Consultar, analisar e exportar.**

A navegação administrativa organiza-se em oito áreas com hierarquia visual clara, estados ativos e atalhos contextuais:

1. **Visão geral (Dashboard):** indicadores sintéticos (KPIs), atividade recente, evolução temporal de coletas e atalhos rápidos para `Preparar avaliação`, `Cadastrar paciente` e `Exportar dados`.
2. **Pacientes:** listagem pesquisável e paginada, cadastro de novo paciente com verificação de duplicidade/homônimos, edição cadastral auditada, inativação lógica e ficha detalhada com histórico longitudinal de projetos, visitas, sessões e avaliações.
3. **Avaliadores:** listagem pesquisável e paginada de avaliadores responsáveis, cadastro com verificação de duplicidade, edição e inativação lógica, e ficha detalhada com histórico de avaliações conduzidas (sem criar conta de login individual).
4. **Preparar avaliação:** assistente/formulário estruturado que seleciona (ou cadastra inline) o paciente e o avaliador responsável, seleciona projeto e instrumento, preenche visita e iniciais (pré-preenchidas do cadastro do paciente), valida vínculos, apresenta **resumo para conferência** e emite o convite de uso único sem digitação manual de IDs internos.
5. **Avaliações e histórico:** acompanhamento operacional de convites emitidos, sessões em andamento/concluídas/interrompidas/expiradas, inspeção de checkpoints incrementais (`ADR-005`) e invalidação auditável quando aplicável.
6. **Resultados e análises:** consulta combinada com catálogo completo de filtros, tabelas analíticas de avaliações, tentativas e métricas oficiais, e visualizações interativas descritivas.
7. **Exportações:** configuração de exportação CSV do conjunto filtrado por nível de granularidade (`pacientes`, `avaliacoes`, `tentativas`, `metricas`, `stroop_21_colunas`), seleção de colunas, modo de identificação (`deidentified` padrão vs. `nominal` autorizado), pré-visualização com contagem de linhas e resumo dos critérios aplicados antes do download.
8. **Administração / configurações:** gestão de projetos, membros/vínculos por projeto, sessão/senha da conta local compartilhada (`ADR-006`) e associação auditada de registros legados (`WEB-027`). A área de importação manual de CSV (`CsvImportPanel`) é **retirada** do produto (`WEB-025`).

### 2. Dashboard principal e indicadores descritivos

O painel `Visão geral` apresenta cartões KPI e gráficos descritivos calculados sobre os projetos autorizados:

- **Total de pacientes cadastrados** (ativos e com participação nos projetos autorizados).
- **Avaliações válidas realizadas** por período (hoje, últimos 7/30 dias, total), por instrumento (`test_code`), por projeto, por status de sessão (`completed`, `preparing`/`running`, `aborted`/`invalidated`/`expired`) e por avaliador responsável.
- **Evolução temporal de coletas:** série temporal de avaliações concluídas por dia/semana/mês.
- **Resumos descritivos das métricas oficiais (Stroop Go/No-Go):** precisão total (%), precisão Go (%), precisão No-Go (%), contagens de `hits`, `omission_errors`, `correct_rejections`, `commission_errors` e tempos de reação (`mean`, `sd`, `median`, `iqr` em segundos/ms sobre `hits`).
- **Rigor metodológico na apresentação:** todo indicador exibe explicitamente sua **origem**, **definição**, **unidade de medida** e **tratamento de valores nulos** (ex.: RT exibido como `Ausente` quando `hits = 0`, nunca convertido em zero). É estritamente proibido exibir diagnóstico clínico, escore normativo, percentil populacional ou classificação "acima/abaixo da média".

### 3. Visualizações interativas, tabelas e estados de interface

- **Visualizações interativas (`Resultados e análises`):**
  - Evolução longitudinal do paciente através de visitas e avaliações (precisão total/Go/No-Go e RT mediano/IIQ ao longo do tempo).
  - Distribuição de tempos de reação e comparação descritiva por condição experimental (`congruent` vs. `incongruent`) e por tipo de resposta/erro (`hit`, `omission`, `correct_rejection`, `commission`).
  - Distribuição de avaliações e erros por projeto, visita e avaliador responsável, sempre acompanhada de tabela acessível equivalente.
- **Tabelas e listagens:** busca textual com debounce, filtros visíveis como *chips* removíveis, ordenação por coluna, paginação com tamanho configurável, ações contextuais por linha (abrir ficha do paciente, inspecionar detalhe da avaliação, exportar CSV individual de 21 colunas) e estados claros de carregamento (*skeleton*/progresso), lista vazia (*empty state* orientativo) e erro recuperável.
- **Critérios de sistema visual e acessibilidade (`REQ-UX-012`):** tipografia legível com algarismos tabulares (`font-variant-numeric: tabular-nums`) em códigos, métricas e timestamps; contraste compatível com WCAG AA nas telas administrativas; navegação completa por teclado com `:focus-visible` nítido; modais/etapas de confirmação antes de inativar cadastro, emitir convite ou revogar sessão; responsividade para desktops e notebooks de pesquisa.
