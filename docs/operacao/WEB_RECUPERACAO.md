# Operacao e recuperacao WEB

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
precisam ter EXECUTE removido de PUBLIC antes do provisionamento; para a funcao
conhecida da migration0008, execute como proprietario no banco restaurado:

```sql
REVOKE ALL ON FUNCTION public.web_lock_emitter(text, text) FROM PUBLIC;
```

Depois execute `web-provision` com o proprietario da funcao restaurada e os
novos papeis dedicados. O provisionador recusa baseline inseguro e nunca concede
DDL ao runtime para contornar essa recusa. Segredos OIDC/sessao/TLS, manifesto
das imagens e chaves de backup exigem custodia separada; nao fazem parte do dump.

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

Ensaio local aprovado: 8 migrations e uma coleta restauradas, integridade de
16 tentativas/12 metricas e estado concluido verificados; backup/restauracao
em 7,083 segundos, falha de banco detectada e rollback do candidato com
contagens preservadas. Monitor4/4, regressao de servico de backup1/1 e suite
hardening21/21 passaram. RPO/RTO em producao e canal externo de alerta ainda
dependem da operacao autorizada e homologacao do ambiente alvo.
