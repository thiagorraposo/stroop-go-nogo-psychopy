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
- PRETO, CINZA e AMARELO devem ser conferidos em Pilot antes de coleta real;
- branco permanece apenas como cor de interface, nao como estimulo;
- HUD mostra `Precisão: —` antes da primeira tentativa concluida e `Precisão: XX%` depois disso;
- barra horizontal textual acompanha a precisao acumulada;
- a pratica calcula precisao apenas da pratica;
- o bloco principal calcula precisao apenas do bloco principal;
- cronometro visual mostra `Tempo: MM:SS`, inicia apenas na primeira tentativa principal e segue ate o fim da ultima tentativa principal.

A precisao ao vivo pode influenciar o comportamento do participante. Essa exibicao e uma decisao de UX e nao uma configuracao metodologicamente neutra. O HUD nao deve ser interpretado como diagnostico, norma, classificacao clinica ou comparacao populacional.

## Limites

O experimento implementa um paradigma experimental de inibicao de resposta. Ele nao fornece diagnostico, escore clinico, classificacao cognitiva ou equivalencia clinica com qualquer produto comercial.

## Registro de dados

A coluna `block` foi adicionada para separar pratica (`practice`) e bloco principal (`main`) nos CSVs de saida. Os tipos de resposta sao registrados como `hit`, `omission`, `correct_rejection` e `commission`.
