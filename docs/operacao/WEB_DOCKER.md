# Aplicacao WEB em Docker

Pacote da W19 validado localmente com dados sinteticos. O aceite permanece no
[roadmap](../ROADMAP_WEB.md). Este procedimento prepara uma pilha independente;
a publicacao na VPS pertence a W22 e sera executada pelo responsavel.
O [ambiente legado](INFRAESTRUTURA_DOCKER.md) conserva seus comandos.

## Configuracao explicita

Use `compose.web.yaml` com `--env-file` em todas as chamadas. O modelo
`deploy/web.env.example` contem apenas configuracoes e caminhos ficticios.
Guarde a configuracao preenchida e os arquivos de secrets fora do repositorio
e do contexto de build; nao reutilize bancos de coleta em testes.

Os arquivos externos fornecem senha do proprietario PostgreSQL, tres DSNs
separadas (migracao/provisionamento, escrita e leitura), cliente/secret Google
OIDC, chave de sessao e certificado/chave TLS. As DSNs apontam para
`web-postgres:5432` e o mesmo banco, com usuarios distintos. A senha deve estar
codificada conforme URI. A API nao descobre arquivos `.env` e recusa configurar
simultaneamente uma variavel secreta e sua variante `_FILE`.

Os bind mounts de secrets devem ser legiveis pelos respectivos containers:
API UID/GID 10001; proxy UID/GID 101; PostgreSQL conforme sua imagem. Configure
permissoes/ACLs no host sem tornar secrets publicamente legiveis. A chave TLS
deve corresponder ao certificado, incluir o hostname da origem e apresentar
cadeia confiavel. Certificados sinteticos exigem simultaneamente ambiente
`test` e permissao explicita de teste; nao sao configuracao de producao.

`WEB_PUBLIC_ORIGIN` e a origem HTTPS publica exata, incluindo porta quando
diferente de 443. O proxy aceita DNS e IPv4; literal IPv6 ainda nao e suportado.
Cadastre o callback Google conforme o
[contrato HTTP WEB](../desenvolvimento/CONTRATO_API_WEB.md) e as
[regras de acesso WEB](../seguranca/ACESSO_WEB.md).
O padrao publica somente o proxy em loopback nas portas 8088/8448. Exposicao
externa, DNS e emissao/renovacao de certificados exigem a operacao autorizada
da W22; possuir dominio/VPS nao concede esse aceite.

## Build e inicializacao

Exemplo com arquivo externo; substitua o caminho antes da execucao:

```bash
docker compose --env-file /CAMINHO-EXTERNO/web.env -f compose.web.yaml --profile web config --quiet
docker compose --env-file /CAMINHO-EXTERNO/web.env -f compose.web.yaml --profile web build
docker compose --env-file /CAMINHO-EXTERNO/web.env -f compose.web.yaml --profile web up -d --wait web-postgres
docker compose --env-file /CAMINHO-EXTERNO/web.env -f compose.web.yaml --profile web-tools run --rm web-migrate
docker compose --env-file /CAMINHO-EXTERNO/web.env -f compose.web.yaml --profile web-tools run --rm web-provision
docker compose --env-file /CAMINHO-EXTERNO/web.env -f compose.web.yaml --profile web up -d --wait
```

Migrations e provisionamento sao jobs explicitos, nunca executados ao iniciar
o servidor. Faca backup e confira compatibilidade antes de atualizar banco
preexistente. Os jobs recebem a credencial proprietaria; o servidor recebe
somente escrita/leitura. Cadastro inicial do administrador permanece operacao
autorizada conforme o contrato de autenticacao.

O provisionador recusa papeis existentes sem sua marca de gerenciamento,
privilegios administrativos, memberships ou propriedade de objetos. Confere
tambem grants inseguros de PUBLIC, sem alterar globalmente um banco compartilhado.
Conceda o baseline necessario por procedimento do operador antes de repetir um
job recusado. A leitura recebe somente as colunas do contrato de consultas;
o writer recebe DML operacional, sem modificar usuarios ou o mapa de legado.
Uma funcao estreita da migration 0008 adquire o lock de usuario necessario a
revogacoes concorrentes, com EXECUTE somente para o writer. O privilegio
UPDATE(name) de projetos permite seu row lock. O baseline PostgreSQL de tabelas
temporarias por PUBLIC permanece; nao ha CREATE persistente para o runtime.

## Fronteiras operacionais

Somente o proxy publica portas. PostgreSQL participa apenas da rede interna
de dados; API e proxy compartilham outra rede interna. Uma rede de saida
exclusiva da API permite verificar Google OIDC. O servidor confia em headers
encaminhados apenas nesta topologia sem porta publicada; o proxy sobrescreve
origem, protocolo e IP encaminhados. Nao exponha a API diretamente mantendo
`--forwarded-allow-ips '*'`.

API/proxy executam sem root, com filesystem somente leitura, capabilities
removidas e temporarios limitados. Cada imagem possui whitelist propria de
contexto; PsychoPy, coletas, bancos e secrets ficam fora. A imagem do proxy
contem o frontend compilado, sem Node no runtime. Headers WEB derivam da fonte
canonica `web/security-headers.json`; respostas da API preservam seus headers.

Healthchecks verificam prontidao da API/banco e funcionamento local do proxy;
nao comprovam DNS publico, Google OIDC ou homologacao temporal. Logs do proxy
limitam-se a metadados operacionais sem URI, query, cookies ou conteudo; API
desativa access logs. Limites por IP na borda complementam os limites da API.

Para parar preservando o volume:

```bash
docker compose --env-file /CAMINHO-EXTERNO/web.env -f compose.web.yaml --profile web down
```

Nao remova volumes para atualizar ou recuperar a aplicacao. Restauracao e
rollback exigem procedimento validado na W20; recriar containers nao restaura
dados nem reverte migrations.

## Evidencias e teste manual sintetico

`python scripts/smoke_web_compose.py` cria projeto/volume/secrets exclusivos,
valida imagens prontas, HTTPS, headers, Host, portas/privilegios, leitura restrita,
convite/resgate/inicio/conclusao, retry idempotente, consulta/exportacao e
persistencia apos reinicio do PostgreSQL. Remove somente seus recursos ao sair.
Use `--build-images` para reconstruir as duas imagens serialmente. Nao comprova
Google real, capacidade da VPS nem a medicao fisica/temporal da W16.

Para teste manual, `python scripts/preview_web.py` cria outra pilha sintetica e
mantem seus containers ativos. Imprime URL loopback, convite de uso unico e
caminho do arquivo de configuracao externo. O certificado e autoassinado;
avance no aviso do navegador somente para a URL local gerada. O convite nunca
fica na URL. A area profissional exige Google configurado e nao faz parte
desse acesso sintetico; a fixture de administrador apenas emite o convite.
Nao use esta ferramenta com dados reais. Guarde o JSON externo para encerrar
com o mesmo `--project-name`/`--env-file`, preservando volumes conforme necessario.

Evidencias locais: build das duas imagens; smoke Compose completo aprovado;
Python307 com uma fixture de upgrade corrigida e modulo migrations11/11
revalidado; runtime11 e proxy5 aprovados; Gitleaks269 fontes sem achados.
Navegador Chromium abriu o frontend compilado, orientacoes e tela de convite
por HTTPS sem erro JavaScript. Nenhum dado operacional ou VPS acessado.
