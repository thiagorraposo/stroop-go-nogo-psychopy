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
- A arquitetura de dados futura adotara SQLite local como armazenamento inicial.
- O dashboard futuro sera local, em Streamlit, lendo apenas SQLite.
- `participant_id` sera o identificador principal da pessoa.
- `initials` serao opcionais e tratadas como dado potencialmente identificavel.
- `assessment_date` sera gerada automaticamente pelo sistema.
- Campos obrigatorios de sessao: `project`, `participant_id`, `visit` e `evaluator`.
- O experimento usa formulario local de sessao antes da primeira tela.
- `participant_id` e o identificador canonico da pessoa no CSV.
- Nomes de arquivo de dados nao devem usar iniciais, visita ou avaliador.
- O CSV oficial deve usar `participant_id` como nome-base do arquivo. `participant_name` e dado pessoal local e nao deve aparecer em nomes de arquivo, screenshots, exemplos publicos ou logs.
- `test_version` atual e `0.2.2`.
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

## Historico de decisoes

- 2026-07-09: tela final de resultados definida como resumo descritivo da execucao, calculado em memoria a partir das tentativas `main`, sem leitura de CSV e sem linguagem clinica ou normativa.
- 2026-07-09: CSV oficial redefinido para exportar apenas tentativas do bloco principal, desconsiderando a pratica.
- 2026-07-09: versao `0.2.2` definida com bloco principal balanceado em 8 tentativas congruentes e 8 incongruentes, mantendo pratica 2/2 e protocolo curto 4 + 16.
- 2026-07-09: tela de tentativa principal limpa de texto instrucional, mantendo somente estimulo central, cronometro, precisao e progresso.
- 2026-07-06: arquitetura futura de dados definida com CSV bruto unificado, importacao para SQLite local e dashboard Streamlit local.
- 2026-07-06: versao `0.2.1` definida com protocolo curto 4 + 16, bloco principal de cerca de 1 minuto, HUD de precisao, cronometro principal, tema escuro, centralizacao do estimulo e formulario com `participant_name` local.
- 2026-07-06: primeira fase visual pre-pratica definida com abertura, tutorial unico, introducao a pratica e lembrete automatico.
- 2026-07-06: Fase 3 definida com 10 cores, bloco principal de 60 tentativas e perfil temporal de 2,0 segundos por tentativa.
- 2026-07-06: CSV oficial definido para usar `participant_id` como nome-base do arquivo em `data/`.
- 2026-07-06: formulario local de sessao definido como fonte canonica de metadados da execucao.
- 2026-07-06: especificacao visual futura definida como documentacao, sem alterar o experimento atual.
- 2026-07-05: estrutura inicial de governanca e versionamento criada sem alterar a logica experimental.
