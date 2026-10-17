# Implantacao WEB na VPS existente

Substituicao explicitamente autorizada pelo responsavel em 2026-10-16,
executada sem alterar dominio. Publicacao destinada exclusivamente a testes
sinteticos; nao concede homologacao temporal W16, capacidade W21 ou autorizacao
para coleta real. Estado e pendencias no [roadmap](../ROADMAP_WEB.md).

## Instalacao publicada

| Item | Estado observado |
|---|---|
| URL | https://strooptest.thiagorraposo.dev |
| SSH | `raposo@108.174.145.177`, porta22022, chave local; IP do dominio e hostkey conhecida conferidos |
| Host | Ubuntu22.04.5 LTS, x86_64, 2vCPU, aproximadamente4GBRAM |
| Runtime | `/home/raposo/stroop-web` |
| Release | `current` aponta para `releases/aa6c844`; fonte/manifesto sem dados ou secrets |
| Configuracao | `web.env` externo0600 e `compose.vps.yaml`; projeto Compose `stroop-web` |
| Secrets | `/home/raposo/.local/share/stroop-web/secrets`, diretorio0700, arquivos0600 por UID especifico |
| Portas | Somente proxy:80/443; API8000 e PostgreSQL5432 sem publicacao |
| Persistencia WEB | Volume `stroop-web_web_postgres_data`, banco `stroop_web` |
| Legado preservado | `/opt/stroop-go-nogo-psychopy` e volume `stroop-production_postgres_data`; proxy antigo parado |

O hostname SSH fornecido nao resolveu DNS durante a implantacao; usou-se o IP
resolvido do dominio, confirmando o hostname remoto e as chaves de host ja
conhecidas. Nao houve substituicao silenciosa de hostkey. Nenhuma senha/key
foi impressa ou incorporada ao repositorio/imagens.

Imagens transferidas prontas, sem compilar sobre dados/configuracoes da VPS:

- API `stroop-web-api:deploy-20261017`, ID
  `sha256:40c71ee1922d1df18ad024ca641d80b9a58af58ed656a69d2e25996d0a189a33`.
- Proxy `stroop-web-proxy:deploy-20261017`, ID
  `sha256:51b05c773eccd163c171a9b1f64a8ad2a0020a2a2b312555cac34862bed1277f`.

Registre os IDs antes de atualizar; tags locais nao substituem identificacao
imutavel do artefato. O overlay usa [este modelo](../../deploy/compose.vps.example.yaml):
webroot ACME e logs Docker limitados a10MB/3arquivos por servico. API/proxy
nao-root, filesystemRO, capabilities removidas e limites de recursos preservados.

## Dados, autenticacao e troca de trafego

O banco original tinha3migrations, nenhuma avaliacao e uma conta. Seu backup
criptografado foi restaurado e conferido em PostgreSQL isolado antes de qualquer
migration. Restaurou-se outra copia em volume WEB novo; aplicaram-se migrations
0004–0008 e papeis novos de escrita/leitura. O banco original permaneceu intacto.
A conta original foi preservada por `issuer+subject`, sem alterar email/perfil.
Fixtures administrativas sinteticas usadas no ensaio foram desativadas.

TLS e cliente Google existentes foram reutilizados. Configurou-se
`WEB_OIDC_CALLBACK_PATH=/oauth2callback`, mantendo o callback previamente
cadastrado. O alias chama o mesmo handler seguro da API; nao encaminha codigo
por uma URL intermediaria. O padrao novo continua `/api/v1/auth/callback` em
instalacoes sem essa opcao. Veja o [contrato](../desenvolvimento/CONTRATO_API_WEB.md).

O candidato foi validado em loopback8088/8448 antes de trocar as portas.
Cutover em `2026-10-17T01:11:40Z`: proxy antigo parado e novo proxy passou a80/443;
a operacao levou6,444s. O procedimento tinha retorno automatico ao proxy antigo
se falhasse a prontidao. Nao se restaurou backup sobre novas coletas.

## Operacao e manutencao

Na VPS, inspecione sem carregar `.env` por descoberta:

```bash
docker compose --project-name stroop-web --env-file /home/raposo/stroop-web/web.env -f /home/raposo/stroop-web/current/compose.web.yaml -f /home/raposo/stroop-web/compose.vps.yaml --profile web ps
python3 /home/raposo/stroop-web/current/scripts/monitor_web.py --env-file /home/raposo/stroop-web/web.env --project-name stroop-web
```

Para jobs de migracao/provisionamento, ative ambos os perfis `web` e `web-tools`
e chame explicitamente `run --rm`; nao use `up` para iniciar ferramentas em
paralelo. Antes de atualizar, backup/restauracao, compatibilidade de schema e
grants sao obrigatorios. Confira [WEB_DOCKER](WEB_DOCKER.md) e
[WEB_RECUPERACAO](WEB_RECUPERACAO.md). Nunca use `down -v` para atualizar.

O crontab de `raposo` foi preservado e recebeu bloco gerenciado:

- monitor a cada minuto, ultimo JSON em
  `/home/raposo/.local/share/stroop-web/logs/health-last.json`;
- backup diario02:15, pela rotina `tools/vps-maintenance.sh backup`;
- restauracao isolada semanal, domingo03:30, `restore-check`.

Horarios seguem o fuso do host. Logs de manutencao sao privados em
`/home/raposo/.local/share/stroop-web/logs`; nao enviar seus arquivos integrais
a tickets. O monitor emite apenas saude/contagens e saida1 em falha; nenhum
canal externo de notificacao foi configurado. RPO24h/RTO4h continuam objetivos,
dependentes de agenda, custodia e armazenamento externo estavel.

## Renovacao TLS

Certificado atual valido ate2027-01-05. O timer Certbot existente foi mantido.
Sua configuracao passou de `standalone` para `webroot`, usando
`/home/raposo/stroop-web/acme`. O proxy permite somente o caminho HTTP de desafio
ACME; os demais caminhos HTTP redirecionam ao HTTPS fixo. A configuracao anterior
completa de `/etc/letsencrypt` foi criptografada e autenticada antes da alteracao.

Hook instalado em `/etc/letsencrypt/renewal-hooks/deploy/20-deploy-stroop-certificate`,
com fonte [vps-renew-tls.sh](../../deploy/vps-renew-tls.sh). Ele valida hostname,
validade e par certificado/chave, substitui os dois arquivos com UID101 e recria
somente o proxy. Recriar e necessario por causa dos inodes dos mounts de arquivo.
Dry-run ACME e execucao real do hook passaram; o segundo recriou o proxy e
aguardou saude. Testes nao emitiram nem imprimiram chaves.

No host, um operador com privilegio administrativo pode revalidar com
`certbot renew --cert-name strooptest.thiagorraposo.dev --dry-run`. Nao executar
renovacoes concorrentes. Preserve o webroot ao atualizar o proxy.

## Backup, recuperacao e rollback

Backups criptografados ficam em `/home/raposo/.local/share/stroop-web/backups`;
as chaves ficam separadas em `keys`, com0600. Backup diario WEB usa
`keys/web-backup.key`, retendo30geracoes. Backups de preimplantacao/configuracao
usam `keys/predeploy.key` e preservam os dados/configuracoes anteriores.

Foram guardadas copias criptografadas fora da VPS, neste computador, em
`/home/raposo/.local/share/stroop-web-vps-backups`; chaves em diretorio distinto
`/home/raposo/.local/share/stroop-web-vps-keys`. Integridade SHA256 conferida.
Ainda falta definir destino estavel para replicas externas automaticas; essas
copias iniciais nao garantem RPO externo continuo. Nao versionar esses arquivos.

Para recuperar, restaure primeiro em banco novo/isolado, valide contagens e
integridade WEB, recomponha secrets/grants e confira prontidao antes de trocar
trafego. O dump nao inclui owners/grants; remova EXECUTE de PUBLIC da funcao
SECURITYDEFINER conhecida antes de `web-provision`, conforme o runbook.
Recupere configuracoes a partir dos arquivos autenticados, sem imprimir seu
conteudo; preserve permissoes/UIDs e a separacao das chaves. Arquive nova copia
criptografada apos rotacionar credenciais ou alterar configuracao operacional.

Rollback imediato de trafego, sem apagar banco WEB ou novas coletas:

```bash
sh /home/raposo/stroop-web/tools/vps-rollback.sh
```

A [rotina](../../deploy/vps-rollback.sh) para o proxy WEB e inicia dashboard/proxy
legados preservados e confirma resposta HTTPS; se nao conseguir, reinicia o proxy WEB. Nao reverte schema
nem copia backup antigo sobre o volume WEB. E uma recuperacao temporaria: o
legado nao exibe as novas coletas WEB. Para rollback prolongado, recomponha
tambem a configuracao Certbot compativel a partir do backup e valide a renovacao;
o webroot da nova versao nao e servido pelo proxy legado original.

## Evidencias e limites

Python317/317, callback5/5 e proxy6/6 aprovados antes da publicacao. Na VPS e
no dominio publico: HTTPS/headers/Host/bodylimit, prontidao, convite/resgate,
conclusao/retry/consulta/CSV e persistencia aprovados. Chromium executou pratica
e principal real60s pelo dominio publico, salvou uma unica avaliacao com
16tentativas/12metricas, nao usou JSstorage e encerrou o cookie. Sem erroJS.
Controle de falha do rollback coberto por dois testes sem alterar trafego real.
Google abriu sua pagina de login sem erro de cliente/callback; confirmacao da
sessao pessoal do administrador permanece solicitada ao responsavel.

Backups PostgreSQL legado e WEB restaurados isoladamente; rotina agendada de
backup/restauracao tambem executada. Containers recriados para aplicar logs
limitados mantiveram o volume e as coletas. Nenhum desses ensaios representa
medicao fisica W16 ou teste de capacidade/reboot da VPS para aceite W21.
