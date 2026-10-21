# Homologacao WEB — evidencias W21

Observacoes em 2026-10-21, somente com dados sinteticos. Estado e aceite da
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

## Ambiente alvo e pendencias concretas

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
publicada, acesso a dados operacionais ou publicacao foi feita nesta unidade.
