# API HTTP

Base FastAPI com autenticacao profissional e fluxo de convites/sessoes/resultados WEB. O estado
de cada etapa fica no [roadmap](../docs/ROADMAP_WEB.md); o
[contrato HTTP](../docs/desenvolvimento/CONTRATO_API_WEB.md) define formatos e limites.

## Organizacao

- `main.py`, `transport.py`, `models.py` e `errors.py` compoem a fronteira HTTP.
- `config.py` valida configuracao sem ler arquivos `.env` operacionais.
- `health.py` implementa verificacoes live/readiness somente leitura.
- `auth.py` expoe login, callback, identidade propria e logout; verifica Origin,
  CSRF e revalida a autorizacao local para cada operacao protegida.
- `sessions.py` expoe projetos/vinculos administrativos, convites profissionais
  e resgate, bootstrap, inicio e abortamento do participante. O backend guarda
  somente hashes de credenciais; sessoes ativas nao viram avaliacoes.
- `results.py` expoe conclusao completa com schema fechado, autorizacao antes
  da validacao, recalculo pelo dominio e recibo idempotente. O mesmo recibo
  pode ser recuperado pelo bootstrap de sessao concluida antes do prazo.
- `google_oidc.py` concentra descoberta do provedor, montagem do pedido de
  autorizacao e verificacao criptografica do token.
- Regras de identidade ficam em `stroop/domain` e `stroop/application`; SQL e
  sessoes ficam em `stroop/persistence`. `dashboard/auth.py` mantem a fachada
  usada pelo Streamlit.
- Alteracoes do schema PostgreSQL ficam em `scripts/migrations/`, preservando o
  local publico e a aplicacao explicita pelo utilitario existente.

O roadmap continua sendo a fonte de aceite; a presenca das rotas nao substitui
as evidencias de teste e integracao registradas no roadmap. Projetos ficam em
modo sintetico; coleta real permanece desabilitada enquanto nao houver a
configuracao explicita exigida por `docs/seguranca/ACESSO_WEB.md`.

Na raiz do checkout, com Python 3.12 e a `.venv` existente:

```bash
.venv/bin/python -m pip install --index-url https://pypi.org/simple -r api/requirements.lock
```

`requirements.txt` declara dependencias diretas e `requirements.lock` fixa a
resolucao completa, incluindo `httpx` para TestClient. Versoes compartilhadas
seguem `dashboard/requirements.lock`. Atualize ambos e valide a suite ao renovar.

Configure no ambiente da sessao `API_DATABASE_URL` (URI PostgreSQL com host e
banco), `API_PUBLIC_ORIGIN` (origem HTTPS sem caminho, credenciais ou query) e
`APP_ENV` (`development`, `test` ou `production`), `OIDC_CLIENT_ID`,
`OIDC_CLIENT_SECRET` e `API_SESSION_SECRET` (ao menos 32 caracteres aleatorios).
Todos sao obrigatorios.
Nenhum `.env` e lido automaticamente. Ausencia ou valor invalido impede a
factory de iniciar com uma mensagem fixa, sem imprimir a configuracao.
`API_LOGIN_RATE_LIMIT` (padrao 20) e
`API_LOGIN_RATE_WINDOW_SECONDS` (padrao 60) configuram a janela por endereco
remoto. A API armazena apenas HMAC do endereco e remove janelas expiradas.
Headers de IP encaminhado nao sao confiados.
`API_REDEEM_RATE_LIMIT` (padrao 10) e
`API_REDEEM_RATE_WINDOW_SECONDS` (padrao 60) aplicam o mesmo principio ao
resgate publico de convites.
`API_PROFESSIONAL_READ_RATE_LIMIT` (120),
`API_PROFESSIONAL_WRITE_RATE_LIMIT` (60) e
`API_PROFESSIONAL_RATE_WINDOW_SECONDS` (60) limitam leituras e escritas por
credencial profissional; somente HMAC da credencial e armazenado.
`API_PARTICIPANT_READ_RATE_LIMIT` (120), `API_PARTICIPANT_WRITE_RATE_LIMIT` (60)
e `API_PARTICIPANT_RATE_WINDOW_SECONDS` (60) aplicam limites independentes ao
participante, tambem por HMAC de credencial, sem misturar os contadores profissionais.

Exemplo exclusivamente sintetico de preparacao local:

```bash
export API_DATABASE_URL='postgresql://synthetic:synthetic-local-only@127.0.0.1:55432/stroop_etapa4_test_web'
export API_PUBLIC_ORIGIN='https://localhost:8000'
export APP_ENV='test'
export OIDC_CLIENT_ID='synthetic-client-id'
export OIDC_CLIENT_SECRET='synthetic-client-secret-never-use'
export API_SESSION_SECRET='synthetic-session-secret-never-use-0000000000'
.venv/bin/python -m uvicorn api.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log --log-level warning --no-proxy-headers
```

O comando expoe HTTP local para verificacao; configure TLS no proxy para o uso
HTTPS pelo navegador. Preserve o Host da origem configurada ao encaminhar a
requisicao. Nao confiar em headers de proxy sem configuracao da origem confiavel.
Access log fica desabilitado para nao registrar caminhos ou queries sensiveis.

- `GET /health/live` responde `200 {"status":"ok"}` sem acessar banco.
- `GET /health/ready` responde `200 {"status":"ready"}` quando o banco aceita
  consulta e o conjunto de migrations aplicadas coincide com os arquivos em
  `scripts/migrations`. Usa conexao read-only e timeout de tres segundos; nao
  escreve, cria schema nem aplica migrations. Indisponibilidade responde 503.
- Respostas incluem `Cache-Control: no-store` e UUID novo em `X-Request-ID`.
  Erros incluem o mesmo UUID, codigo e mensagem fixos. Headers de ID enviados
  pelo cliente nao sao reutilizados. Docs interativas e redirects automaticos
  de barra final ficam desativados.
- O transporte conta bytes recebidos, inclusive chunks sem Content-Length,
  limitados a 65536. Aceita somente JSON UTF-8 e encoding ausente/identity;
  nao descomprime corpos. Tipo/encoding incorreto e 415, excesso e 413,
  sintaxe/duplicatas/NaN/infinito sao 400 e falha de schema e 422.

Para integrar routers posteriores, use `app.include_router(..., prefix="/api/v1")`
na factory. `app.state.config` contem configuracao validada. Corpos derivam de
`api.models.RequestModel`; falhas de negocio usam `api.errors.APIError` com
codigo fixo do contrato. Routers validam queries declaradas e regras de acesso.
O middleware captura falhas inesperadas sem propagar texto ou traceback ao
servidor; logs proprios contem apenas categoria fixa e request_id.

Validacoes:

```bash
.venv/bin/python -m unittest tests.test_api_base tests.test_web_auth tests.test_web_sessions tests.test_web_results tests.test_web_assessments tests.test_web_export -v
.venv/bin/python -m compileall -q api
.venv/bin/python -m pip check
git diff --check
```

Integracao real usa `TEST_DATABASE_URL` de banco **descartavel** com nome iniciado
por `stroop_etapa4_test`; a suite integral existente recria schemas e deve ser
executada sequencialmente. Os testes de readiness desta camada consultam o banco
com migrations previamente aplicadas e nao iniciam servicos.

Referencias primarias: [TestClient](https://fastapi.tiangolo.com/tutorial/testing/),
[configuracao por ambiente](https://fastapi.tiangolo.com/advanced/settings/) e
[ADR-001](../docs/arquitetura/ADR-001-evolucao-web.md).

## Consulta profissional

`API_READ_DATABASE_URL` deve apontar para usuario PostgreSQL dedicado com
SELECT somente nas colunas de `REQUIRED_COLUMNS` em
[`web_assessments.py`](../stroop/persistence/web_assessments.py), mais USAGE
no schema e CONNECT no banco. Esse papel nao precisa ler `participant_name`,
`initials` ou `source_file` e nao deve possuir privilegios de escrita. Nao ha fallback para `API_DATABASE_URL`;
ausencia da credencial de leitura produz indisponibilidade nas consultas.
Autenticacao e limites continuam na conexao de operacoes da API.

Coletas legadas somente serao associadas por mapa operacional explicito
`web_legacy_project_links`, inicialmente vazio. Criar projeto com codigo igual
a um rotulo legado nao concede acesso; veja [ADR-003](../docs/arquitetura/ADR-003-escopo-legado-web.md).
Rotas registradas: listagem paginada, detalhe e `/export` sob
`/api/v1/projects/{project_id}/assessments`. Exigem sessao profissional ativa e
vinculo inclusive para administracao. Leitura consulta escopo na mesma transacao
somente leitura; exportacao reautoriza a cada download. Filtros opcionais:
`participant_id` e `visit`; cursor assinado depende de usuario/projeto/filtros.

Metricas Stroop sao recalculadas pelo nucleo sobre tentativas persistidas;
metricas de outros instrumentos conservam seu contrato. CSV oficial de 21
colunas e exclusivo do Stroop; outros instrumentos sem esse contrato recebem
422 na exportacao, preservando consulta/detalhe. Nome/iniciais nunca chegam ao
JSON e sao mascarados no CSV. Avaliador legado sem identidade WEB tem ID null
na consulta e marcador `LEGADO_NAO_MAPEADO` no CSV, sem revelar seu texto antigo.
Horarios legados sem fuso permanecem sem fuso; nao se presume UTC.

A prontidao existente consulta migrations da conexao de operacoes. Configuracao
real da credencial de leitura e seus grants pertence a operacao/implantacao;
nao usar o papel administrativo sintetico dos testes na VPS.

Finalizacao participante: `POST /api/v1/participant/logout` com `{}`, Origin e
CSRF invalida a credencial e remove cookie HttpOnly; preserva avaliacao concluida.
Sem cookie, a operacao permanece idempotente com Origin valido. Bootstrap
completed mantem recibo JSON e retorna `X-CSRF-Token`/`X-Session-Expires-At` nos
headers para permitir finalizacao apos recuperacao de recibo. Contrato e limites:
[contrato HTTP](../docs/desenvolvimento/CONTRATO_API_WEB.md).

Hardening W17: a fronteira ASGI aplica no-store/nosniff/CSP restrita a dados,
X-Frame-Options DENY, no-referrer e CORP same-origin inclusive em erros e CSV.
Framing ambiguo (Content-Length com Transfer-Encoding, TE duplicado/invalido
ou tamanho divergente) e rejeitado. Cookies participantes nao emitidos recebem
401 sem criar contadores; limites de volume por IP/conexao no proxy continuam
necessarios. A CSP de paginas/bundle e separada, em `web/security-headers.json`;
a API nao serve HTML da aplicacao.

## Runtime e imagem WEB

`Dockerfile.api` usa a mesma base Python fixada do dashboard, mas instala somente
`api/requirements.lock`. O contexto proprio em `Dockerfile.api.dockerignore`
permite apenas o adaptador, nucleo Python, migrador/migrations e as tres fontes
canonicas de condicoes. Dados, `.env`, secrets, PsychoPy, frontend, testes e
artefatos locais ficam fora da imagem. O processo executa como UID/GID 10001,
porta interna 8000, sem access log nem header de versao do servidor. A imagem
aceita filesystem somente leitura; nao escreve codigo, dados ou migrations.

A configuracao aceita os pares abaixo, com **somente uma origem por valor**:

| Valor de ambiente | Arquivo externo explicito |
|---|---|
| `API_DATABASE_URL` | `API_DATABASE_URL_FILE` |
| `API_READ_DATABASE_URL` | `API_READ_DATABASE_URL_FILE` |
| `OIDC_CLIENT_ID` | `OIDC_CLIENT_ID_FILE` |
| `OIDC_CLIENT_SECRET` | `OIDC_CLIENT_SECRET_FILE` |
| `API_SESSION_SECRET` | `API_SESSION_SECRET_FILE` |

O caminho `_FILE` deve apontar para arquivo regular legivel pelo UID 10001,
UTF-8 de ate 16 KiB; um LF/CRLF final e removido. Ausencia, conflito entre
valor e arquivo, arquivo vazio/invalido ou configuracao resultante invalida
produzem mensagem fixa. Nao ha descoberta de arquivos `.env` ou secrets.
Montagens e permissoes sao responsabilidade do operador; nao copie secrets ao
contexto de build. A credencial de leitura continua sem fallback para escrita.

Entrypoint: `python -m api.runtime`. Subcomandos:

- `serve`: valida configuracao e inicia somente a API. Nao aplica migrations.
- `healthcheck`: consulta `http://127.0.0.1:8000/health/ready`, com Host da
  `API_PUBLIC_ORIGIN`, timeout de quatro segundos e sem proxies do ambiente;
  retorna codigo zero apenas para resposta 200 `{"status":"ready"}`. O
  healthcheck nao necessita ler secrets e nao altera o schema.
- `migrate`: exige **exclusivamente** `API_MIGRATION_DATABASE_URL` ou
  `API_MIGRATION_DATABASE_URL_FILE`, chama o migrador canonico explicitamente e
  encerra. Nao herda a credencial de runtime nem exige OIDC. A credencial DDL
  deve ser montada somente no job operacional, nunca no servico API permanente.

`serve` ignora headers encaminhados por padrao. A opcao explicita
`serve --forwarded-allow-ips IP,CIDR` habilita confianca apenas na lista
informada; valores sao IPs/CIDRs, sem resolucao implicita de nomes. `*` e
permitido somente por escolha explicita e exige API sem porta publicada e rede
confinada exclusivamente ao proxy autorizado. O proxy deve sobrescrever
X-Forwarded-For/Proto, para o limitador por endereco remoto nao aceitar valores
forjados pelo cliente externo. Rede Docker compartilhada com outros aplicativos
nao satisfaz esse confinamento. O Compose WEB e a validacao de spoofing do proxy
sao entregaveis de infraestrutura separados; esta opcao nao torna confiavel um
proxy arbitrario.

Build local: `docker build -f Dockerfile.api -t stroop-web-api:w19 .` na raiz.
Readiness consulta migrations na conexao operacional e nao comprova os grants
da credencial de consulta; valide leitura autorizada e rejeicao de escrita
separadamente antes da operacao. Aplicacao de migrations, provisionamento de
papeis e conexao do proxy sao acoes explicitas; nenhum launcher legado mudou.

Testes adicionais: `.venv/bin/python -m unittest tests.test_web_runtime -v`.
