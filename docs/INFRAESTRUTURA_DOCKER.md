# Infraestrutura Docker local — Etapa 3

Data: 2026-09-01.

Esta etapa introduz somente a infraestrutura local de desenvolvimento. O
PsychoPy continua instalado e executado no host. O fluxo funcional vigente
permanece CSV -> SQLite -> dashboard; schema PostgreSQL, importacao PostgreSQL e
integracao do dashboard com PostgreSQL pertencem a etapas posteriores do
[workflow](WORKFLOW_EVOLUCAO.md).

## Componentes

- `postgres`: PostgreSQL 17.6, com volume nomeado persistente e healthcheck por
  `pg_isready`;
- `dashboard`: Python 3.12 e Streamlit em imagem propria, preservando
  `dashboard/app.py` como ponto de entrada;
- inicializacao do dashboard condicionada ao estado saudavel do PostgreSQL;
- `DATABASE_URL` entregue ao container do dashboard como contrato de
  configuracao, ainda nao consumido pela camada SQLite vigente.

O PostgreSQL tambem publica a porta configuravel `POSTGRES_PORT` somente em
`127.0.0.1`, usando 55432 por padrao. Isso permite executar no host as
[migrations PostgreSQL](MIGRACOES_POSTGRESQL.md) sem expor o banco na rede.

O contexto da imagem exclui coletas, bancos, backups, exports, logs,
credenciais, chaves, secrets, PsychoPy e arquivos do experimento. A telemetria
de uso do Streamlit fica desativada no container.

## Configuracao e execucao

Crie uma configuracao local a partir do exemplo e substitua a senha ficticia:

```bash
cp .env.example .env
docker compose config
docker compose up --build -d --wait
docker compose ps
```

O dashboard fica em `http://localhost:8501`. Nesta etapa ele pode exibir a
mensagem esperada de SQLite ausente dentro da imagem; a saude do servico apenas
confirma que o ponto de entrada Streamlit responde. Os launchers publicos do
host continuam sendo o caminho funcional para consultar o SQLite local.

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
