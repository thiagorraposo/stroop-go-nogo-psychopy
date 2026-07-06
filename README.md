# Stroop Go/No-Go PsychoPy

Experimento PsychoPy Builder de Stroop Go/No-Go em portugues brasileiro.

Regra da tarefa: pressionar `Espaco` apenas quando a palavra e a cor da tinta forem congruentes. Nao responder quando forem incongruentes.

Este projeto e mantido para fins educacionais e de pesquisa exploratoria. Ele nao e instrumento clinico validado, nao produz diagnostico e nao deve ser usado para classificacao clinica ou normativa.

## Arquivos

- `stroop_go_nogo_ptbr.psyexp`: experimento para abrir no PsychoPy Builder.
- `condicoes/pratica_stroop_go_nogo_ptbr.csv`: tentativas do bloco de pratica.
- `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv`: tentativas do bloco principal.
- `condicoes/contagem_regressiva.csv`: telas breves de preparacao antes dos blocos.
- `data/`: pasta onde o CSV unificado por execucao e salvo pelo PsychoPy.
- `scripts/analisar_stroop.py`: script para validar e analisar um CSV unificado.
- `docs/UX_DECISIONS.md`: notas sobre as decisoes de experiencia de usuario.
- `AGENTS.md`: regras persistentes para agentes e contribuicoes futuras.
- `docs/`: documentacao de governanca, decisoes e historico.
- `assets/`: assets proprios do projeto.
- `tests/`: espaco reservado para validacoes futuras.

## Como abrir no Builder

1. Abra o PsychoPy.
2. Selecione a interface Builder.
3. Use `File > Open...` e escolha `stroop_go_nogo_ptbr.psyexp`.
4. Verifique se os arquivos em `condicoes/` estao acessiveis.

## Como executar em modo Pilot

1. Abra o experimento no Builder.
2. Use o modo `Pilot` para testar a tarefa sem tratar a execucao como coleta definitiva.
3. Preencha o formulario local de sessao quando solicitado.
4. Confirme a sequencia pre-pratica: abertura, tutorial, inicio da pratica, lembrete rapido e contagem regressiva.
5. Confirme se a pratica mostra feedback e se o bloco principal nao mostra feedback.
6. Use Pilot para verificacoes antes de qualquer coleta real.

## Como executar em modo Run

1. Abra o experimento no Builder.
2. Use o modo `Run` para coleta.
3. Preencha o formulario local de sessao.
4. O CSV unificado da execucao sera gravado em `data/`.
5. Nao versione arquivos gerados em `data/`.

## Condicoes

As palavras usadas sao `VERDE`, `AMARELO`, `ROSA`, `PRETO`, `VERMELHO`, `LARANJA`, `MARROM`, `ROXO`, `AZUL` e `CINZA`.

- `congruent`: palavra e cor correspondem; resposta correta e pressionar `Espaco`.
- `incongruent`: palavra e cor nao correspondem; resposta correta e nao pressionar nada.

Cada tentativa tem:

- fixacao: 300 ms;
- estimulo/resposta: 1500 ms;
- intervalo vazio entre tentativas: 200 ms.

A pratica tem 10 tentativas, com 5 Go/congruentes e 5 No-Go/incongruentes. O bloco principal tem 60 tentativas, com 40 Go/congruentes e 20 No-Go/incongruentes, totalizando cerca de 120 segundos no bloco principal. O fluxo completo e maior por incluir formulario, instrucoes e pratica.

## Dados

Os CSVs locais ficam em `data/`. Essa pasta e ignorada pelo Git para proteger dados de teste, execucao e participantes.

Cada execucao concluida normalmente deve gerar um unico CSV oficial por tentativa, nomeado pelo `assessment_id`. Pratica e bloco principal ficam no mesmo arquivo e sao diferenciados pela coluna `block`.

As colunas principais registradas por tentativa sao:

`project`, `participant_id`, `initials`, `visit`, `evaluator`, `assessment_id`, `assessment_date`, `started_at`, `test_code`, `test_version`, `block`, `trial_number`, `word`, `ink_color`, `condition`, `correct_response`, `key_pressed`, `reaction_time`, `correct`, `error_type`.

`ink_color` usa nomes de cor simples (`green`, `yellow`, `pink`, `black`, `red`, `orange`, `brown`, `purple`, `blue`, `gray`) para manter o CSV unificado compativel com pandas, R e SPSS sem campos RGB com virgulas internas.

`block` diferencia:

- `practice`: bloco de pratica;
- `main`: bloco principal.

`error_type` usa:

- `hit`: pressionou `Espaco` corretamente em tentativa congruente;
- `omission`: deixou de responder em tentativa congruente;
- `correct_rejection`: nao respondeu corretamente em tentativa incongruente;
- `commission`: pressionou `Espaco` em tentativa incongruente.

## Analise

Depois de coletar dados, execute:

```bash
python3 scripts/analisar_stroop.py data/ASSESSMENT_ID.csv
```

O script valida o CSV unificado, calcula metricas descritivas do bloco principal e nao modifica o arquivo original. O contrato completo esta em `docs/CSV_UNIFICADO.md`.

## Camada de dados e dashboard

A arquitetura futura prevista e: PsychoPy -> CSV bruto unificado -> script de importacao -> SQLite local -> dashboard Streamlit local.

A Fase 1 dessa camada, com formulario local de sessao, foi implementada. A Fase 2, com CSV unificado por execucao e analisador tecnico, foi implementada e depende de aprovacao manual em Pilot. Importacao, SQLite e dashboard ainda estao pendentes. O modelo de dados, regras de privacidade e plano incremental estao documentados em `docs/DADOS_E_DASHBOARD.md`, `docs/MODELO_DE_DADOS.md`, `docs/CSV_UNIFICADO.md` e `docs/PLANO_DE_IMPLEMENTACAO_DASHBOARD.md`.

## Metadados da sessao

Antes da primeira tela, o experimento exibe um formulario local com `project`, `participant_id`, `initials`, `visit` e `evaluator`. A data, hora, `assessment_id`, `test_code` e `test_version` sao gerados automaticamente.

Use identificadores pseudonimizados. Nao informe nome completo, CPF, e-mail, telefone, endereco, idade ou sexo. As regras completas estao em `docs/FORMULARIO_DE_SESSAO.md`.

## Interface pre-pratica

A primeira parte da interface visual conduz o participante por abertura, tutorial da regra, introducao a pratica e lembrete rapido antes da contagem regressiva. As telas navegaveis aceitam clique, `Espaco` e `Enter`. Essa etapa nao registra linhas no CSV canonico e nao altera as tentativas Stroop.

## Estrutura do projeto

```text
.
├── AGENTS.md
├── README.md
├── .gitignore
├── stroop_go_nogo_ptbr.psyexp
├── assets/
│   ├── README.md
│   └── ui/
├── condicoes/
│   ├── AGENTS.md
│   ├── README.md
│   ├── bloco_principal_stroop_go_nogo_ptbr.csv
│   ├── contagem_regressiva.csv
│   └── pratica_stroop_go_nogo_ptbr.csv
├── data/
│   └── README.md
├── dashboard/
│   ├── AGENTS.md
│   └── README.md
├── docs/
│   ├── AGENTS.md
│   ├── COPY_DAS_TELAS.md
│   ├── CSV_UNIFICADO.md
│   ├── DADOS_E_DASHBOARD.md
│   ├── DECISOES_DO_EXPERIMENTO.md
│   ├── ESPECIFICACAO_VISUAL_E_FLUXO.md
│   ├── ESTRUTURA_DO_PROJETO.md
│   ├── FORMULARIO_DE_SESSAO.md
│   ├── MODELO_DE_DADOS.md
│   ├── PADRAO_DE_COMMITS.md
│   ├── PLANO_DE_IMPLEMENTACAO_DASHBOARD.md
│   ├── REGISTRO_DE_ALTERACOES.md
│   ├── UX_DECISIONS.md
│   └── VALIDACAO_CONDICOES.md
├── scripts/
│   ├── AGENTS.md
│   ├── README.md
│   └── analisar_stroop.py
└── tests/
    ├── AGENTS.md
    ├── README.md
    ├── test_csv_unificado.py
    ├── test_fase3_condicoes_tempos.py
    └── test_interface_pre_pratica.py
```

Nota: a pasta existente `condicoes/` e preservada como diretoria de CSVs de condicoes do experimento. Ela cumpre o papel da pasta `conditions/` sem duplicar conteudo.
