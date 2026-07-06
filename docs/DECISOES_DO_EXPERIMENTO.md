# Decisoes do experimento

## Decisoes estabelecidas

- O paradigma e Stroop Go/No-Go.
- A resposta esperada e pressionar `Espaco` apenas quando palavra e cor coincidirem.
- Tentativas incongruentes devem ser inibidas, sem resposta.
- A pratica e separada do bloco principal.
- As cores previstas para o experimento sao verde, amarelo, rosa, preto, vermelho, laranja, marrom, roxo, azul e cinza.
- A lista oficial de palavras futuras e `VERDE`, `AMARELO`, `ROSA`, `PRETO`, `VERMELHO`, `LARANJA`, `MARROM`, `ROXO`, `AZUL` e `CINZA`.
- O bloco principal deve permanecer sem feedback por tentativa.
- A pratica podera ser repetida antes do bloco principal em implementacao futura.
- Resultados exibidos ao participante devem ser apenas descritivos.
- Idade e sexo nao devem ser usados para pontuacao, classificacao ou comparacao normativa.
- O projeto nao faz alegacoes clinicas, normativas, diagnosticas ou de equivalencia psicometrica.
- Dados locais de execucao e coleta ficam em `data/` e nao devem ser versionados.
- A pasta `condicoes/` e mantida como pasta existente de CSVs de condicoes, equivalente funcional ao nome `conditions/` solicitado para estrutura.

## Regras de classificacao de resposta

- Congruente + Espaco = `hit`.
- Congruente sem resposta = `omission`.
- Incongruente sem resposta = `correct_rejection`.
- Incongruente + Espaco = `commission`.

## Historico de decisoes

- 2026-07-06: especificacao visual futura definida como documentacao, sem alterar o experimento atual.
- 2026-07-05: estrutura inicial de governanca e versionamento criada sem alterar a logica experimental.
