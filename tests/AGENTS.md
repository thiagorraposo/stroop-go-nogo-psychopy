# Testes

Escopo: `tests/`. Herda todas as regras da raiz.

- Use `unittest` conforme a suite existente e mantenha descoberta por
  `.venv/bin/python -m unittest discover -s tests -v`.
- Fixtures devem ser inequivocamente sinteticas. Nao leia CSVs de `data/`, o
  SQLite local, backups ou qualquer coleta real.
- Use diretorios temporarios e bancos descartaveis; testes nao podem iniciar
  coleta, Streamlit interativo, Docker ou servicos externos.
- Para mudancas no `.psyexp` ou em condicoes, valide estaticamente Flow, nomes de
  variaveis, colunas, tempos e compatibilidade entre arquivos.
- Cubra comportamento e regressao do escopo; nao enfraqueca assercoes nem altere
  funcionalidade apenas para fazer a suite passar.
- Para etapas WEB, cubra os limites e fluxos reais exigidos na ficha, incluindo
  autorizacao negativa, erros e integracao quando aplicaveis. Doubles e relogios
  controlados servem a testes isolados; nao substituem banco, navegador ou
  medicao fisica quando estes forem criterios de aceite.
- Use os comandos de teste, lint, tipos e build documentados para cada camada
  implementada; registre aprovados, falhas, erros e skips separadamente. Uma
  verificacao obrigatoria indisponivel mantem o criterio pendente.
