# Hardening de producao

Esta configuracao prepara a exposicao futura do sistema sem realizar deploy,
configurar dominio, certificado real, destino externo ou OCI. O
[backlog canonico](Projeto%20Stroop%20Test.md) continua sendo a unica fonte de
estado e aceite. O dashboard de resultados usa PostgreSQL por
`DASHBOARD_DATABASE_URL`; SQLite permanece apenas como fallback local.

## Configuracoes separadas

- `compose.yaml`: desenvolvimento local; dashboard e PostgreSQL vinculados
  somente a `127.0.0.1`;
- `compose.production.yaml`: perfil endurecido e independente; somente o Nginx
  publica as portas 80 e 443;
- `compose.restore-test.yaml`: PostgreSQL descartavel em `tmpfs`, rede interna e
  sem porta publicada, usado exclusivamente para validar restauracoes;
- `.env.production.example`: nomes e limites ficticios, nunca credenciais.

As imagens-base estao fixadas por versao e digest de manifesto. O proxy tambem
fixa o pacote OpenSSL 3.3.7-r0 usado para validar os arquivos TLS. Os manifests
oficiais verificados em 2026-09-13 incluem `linux/arm64/v8` para PostgreSQL
17.6, Nginx 1.28.0 e Python 3.12.11. As dependencias Python diretas tambem usam
versoes exatas; `dashboard/requirements.lock` fixa todo o conjunto transitivo
instalado na imagem. Atualizacoes exigem novo build, suite completa e nova consulta
dos manifests; nao remover a fixacao apenas para obter uma versao recente.

O arquivo de producao segue a recomendacao de manter configuracao especifica
para esse ambiente e usa controles previstos pelo Compose, como secrets,
`read_only`, limites e reducao de capabilities:
[Compose em producao](https://docs.docker.com/compose/how-tos/production/) e
[servicos Compose](https://docs.docker.com/reference/compose-file/services/).

## Fronteiras e menor privilegio

O Nginx participa apenas da rede `frontend`; o PostgreSQL, apenas da rede
interna `backend`; o dashboard conecta as duas redes sem publicar porta. Os tres
servicos eliminam capabilities, impedem elevacao de privilegio, limitam PIDs e
usam sistema de arquivos raiz somente leitura com `tmpfs` estritamente
necessarios. Dashboard e proxy executam como UIDs sem privilegio; o PostgreSQL
executa como seu UID dedicado sobre o volume de dados.

O perfil inicial para uma futura instancia Ampere A1 de 2 OCPUs limita os
servicos permanentes a 1,55 CPU no total:

| Servico | CPU | Memoria |
|---|---:|---:|
| PostgreSQL | 0,75 | 1536 MiB |
| dashboard | 0,65 | 768 MiB |
| Nginx | 0,15 | 128 MiB |

Todos os valores sao configuraveis no arquivo de ambiente. Eles sao provisórios
e serao medidos e confirmados na Etapa 11; a reserva de 0,45 CPU e a memoria nao
alocada permanecem disponiveis para sistema operacional e tarefas operacionais.

## TLS obrigatorio e proxy

O perfil de producao exige tres arquivos externos antes de iniciar: secrets
OIDC, certificado TLS e chave privada TLS. Nenhum deles possui valor padrao ou e
incluido na imagem. O HTTP somente redireciona para HTTPS; o Nginx aceita TLS
1.2/1.3 e envia HSTS, protecao contra sniffing, framing, referrer e uma politica
CSP minima compativel com Streamlit.

O entrypoint recusa ausencia, arquivo invalido e certificados de teste marcados
com `synthetic.invalid` ou `STROOP SYNTHETIC TEST` quando `APP_ENV=production`.
Uma excecao exige simultaneamente `APP_ENV=test` e
`ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS=1`; ela e usada somente em validacao
descartavel. Certificado sintetico nunca e apresentado como confiavel e nunca e
gravado no repositorio. Dominio, certificado real e ativacao publica pertencem
exclusivamente a Etapa 11.

Os arquivos devem ter modo `0600` e pertencer aos UIDs sem privilegio definidos
por `APPLICATION_UID/GID` e `PROXY_UID/GID`. O exemplo usa o UID/GID 1000 do
operador de deploy; a Etapa 11 confirmara esses numeros no host. O PostgreSQL
mantem seu UID dedicado 999.

O proxy preserva o upgrade WebSocket exigido pelo Streamlit, conforme a
[documentacao do Nginx](https://nginx.org/en/docs/http/websocket.html). Limita
cada IP a 10 requisicoes por segundo com burst 30 e a 20 conexoes. O corpo HTTP
tem limite de 6 MiB; o Streamlit limita arquivo a 5 MiB e mensagem a 6 MiB.

## Logs, erros, saude e monitoramento

O Streamlit oculta detalhes de excecao, reduz logging a `warning` e desativa
telemetria. O formato de acesso do Nginx registra somente horario, metodo,
status, quantidade de bytes, duracao e ID aleatorio. Ele deliberadamente nao
registra URI, query string, cookies, headers, corpo, tokens, credenciais ou CSV.
O erro do Nginx fica em nivel `emerg`, sem registrar falhas normais de requisicao.
O driver `local` limita volume por arquivo
e numero de arquivos.

O prazo operacional provisório e 30 dias. Como a rotacao Docker e limitada por
tamanho, a Etapa 11 devera configurar no host o descarte temporal de qualquer
arquivo remanescente em no maximo 30 dias. A auditoria OIDC usa 180 dias. A
limpeza do banco e deliberadamente separada dos dados da pesquisa:

```bash
docker compose --env-file .env.production -f compose.production.yaml \
  exec -T dashboard python scripts/aplicar_retencao.py
docker compose --env-file .env.production -f compose.production.yaml \
  exec -T dashboard python scripts/aplicar_retencao.py --apply
```

O primeiro comando apenas conta; o segundo elimina somente auditorias de
importacao vencidas e eventos OIDC vencidos. Nenhum deles consulta ou remove
avaliacoes, metricas ou tentativas.

Cada servico possui healthcheck. Monitoramento futuro deve observar estado
`unhealthy`, reinicios, uso sustentado acima de 80% dos limites, espaco livre
abaixo de 20%, falhas de backup e vencimento do certificado. Alertas devem usar
somente contagens e estado tecnico, nunca payloads ou identificadores.

## Backup criptografado

`scripts/backup_postgres.py` transmite `pg_dump` em formato custom diretamente
para AES-256-GCM; nao cria dump em claro. O resultado e escrito atomicamente com
permissao `0600`, recebe checksum SHA-256 e mantem 30 geracoes por padrao. A
chave base64 de 256 bits deve ter permissao `0600` e ficar fora do diretorio de
backups. Ela nao deve ser sincronizada, copiada ou armazenada junto dos dumps.

Exemplo de preparacao, sem valores reais:

```bash
python scripts/backup_postgres.py generate-key \
  --key-file /CAMINHO_SEGURO_SEPARADO/backup.key
python scripts/backup_postgres.py backup \
  --env-file .env.production \
  --key-file /CAMINHO_SEGURO_SEPARADO/backup.key \
  --output-dir /CAMINHO_PROTEGIDO/backups \
  --database NOME_DO_BANCO --user USUARIO_DO_BANCO
```

Um agendador do host devera executar o backup diariamente. O destino externo e
sua credencial serao definidos apenas na Etapa 11. Falha nao remove uma geracao
valida e nao imprime stderr do PostgreSQL, comandos, paths ou credenciais.

Mensalmente, execute a restauracao isolada:

```bash
python scripts/backup_postgres.py restore-test \
  --key-file /CAMINHO_SEGURO_SEPARADO/backup.key \
  --backup /CAMINHO_PROTEGIDO/backups/ARQUIVO.dump.enc
```

O processo verifica checksum e autenticidade, inicia o ambiente fixo
`stroop-restore-validation` em `tmpfs`, restaura sem portas e informa somente
contagens agregadas. O ambiente e removido mesmo em falha. O formato custom e o
uso de `pg_restore` seguem a
[documentacao PostgreSQL 17](https://www.postgresql.org/docs/17/backup-dump.html).

## Verificacao antes de qualquer deploy

Crie `.env.production` fora do Git a partir do exemplo e substitua todos os
valores ficticios. Nao use o exemplo para iniciar servicos. Antes de cada
ativacao, confirme:

```bash
docker compose --env-file .env.production -f compose.production.yaml config --quiet
docker compose --env-file .env.production -f compose.production.yaml build
docker compose --env-file .env.production -f compose.production.yaml up -d --wait
docker compose --env-file .env.production -f compose.production.yaml ps
```

Tambem confirme que somente 80/443 estao publicados, o redirecionamento HTTP
funciona, o certificado e confiavel para o hostname real, os headers estao
presentes e backup/restauracao passaram. Essas acoes de producao nao foram
autorizadas nesta etapa.
