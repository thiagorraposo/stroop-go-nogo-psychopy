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
- O fluxo participante usa cookie/token separado, hash no banco, Origin/CSRF,
  prazos absolutos e revalidacao do projeto, emissor e vinculo em cada operacao.
  Projetos WEB permanecem sinteticos ate uma etapa implementar e habilitar a
  configuracao aprovada de pesquisa real.
- Conclusao valida schema dentro do fluxo autenticado/transacional, depois de
  acesso, prazo e estado. Participantes e profissionais possuem limites HMAC
  independentes; hash de payload/recibo nao substitui a revalidacao de acesso.
- Readiness apenas consulta migrations; sua aplicacao continua sendo operacional.
- Nao habilitar access log com path/query sensiveis nem CORS arbitrario.
- Atualize requirements e lock juntos, respeitando versoes compartilhadas com o
  dashboard; valide com `tests/test_api_base.py`, `tests/test_web_auth.py`,
  `tests/test_web_sessions.py`, `tests/test_web_results.py` e regressao integral.

- Consultas profissionais usam `API_READ_DATABASE_URL` dedicado, sem fallback
  para escrita; papel SELECT nas colunas necessarias e transacao READ ONLY.
  Revalidar usuario/vinculo/projeto em cada consulta/download; nome/iniciais
  nao integram projecoes JSON nem sao lidos pela credencial de consulta.
  Legado exige mapa operacional explicito, nunca coincidencia de codigos
  (ADR-003). Metricas Stroop sao recalculadas pelo nucleo; nao reinterpretar
  metricas de outros instrumentos como resultados desta tarefa.
