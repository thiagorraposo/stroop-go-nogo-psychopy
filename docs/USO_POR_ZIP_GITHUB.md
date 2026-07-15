# Uso por Download ZIP do GitHub

Este guia explica como receber e usar o projeto sem Git, a partir do arquivo ZIP fornecido pelo GitHub.

## Baixar e abrir a pasta

1. Abra a pagina do repositorio no GitHub.
2. Selecione `Code` e depois `Download ZIP`.
3. Descompacte o ZIP em uma pasta local onde voce tenha permissao de escrita.
4. Abra um terminal dentro da pasta descompactada, na mesma pasta em que estao `README.md`, `setup.bat` e `setup.sh`.

Se o repositorio for privado, a pessoa precisa estar autorizada e conectada a uma conta do GitHub com acesso ao repositorio. Sem essa permissao, a pagina e o Download ZIP nao ficam disponiveis.

## Instalar o dashboard

O instalador leve cria uma pasta local `.venv` e instala as dependencias do dashboard nela.

### Windows

1. Instale o Python 3.9 ou mais recente pelo site oficial do Python e habilite a opcao para adicionar o Python ao `PATH`, quando oferecida.
2. Na pasta descompactada, execute `setup.bat`.
3. Depois da configuracao, execute `abrir_dashboard.bat`.

### Linux e macOS

1. Instale o Python 3.9 ou mais recente.
2. No terminal aberto na pasta descompactada, execute `bash setup.sh`.
3. Para abrir o dashboard, execute `bash abrir_dashboard.sh`.

O computador precisa ter acesso a internet durante o setup para baixar Streamlit, pandas e suas dependencias.

## Instalar e usar o PsychoPy

O PsychoPy nao faz parte da `.venv` do dashboard e precisa ser instalado separadamente.

1. Instale o PsychoPy de acordo com as instrucoes do projeto PsychoPy para seu sistema.
2. Abra o PsychoPy e selecione a interface Builder.
3. No Builder, abra `stroop_go_nogo_ptbr.psyexp` a partir da pasta descompactada.
4. Rode primeiro um teste em modo Pilot.
5. Ao concluir uma execucao, confirme a criacao do CSV unificado em `data/`.

## Fluxo normal de uso

1. Rode o experimento no PsychoPy.
2. Conclua a execucao para gerar o CSV unificado `*_trials.csv` em `data/`.
3. Abra o dashboard pelo atalho do seu sistema.
4. O launcher seleciona o CSV mais recente, valida e importa seus dados para `database/stroop_results.sqlite3`.
5. O Streamlit abre o dashboard e mostra resultados descritivos.

Se o CSV mais recente ja tiver sido importado, o launcher preserva a avaliacao existente e continua abrindo o dashboard. Para selecionar manualmente outro arquivo, consulte `INSTALACAO_MULTIPLATAFORMA.md`.

## Privacidade e arquivos locais

- Os CSVs permanecem localmente em `data/`.
- O banco SQLite permanece localmente em `database/`.
- Nao envie as pastas `data/` ou `database/` para repositorios, servicos de compartilhamento ou terceiros sem uma politica de dados apropriada.
- Nao use dados reais, nomes, identificadores, capturas do dashboard ou trechos do CSV em issues publicas, prints de suporte ou exemplos.
- `.venv`, logs, CSVs reais e bancos locais tambem nao devem ser versionados.

Os resultados sao descritivos e exploratorios. O projeto nao fornece diagnostico, equivalencia psicometrica ou avaliacao clinica.

## Solucao de problemas

### Python nao encontrado

Confirme que Python 3.9 ou mais recente esta instalado. No Windows, feche e abra o terminal depois da instalacao e confirme que a opcao de adicionar Python ao `PATH` foi habilitada. Em Linux ou macOS, tente `python3 --version` e execute novamente `bash setup.sh`.

### Erro de ambiente gerenciado

Alguns sistemas bloqueiam instalacoes com `pip` no Python global e exibem mensagens como `externally managed environment`. Nao instale as dependencias globalmente: execute o atalho `setup.bat` ou `bash setup.sh`, que cria e usa a `.venv` local. Se `.venv` tiver sido criada parcialmente, remova somente essa pasta local e repita o setup.

### Streamlit nao instalado

Execute novamente `setup.bat` no Windows ou `bash setup.sh` no Linux/macOS. O dashboard deve ser aberto pelo atalho do projeto, que usa o Python dentro de `.venv`, e nao por um comando Streamlit global.

### Banco SQLite nao encontrado

Rode o experimento ate gerar um CSV em `data/` e abra novamente o dashboard. O launcher cria `database/stroop_results.sqlite3` durante a primeira importacao valida.

### Nenhum CSV encontrado

Confirme que o experimento terminou e que existe um arquivo com sufixo `_trials.csv` dentro de `data/`. Se ainda nao houver coleta e tambem nao existir banco local, o dashboard nao tera dados para abrir.

### CSV com cabecalho incompativel

Use o CSV unificado oficial gerado por esta versao do experimento. Nao use CSV automatico de loop, arquivo editado em planilha ou exportacao de outra versao sem verificar o contrato em `CSV_UNIFICADO.md`. O importador rejeita cabecalhos diferentes para evitar dados inconsistentes.

## Checklist do usuario

- [ ] PsychoPy instalado separadamente.
- [ ] Python 3.9 ou mais recente instalado.
- [ ] Projeto baixado e descompactado.
- [ ] Setup executado sem erro.
- [ ] Experimento aberto no PsychoPy Builder e teste Pilot realizado.
- [ ] CSV unificado gerado em `data/`.
- [ ] Dashboard aberto pelo atalho do sistema.
