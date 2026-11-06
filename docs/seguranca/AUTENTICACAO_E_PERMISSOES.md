# Autenticacao e permissoes

Nota de 2026-11-06: o alvo WEB muda para login local conforme
[especificação CHG-004](#autenticação-local--especificação-alvo-chg-004).
As seções OIDC/Streamlit anteriores a essa especificação descrevem o código
atual e histórico preservado, sem autorizar sua execução ou retirada.


A aplicacao usa o OIDC nativo do Streamlit com Google Identity. O Google
autentica a conta; o PostgreSQL decide se a identidade pode acessar o sistema e
qual perfil possui. Estado e aceite da etapa permanecem somente no
[backlog canonico](../legado/Projeto%20Stroop%20Test.md).

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

Na WEB, apos validar OIDC, uma identidade ainda nao cadastrada recebe somente
seus proprios `iss` e `sub` numa resposta sem sessao; a tela orienta solicitar
cadastro ao responsavel por canal institucional. Somente a area **Administracao**
WEB cadastra ou altera contas. E-mail auxiliar aparece apenas nesse contexto e
nao e aceito como identidade nem como autorizacao.

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
  [`../dados/DASHBOARD_POSTGRESQL.md`](../dados/DASHBOARD_POSTGRESQL.md).

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
python -m scripts.gerenciar_usuarios bootstrap \
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

Esse comando continua no fluxo legado local. Na WEB, `/equipe` oferece upload
dedicado somente a perfis `importacao`/`administracao` com vinculo ativo ao
projeto escolhido. O navegador envia uma copia com `participant_name` fixo
`NAO_COLETADO` e `initials` vazio; a API rejeita arquivo nao minimizado, limita
10.000 registros, audita UUID/hash/estado e permite reconsulta sem repeticao
automatica. O contrato HTTP e a fonte canonica dos limites e respostas.

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
python -m scripts.gerenciar_usuarios recover-admin \
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
[hardening](../operacao/HARDENING_PRODUCAO.md) e
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

## Autenticação local — especificação alvo CHG-004

Decisão de 2026-11-06: [ADR-006](../arquitetura/ADR-006-autenticacao-local.md).
As seções OIDC acima descrevem o código/legado e seu histórico; a versão alvo
WEB passa a usar conta administrativa local única, implementada e verificada em
M6 (WEB-021/024), com evidências e aceite somente no
[backlog canônico](../Projeto%20Stroop%20Test.md). Permissões por projeto em
[ACESSO_WEB](ACESSO_WEB.md) continuam válidas.

### Credenciais e procedimento administrativo futuro

- Usuário único técnico, não civil, normalizado conforme contrato; senha nunca
  é aparada, convertida de caixa ou truncada. Exigir 15–128 caracteres,
  permitir espaços/Unicode e colagem/gerenciadores; recusar senhas comuns ou
  comprometidas por lista local, sem enviar senha a serviço externo. Sem
  composição arbitrária nem troca periódica sem motivo; trocar por exposição,
  recuperação ou alteração da equipe.
- Persistir exclusivamente hash Argon2id com salt aleatório por senha e
  parâmetros/versionamento codificados. Piso de engenharia: 19 MiB, duas
  iterações, paralelismo 1; medir custo/concorrência no ambiente autorizado e
  aumentar se suportado, sem afrouxar piso para passar testes. Biblioteca e
  lock serão selecionados/revisados na implementação; sem criptografia própria.
  Hash nunca retorna por API, log, exportação ou auditoria. Rehash só após
  verificação bem sucedida, com escrita transacional e sem perder revogação.
- Nenhuma senha padrão, em texto puro no banco, hardcoded, versionada ou em
  argumentos de processo/histórico shell. Bootstrap via comando administrativo
  futuro com entrada oculta em terminal protegido e confirmação, usando acesso
  de operador separado do runtime; só cria a primeira conta quando inexistente,
  sob trava transacional para impedir dois admins iniciais. Sem endpoint público
  de bootstrap nem recriação silenciosa por reinício do container.
- Alteração normal exige sessão válida, CSRF/Origin e senha atual; recuperação
  break-glass usa operador autorizado no host/terminal e acesso administrativo
  protegido, confirmação explícita e evento fechado auditado. Não depender de
  e-mail Google, perguntas pessoais ou credenciais universais. Erros não exibem
  DSN/hash/usuário. O procedimento exato da CLI é entrega WEB-021, sem modificar
  o comando legado por inferência nesta missão.
- Troca/recuperação atualiza hash e versão da credencial e revoga **todas** as
  sessões na mesma transação. Concorrência com login não pode emitir sessão da
  versão anterior após o commit. Recuperação não concede novos vínculos nem
  altera resultados; testar recuperação sem destruir proteção do último admin.

### Antiabuso, erros e observabilidade

Combinar limite por origem confiável e por identificador normalizado em bucket
HMAC, inclusive inexistente, persistente entre processos/reinícios. Defaults
alvo: 20 tentativas/min por origem e cinco falhas/15 min por identificador;
bloqueio temporário da janela, nunca bloqueio permanente acionável anonimamente.
Testar concorrência, expiração e resistência a distribuição por IP sem facilitar
DoS da conta única; limitar também volume/conexões no proxy e concorrência/custo
da verificação. Não confiar em X-Forwarded-For arbitrário. Falha no contador ou
banco nega login com erro sanitizado, sem bypass.

Senha incorreta, usuário inexistente e conta bloqueada retornam o mesmo 401,
corpo e mensagem genérica. Verificar hash fictício de custo equivalente para
usuário inexistente; medir diferenças grosseiras de tempo/status/tamanho e
eliminar atalhos de enumeração. 429 genérico com Retry-After, sem dizer se a
conta existe. Falha operacional 503 sanitizada. Não registrar usuário tentado,
senha, hash, token, cookie, corpo, query ou IP bruto; eventos fechados de sucesso,
falha, limitação, rotação e recuperação usam ID aleatório/principal técnico
quando autenticado, sem atribuição individual. Retenção depende da política
existente e DEC-03, sem prazo novo inventado.

### Sessões e conta compartilhada

Prazos e formato HTTP no [contrato](../desenvolvimento/CONTRATO_API_WEB.md#autenticação-local--contrato-alvo-chg-004).
Revogar sessão corrente no logout e todas por procedimento administrativo,
bloqueio, alteração/recuperação de senha. Validar versão da credencial/estado
em cada acesso; não basta apagar cookie. Nenhum token/senha/resultados em
localStorage, sessionStorage, IndexedDB ou URL. CSRF somente em RAM; senha
limpa após envio/falha/saída, sem telemetria. Não renovar participante por
atividade do profissional nem usar cookie participante em área administrativa.

Conta `administracao` pode gerir projetos/vínculos; resultados e emissão de
convites exigem vínculo explícito. Por padrão inicial, **nenhum projeto** é
concedido pelo bootstrap. Criar vínculo é operação explícita auditada. Modelo
preserva perfis consulta/importacao/administracao para autorização/regressão,
sem implementar múltiplas contas nesta entrega. UI não oferece criar contas
adicionais; backend também recusa essa ampliação na versão alvo.

Credenciais compartilhadas não identificam quem operou. Não há revogação de uma
pessoa isolada: trocar senha e invalidar todas as sessões quando equipe mudar,
usar canal protegido e custodiante definido. Identificador `evaluator_id`
representa a conta emissora, não prova pessoa física. Uso real requer decisão
institucional DEC-03; hash e HTTPS não eliminam R12 nem tornam auditoria
individual. Se inadequado, planejar contas individuais em mudança posterior
antes do uso real. Testes futuros AUTH-L01–L09 em [validação](../VALIDACAO_WEB.md#autenticação-local--plano-de-verificação-chg-004).

Referências técnicas consultadas em 2026-11-06: [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
para Argon2id e [OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
para respostas genéricas e limitação. Defaults locais são especificação de
engenharia a ensaiar, não evidência de proteção implantada.
