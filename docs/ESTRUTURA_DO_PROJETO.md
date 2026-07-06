# Estrutura do projeto

## Arvore final

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
    └── README.md
```

Os nomes dos CSVs de condicoes foram preservados porque sao referenciados diretamente pelo `.psyexp`.

## Finalidade das pastas

- `assets/`: assets proprios do projeto.
- `assets/ui/`: futuros elementos visuais proprios da interface.
- `condicoes/`: CSVs-fonte usados pelos loops do PsychoPy.
- `data/`: saidas locais de execucao e coleta, ignoradas pelo Git.
- `dashboard/`: documentacao e futura aplicacao Streamlit local.
- `docs/`: documentacao metodologica, historico e governanca.
- `scripts/`: scripts auxiliares de analise e manutencao.
- `tests/`: espaco reservado para validacoes estaticas futuras.

## Arquivos-fonte

- `stroop_go_nogo_ptbr.psyexp`
- `condicoes/*.csv`
- `scripts/*.py`
- futuros arquivos-fonte do dashboard
- `README.md`
- `AGENTS.md`
- `docs/*.md`
- READMEs e `AGENTS.md` locais

## Arquivos gerados

- `*_lastrun.py`
- arquivos de dados criados em `data/`
- exports locais em `.csv`, `.tsv`, `.xlsx`, `.psydat` e `.log`
- bancos locais em `.sqlite`, `.sqlite3` e `.db`
- pastas locais `exports/`, `storage/`, `database/` e `backups/`
- caches Python e caches de ferramentas

## Arquivos ignorados pelo Git

O `.gitignore` deve manter fora do versionamento:

- `data/`
- `*_lastrun.py`
- `*.psydat`
- `*.log`
- exports gerais em `*.csv`, `*.tsv` e `*.xlsx`, exceto `condicoes/*.csv`
- bancos locais em `*.sqlite`, `*.sqlite3` e `*.db`
- exports, storage, database e backups locais
- segredos e configuracoes locais do dashboard
- caches, ambientes virtuais, credenciais e temporarios locais

## Fluxo recomendado

1. Editar condicoes ou `.psyexp`.
2. Testar em modo Pilot.
3. Verificar a saida local em `data/`.
4. Validar consistencia.
5. Atualizar documentacao.
6. Criar commit.
