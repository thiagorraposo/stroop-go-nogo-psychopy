# Stroop Go/No-Go PsychoPy

Experimento PsychoPy Builder de Stroop Go/No-Go em portugues brasileiro.

Regra da tarefa: pressionar `Espaco` apenas quando a palavra e a cor da tinta forem congruentes. Nao responder quando forem incongruentes.

Este projeto e mantido para fins educacionais e de pesquisa exploratoria. Ele nao e instrumento clinico validado, nao produz diagnostico e nao deve ser usado para classificacao clinica ou normativa.

## Arquivos

- `stroop_go_nogo_ptbr.psyexp`: experimento para abrir no PsychoPy Builder.
- `condicoes/pratica_stroop_go_nogo_ptbr.csv`: tentativas do bloco de pratica.
- `condicoes/bloco_principal_stroop_go_nogo_ptbr.csv`: tentativas do bloco principal.
- `condicoes/contagem_regressiva.csv`: telas breves de preparacao antes dos blocos.
- `data/`: pasta onde os CSVs por tentativa sao salvos pelo PsychoPy.
- `scripts/analisar_stroop.py`: script simples para analisar os CSVs gerados.
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
3. Preencha `participant` e `session` quando solicitado.
4. Confirme se a pratica mostra feedback e se o bloco principal nao mostra feedback.
5. Use Pilot para verificacoes antes de qualquer coleta real.

## Como executar em modo Run

1. Abra o experimento no Builder.
2. Use o modo `Run` para coleta.
3. Preencha `participant` e `session`.
4. Os arquivos CSV serao gravados em `data/`.
5. Nao versione arquivos gerados em `data/`.

## Condicoes

As palavras usadas sao `VERMELHO`, `AZUL`, `VERDE` e `AMARELO`.

- `congruente`: palavra e cor correspondem; resposta correta e pressionar `Espaco`.
- `incongruente`: palavra e cor nao correspondem; resposta correta e nao pressionar nada.

Cada tentativa tem:

- fixacao: cerca de 400 ms;
- intervalo vazio: cerca de 100 ms;
- estimulo/resposta: 1500 ms;
- intervalo entre tentativas: cerca de 300 ms.

## Dados

Os CSVs locais ficam em `data/`. Essa pasta e ignorada pelo Git para proteger dados de teste, execucao e participantes.

As colunas principais registradas por tentativa sao:

`participant`, `session`, `trial_number`, `word`, `ink_color`, `condition`, `correct_response`, `key_pressed`, `reaction_time`, `correct`, `error_type`, `block`.

`ink_color` usa nomes de cor simples (`red`, `blue`, `green`, `yellow`) para manter os CSVs compativeis com pandas, R e SPSS sem campos RGB com virgulas internas.

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
python3 scripts/analisar_stroop.py
```

O script procura arquivos `.csv` em `data/`, calcula acuracia geral, por condicao e por bloco, e compara a mediana do tempo de reacao das respostas corretas entre condicoes congruentes e incongruentes.

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
├── docs/
│   ├── AGENTS.md
│   ├── DECISOES_DO_EXPERIMENTO.md
│   ├── ESTRUTURA_DO_PROJETO.md
│   ├── PADRAO_DE_COMMITS.md
│   ├── REGISTRO_DE_ALTERACOES.md
│   └── UX_DECISIONS.md
├── scripts/
│   ├── AGENTS.md
│   ├── README.md
│   └── analisar_stroop.py
└── tests/
    ├── AGENTS.md
    └── README.md
```

Nota: a pasta existente `condicoes/` e preservada como diretoria de CSVs de condicoes do experimento. Ela cumpre o papel da pasta `conditions/` sem duplicar conteudo.
