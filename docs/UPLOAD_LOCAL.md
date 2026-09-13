# Upload local de CSV

A area de upload recebe arquivos de outro computador depois que forem copiados
para a maquina local, ou CSVs exportados por planilhas em um contrato de
instrumento registrado. O contrato do Stroop e o adaptador demonstrativo estão
em [MULTIPLOS_INSTRUMENTOS.md](MULTIPLOS_INSTRUMENTOS.md).
Ela importa no PostgreSQL e preserva o dashboard SQLite e seus atalhos.
Estado e aceite ficam no [backlog canonico](Projeto%20Stroop%20Test.md).

## Abrir a area de upload

Usar a `.venv` existente, PostgreSQL local e
[migrations aplicadas](MIGRACOES_POSTGRESQL.md). Configurar `DATABASE_URL` no
ambiente sem imprimir ou versionar credenciais. Na raiz do repositorio:

```bash
.venv/bin/python scripts/upload_local.py --local
```

No Windows, substituir o executavel por `.venv\Scripts\python.exe`.
Abrir `http://127.0.0.1:8765` no navegador da mesma maquina. `--port` permite
escolher outra porta local. O endereco de escuta e fixo em `127.0.0.1`.

1. Selecionar um CSV sintetico UTF-8, com ou sem BOM, de ate 5 MiB.
2. Clicar em **Enviar e importar**.
3. Conferir o resultado: recebido, validado e importado; ou rejeitado.

O botao fica desabilitado durante o envio e a selecao e limpa ao terminar.
Duplicatas por `assessment_id` sao recusadas; esta interface nao oferece
sobrescrita. A importacao usa o [importador PostgreSQL](IMPORTACAO_POSTGRESQL.md)
sem alterar suas formulas ou regras.

O servico exige `--local`, `DATABASE_URL` e ambiente `APP_ENV` igual a `local`,
`development` ou `test` (padrao: `local`). Outros valores, incluindo `production`,
impedem a inicializacao. Encerrar com Ctrl+C. Nao configurar proxy, tunel,
publicacao Docker ou acesso pela rede para este servico.

## Limites de recepcao

Aceita um unico corpo CSV por requisicao, limitado a 5 MiB tanto no navegador
quanto no servidor. Multipart, transferencia chunked, tamanho ausente/invalido,
encoding invalido, byte NUL, extensao diferente de `.csv` e estrutura CSV invalida
sao recusados. A extensao sozinha nao aprova um arquivo.

O servidor admite ate quatro conexoes simultaneas e limita a leitura do socket
a 15 segundos por operacao. Excesso de conexoes e encerrado sem criar threads
adicionais; o navegador orienta conferir o servico antes de repetir o envio.
A serializacao transacional do importador continua protegendo duplicidade.

O upload exige Host e Origin correspondentes ao endereco local e token aleatorio
da pagina. Nao habilita CORS nem serve arquivos de diretorios. Essa protecao
contra envios de outras origens nao substitui autenticacao: processos locais
podem acessar o servico. Nao ha exposicao publica autorizada.

## Retencao e rastreabilidade

Decisao autorizada pelo usuario na sessao do Codex CLI em 2026-09-13:
interface local separada, um CSV UTF-8 de ate 5 MiB, sem substituicao de duplicatas,
exclusao do temporario ao finalizar e registro minimo sem conteudo sensivel.

Cada envio usa diretorio temporario privado do sistema e nome aleatorio `.csv`;
o nome original nunca e usado como caminho. Os bytes sao gravados sem
transformacao, validados e importados. O diretorio e removido em sucesso ou erro,
inclusive se a importacao recusar uma duplicata. Nao se cria copia em `data/`,
`database/`, repositorio ou area de download. Conteudo recebido nunca e executado.

A limpeza automatica cobre encerramento normal do processamento e excecoes.
Uma queda de energia ou encerramento forcado do processo pode impedir essa
limpeza: antes de retomar, o operador deve remover apenas os diretorios temporarios
`stroop-upload-*` daquela execucao, sem abrir seu conteudo e sem apagar diretorios
de um processo ainda ativo. Nao usar esta versao com dados reais.

Os eventos sao JSON no terminal com somente `id` aleatorio, `origin` fixo
`upload local`, `at` UTC e `status`. O servico nao cria arquivo de log nem guarda
historico de eventos em memoria. O terminal pode reter sua propria saida; nao
redirecionar para arquivo versionado. Requisicoes recusadas antes da recepcao do
corpo recebem erro generico sem log de headers ou caminhos.

A origem no PostgreSQL e o caminho temporario com esse ID, para correlacionar
com os eventos; o arquivo nao permanece disponivel. O banco conserva a avaliacao,
metricas e tentativas importadas, conforme seu contrato existente. A retencao de
dados operacionais reais permanece uma decisao externa futura no backlog.

## Falhas e verificacao

A interface mostra mensagens fixas, sem nomes, linhas de CSV, caminhos internos,
credenciais ou traceback. Perda de conexao durante commit pode deixar a
confirmacao incerta; repetir sem sobrescrita preserva o bloqueio de duplicatas.
`--validate-only` do importador valida o CSV, mas nao comprova disponibilidade ou
permissoes do banco.

Com `TEST_DATABASE_URL` apontando exclusivamente para PostgreSQL descartavel
com nome iniciado por `stroop_etapa4_test`:

```bash
.venv/bin/python -m unittest discover -s tests -p test_upload_local.py -v
.venv/bin/python -m unittest discover -s tests -v
docker compose --env-file .env.example config --quiet
git diff --check
```

Os testes nao iniciam servidor: exercitam o processamento e handlers em memoria,
e a integracao usa o banco sintetico disponibilizado externamente. O smoke HTTP
local verifica separadamente abertura da pagina, envio sintetico, duplicidade,
rejeicao e limpeza. Nao ha nova dependencia, migration ou mudanca no experimento.
