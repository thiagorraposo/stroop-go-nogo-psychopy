# Estrutura do projeto

## Arvore principal

```text
.
├── AGENTS.md
├── README.md
├── .gitignore
├── requirements.txt
├── setup.bat
├── setup.sh
├── abrir_dashboard.bat
├── abrir_dashboard.sh
├── stroop_go_nogo_ptbr.psyexp
├── assets/
│   ├── README.md
│   └── ui/
├── condicoes/
│   ├── AGENTS.md
│   ├── README.md
│   └── *.csv
├── data/
│   └── README.md
├── dashboard/
│   ├── AGENTS.md
│   ├── README.md
│   ├── app.py
│   └── requirements.txt
├── docs/
│   ├── AGENTS.md
│   ├── GUIA_DO_USUARIO.md
│   ├── INSTALACAO_MULTIPLATAFORMA.md
│   ├── USO_POR_ZIP_GITHUB.md
│   └── demais documentos metodologicos e de governanca
├── scripts/
│   ├── AGENTS.md
│   ├── README.md
│   ├── analisar_stroop.py
│   ├── db_schema.sql
│   ├── importar_csv_sqlite.py
│   ├── run_dashboard.py
│   └── setup_env.py
└── tests/
    ├── AGENTS.md
    ├── README.md
    └── test_*.py
```

Os nomes dos CSVs de condicoes sao preservados porque eles sao referenciados diretamente pelo `.psyexp`.

## Finalidade das pastas

- `assets/`: assets proprios do projeto.
- `assets/ui/`: elementos visuais proprios da interface.
- `condicoes/`: CSVs-fonte usados pelos loops do PsychoPy.
- `data/`: saidas locais de execucao e coleta, ignoradas pelo Git.
- `dashboard/`: aplicacao Streamlit local e suas dependencias.
- `docs/`: documentacao metodologica, historico, guias e governanca.
- `scripts/`: analise, importacao, configuracao e inicializacao local.
- `tests/`: validacoes estaticas e testes automatizados sem dados reais.

Os atalhos `setup.bat`, `setup.sh`, `abrir_dashboard.bat` e `abrir_dashboard.sh` ficam na raiz para facilitar o uso por outra pessoa, inclusive depois de `Code` -> `Download ZIP` no GitHub. A logica multiplataforma correspondente fica nos scripts Python em `scripts/`.

## Arquivos-fonte

- `stroop_go_nogo_ptbr.psyexp`
- `condicoes/*.csv`
- `scripts/*.py` e `scripts/db_schema.sql`
- `dashboard/app.py` e `dashboard/requirements.txt`
- atalhos e requisitos multiplataforma da raiz
- `README.md`, `AGENTS.md`, `docs/*.md` e documentos locais

## Arquivos gerados

- `*_lastrun.py`
- arquivos de dados criados em `data/`
- exports locais em `.csv`, `.tsv`, `.xlsx`, `.psydat` e `.log`
- bancos locais em `.sqlite`, `.sqlite3` e `.db`
- pastas locais `exports/`, `storage/`, `database/` e `backups/`
- `.venv`, caches Python e caches de ferramentas

## Arquivos ignorados pelo Git

O `.gitignore` mantem fora do versionamento:

- conteudo de `data/`, exceto `data/README.md`;
- `*_lastrun.py`, `*.psydat` e `*.log`;
- CSVs e exports gerais, exceto os CSVs-fonte em `condicoes/`;
- bancos locais em `.sqlite`, `.sqlite3` e `.db`;
- `exports/`, `storage/`, `database/` e `backups/`;
- `.venv`, caches, credenciais, segredos e temporarios locais.

## Fluxo para uso por ZIP

1. Baixar pelo GitHub em `Code` -> `Download ZIP` e descompactar.
2. Instalar Python e executar o atalho de setup do sistema.
3. Instalar o PsychoPy separadamente e abrir o `.psyexp` no Builder.
4. Testar em modo Pilot e confirmar a saida local em `data/`.
5. Executar o atalho do dashboard para importar o CSV mais recente e abrir o Streamlit.

Consulte `USO_POR_ZIP_GITHUB.md` para o procedimento completo e as regras de privacidade.
