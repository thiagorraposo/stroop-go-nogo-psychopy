# Instalacao multiplataforma

Este fluxo configura o dashboard local em Windows, Linux e macOS. Ele nao instala o PsychoPy, que deve ser instalado separadamente para executar ou editar `stroop_go_nogo_ptbr.psyexp`.

## Requisitos

- Python 3.9 ou mais recente disponivel no sistema;
- acesso ao indice de pacotes Python durante a configuracao;
- um CSV oficial `*_trials.csv` em `data/`, ou um banco local ja importado.

## Windows

Na raiz do projeto, execute `setup.bat`. O atalho chama `scripts/setup_env.py`, cria `.venv` e instala `dashboard/requirements.txt`. Depois execute `abrir_dashboard.bat`.

## Linux e macOS

Na raiz do projeto, execute:

```bash
bash setup.sh
bash abrir_dashboard.sh
```

Nao e necessario instalar atalhos `.desktop` nem usar comandos exclusivos de Linux.

## Uso manual

Os scripts tambem podem ser chamados diretamente com o Python instalado no sistema:

```text
python scripts/setup_env.py
python scripts/run_dashboard.py
```

Em sistemas onde o comando do interpretador e `python3`, substitua `python` por `python3`.

Por padrao, o launcher seleciona o CSV com modificacao mais recente em `data/*_trials.csv`, importa-o para `database/stroop_results.sqlite3` e inicia o Streamlit. Uma avaliacao ja importada e mantida sem duplicacao e o dashboard abre normalmente.

Opcoes:

```text
python scripts/run_dashboard.py --csv data/ARQUIVO_trials.csv
python scripts/run_dashboard.py --force
python scripts/run_dashboard.py --csv data/ARQUIVO_trials.csv --force
```

`--force` substitui no SQLite somente a avaliacao identificada pelo `assessment_id` do CSV selecionado. O CSV original nunca e modificado.

## Dados e limites

- CSVs reais ficam somente em `data/`.
- O SQLite local fica em `database/`.
- `data/` e `database/` nao devem ser versionadas, salvo o README permitido em `data/`.
- O dashboard usa Python e Streamlit e le o SQLite em modo somente leitura.
- Os resultados sao descritivos e exploratorios; nao representam avaliacao clinica ou diagnostico.

O fluxo foi projetado e validado estaticamente para os tres sistemas. A execucao deve ser confirmada no sistema operacional de destino antes do uso em coleta.
