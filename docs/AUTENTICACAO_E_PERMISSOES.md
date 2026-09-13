# Autenticacao e permissoes

A aplicacao usa o OIDC nativo do Streamlit com Google Identity. O Google
autentica a conta; o PostgreSQL decide se a identidade pode acessar o sistema e
qual perfil possui. Estado e aceite da etapa permanecem somente no
[backlog canonico](Projeto%20Stroop%20Test.md).

## Identidade e cadastro previo

A chave permanente e a combinacao exata `iss` + `sub` do ID token. Sao aceitos
os emissores Google `https://accounts.google.com` e o valor legado
`accounts.google.com`. O e-mail e auxiliar, pode ser alterado pelo administrador
e nunca participa de login, busca de autorizacao ou unicidade.

Nao existe autocadastro. Uma conta Google autenticada mas ausente de `app_users`
ve somente seus proprios valores `iss` e `sub`, para solicitar cadastro manual,
e nao acessa dados, upload, exportacao ou administracao. A referencia do Google
tambem determina o uso de `sub`, e nao do e-mail, como identificador:
[OpenID Connect do Google](https://developers.google.com/identity/openid-connect/openid-connect).

## Configuracao sem versionar secrets

O Streamlit exige Authlib para OIDC; a dependencia fica declarada em
`dashboard/requirements.txt`. Copie `.streamlit/secrets.toml.example` para
`.streamlit/secrets.toml` e substitua somente na copia ignorada pelo Git:

- `redirect_uri`: URL absoluta terminada em `/oauth2callback`, exatamente igual
  a uma URI autorizada no cliente Google;
- `cookie_secret`: segredo aleatorio forte e exclusivo da aplicacao;
- `client_id` e `client_secret`: credenciais do cliente OIDC Google;
- `server_metadata_url`: discovery oficial do Google, ja indicado no exemplo.

O arquivo real `.streamlit/secrets.toml`, `.env` e credenciais Google ficam
ignorados por Git e pelo contexto da imagem. Nao enviar seus valores por chat,
terminal compartilhado, logs ou commits. A configuracao segue a
[autenticacao oficial do Streamlit](https://docs.streamlit.io/develop/concepts/connections/authentication).

Configure separadamente:

- `AUTH_DATABASE_URL`: conexao usada para usuarios, permissoes e auditoria;
- `DATABASE_URL`: conexao de escrita usada apenas pela importacao PostgreSQL.
- `DASHBOARD_DATABASE_URL`: conexao da conta `dashboard_ro`, somente leitura
  das tabelas de dominio; detalhes da concessao ficam em
  [`DASHBOARD_POSTGRESQL.md`](DASHBOARD_POSTGRESQL.md).

Em Docker, `STREAMLIT_SECRETS_FILE` aponta para o arquivo real no host, montado
como somente leitura em `/app/.streamlit/secrets.toml`. O exemplo versionado
contem somente valores evidentemente ficticios.

## Migration e primeiro administrador

Aplique as migrations antes de abrir a interface:

```bash
python scripts/migrations.py
```

A migration `0002_authentication.sql` cria `app_users` e
`auth_audit_events`. Para descobrir o `sub` da primeira conta sem cadastra-la
automaticamente, tente entrar com Google: a tela recusada mostra somente o
`iss` e o `sub` daquela propria sessao.

Com `AUTH_DATABASE_URL` ja configurada no ambiente, crie o primeiro
administrador:

```bash
python scripts/gerenciar_usuarios.py bootstrap \
  --issuer https://accounts.google.com \
  --subject IDENTIFICADOR_SUB_GOOGLE
```

O bootstrap usa lock exclusivo e so funciona quando `app_users` esta vazia.
Depois dele, cadastros e alteracoes comuns sao feitos pela area **Administracao**.

## Perfis

| Operacao | consulta | importacao | administracao |
|---|:---:|:---:|:---:|
| Visualizar resultados e detalhe | sim | sim | sim |
| Exportar a visao filtrada | sim | sim | sim |
| Enviar e importar CSV | nao | sim | sim |
| Cadastrar, bloquear e alterar perfis | nao | nao | sim |

As areas sem permissao nao aparecem na navegacao. A aplicacao consulta novamente
`app_users` e valida `exp`, bloqueio e perfil antes de cada renderizacao de dados
e imediatamente antes de exportar, importar ou administrar usuarios. Exportacao
usa o callback sob demanda do Streamlit, evitando preparar os bytes antes dessa
segunda verificacao.

A ultima conta administrativa ativa nao pode ser bloqueada nem rebaixada pela
interface. Alteracoes concorrentes sao serializadas por lock no PostgreSQL.

## Upload autenticado

O comando existente continua disponivel:

```bash
python scripts/upload_local.py --local
```

Ele agora abre o dashboard Streamlit em `127.0.0.1:8501`, inicialmente na area
**Importacao**, e exige OIDC, cadastro previo e perfil autorizado. A antiga rota
HTTP propria, que usava apenas token efemero local, nao e mais iniciada nem faz
parte do codigo. Para outra porta, ajuste `--port` e use a mesma porta no
`redirect_uri` autorizado no Google.

O processamento continua limitado a um CSV UTF-8 de ate 5 MiB, sem
sobrescrever duplicatas. O nome recebido nao vira caminho; o arquivo usa nome
aleatorio em diretorio temporario privado e e removido ao finalizar.

## Expiracao, recusas e recuperacao

O Streamlit valida assinatura, emissor, audiencia e fluxo OIDC. Como sua sessao
nao expira automaticamente junto com o `exp` do ID token, a aplicacao compara
`exp` com o horario atual em toda autorizacao e recusa tokens vencidos.

Tentativas de credencial, recuperacao de senha e controles adicionais da conta
pertencem ao Google Identity. Depois de uma autenticacao Google valida, cinco
recusas locais da mesma identidade em 15 minutos limitam temporariamente novas
operacoes. Isso nao substitui o hardening de requisicoes previsto para etapa
posterior.

Bloqueio local e revertido por outro administrador. Se todas as contas
administrativas ficarem operacionalmente indisponiveis, a recuperacao de
emergencia exige credencial de banco, identidade ja cadastrada e confirmacao
explicita:

```bash
python scripts/gerenciar_usuarios.py recover-admin \
  --issuer https://accounts.google.com \
  --subject IDENTIFICADOR_SUB_GOOGLE \
  --confirm-break-glass
```

Esse comando nunca cria usuario e deixa evento de auditoria. Recuperar senha ou
conta Google continua sendo responsabilidade do provedor.

## Auditoria e limites

`auth_audit_events` guarda somente horario, `iss`, `sub`, acao fixa, resultado e
`request_id` aleatorio. Nao possui e-mail, nome, CSV, metrica, identificador de
participante, caminho, credencial, token ou texto livre.

O prazo provisorio da auditoria OIDC e 180 dias. Resultados de importacao ficam
em tabela separada, sem e-mail, nome de arquivo ou identidade: somente hash
SHA-256 do conteudo, status, codigo fechado de erro, horario e identificador
aleatorio por 30 dias. Prazos, expurgo e logging de producao estao em
[hardening](HARDENING_PRODUCAO.md) e
[tratamento de dados](TRATAMENTO_DE_DADOS.md).

O logout remove a sessao atual do Streamlit. Uma aba ja aberta pode continuar
mostrando o que foi renderizado ate sua proxima interacao; nessa interacao, toda
operacao protegida consulta novamente bloqueio e expiracao. Secrets reais e um
login Google real nao fazem parte dos testes automatizados nem devem ser
versionados. Exposicao publica ainda nao foi realizada. O proxy e HTTPS foram
preparados com TLS fail-closed; dominio, certificado real e ativacao pertencem
a Etapa 11.

## Validacao sintetica

Com `TEST_DATABASE_URL` apontando exclusivamente para banco descartavel com nome
iniciado por `stroop_etapa4_test`:

```bash
.venv/bin/python -m unittest discover -s tests -p test_authentication.py -v
.venv/bin/python -m unittest discover -s tests -v
docker compose --env-file .env.example config --quiet
git diff --check
```
