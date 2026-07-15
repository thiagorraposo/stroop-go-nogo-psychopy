# Guia do usuario

## O que este projeto faz

O projeto executa um experimento original Stroop Go/No-Go no PsychoPy e apresenta resultados descritivos em um dashboard local. O experimento gera um CSV unificado; o launcher importa esse CSV para um banco SQLite local; o Streamlit le o banco e abre o dashboard.

```text
PsychoPy -> data/*_trials.csv -> SQLite local -> dashboard Streamlit
```

O projeto e educacional e exploratorio. Ele nao e instrumento clinico, nao produz diagnostico e nao oferece comparacao normativa.

## Primeira configuracao

Se voce recebeu o projeto como ZIP, siga primeiro `USO_POR_ZIP_GITHUB.md`. Em resumo:

- Windows: instale Python, execute `setup.bat` e depois `abrir_dashboard.bat`.
- Linux/macOS: instale Python, execute `bash setup.sh` e depois `bash abrir_dashboard.sh`.

O PsychoPy deve ser instalado separadamente do ambiente usado pelo dashboard.

## Executar o experimento

1. Abra o PsychoPy.
2. Entre na interface Builder.
3. Abra `stroop_go_nogo_ptbr.psyexp`.
4. Antes de uma coleta, rode o experimento em modo Pilot e confira instrucoes, pratica, respostas e tela de resultados.
5. Para a execucao desejada, preencha apenas os campos solicitados pelo formulario local.
6. Ao final, confirme que um CSV unificado com sufixo `_trials.csv` foi criado em `data/`.

Nao mova o `.psyexp` sozinho para outra pasta: ele depende dos arquivos versionados em `condicoes/` e da estrutura do projeto.

## Abrir o dashboard

Depois que houver um CSV oficial em `data/`:

- Windows: execute `abrir_dashboard.bat`.
- Linux/macOS: execute `bash abrir_dashboard.sh`.

O launcher usa o CSV `*_trials.csv` modificado mais recentemente, importa a avaliacao para `database/stroop_results.sqlite3` e inicia o Streamlit. Se a avaliacao ja estiver no banco, ela nao e duplicada.

Para escolher outro CSV ou reimportar uma avaliacao, consulte `INSTALACAO_MULTIPLATAFORMA.md`. O CSV de origem nunca e alterado pelo launcher ou pelo dashboard.

## Encerrar

Feche a aba do navegador e encerre o processo do dashboard no terminal com `Ctrl+C`. Os dados importados permanecem no SQLite local para a proxima abertura.

## Cuidado com dados pessoais

Os dados ficam no computador do usuario, dentro de `data/` e `database/`. Essas pastas nao devem ser publicadas nem enviadas junto com contribuicoes ao projeto. Nao coloque dados reais em screenshots, issues publicas, mensagens de suporte ou exemplos de documentacao.

Use `participant_id` como identificador tecnico. `participant_name` e informacao pessoal local e nao deve aparecer em nomes de arquivo, capturas publicas ou logs compartilhados.

## Ajuda rapida

- Python nao abre: reinstale uma versao compativel e confira o `PATH`.
- Setup informa ambiente gerenciado: use o script de setup, sem instalar pacotes globalmente.
- Streamlit ausente: execute o setup novamente e use o launcher do projeto.
- Banco ausente: gere um CSV oficial e abra o dashboard novamente.
- Nenhum CSV encontrado: confirme o sufixo `_trials.csv` dentro de `data/`.
- Cabecalho incompativel: use o CSV oficial sem edicao manual e consulte `CSV_UNIFICADO.md`.

Para instrucoes detalhadas de Download ZIP e solucao de problemas, consulte `USO_POR_ZIP_GITHUB.md`.
