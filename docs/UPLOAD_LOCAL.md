# Upload autenticado de CSV

A area recebe CSVs de um instrumento registrado e importa no PostgreSQL. Desde
a Etapa 8, ela faz parte do dashboard protegido por Google OIDC e exige usuario
previamente cadastrado com perfil `importacao` ou `administracao`. O contrato do
Stroop e o adaptador demonstrativo estao em
[MULTIPLOS_INSTRUMENTOS.md](MULTIPLOS_INSTRUMENTOS.md); identidade, perfis e
bootstrap estao em [AUTENTICACAO_E_PERMISSOES.md](AUTENTICACAO_E_PERMISSOES.md).
O dashboard ainda consulta o SQLite ate a etapa prevista para troca do backend.
Estado e aceite ficam no [backlog canonico](Projeto%20Stroop%20Test.md).

## Abrir a area de upload

Usar a `.venv` existente, PostgreSQL local, OIDC configurado e
[migrations aplicadas](MIGRACOES_POSTGRESQL.md). Configurar `DATABASE_URL` no
ambiente, `AUTH_DATABASE_URL` separadamente e o arquivo local de secrets sem
imprimir ou versionar credenciais. Na raiz do repositorio:

```bash
.venv/bin/python scripts/upload_local.py --local
```

No Windows, substituir o executavel por `.venv\Scripts\python.exe`.
Abrir `http://127.0.0.1:8501` no navegador da mesma maquina. `--port` permite
escolher outra porta local, que tambem deve constar no `redirect_uri` do cliente
Google. O endereco de escuta desse comando permanece fixo em `127.0.0.1`.

1. Selecionar um CSV sintetico UTF-8, com ou sem BOM, de ate 5 MiB.
2. Entrar com uma conta Google previamente cadastrada e abrir **Importacao**.
3. Clicar em **Validar e importar**.
4. Conferir o resultado importado ou rejeitado.

O botao fica desabilitado sem arquivo.
Duplicatas por `assessment_id` sao recusadas; esta interface nao oferece
sobrescrita. A importacao usa o [importador PostgreSQL](IMPORTACAO_POSTGRESQL.md)
sem alterar suas formulas ou regras.

O comando exige `--local`, `DATABASE_URL`, `AUTH_DATABASE_URL` e ambiente
`APP_ENV` igual a `local`, `development` ou `test` (padrao: `local`). Outros
valores, incluindo `production`, impedem a inicializacao. Encerrar com Ctrl+C.
Publicacao, proxy e HTTPS pertencem a etapas posteriores.

## Limites de recepcao

Aceita um unico CSV por operacao. Tamanho vazio ou superior a 5 MiB, encoding
invalido, byte NUL, extensao diferente de `.csv` e estrutura CSV invalida sao
recusados. A extensao sozinha nao aprova um arquivo. O importador preserva a
serializacao transacional e a recusa de duplicidade.

A antiga rota HTTP propria foi removida para eliminar um caminho de importacao
sem OIDC. O Streamlit revalida expiracao, cadastro, bloqueio e perfil antes de
encaminhar bytes ao processador.

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

O fluxo autenticado registra no PostgreSQL somente identidade OIDC, acao fixa,
resultado, horario e `request_id` aleatorio. Nao registra nome do arquivo,
conteudo, metadados clinicos, caminhos, e-mail ou credenciais.

Em tabela operacional separada, o resultado final guarda somente SHA-256 do
conteudo, status, codigo fechado de erro, horario e UUID aleatorio. Assim, uma
rejeicao nao persiste arquivo, nome, identidade ou texto livre. O prazo
provisorio desse registro e 30 dias.

A origem da avaliacao importada e o caminho temporario aleatorio com esse ID;
o arquivo nao permanece disponivel. O banco conserva a avaliacao,
metricas e tentativas importadas, conforme seu contrato existente. A retencao de
dados e provisoria e esta em [tratamento de dados](TRATAMENTO_DE_DADOS.md).

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

Os testes nao iniciam login real nem usam secrets: exercitam o processamento,
o launcher autenticado e a integracao em banco sintetico. Autenticacao,
autorizacao negativa e auditoria sao cobertas por `test_authentication.py`.
Nenhuma mudanca foi feita no experimento ou nas formulas.
