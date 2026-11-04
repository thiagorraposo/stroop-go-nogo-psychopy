# Homologacao WEB — evidencias W21

Observacoes em 2026-10-21 e retomada em 2026-10-27, somente com dados sinteticos. Estado e aceite da
etapa permanecem no [roadmap](../ROADMAP_WEB.md). Este relatorio distingue a
pilha local efetivamente ensaiada do ambiente alvo; nao extrapola capacidade
da VPS nem aplica a W21 o aceite excepcional concedido a W16.

## Ambiente e metodo da carga local

`scripts/benchmark_web.py` cria projeto Compose, volume, certificado e secrets
exclusivos; aceita somente esse alvo loopback, sem parametro de URL externa.
API/proxy atuais compilados, PostgreSQL 17.6, HTTPS com certificado sintetico
verificado pelo cliente, papeis separados de escrita/leitura. O smoke confere
restricoes de privilegios e portas antes da carga. Todos os recursos exclusivos
sao removidos ao sair, inclusive em falha; os demais projetos Docker nao sao
interrompidos. Configuracao canonica em [WEB_DOCKER](WEB_DOCKER.md).

Host local com 12 processadores logicos. Limites observados por container:
PostgreSQL 1 CPU/768 MiB, API 1 CPU/384 MiB e proxy 0,5 CPU/128 MiB. Esses limites
nao reproduzem integralmente a VPS de 2 vCPUs; nao houve isolamento dos demais
processos do host. Imagens imutaveis ensaiadas:

- API: `sha256:da5995ea91f5a18b6b4efd77ead0c839a937b88ae70e1dc60205de04102ad8fa`.
- Proxy: `sha256:cb4ccf3b1eb0fa795058ea3e270176b07a2893fdf0593049743924f253a13afb`.

Massa: **uma avaliacao**, 16 tentativas e 12 metricas. O fluxo HTTP cria projeto,
vinculo, convite, resgate, inicio, conclusao, retry idempotente, consulta e CSV.
As sessoes profissionais sao fixtures sinteticas no banco; Google OIDC real
nao e simulado como autenticacao externa aprovada. O resultado inicial e um
payload nominal sintetico; sua gravacao HTTP nao e um ensaio do motor no navegador.

Quatro consultas autenticadas alternadas: projetos, lista de resultados,
detalhe e CSV. Uma sessao independente por cliente ativo; 1 GET/s por cliente
durante 30 s por nivel, com inicio escalonado. Cliente abre conexao TLS por
requisicao; latencia inclui handshake, leitura e validacao da resposta. Nao ha
motor experimental executando durante a carga. Limites padrao ativos, sem
spoofing de IP ou aumento das cotas: proxy 10 requisicoes/s por IP e burst 20.
O pico de clientes ativos com pacing nao e o maximo de requisicoes simultaneas
nem uma medida de participantes experimentais suportados.

## Resultados observados

| Clientes ativos / GET/s oferecidos | Respostas validas / programadas | HTTP 429 | Latencia p95 dos sucessos (ms) | p99 (ms) | Sucessos/s observados |
|---|---:|---:|---:|---:|---:|
| 1 | 30/30 | 0 | 116,43 | 120,62 | 1,00 |
| 4 | 120/120 | 0 | 119,01 | 125,80 | 4,00 |
| 8 | 240/240 | 0 | 115,42 | 122,75 | 8,00 |
| 16 | 320/480 | 160 | 860,92 | 1034,24 | 10,66 |

870 requisicoes registradas: 710 respostas 200 com conteudo validado e 160
rejeicoes 429; nenhum 5xx, erro de transporte ou resposta 200 invalida. O maior
nivel ensaiado sem rejeicoes foi **8 clientes ativos a 1 GET/s**, nesse conjunto
de dados e janela. Nao e teto de hardware nem recomendacao de capacidade da
VPS. A taxa de 10,66 sucessos/s na ultima janela inclui o burst; nao e promessa
de throughput sustentado. Percentis usam nearest-rank, apenas sucessos;
rejeicoes e perdas de requisicoes programadas nao sao contadas como sucesso.

Os tokens sinteticos usados como canarios nao apareceram nos logs dos containers
API/proxy durante as quatro etapas. Essa verificacao por canarios nao representa
prova universal de ausencia de vazamento. O artefato do medidor guarda apenas
operacao generica, indice do cliente, status e tempos; nunca corpos, URLs com
IDs, cookies, DSNs ou texto livre de excecoes.

Depois da carga, os tres containers foram reiniciados, voltaram a ficar saudaveis
e preservaram 1 avaliacao/16 tentativas/12 metricas. **Nao houve reboot do host**.

## Recuperacao e regressao

O [ensaio de recuperacao](WEB_RECUPERACAO.md) foi executado com as mesmas imagens:
backup criptografado, restauracao isolada de **9 migrations e 1 avaliacao**,
integridade WEB, indisponibilidade de banco detectada e rollback de candidato
deliberadamente invalido. Contagens preservadas. Backup + restauracao medidos
em 6,927 s no ensaio local; isso nao garante RPO/RTO no ambiente alvo.

Regressao Python: **352 testes aprovados, zero skips**, com PostgreSQL novo e
descartavel `stroop_etapa4_test_w21`, sem ler `.env` operacional. Inclui cinco
testes do medidor (contagens, cauda de latencia, limites e preservacao de arquivo).
Integracao Chromium/Firefox em HTTPS/API/PostgreSQL reais: **36/36 aprovados**,
sem retries, em 10,9 minutos; typecheck e build tambem aprovados. Cobre perfis,
projetos, cadastro, convite, pratica/principal reais, recibo perdido, reenvio,
CSV/importacao, revogacao e CSP. Essa suite usa seu proprio proxy HTTPS de teste;
a borda Nginx real foi ensaiada no Compose, na carga e na recuperacao. Nenhum
desses testes concede aceite Google externo ou homologacao temporal fisica.

Comandos: `.venv/bin/python -m unittest discover -s tests -v` na raiz e
`npm run test:integration` em `web/`, com `TEST_DATABASE_URL` apontando apenas
ao banco novo descartavel. Esse banco e removido depois do ensaio; nunca usar
uma DSN operacional nem carregar `.env` para obter credenciais de teste.

## Problemas encontrados e corrigidos

1. A imagem atual do proxy nao iniciava: a regex da rota CSV continha `{36}`
   sem aspas e o parser Nginx a interpretava como estrutura de configuracao.
   Corrigida a delimitacao, preservando o match e os limites. Smoke real agora
   comprova que corpo maior que 64 KiB chega a autenticacao da rota CSV,
   enquanto outras rotas respondem 413. O teste estatico anterior conferia
   apenas a string e nao detectou a falha de sintaxe no parser real.
2. O check novo de transporte inicialmente enviava o Content-Type JSON para
   a rota CSV. Corrigida a fixture para `text/csv; charset=utf-8`; nenhuma regra
   da API foi relaxada. As duas execucoes sem carga foram preservadas.
3. O ensaio de recuperacao ainda exigia oito migrations. Passou a consultar
   `discover_migrations()`, preservando o contrato de verificar a versao vigente.

## Reproducao e artefatos locais

Na raiz, com Docker disponivel, escolher um **arquivo de saida novo**:

```bash
.venv/bin/python scripts/benchmark_web.py --build-images --output exports/w21/capacity-NOVA.json
.venv/bin/python scripts/smoke_web_recovery.py --api-image stroop-web-api:w21 --proxy-image stroop-web-proxy:w21
```

O medidor recusa sobrescrever arquivos existentes e limita niveis a 1–32
clientes, em ordem crescente e sem duplicatas; duracao de 5–120 s. Padroes:
`--levels 1,4,8,16 --duration-seconds 30`. Todas as respostas, inclusive 429 e
falhas de transporte, entram na evidencia. Sem retries automaticos. Codigo de
saida 0 significa ensaio medido e encerrado corretamente, nao aceite W21; ler
os contadores e limites do resultado. Logs/exports permanecem ignorados pelo Git.

Artefatos locais em `exports/w21/`, ignorados pelo Git:

- `capacity-local-20261021.json`: falha antes da carga, sintaxe Nginx.
- `capacity-local-20261021-r2.json`: falha antes da carga, fixture do transporte.
- `capacity-local-20261021-r3.json`: medicao completa, resumos e 870 amostras.
- `recovery-local-20261021.json`: restauracao/alerta/rollback aprovados.
- `validation-local-20261021.json`, `python-20261021.txt` e
  `integration-20261021.txt`: regressao e integracao sem skips/falhas.
- `public-smoke-20261021.json`, `ssh-access-20261021.json` e
  `source-hashes-20261021.json`: sondagens e proveniencia do codigo ensaiado.

O manifesto `SHA256SUMS-20261021` tem 10 entradas, verificadas com
`sha256sum --check SHA256SUMS-20261021 --quiet` nesse diretorio. SHA-256 do
manifesto: `63fcf49763f999778d977a5441372985a6c150723b970c7b14d5459b77ffafa0`.
Os hashes identificam as fontes exatas, pois o ensaio ocorreu antes do commit
das alteracoes W21. Nao versionar logs, dumps, exports, configuracao privada ou
secrets. Os recursos temporarios destes ensaios foram removidos; projetos e
containers preexistentes permaneceram intactos.

## Historico — ambiente alvo em 2026-10-21

O smoke publico leu apenas pagina e prontidao por HTTPS: ambos responderam 200,
HSTS presente, CSP na pagina e prontidao com corpo esperado. Foram duas consultas,
nao teste de carga, login ou identificacao da release remota atual.

O SSH de leitura com a chave local conhecida foi recusado (`publickey`); a chave
esta protegida por passphrase e foi solicitado seu desbloqueio no agente, sem
envio de segredo na conversa. O agente indicado nesta sessao nao esta acessivel;
a tentativa de desbloqueio por dialogo grafico nao carregou a chave e seu agente
temporario foi removido. Nenhuma alteracao remota foi executada. O inventario
em [DEPLOY_WEB_VPS](DEPLOY_WEB_VPS.md) e historico; a release atual nao foi
reconfirmada por SSH.

Para concluir W21 ainda e preciso acesso ao ambiente de homologacao alvo para
ensaiar o candidato atual isoladamente, medir capacidade nesse ambiente,
validar recuperacao e o reboot autorizado, conferir autenticacao externa e
fechar a lista de pendencias. A validacao local nao substitui essas evidencias.
As duas falhas Firefox registradas no aceite excepcional W16 continuam riscos
conhecidos, sem causa determinada. Nenhuma coleta real, alteracao da versao
publicada, acesso a dados operacionais ou publicacao foi feita naquela unidade.

## Retomada no ambiente alvo — 2026-10-27

O responsavel autorizou concluir as etapas restantes. O agente SSH voltou a
autenticar no alvo conhecido. Inventario reconfirmado: duas CPUs logicas,
aproximadamente 4 GiB de RAM, 84 GiB livres; a aplicacao publica ainda utiliza
`26fa9bf`. O candidato `af73939` foi transferido por arquivo completo de fontes
versionadas para `/home/raposo/stroop-web/homologacao/af73939`. Nenhum dado ou
secret operacional foi incluido. SHA-256 do arquivo de fontes:
`6f3553be0d26eb1624aa764528a987474168e8fae6d05d6703ed4d2e8411ed3e`.
Arquivo das duas imagens: `ddd9dffbe9d3059c27b174d66953f28a9d369518f540156336253c2e20165f40`.
Checksums conferidos na origem e no alvo; IDs das imagens iguais aos do ensaio
local acima. O ambiente publicado permaneceu ativo durante a campanha.

### Capacidade medida na VPS

O comando `python3 scripts/benchmark_web.py --output exports/w21/capacity-vps-20261027.json`
foi executado **na propria VPS**, em Compose, volume e portas loopback exclusivos.
O campo `scope=isolated-local-compose` do artefato indica o loopback do host
executor, que nesta campanha e a VPS, nao o computador de desenvolvimento.
Mesma massa de uma avaliacao, quatro operacoes, 30 segundos por nivel e limites
padrao do metodo acima; os servicos publicados e legados permaneceram ativos.

| Clientes ativos / GET/s oferecidos | Respostas validas / programadas | HTTP 429 | p95 dos sucessos (ms) | p99 (ms) |
|---|---:|---:|---:|---:|
| 1 | 30/30 | 0 | 57,49 | 82,91 |
| 4 | 120/120 | 0 | 59,31 | 91,50 |
| 8 | 240/240 | 0 | 58,73 | 64,39 |
| 16 | 320/480 | 160 | 64,97 | 82,15 |

Total: 870 requisicoes, 710 sucessos validos e 160 rejeicoes pelo limitador,
sem 5xx, falhas de transporte ou respostas 200 invalidas. Maior nivel testado
sem rejeicao: **8 clientes ativos a 1 GET/s**. Nao representa capacidade de
participantes executando o motor nem limite de hardware, e nao extrapola para
outras massas/duracoes. Canarios de sessao ausentes dos logs da pilha sintetica.
Reinicio dos tres containers aprovou prontidao e preservou 1 avaliacao,
16 tentativas e 12 metricas. Nao houve reboot do host.

### Correcao operacional e verificacao publica

O ensaio `scripts/smoke_web_recovery.py`, tambem executado na VPS com as mesmas
imagens e uma pilha sintetica exclusiva, aprovou backup criptografado,
restauracao isolada de nove migrations e uma avaliacao, deteccao da falha de
banco e retorno da imagem deliberadamente invalida. Contagens preservadas;
backup mais restauracao medidos em **5,943 s**. O resultado nao garante RPO/RTO
operacional nem equivale a reboot do host. A primeira chamada falhou antes de
criar a pilha por ausencia de `psycopg` no Python do host; para a segunda foram
extraidos wheels das mesmas versoes do lock em diretorio privado do harness,
sem instalar pacotes globalmente ou alterar a aplicacao publicada.

A rotina publicada criou novo backup criptografado, mas `restore-check` falhou:
o pacote antigo omitia `compose.restore-test.yaml`. Reposto o arquivo com
conteudo identico ao do commit original, sem mudar imagem, banco ou trafego;
o mesmo `tools/vps-maintenance.sh restore-check` passou apos a correcao.
O empacotamento completo e sua verificacao estao documentados na
[transicao](TRANSICAO_WEB.md). Nova copia criptografada foi transferida para
fora da VPS e teve SHA-256 conferido; isso ainda nao configura replicacao
externa automatica nem garante RPO externo continuo.

Smoke publico: pagina e readiness 200, HSTS/CSP presentes; inicio OIDC 303
para `accounts.google.com`. Nao foi executado login pessoal nem concluido o
callback Google nesta verificacao. Nenhum cookie ou parametro OIDC foi gravado
nos artefatos. Esses resultados pertencem a release publicada antiga.

Evidencias privadas/ignoradas em `exports/w21/20261027-vps/`; os JSONs de carga
e recuperacao tambem sao mantidos no diretorio de homologacao da VPS.
O acesso administrativo para reboot, o aceite Google pessoal e o destino
estavel de backup externo foram solicitados ao responsavel sem pedir senhas.
W21 ainda exige o fechamento dessas evidencias aplicaveis; W22/W23 nao recebem
aceite automatico pela medicao de capacidade ou pela documentacao preparada.

## Correcao validada com runtime restrito — 2026-10-28

A campanha de interface compilada no alvo encontrou um defeito que os testes
com proprietario nao mostravam: criacao de conta administrativa retornava503,
pois o writer corretamente nao possui INSERT/UPDATE direto em app_users.
Vinte e cinco verificacoes de consulta, CSV, importacao e convites passaram;
o cadastro permaneceu reprovado ate a correcao.

O commit `ad3a469` introduz a capacidade SQL estreita da migration0010 para
gestao administrativa, com ator revalidado, serializacao, ultimo administrador
protegido e auditoria atomica. Grants diretos em usuarios seguem negados;
somente o writer recebe EXECUTE. A persistencia legada permanece preservada.
API corrigida: `stroop-web-api:w21-admin-20261028`, ID
`sha256:7751933be0d4ba24eceff9e65bc388a76d0cd7fdba66f096542736f348a649ad`.
Proxy W21 inalterado. Fontes e imagem conferidas na origem e na VPS:

- Arquivo de fontes: `71300ebe10450fa8812449c2d62ebd7d8e43ddce7685696947793f286a280906`.
- SHA-256 do pacote de imagem: `9c69e92a4afc1fad235b4478132aa6cf321a53d09884698a7b84ce3346072fc4`.

Suite Python corrigida:357/357, sem skips; testes focados13/13 incluem HTTP
com writer real, grants, ator bloqueado e duas despromocoes concorrentes que
preservam um administrador. Administracao integrada HTTPS/API/PostgreSQL
aprovada em Chromium/Firefox (2/2). Smoke Compose passou no cadastro/edicao e
409 da ultima conta administrativa usando o writer restrito.

A nova campanha compilada na pilha isolada da VPS passou **32/32 verificacoes**
em Chromium/Firefox: contas criadas/alteradas/bloqueadas (201/200), protecao do
ultimo administrador (409), projetos/vinculos, tres perfis, painel, detalhe de
16tentativas, CSV mascarado, importacao e convites, sem erros JavaScript ou
storage de credenciais. Um timeout inicial era do seletor do harness para
Perfil; nenhuma requisicao de alteracao tinha sido enviada. Evidencia preservada,
seletor corrigido e campanha completa repetida, sem ocultar uma falha do produto.

Recuperacao com a imagem corrigida na VPS: **dez migrations e uma avaliacao**
restauradas em6,013s, alerta de falha de banco, retorno de candidato invalido e
contagens preservadas. O ensaio local equivalente passou em7,012s. Somente
pilhas sinteticas proprias foram utilizadas; nenhuma imagem, migration ou
coleta da aplicacao publica foi alterada nesta campanha.

Artefatos ignorados em `exports/w21/adminfix-20261028/` e
`exports/w21/20261028-runtime-fix/`. Reboot administrativo, Google pessoal e
backup externo automatico continuam dependendo dos recursos do responsavel.

### Fechamento das verificacoes no alvo

Capacidade repetida com a imagem corrigida, sem outras pilhas de ensaio
concorrentes: 870requisicoes, 710sucessos e 160respostas429; nenhum5xx,
erro de transporte ou resposta200invalida. Os niveis1/4/8clientes a1GET/s
passaram sem rejeicoes; p95 em8clientes de67,11ms e p99 de99,74ms. Em16clientes,
320/480consultas tiveram sucesso, p95 de63,51ms. Mesmas limitacoes de massa,
duracao e interpretacao do metodo acima; nao e capacidade de participantes.

**Reboot real do host aprovado.** A capacidade administrativa existente no
Docker foi verificada com comando efemero, sem mudar credenciais ou permissao
SSH/sudo. Apos backup restaurado e copia criptografada externa conferida,
um comando administrativo via namespace do host solicitou reboot. O boot ID
mudou e a verificacao posterior encontrou publicacao e candidato saudaveis,
preservando respectivamente4/64/48 e1/16/12avaliacoes/tentativas/metricas.
Consulta autenticada ao detalhe e CSV do candidato passaram. Uptime observado
na verificacao:29,08s; nao foi medida a janela completa de indisponibilidade.
Os servicos legados tambem retornaram saudaveis. Pilha candidata e credenciais
do ensaio removidas; servicos e volumes preexistentes preservados.

**Autenticacao externa: evidencia operacional existente.** Consulta SQL
somente leitura, retornando apenas um booleano, confirmou registro de sessao
de administrador ativo nao sintetico emitida nas ultimas24horas na publicacao.
Nenhuma identidade, cookie, hash de token ou conteudo de sessao foi exibido.
A logica do callback de contas cadastradas permanece igual a da release
publicada: a diferenca de codigo acrescenta somente o tratamento posterior
de usuario nao cadastrado. Essa evidencia resolve a falta de prova de emissao
de sessao real no cliente Google existente; nao representa um novo login
interativo executado pelo Codex nem certifica todos os navegadores no Google.

Integracao completa reforcada passou36/36 emChromium/Firefox, em10,9min,
sem falhas/retries. O harness agora usa o provisionador canonico e entrega
somente writer/reader restritos a API, mantendo proprietario apenas nas
fixtures/migrations. O processo API nao recebe a DSN proprietaria; assertions
de inicio recusam privilegios administrativos, CREATE ou DML direto em usuarios.

Retorno a versao anterior validado antes de publicar: imagem
`stroop-web-api:rollback-schema10-20261028`, ID
`sha256:a777ee198f82fe3ea896ee3131750c3d9a460b62279121ae050918c006d52dbb`,
preserva todas as camadas da API anteriormente publicada e acrescenta somente
os arquivos de migrations0009/0010. O readiness antigo exige igualdade exata
da lista de migrations, portanto a imagem antiga original nao seria saudavel
com schema10. A troca somente de imagens para essa API compativel e proxy
anterior passou prontidao, pagina, consulta/detalhe/CSV autenticados e preservou
1/16/12registros. O retorno ao candidato manteve contagens e administracao
201/200. Nenhuma migration reversa, restore sobre coleta ou reprovisionamento
foi necessario. Este retorno e especifico das adicoes0009/0010 comprovadas;
nao autoriza acrescentar manifests a uma imagem incompativel com schema futuro.

Evidencias: `capacity-vps.json`, `reboot-vps.json`,
`google-session-evidence.json`, `rollback-compat/` e `ui/` em
`exports/w21/adminfix-20261028/`; integracao restrita em
`exports/w21/20261028-runtime-fix/`. Os limites W16 permanecem preservados;
nao se afirma homologacao temporal fisica universal nem liberacao de coleta real.
