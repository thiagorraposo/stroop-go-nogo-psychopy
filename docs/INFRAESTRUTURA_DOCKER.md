# Infraestrutura Docker local — Etapa 3

Data: 2026-09-01.

Esta etapa introduz a infraestrutura local de desenvolvimento. O PsychoPy
continua instalado e executado no host. O fluxo aceita CSV -> PostgreSQL ->
dashboard autenticado; sem URL de leitura, o fallback CSV -> SQLite -> dashboard
permanece disponível. O schema ja possui
[migrations documentadas](MIGRACOES_POSTGRESQL.md); sequenciamento, escopo e
aceite das entregas sao definidos somente no
[backlog canonico](Projeto%20Stroop%20Test.md).

A configuracao endurecida, separada desta base local, esta em
[Hardening de producao](HARDENING_PRODUCAO.md). Ela nao altera o comando de
desenvolvimento descrito neste documento.

## Componentes

- `postgres`: PostgreSQL 17.6, com volume nomeado persistente e healthcheck por
  `pg_isready`;
- `dashboard`: Python 3.12 e Streamlit em imagem propria, preservando
  `dashboard/app.py` como ponto de entrada;
- inicializacao do dashboard condicionada ao estado saudavel do PostgreSQL;
- `DATABASE_URL` entregue ao container para importacao PostgreSQL;
- `DASHBOARD_DATABASE_URL` entregue ao container para leitura PostgreSQL;
- `AUTH_DATABASE_URL` separado para autorizacao e auditoria;
- arquivo local de secrets OIDC montado como somente leitura, nunca incorporado
  a imagem;
- camada de resultados consulta PostgreSQL quando a URL de leitura está configurada.

O dashboard e o PostgreSQL publicam suas portas configuraveis somente em
`127.0.0.1` no desenvolvimento; o PostgreSQL usa 55432 por padrao. Isso permite executar no host as
[migrations PostgreSQL](MIGRACOES_POSTGRESQL.md) sem expor o banco na rede.

O contexto da imagem exclui coletas, bancos, backups, exports, logs,
credenciais, chaves, secrets, PsychoPy e arquivos do experimento. A telemetria
de uso do Streamlit fica desativada no container.

## Configuracao e execucao

Crie uma configuracao local a partir do exemplo, substitua a senha ficticia e
aponte `STREAMLIT_SECRETS_FILE` para um arquivo OIDC real ignorado pelo Git:

```bash
cp .env.example .env
docker compose config
docker compose up --build -d --wait
docker compose ps
```

O dashboard fica em `http://localhost:8501` e exige Google OIDC e cadastro
previo. Ele pode exibir a mensagem esperada de SQLite ausente dentro da imagem
de desenvolvimento; a saude do servico apenas confirma que o ponto de entrada
Streamlit responde. Consulte
[AUTENTICACAO_E_PERMISSOES.md](AUTENTICACAO_E_PERMISSOES.md).

Para encerrar sem apagar o volume PostgreSQL:

```bash
docker compose down
```

Nao use `docker compose down --volumes` quando desejar preservar o banco local.
O arquivo `.env` e dados do volume nao devem ser versionados.

## Validacao realizada

Com valores exclusivamente ficticios de `.env.example`:

- `docker compose config`: valido;
- build das imagens: concluido;
- `postgres` e `dashboard`: saudaveis;
- endpoint `/_stcore/health`: `ok`;
- marcador operacional sintetico criado no PostgreSQL: uma linha;
- parada, nova inicializacao e consulta: a mesma linha permaneceu no volume;
- nenhum CSV ou SQLite local foi aberto ou copiado para containers.

A tabela usada como marcador foi criada somente no volume local de validacao e
nao e uma migration de dominio versionada.
