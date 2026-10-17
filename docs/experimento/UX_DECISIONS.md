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
