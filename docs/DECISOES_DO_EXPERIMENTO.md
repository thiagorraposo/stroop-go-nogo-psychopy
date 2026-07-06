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
- A arquitetura de dados futura adotara SQLite local como armazenamento inicial.
- O dashboard futuro sera local, em Streamlit, lendo apenas SQLite.
- `participant_id` sera o identificador principal da pessoa.
- `initials` serao opcionais e tratadas como dado potencialmente identificavel.
- `assessment_date` sera gerada automaticamente pelo sistema.
- Campos obrigatorios de sessao: `project`, `participant_id`, `visit` e `evaluator`.
- O experimento usa formulario local de sessao antes da primeira tela.
- `participant_id` e o identificador canonico da pessoa no CSV.
- Nomes de arquivo de dados nao devem usar identificadores do participante, iniciais, visita ou avaliador.
- `test_version` inicial do formulario estruturado e `0.1.0`.
- Dados clinicos, normativos e diagnosticos permanecem proibidos.
- `response_time` sera definido como mediana dos tempos de reacao dos hits validos.
- O projeto nao faz alegacoes clinicas, normativas, diagnosticas ou de equivalencia psicometrica.
- Dados locais de execucao e coleta ficam em `data/` e nao devem ser versionados.
- A pasta `condicoes/` e mantida como pasta existente de CSVs de condicoes, equivalente funcional ao nome `conditions/` solicitado para estrutura.

## Regras de classificacao de resposta

- Congruente + Espaco = `hit`.
- Congruente sem resposta = `omission`.
- Incongruente sem resposta = `correct_rejection`.
- Incongruente + Espaco = `commission`.

## Historico de decisoes

- 2026-07-06: arquitetura futura de dados definida com CSV bruto unificado, importacao para SQLite local e dashboard Streamlit local.
- 2026-07-06: formulario local de sessao definido como fonte canonica de metadados da execucao.
- 2026-07-06: especificacao visual futura definida como documentacao, sem alterar o experimento atual.
- 2026-07-05: estrutura inicial de governanca e versionamento criada sem alterar a logica experimental.
