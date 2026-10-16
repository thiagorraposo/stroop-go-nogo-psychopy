# API HTTP

Base FastAPI de W05, sem rotas de coleta ou autenticacao. O estado de cada etapa
fica no [roadmap](../docs/ROADMAP_WEB.md); o
[contrato HTTP](../docs/desenvolvimento/CONTRATO_API_WEB.md) define formatos e limites.

Na raiz do checkout, com Python 3.12 e a `.venv` existente:

```bash
.venv/bin/python -m pip install --index-url https://pypi.org/simple -r api/requirements.lock
```

`requirements.txt` declara dependencias diretas e `requirements.lock` fixa a
resolucao completa, incluindo `httpx` para TestClient. Versoes compartilhadas
seguem `dashboard/requirements.lock`. Atualize ambos e valide a suite ao renovar.

Configure no ambiente da sessao `API_DATABASE_URL` (URI PostgreSQL com host e
banco), `API_PUBLIC_ORIGIN` (origem HTTPS sem caminho, credenciais ou query) e
`APP_ENV` (`development`, `test` ou `production`). As tres sao obrigatorias.
Nenhum `.env` e lido automaticamente. Ausencia ou valor invalido impede a
factory de iniciar com uma mensagem fixa, sem imprimir a configuracao.

Exemplo exclusivamente sintetico de preparacao local:

```bash
export API_DATABASE_URL='postgresql://synthetic:synthetic-local-only@127.0.0.1:55432/stroop_etapa4_test_web'
export API_PUBLIC_ORIGIN='https://localhost:8000'
export APP_ENV='test'
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
.venv/bin/python -m unittest tests.test_api_base -v
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
