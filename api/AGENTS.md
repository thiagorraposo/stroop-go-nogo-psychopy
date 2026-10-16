# Adaptador HTTP

Herda [as regras da raiz](../AGENTS.md). Contrato canonico em
[CONTRATO_API_WEB.md](../docs/desenvolvimento/CONTRATO_API_WEB.md).

- `main.create_app` compoe FastAPI sem iniciar Streamlit, servicos ou migrations.
- Configuracao por ambiente e validada antes de servir; nao ler `.env` operacional.
- Routers HTTP usam os casos de uso de `stroop`; formulas ficam no dominio.
- Use `RequestModel` nos corpos: tipos estritos, campos fechados e numeros finitos.
- Preserve o limite ASGI de 64 KiB, erros estaticos e identificador aleatorio.
  Nunca devolver `exc.detail`, erros de schema, entrada, DSN ou traceback.
- Novas rotas validam queries permitidas e aplicam autenticacao, escopo e CSRF
  previstos na respectiva etapa. Nao criar rotas de coleta antes das dependencias.
- Readiness apenas consulta migrations; sua aplicacao continua sendo operacional.
- Nao habilitar access log com path/query sensiveis nem CORS arbitrario.
- Atualize requirements e lock juntos, respeitando versoes compartilhadas com o
  dashboard; valide com `tests/test_api_base.py` e regressao integral.
