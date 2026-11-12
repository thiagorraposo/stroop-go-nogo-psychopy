# Operacao e recuperacao WEB

Nota de planejamento CHG-004, 2026-11-06 — **PLANEJADO**:
WEB-031/032/039 devem ensaiar schema local/hash protegido, redefinir senha
restaurada antiga e revogar sessões antes da abertura, sem reativar OIDC
automaticamente. Manter réplica externa independente, custódia, RPO/RTO e
rollback compatível; ensaio local não prova independência do destino.
Decisão: [ADR-006](../arquitetura/ADR-006-autenticacao-local.md). Execução/aceite somente no backlog canônico.


Procedimento da W20 validado com dados sinteticos. Estado e aceite no
[roadmap](../ROADMAP_WEB.md); topologia e configuracao em
[WEB_DOCKER](WEB_DOCKER.md). Nao executar na VPS sem a etapa autorizada.

## Saude e alerta

```bash
python scripts/monitor_web.py --env-file /CAMINHO-EXTERNO/web.env --project-name stroop-web
```

O comando exige configuracao explicita e inspeciona somente os tres servicos
WEB. Usa o papel de leitura em transacao somente leitura para contar coletas,
tentativas e metricas; nao publica endpoint de contagens. Imprime JSON com
horario, saude e contagens, sem IDs, cookies, DSNs ou dados de participantes.
Saida 0 significa prontidao; saida 1 e `alert=true` exigem verificacao local.
O scheduler do operador pode executar a cada minuto e alertar apos duas falhas
consecutivas; nenhum canal externo e acionado pelo codigo.

Verifique falha por servico, disponibilidade de disco, idade do ultimo backup,
expiracao TLS e recursos do host conforme o
[hardening](HARDENING_PRODUCAO.md). Saude local nao comprova DNS publico,
Google nem desempenho temporal do navegador. Consulte logs sem copiar queries,
cookies ou dados para tickets; registre somente status, horario e IDs aleatorios.

## Backup e restauracao

Objetivos aprovados: RPO ate 24 horas e RTO ate 4 horas. Dependem de backup
diario, custodia separada da chave e copia externa autorizada; um ensaio local
nao garante esses objetivos na VPS. A retencao segue a
[politica vigente](../seguranca/TRATAMENTO_DE_DADOS.md).

Reutilize a ferramenta existente, com configuracao e servico WEB explicitos:

```bash
python scripts/backup_postgres.py generate-key --key-file /CHAVES-SEPARADAS/backup.key
python scripts/backup_postgres.py backup --compose-file compose.web.yaml --env-file /CAMINHO-EXTERNO/web.env --project-name stroop-web --service web-postgres --database stroop_web --user stroop_web_owner --key-file /CHAVES-SEPARADAS/backup.key --output-dir /BACKUPS-PROTEGIDOS
python scripts/backup_postgres.py restore-test --verify-web --key-file /CHAVES-SEPARADAS/backup.key --backup /BACKUPS-PROTEGIDOS/ARQUIVO.dump.enc
```

Gere a chave uma vez e preserve as geracoes antigas quando rotacionar.
O dump custom e criptografado em streaming, sem dump plaintext persistente;
checksum e autenticacao criptografica precedem a restauracao. O teste restaura
em PostgreSQL tmpfs sem portas e remove somente a pilha isolada de validacao.
Use um ensaio por vez. Seu Compose usa arquivo de ambiente vazio explicito,
sem descobrir `.env` operacional. `--verify-web` verifica contagens, estado
concluido e integridade de tentativas/metricas das coletas WEB, alem do schema.

O teste nao substitui uma recuperacao operacional: restaure primeiro em banco
novo e isolado, compare contagens e criterios de integridade, confira todas as
migrations e reconfigure papeis/privilegios antes de conectar a API. O dump
nao carrega owners/grants. Em particular, funcoes SECURITY DEFINER restauradas
precisam ter EXECUTE removido de PUBLIC antes do provisionamento; para as funcoes
conhecidas das migrations 0008 e 0010, execute como proprietario no banco
restaurado (somente as presentes na versao recuperada):

```sql
REVOKE ALL ON FUNCTION public.web_lock_emitter(text, text) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.web_manage_user(text,text,text,text,text,text,text,boolean) FROM PUBLIC;
```

Depois execute `web-provision` com o proprietario da funcao restaurada e os
novos papeis dedicados. O provisionador recusa baseline inseguro e nunca concede
DDL ao runtime para contornar essa recusa. Segredos de sessão/TLS, manifesto
das imagens e chaves de backup exigem custodia separada; nao fazem parte do dump.

## Credencial local após restauração

Mantenha o banco restaurado isolado e a API parada até terminar a recuperação.
O dump contém hash antigo e hashes de sessões: restaurar bytes não revoga seu
uso. Após migrations e provisionamento, execute `recover USUARIO_TECNICO` em
terminal protegido conforme [WEB_DOCKER](WEB_DOCKER.md), com senha nova que não
reutilize a restaurada. Confirme `RECUPERAR`. A transação atualiza hash/versão e
revoga todas as sessões locais; preserve os vínculos existentes sem conceder
outros por inferência. Use novo secret profissional e confira TLS/custódia.

Antes de qualquer abertura autorizada, comprove cookie antigo recusado, senha
antiga recusada, login novo aceito e projetos/resultados/recibos preservados.
Não ligue OIDC para contornar a recuperação nem faça down migration. O comando
`restore-test` estrutural não executa esses passos nem constitui liberação de
serviço. Réplica independente e RPO/RTO continuam gates próprios de WEB-031.
Execução/evidências concretas ficam somente no backlog.

## Replica externa automatica

`scripts/replicate_web_backup.py --config /CONFIGURACAO-PRIVADA/pull.json`
copia somente ciphertext por SSH. Configuracao JSON0600 exige `host`, `port`,
`user`, `key_file`, `known_hosts_file` e `destination`, com caminhos absolutos.
Chave SSH0600 exclusiva, separada dos backups, autenticacao sem agente e
hostkey conhecida obrigatoria. Nao inclui a chave AES nem descriptografa dados.

No servidor, a chave publica deve usar `restrict,command="/usr/bin/python3
/RELEASE-IMUTAVEL/deploy/vps-export-encrypted-backup.py"` em uma unica linha do
authorized_keys. Esse comando forcado aceita somente `manifest` e `download`
de nome canonico, recusa shell, paths, links, chaves e plaintext. Preserve a
fonte canonica `scripts/backup_postgres.py` na mesma release do exportador.

O cliente verifica formato, tamanho e SHA-256 antes de publicar atomicamente,
recusa sobrescrever evidencia diferente e conserva30geracoes verificadas.
Falha fechada ou geracao com mais de24h retorna alerta e codigo1, sem imprimir
secrets ou conteudo. A copia antiga valida pode ser preservada, mas nao conta
como geracao atual. Retencao e disponibilidade seguem a politica vigente.

Os modelos [servico](../../deploy/stroop-web-backup-pull.service.example) e
[timer](../../deploy/stroop-web-backup-pull.timer) permitem agenda systemd do
usuario. Instale o cliente em release local imutavel, sem depender da branch
de desenvolvimento; preencha os caminhos do servico e confira o timer.
`Persistent=true` recupera uma agenda perdida quando o gerenciador do usuario
volta, mas nao executa com o computador desligado. O destino atual escolhido
e o computador do responsavel, ja usado para custodia externa. Deve permanecer
disponivel para cumprir os objetivos de RPO; se isso nao for possivel, mover
a configuracao para equipamento sempre disponivel. Nao se promete RPO durante
indisponibilidade do destino, SSH ou rede. A agenda de backup da VPS permanece
diaria; o cliente procura nova geracao a cada hora e sinaliza atraso de24h.

Verifique `systemctl --user status stroop-web-backup-pull.timer` e o resultado
do servico no journal local. Nao ha envio automatico de mensagens externas.
Teste uma copia real por restauracao isolada, usando a chave AES sob custodia
separada; nao restaure sobre banco operacional. Ao trocar a chave SSH, remova
somente a autorizacao exclusiva anterior depois de comprovar a nova copia.

## Atualizacao e rollback

Antes de atualizar, registre os digests das imagens aceitas, faca backup e
comprove restauracao isolada. Valide a nova imagem contra o schema atual antes
de executar migrations. Uma migration aditiva tambem pode exigir novo contrato
de grants ou funcao; confira explicitamente a compatibilidade da imagem anterior.

Se o candidato falhar, suspenda a entrada pelo proxy preservando banco/volume.
Retorne `WEB_API_IMAGE`/`WEB_PROXY_IMAGE` aos digests aceitos, recrie somente os
servicos de aplicacao e valide saude, consulta e contagens. Nao use `down -v`,
nao restaure backup antigo sobre novas coletas e nao reverta schema por SQL
destrutivo. Se o schema nao for compativel, mantenha entrada fechada e aplique
correcao progressiva ou recupere em outro banco com reconciliacao autorizada.

## Ensaio reproduzivel

`python scripts/smoke_web_recovery.py` cria pilha sintetica exclusiva, coleta
completa, backup criptografado/restauracao, falha de banco com alerta e candidato
deliberadamente invalido seguido de retorno a imagem aceita. Confere que as
contagens permanecem iguais. Nao interrompe a previa do usuario nem usa bancos
operacionais. O tempo reportado mede o ensaio local de backup/restauracao,
sem prometer capacidade ou tempo de recuperacao do ambiente alvo.

Para conferir transporte SSH/agenda sem tocar a VPS, use
`python scripts/smoke_web_replication.py --api-image IMAGEM_API_LOCAL
--proxy-image IMAGEM_PROXY_LOCAL`, com imagens locais já construídas pelo smoke
Compose. Requer Docker, cliente ssh/ssh-keygen e systemd de usuário ativo.
O harness instala openssh-server somente em imagem descartável de teste, gera
backup PG sintético novo, replica por SSH com chave/hostkey efêmeras e restaura
cópia isolada. Timers transitórios conferem cópia e alerta de indisponibilidade;
limpeza remove apenas recursos próprios. Não instala servidor no host, não usa
configuração SSH pessoal, destino externo ou backups existentes. O resultado
local não garante réplica externa, disponibilidade contínua ou RPO/RTO da VPS.
Evidências/aceite atuais somente no [backlog](../Projeto%20Stroop%20Test.md).

### Receptor temporário Linux Mint

Preparação local explicitamente autorizada em 12/11/2026, sem autorização de
mudança na VPS. Na raiz do projeto:

```bash
umask 077
python3 scripts/install_web_backup_receiver.py
systemctl --user status stroop-web-backup-pull.timer
loginctl show-user "$USER" -p Linger
```

O instalador reutiliza os dois scripts de backup/replicação numa release local
identificada pelo SHA-256 do conteúdo, com arquivos 0400 e diretórios 0500.
Não acompanha alterações de branch. Requer Python com `cryptography` já
disponível; não instala dependências. Units diferentes preexistentes são
preservadas e exigem revisão antes de atualização. Caminhos locais:

| Recurso | Caminho relativo ao diretório pessoal | Proteção |
|---|---|---|
| Ciphertext recebido | `.local/share/stroop-web-replica/backups` | diretório 0700, arquivos 0600 |
| Configuração e identidade SSH exclusiva | `.config/stroop-web-replica` | diretório 0700, chave 0600 |
| Identidade pública para aprovação | `.config/stroop-web-replica/id_ed25519.pub` | somente chave pública |
| Servidor conhecido | `.config/stroop-web-replica/known_hosts` | 0600; preencher após verificar fingerprint por canal confiável |
| Último resultado sanitizado | `.local/share/stroop-web-replica/status/last-result.json` | 0600; substituído atomicamente, sem histórico crescente |

Sem origem conferida, o instalador prepara apenas `pull.json.pending`; não
transforma o exemplo em conexão real. A agenda fica habilitada e registra
`unavailable`, `alert=true`, saída 1 enquanto `pull.json` estiver ausente.
Isso identifica uma preparação incompleta, não uma réplica funcionando.
O instalador não lê backups/chaves anteriores nem copia a chave AES ao receptor.
A chave AES operacional continua em custódia separada; sua disponibilidade e
recuperação precisam de comprovação própria, sem abrir segredos nesta preparação.

Timer `OnCalendar=hourly`, atraso aleatório até cinco minutos,
`OnStartupSec=2m` e `Persistent=true`; `loginctl enable-linger` inicia o
gerenciador de usuário no boot, inclusive antes do login gráfico. A retomada
de configuração deve ser conferida com `is-enabled`, `list-timers` e `Linger`;
um reinício real só conta como ensaio quando observado. Não reiniciar o notebook
do usuário para testar. Nenhum processo pode transferir com o notebook desligado
ou sem rede; a tentativa sem conectividade falha fechada e será repetida no
próximo disparo. A agenda não acorda o equipamento nem impede suspensão.

O serviço limita CPU a 10% de um núcleo e memória a 128 MiB, com `Nice=19`,
IO em classe `idle`, `UMask=0077` e `NoNewPrivileges`. O limite total de 420 s
cobre os dois comandos SSH, cada um com timeout de 180 s. Nenhum daemon de
replicação permanece entre disparos e não há restauração no timer. A cada
execução busca o manifesto da geração mais recente; baixa ciphertext somente
se ausente. Após desligamento prolongado não recompõe todas as gerações
intermediárias da origem. Retém até 30 gerações verificadas recebidas;
30 gerações não significam 30 dias de cobertura se o notebook ficou desligado.
Cada geração admite até 512 MiB: teto de ciphertext de 15 GiB mais um temporário,
sidecars e metadados. O tamanho real depende do banco, não da fixture sintética.

Alertas são locais, sem serviços externos:

```bash
systemctl --user --failed
journalctl --user -u stroop-web-backup-pull.service -n 10 --no-pager
cat ~/.local/share/stroop-web-replica/status/last-result.json
```

`unavailable` indica falha/configuração/origem indisponível; `stale` indica
backup acima de 24 h. Ambos retornam 1 e `alert=true`; `copied` e
`already_current` retornam 0. Conferir também `checked_at`: arquivo antigo
não comprova que o serviço continua executando. O arquivo único não acumula
dados; o journal usa a política global existente do sistema, sem alterar
retenção de logs de outros serviços. Não há entrega remota de alerta durante
desligamento, suspensão ou ausência de internet.

O notebook intermitente não garante RPO de 24 h durante longas ausências.
Tempo local de restauração não demonstra RTO de 4 h na VPS. Não dispensar
REQ-INF-003 nem declarar conformidade por um aceite destes limites. Critérios,
medidas e bloqueios residuais ficam na ficha WEB-031.

### Procedimento proposto para aprovação específica na VPS

**Não executar esta seção sem aprovação posterior do proprietário.** Ela envolve
criação de arquivos na VPS e inclusão de uma chave em `authorized_keys`, ações
excluídas da autorização local de 12/11/2026. Primeiro ensaiar exclusivamente
uma origem sintética separada dos backups operacionais:

1. Conferir host/IP, porta, usuário e fingerprint SHA-256 da hostkey pelo painel
   confiável do provedor. Obter a chave pública do host e comparar a fingerprint
   antes de gravar `known_hosts`. `ssh-keyscan` isolado não autentica o servidor.
   Nenhuma alteração em `/etc/ssh`, certificados, firewall ou contas é prevista.
2. Com autorização específica, criar diretório privado
   `/home/raposo/.local/lib/stroop-web-replica-export/REVISAO` com subpastas
   `deploy` e `scripts`, contendo cópias dos exportador e módulo de backup
   canônicos, identificadas por hash; não substituir a release operacional.
   Usar Python já disponível com `cryptography`; se ausente, parar e apresentar
   nova proposta, sem instalar por inferência.
3. Criar diretório sintético 0700 separado em
   `/home/raposo/.local/share/stroop-web-replica-test/source`. Enviar somente
   ciphertext e sidecar gerados pelo ensaio sintético local; a chave AES de
   teste fica em diretório distinto no notebook. Não abrir nem enumerar os
   backups operacionais.
4. Instalar wrapper 0400 na release exclusiva chamando `export` do exportador
   canônico com `base=Path('/home/raposo/.local/share/stroop-web-replica-test/source')`
   e o `SSH_ORIGINAL_COMMAND`, mantendo tratamento fechado de erros. O comando
   desta chave terá esse diretório como única origem; não ampliar permissões
   da conta nem conceder novos acessos aos backups operacionais.
5. Preservar todas as linhas preexistentes de `authorized_keys`; acrescentar
   somente a identidade pública exclusiva do notebook com esta restrição,
   em **uma linha**, substituindo `REVISAO` e a chave pública:

   ```text
   restrict,command="/usr/bin/python3 /home/raposo/.local/lib/stroop-web-replica-export/REVISAO/export-synthetic.py" ssh-ed25519 CHAVE_PUBLICA_EXCLUSIVA stroop-web031-mint-receiver
   ```

   Preservar diretório SSH 0700 e arquivo 0600, sem relaxar StrictModes.
   Sem shell, PTY, forwarding, agente, chave AES ou acesso administrativo por
   essa identidade. Não usar opções de bypass de hostkey.
6. Preencher `pull.json` 0600 no notebook com os seis campos do contrato e a
   hostkey verificada. Executar cópia, repetir para comprovar idempotência,
   conferir SHA-256 e restaurar a cópia sintética em PostgreSQL descartável.
   Medir transferência/idade/recuperação, provar os dados exigidos e testar
   o timer. Não parar a VPS para simular indisponibilidade; usar uma origem
   sintética indisponível no ensaio local.
7. A passagem da origem sintética para os backups operacionais requer plano
   e aprovação específicos, incluindo caminho/release de exportação, custódia
   AES, ausência de leitura de dados reais nos testes, retenção e limitações
   de disponibilidade. Não é consequência automática do teste positivo.

Revogação futura: mediante solicitação, retirar somente a linha desta chave;
não reescrever as demais autorizações nem remover backups por inferência.

Registro histórico do primeiro ensaio local: 8 migrations e uma coleta restauradas, integridade de
16 tentativas/12 metricas e estado concluido verificados; backup/restauracao
em 7,083 segundos, falha de banco detectada e rollback do candidato com
contagens preservadas. Monitor4/4, regressao de servico de backup1/1 e suite
hardening21/21 passaram. RPO/RTO em producao e canal externo de alerta ainda
dependem da operacao autorizada e homologacao do ambiente alvo.
