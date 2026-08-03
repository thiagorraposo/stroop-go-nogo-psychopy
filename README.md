# Stroop Go/No-Go PsychoPy

Experimento PsychoPy Builder de Stroop Go/No-Go em portugues brasileiro.

Regra da tarefa: pressionar `Espaco` apenas quando a palavra e a cor da tinta forem congruentes. Nao responder quando forem incongruentes.

Este projeto e mantido para fins educacionais e de pesquisa exploratoria. Ele nao e instrumento clinico validado, nao produz diagnostico e nao deve ser usado para classificacao clinica ou normativa.

## Uso em qualquer sistema

O PsychoPy precisa ser instalado separadamente para executar ou editar o experimento. O fluxo abaixo configura apenas o dashboard local, baseado em Python, Streamlit e SQLite.

Para usar sem Git, abra o repositorio no GitHub e escolha `Code` -> `Download ZIP`, descompacte o arquivo e abra um terminal dentro da pasta. Em repositorios privados, e necessario estar conectado a uma conta autorizada. Consulte o passo a passo em [`docs/USO_POR_ZIP_GITHUB.md`](docs/USO_POR_ZIP_GITHUB.md) e o fluxo cotidiano em [`docs/GUIA_DO_USUARIO.md`](docs/GUIA_DO_USUARIO.md).

No Windows:

1. Instale o Python 3.9 ou mais recente.
2. Execute `setup.bat`.
3. Execute `abrir_dashboard.bat`.

No Linux ou macOS:

1. Instale o Python 3.9 ou mais recente.
2. Execute `bash setup.sh`.
3. Execute `bash abrir_dashboard.sh`.

Para verificar o ambiente sem instalar dependencias, modificar dados, criar banco ou
abrir o dashboard, execute a partir da raiz do projeto:

```text
Windows:     py scripts\doctor.py
Linux/macOS: python3 scripts/doctor.py
```

O diagnostico informa `OK`, `ERRO` ou `AVISO` para os componentes necessarios e
mostra instrucoes de correcao especificas para cada plataforma.

Uso manual, a partir da raiz do projeto:

```text
python scripts/setup_env.py
python scripts/run_dashboard.py
```

O launcher importa o arquivo mais recente em `data/*_trials.csv` e abre o dashboard. Use `--csv CAMINHO` para selecionar outro CSV e `--force` para reimportar uma avaliacao. Os CSVs e o banco permanecem locais em `data/` e `database/`; `database/` nao deve ser enviada ao Git. Os resultados apresentados sao descritivos, nao clinicos.

## Arquivos

- `stroop_go_nogo_ptbr.psyexp`: experimento para abrir no PsychoPy Builder.
- `condicoes/pratica_stroop_go_nogo_ptbr.csv`: tentativas do bloco de pratica.
- `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv`: tentativas do bloco principal.
- `condicoes/contagem_regressiva.csv`: telas breves de preparacao antes dos blocos.
- `data/`: pasta onde o CSV unificado por execucao e salvo pelo PsychoPy.
- `scripts/analisar_stroop.py`: script para validar e analisar um CSV unificado.
- `scripts/importar_csv_sqlite.py`: script para validar e importar CSV unificado para SQLite local.
- `scripts/db_schema.sql`: schema SQLite local da camada de importacao.
- `dashboard/app.py`: dashboard Streamlit local para consulta descritiva do SQLite.
- `dashboard/requirements.txt`: dependencias do dashboard local.
- `docs/UX_DECISIONS.md`: notas sobre as decisoes de experiencia de usuario.
- `docs/USO_POR_ZIP_GITHUB.md`: instalacao e uso a partir do Download ZIP do GitHub.
- `docs/GUIA_DO_USUARIO.md`: fluxo cotidiano do experimento ao dashboard.
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

Na versao `0.2.2`, cada tentativa da pratica tem:

- fixacao: 300 ms;
- estimulo/resposta: 2000 ms;
- intervalo vazio entre tentativas: 500 ms;
- feedback automatico: 500 ms apos cada tentativa.

Cada tentativa do bloco principal tem:

- fixacao: 300 ms;
- estimulo/resposta: 2500 ms;
- intervalo vazio entre tentativas: 950 ms.

A pratica tem 4 tentativas, com 2 Go/congruentes e 2 No-Go/incongruentes. O bloco principal tem 16 tentativas, com 8 Go/congruentes e 8 No-Go/incongruentes, totalizando cerca de 60 segundos exclusivamente no bloco principal. O fluxo completo e maior por incluir formulario, instrucoes, contagens, pratica e feedbacks.

Durante a pratica e o bloco principal ha um HUD discreto com precisao acumulada. O cronometro visual inicia apenas no comeco da primeira tentativa principal e segue ate o fim do intervalo da ultima tentativa principal. O bloco principal nao exibe texto instrucional durante as tentativas. A precisao ao vivo pode influenciar o comportamento do participante e e uma decisao de UX, nao uma configuracao metodologicamente neutra.

A interface usa tema escuro original com fundo `#0B1020`; os estimulos aparecem sobre um cartao claro para preservar contraste, sem adicionar branco como cor de estimulo.

## Dados

Os CSVs locais ficam em `data/`. Essa pasta e ignorada pelo Git para proteger dados de teste, execucao e participantes.

Cada execucao concluida normalmente gera um unico CSV oficial por tentativa no formato `data/stroop_go_nogo_ptbr_YYYY-MM-DD_HHhMMmSSs_trials.csv`. Nenhum metadado do participante entra no nome do arquivo. Nas execucoes atuais, apenas tentativas do bloco principal sao exportadas no CSV oficial, com `block = main`.

As colunas principais registradas por tentativa sao:

`project`, `participant_id`, `participant_name`, `initials`, `visit`, `evaluator`, `assessment_id`, `assessment_date`, `started_at`, `test_code`, `test_version`, `block`, `trial_number`, `word`, `ink_color`, `condition`, `correct_response`, `key_pressed`, `reaction_time`, `correct`, `error_type`.

`ink_color` usa nomes de cor simples (`green`, `yellow`, `pink`, `black`, `red`, `orange`, `brown`, `purple`, `blue`, `gray`) para manter o CSV unificado compativel com pandas, R e SPSS sem campos RGB com virgulas internas.

Nas execucoes atuais, o CSV oficial exporta apenas o bloco principal. A coluna `block` permanece no contrato e deve usar `main`; a pratica e executada no experimento, mas nao gera linhas no CSV oficial.

`error_type` usa:

- `hit`: pressionou `Espaco` corretamente em tentativa congruente;
- `omission`: deixou de responder em tentativa congruente;
- `correct_rejection`: nao respondeu corretamente em tentativa incongruente;
- `commission`: pressionou `Espaco` em tentativa incongruente.

## Analise

Depois de coletar dados, execute:

```bash
python3 scripts/analisar_stroop.py data/PARTICIPANT_ID.csv
```

O script valida o CSV unificado, calcula metricas descritivas do bloco principal e nao modifica o arquivo original. O contrato completo esta em `docs/CSV_UNIFICADO.md`.

## Importacao SQLite

Para importar um CSV validado para SQLite local:

```bash
python3 scripts/importar_csv_sqlite.py data/PARTICIPANT_ID.csv
```

Banco padrao:

```text
database/stroop_results.sqlite3
```

Use `--db` para escolher outro caminho e `--force` para reimportar um `assessment_id` ja existente. A pasta `database/` e local e ignorada pelo Git. A documentacao completa esta em `docs/IMPORTACAO_SQLITE.md`.

## Camada de dados e dashboard

A arquitetura prevista e: PsychoPy -> CSV bruto unificado -> script de importacao -> SQLite local -> dashboard Streamlit local.

A Fase 1 dessa camada, com formulario local de sessao, foi implementada. A Fase 2, com CSV unificado por execucao e analisador tecnico, foi implementada. A Fase 7, com importacao para SQLite local, foi implementada e segue pendente de validacao manual com CSV real em Pilot. A Fase 8, com dashboard Streamlit local, foi implementada tecnicamente e segue pendente de validacao manual com banco real importado. O modelo de dados, regras de privacidade e plano incremental estao documentados em `docs/DADOS_E_DASHBOARD.md`, `docs/MODELO_DE_DADOS.md`, `docs/CSV_UNIFICADO.md`, `docs/IMPORTACAO_SQLITE.md` e `docs/PLANO_DE_IMPLEMENTACAO_DASHBOARD.md`.

Para rodar o dashboard:

```bash
python3 -m pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

Banco padrao esperado:

```text
database/stroop_results.sqlite3
```

O dashboard le apenas SQLite, abre o banco em modo somente leitura e exibe resultados descritivos sem diagnostico ou interpretacao clinica.

## Metadados da sessao

Antes da primeira tela, o experimento exibe um formulario local com `project`, `participant_id`, `participant_name`, `initials`, `visit` e `evaluator`. A data, hora, `assessment_id`, `test_code` e `test_version` sao gerados automaticamente.

Use `participant_id` como identificador tecnico principal. `participant_name` e dado pessoal local e nao deve aparecer em nome de arquivo, screenshots, exemplos publicos, logs ou commits. Nao informe nome completo, CPF, e-mail, telefone, endereco, idade ou sexo. As regras completas estao em `docs/FORMULARIO_DE_SESSAO.md`.

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
│   ├── README.md
│   ├── app.py
│   └── requirements.txt
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
    ├── test_dashboard.py
    ├── test_fase3_condicoes_tempos.py
    └── test_interface_pre_pratica.py
```

Nota: a pasta existente `condicoes/` e preservada como diretoria de CSVs de condicoes do experimento. Ela cumpre o papel da pasta `conditions/` sem duplicar conteudo.
