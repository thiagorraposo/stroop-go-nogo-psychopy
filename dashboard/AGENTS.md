# Dashboard Streamlit

Escopo: `dashboard/`. Herda todas as regras da raiz.

- Preserve Streamlit e o comando publico de inicializacao. Separe interface,
  acesso a dados, transformacoes e componentes sem alterar o resultado visivel,
  salvo requisito da etapa.
- A camada de interface nao acessa CSV bruto. No estado SQLite, conexoes do
  dashboard sao somente leitura e devem tratar banco ausente, vazio ou invalido.
- Preserve filtros, metricas, graficos, tabela, detalhe, exportacao manual e aviso
  nao clinico documentados em `dashboard/README.md`.
- Nao exponha dados sensiveis em mensagens, logs, screenshots ou fixtures. Teste
  acesso a dados com bancos temporarios inteiramente sinteticos.
- Mudanca visual vai para `docs/UX_DECISIONS.md`; mudanca de dados/arquitetura,
  para o documento canonico correspondente e o registro de alteracoes.
