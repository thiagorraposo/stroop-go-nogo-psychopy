# Decisoes de UX

Este experimento usa uma interface original para uma tarefa Stroop Go/No-Go em portugues brasileiro. A experiencia foi desenhada para ser clara, limpa e adequada a uma tarefa cognitiva digital, sem copiar marca, logotipo, paleta proprietaria, textos, layout, assets ou sistema de pontuacao da CogniFit.

## Principios aplicados

- Tela cheia, cursor oculto e unidades relativas (`height`) para reduzir distracoes.
- Fundo escuro suave com texto de alto contraste.
- Instrucoes curtas em telas separadas, evitando paragrafos longos.
- Exemplos visuais reais antes da pratica.
- Contagem regressiva visual antes da pratica e antes do bloco principal.
- Feedback apenas na pratica, com texto explicito e sem depender apenas de cor.
- Bloco principal sem feedback de desempenho, pontos, ranking ou classificacao.
- Indicador de progresso discreto durante o bloco principal.

## Limites

O experimento implementa um paradigma experimental de inibicao de resposta. Ele nao fornece diagnostico, escore clinico, classificacao cognitiva ou equivalencia clinica com qualquer produto comercial.

## Registro de dados

A coluna `block` foi adicionada para separar pratica (`practice`) e bloco principal (`main`) nos CSVs de saida. Os tipos de resposta sao registrados como `hit`, `omission`, `correct_rejection` e `commission`.
