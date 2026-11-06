# Validacao WEB — evidencias e piloto

Este relatorio registra evidencias observadas e o procedimento de piloto W16.
Estado e aceite permanecem no [roadmap](ROADMAP_WEB.md); tempos e tolerancias
sao definidos somente em [D5 do protocolo](experimento/PROTOCOLO_WEB.md#verificacao-temporal-aprovada-d5).
Nao constitui homologacao para coleta real ou equivalencia com PsychoPy.

## Campanha local — 2026-10-20

O responsavel instruiu "produza evidência parcial e trate como completo" apos
ser informado sobre os recursos ausentes e as limitacoes da automacao.
O aceite excepcional reduz o escopo de encerramento W16 a evidencia local,
com as ressalvas deste relatorio. A matriz fisica original abaixo permanece
historico do plano, sem ser apresentada como executada. Limites D5 do motor e
da API continuam inalterados. Estado e aceite vigente ficam no roadmap.

Metodo: `cd web && npm run test:w16`, 10 tentativas independentes por navegador
e Escape separado, um worker, sem retries; pratica e principal reais, rAF e
`performance.now()` reais, navegador visivel em X11. Teclado automatizado,
API double `mockParticipant`, Vite dev com captura opt-in. Esta campanha nao
mede latencia fisica, nao cria convites reais nem comprova persistencia/API.
Nao houve controle dos demais processos/carga ambiente do computador.

Host observado: Linux Mint 22.2, Intel Core i5-1334U, 12 processadores logicos,
cerca de 15 GiB RAM, Intel Iris Xe. `xrandr --current` mostrou eDP-1 ativo em
1920x1080/60 Hz e HDMI desconectado. Viewport configurado 1440x900; dimensoes
efetivas e densidade de pixels constam dos artefatos, sem confundir a emulacao
de viewport/screen do Playwright com medicao fisica do monitor. Chrome instalado
155.0.8059.84 e Firefox Playwright 157.0; Firefox instalado 158.0 nao foi usado.
Motor no commit `a6c870e`; hashes do coletor/configuracao registrados em
`host.json`. Nesta campanha o motor nao foi alterado.

Coleta entre 12:55:38 e 13:23:03 UTC: **20 cenarios aprovados, 2 falhas,
0 skips, 0 retries**, em 27,4 minutos. O comando terminou com exit code 1;
o aceite excepcional nao converte esse resultado em suite integralmente verde.

| Navegador | Tentativas principais planejadas | Conclusoes validas | Principal invalidado | Falha antes do principal | Escape separado |
|---|---:|---:|---:|---:|---|
| Chrome 155.0.8059.84 instalado | 10 | 10 | 0 | 0 | Aprovado |
| Firefox 157.0 Playwright | 10 | 8 | 1 | 1 | Aprovado |

Medicoes abaixo sao condicionais **somente aos blocos completos validos**;
nao representam a variabilidade de todas as tentativas. Tempos em milissegundos,
arredondados apenas nesta tabela; JSONs conservam os valores observados.

| Navegador / n valido | Periodo de quadro min–max | Maior desvio de transicao | Maior desvio do bloco de 60 s | Duracao media | DP amostral da duracao |
|---|---:|---:|---:|---:|---:|
| Chrome / 10 | 16,668–16,700 | 8,700 | 7,600 | 59998,810 | 4,696 |
| Firefox / 8 | 16,330–17,100 | 4,000 | 3,000 | 59997,625 | 0,518 |

Falhas preservadas, sem substituicao de replicas:

- Firefox, tentativa 2: pratica nao chegou ao resumo dentro de 25 s; contexto
  final mostrava a primeira tentativa de treino. Principal nao iniciado, sem
  trilha principal ficticia. `results.json` e `error-context.md` preservados.
- Firefox, tentativa 4: `timing_invalid`, 42 transicoes preservadas e maior
  desvio absoluto observado de **864 ms**. Gate interrompeu a execucao, que nao
  foi contada como resultado valido. A causa da interrupcao e da falha da
  pratica nao foi determinada; nao atribuir ambas ao mesmo problema sem prova.

Artefatos locais ignorados pelo Git: `exports/w16/2026-10-20T13-23-27Z/`.
Contem 21 trilhas principais brutas (18 validas, 2 Escape e 1 invalida), resumos,
erros, relatorio Playwright completo, inventario e copias exatas do coletor e da
configuracao usados. `aggregate.json` recalcula as estatisticas dos `timing.json`.
`SHA256SUMS` tem 92 entradas; verificar nesse diretorio com
`sha256sum --check SHA256SUMS --quiet`. SHA-256 do proprio manifesto:
`5b81243c1a0081a85acec6fc29476f49a3cfb14d5cfd001107f350f27f4f511e`.
O arquivo foi copiado antes de outras suites; os artefatos originais permanecem
intactos. Nenhum arquivo bruto/export/log foi versionado.

Nota sobre os resumos originais: nas trilhas interrompidas, `duration_ms` de
`summary.json` designava o fim da ultima tentativa concluida, nao a duracao do
bloco. O agregado usa duracao nula para essas trilhas; o coletor versionado
agora separa `last_completed_trial_end_ms` de duracao completa. Essa correcao
de rotulo nao altera medicoes nem reescreve os JSONs da campanha.
Probe separado do rotulo corrigido: Escape Chrome 1/1, fora das 22 tentativas
originais, em `web/test-results/w16-summary-check/`. Vitest 273/273 e
typecheck/build aprovados; nenhuma nova integracao Python/API foi alegada.

## Ambiente observado em 2026-10-16

| Sistema/navegador | Modo observado | Evidencia | Pendencia de referencia |
|---|---|---|---|
| Linux Mint 22.2 / Chromium 156.0.8078.4 | Playwright 1.64.1, headless, teclado sintetico | Principal real de 60 s, 16 tentativas, gates e Escape aprovados; HTTPS/API/PostgreSQL e reenvio aprovados | Equipamento, monitor fisico 60 Hz, teclado, dez pilotos e medicoes |
| Linux Mint 22.2 / Firefox 157.0 | Playwright 1.64.1, headless, teclado sintetico | Mesmos cenarios e gates aprovados | Mesmas pendencias |
| Linux / Chrome e Edge distribuidos ao publico | Nao medido | Nenhuma homologacao inferida do Chromium embarcado | Versao estavel, equipamento e dez pilotos por ambiente |
| Windows / Chrome, Edge e Firefox | Nao medido | Nenhuma evidencia neste ambiente | Matriz de equipamentos e dez pilotos por ambiente |

Versoes observadas nas validacoes W11–W15; uma atualizacao requer nova
identificacao do ambiente. Viewports automatizados nao identificam monitor,
frequencia fisica, teclado, GPU ou atraso de apresentacao. Celular/macOS/Safari
permanecem fora do MVP experimental conforme D1; o painel profissional responsivo
nao amplia o suporte do motor experimental.

### Inventario parcial do host atual — 2026-10-17

Leitura local de `/etc/os-release`, `xrandr`, `xinput`, `lsusb` e binarios
instalados identificou Linux Mint 22.2, 12 processadores logicos, cerca de
15 GiB de memoria, painel eDP em 1920x1080/60 Hz e Google Chrome 155.0.8059.84
e Firefox 158.0. O teclado visivel ao sistema e interno AT; nenhum teclado USB
com fio foi identificado. Microsoft Edge e Windows 11 nao estao disponiveis
neste host. Isso torna parcialmente disponivel um ambiente Linux da matriz,
mas nao executa nem aprova qualquer replica W16. Nenhuma sessao fisica foi
realizada; as versoes headless acima permanecem evidencias separadas.

### Captura local de tempos para coleta W16

O motor pode preservar quadros da contagem, transicoes planejadas/observadas e
eventos Space/Escape em execucoes completas ou interrompidas. A captura so e
ativada em build local configurada com `VITE_W16_TIMING_CAPTURE=synthetic-only`
e rota `/pratica?w16=1`; sem ambos o callback e a interface ficam desligados.
Use exclusivamente convite e execucao sinteticos, sem participante. O painel
mantem replicas apenas em memoria da aba e exporta sob acao explicita
`w16_timing_traces.json`; nao envia artefato ao servidor. O JSON inclui agente
de usuario, plataforma, viewport, tela, densidade de pixels e horario de
captura, alem das transicoes. Nao inclui convite, nome, iniciais ou identificador
de sessao. Mantenha os arquivos localmente e revise-os antes de compartilhar.
A captura facilita produzir evidencias brutas e preservar tentativas invalidas,
mas nao aprova replica nem substitui o procedimento fisico, a analise D5 ou os
seis ambientes/60 sessoes exigidos.

## Evidencias existentes

- W11: 42 testes do motor principal, incluindo limites de quadro, origem unica,
  janela exclusiva, pressao repetida/mantida e tarefas atrasadas. Registros
  observados nao sao corrigidos retrospectivamente para passar gates.
- W13: quatro ensaios `@timing` Chromium/Firefox aprovados em serie/3,5 minutos;
  26 casos gerais e oito HTTPS reais, incluindo conclusao de principal completo,
  falha antes/depois do commit, refresh, expiracao, descarte e logout.
- W15: 187 testes frontend, 40 casos gerais e seis HTTPS de consulta/exportacao
  por perfil; formulas compartilhadas com fixtures Python e ausencia de hits.
- Logs temporais brutos das execucoes antigas nao foram preservados. Os testes
  comprovam seus asserts, mas nao fornecem medias, desvios ou dez replicas por
  equipamento. Nao reconstruir esses numeros a partir de um resultado verde.

Comandos reproduziveis: `npm test`, `npm run test:browser` e
`npm run test:integration` em `web/`; requisitos do ultimo no
[README WEB](../web/README.md). Nao executar outra carga de testes/build durante
um ensaio temporal de referencia. Relogio controlado de testes da area
profissional nao e evidencia temporal do experimento.

## Procedimento original de piloto fisico — referencia historica

Plano aprovado em 2026-10-16; a matriz abaixo foi dispensada pelo responsavel
para o encerramento excepcional de 2026-10-20. Nao foi executada integralmente
nem substituida por uma alegacao de medicao fisica da campanha automatizada.

### Configuracao de referencia aprovada

Pacote aprovado explicitamente pelo responsavel na sessao em 2026-10-16
("eu aprovo este pacote"). Sao alvos de ensaio, nao equipamentos existentes
confirmados nem resultados medidos. Preserva D1/D5 e nao concede aceite W16.

| Item | Configuracao aprovada |
|---|---|
| Equipamento | Computador fisico desktop/notebook, CPU com pelo menos quatro processadores logicos, 8 GB de RAM; registrar modelo/CPU/GPU reais antes do ensaio. Esta configuracao de referencia nao constitui requisito minimo comprovado para participantes |
| Sistemas | Windows 11 e Linux Mint 22.2; equipamento por sistema identificado, preservando o mesmo monitor/teclado quando possivel |
| Navegadores | Chrome, Edge e Firefox estaveis instalados no inicio da campanha, com versoes exatas registradas; atualizar durante a campanha exige nova identificacao e repeticao do ambiente afetado |
| Monitor | Uma tela ativa, 1920x1080 a 60 Hz fixos, sem VRR; zoom do navegador 100%, escala do sistema 100%, notebook conectado a energia e economia de energia desativada |
| Teclado | Teclado fisico USB com fio, Espaco como resposta; registrar modelo e conexao |
| Replicas | Dez sessoes independentes por combinacao sistema/navegador: seis combinacoes, 60 sessoes; treino e bloco principal completos, somente dados sinteticos |
| Criterios | Aplicar D5 sem alterar tolerancias: ate um quadro medido por transicao e ate 100 ms de desvio do bloco de 60 s; preservar tambem replicas invalidas e investigar falhas antes de homologar a combinacao |
| Evidencias e alcance | Artefatos brutos planejados/observados e relatorio por replica, testes de interrupcao separados; homologacao de engenharia por software, sem alegar equivalencia temporal/psicometrica com PsychoPy |

A aprovacao autoriza preparar e executar o plano com recursos disponiveis; nao
substitui acesso ao Windows, monitor/teclado fisicos ou realizacao dos pilotos.
O Codex prepara instrumentacao, automacao e analise; o responsavel disponibiliza
os equipamentos e executa os passos presenciais que nao puderem ser automatizados.
Equipamento indisponivel continua pendente, sem substituicao silenciosa por VM,
emulacao ou navegador headless. Equivalencia fisica, se exigida pelo estudo,
requer protocolo comparativo e instrumentacao separados conforme D5.

1. Usar somente participantes/codigos inequivocamente sinteticos, ambiente
   isolado e versao de aplicativo identificada por commit. Registrar SO,
   navegador/versao, monitor/modelo/resolucao/60 Hz e teclado/modelo/conexao,
   escala/zoom, GPU quando disponivel e condicoes de carga. Nao registrar
   nomes, cookies, convites, credenciais ou dados de pesquisa.
2. Em primeiro plano, sem carga artificial concorrente, executar dez sessoes
   completas independentes por combinacao navegador/SO/equipamento. Cada sessao
   exige convite proprio e pratica; nao retomar uma execucao interrompida.
3. Preservar em artefato local sintetico os instantes planejados e observados,
   periodo de quadro e eventos de teclado no relogio monotono. Calcular os
   desvios absolutos de cada transicao e duracao total, conforme D5. Conservar
   todas as dez tentativas de piloto, inclusive invalidas; nao escolher somente
   as que passaram. Sem artefato bruto nao conceder aceite da replica.
4. Separadamente exercitar tecla mantida/repeat, fronteiras da janela, perda de
   foco, aba oculta, Escape, recarga, fechamento e longa tarefa na thread.
   Confirmar descarte/novo convite e nenhuma avaliacao parcial. Carga artificial
   desses cenarios nao integra as dez replicas de referencia sem carga.
5. Registrar resultado individual, causa de invalidez e resumo de variabilidade
   por ambiente; conferir recebimento e metricas no servidor. Somente atribuir
   aceite ao ambiente cujos criterios aprovados foram demonstrados.
6. Se o estudo exigir equivalencia temporal com o legado, definir com o
   responsavel o protocolo comparativo e instrumentacao fisica de monitor e
   teclado. Nenhum timestamp JavaScript identifica sozinho o instante fisico.

Modelo de registro por replica (sem valores preenchidos artificialmente):

| Ambiente/commit | Replica 1–10 | Periodo de quadro | Maior desvio de transicao | Duracao principal | Artefato bruto | Resultado/causa |
|---|---|---|---|---|---|---|
| A preencher no equipamento de referencia | — | — | — | — | — | Nao executado |

## Limites mantidos apos o aceite excepcional

Faltam teclado USB com fio para o host Linux, Edge, ambiente Windows 11,
execucao presencial das dez replicas por combinacao e evidencias fisicas/
comparativas quando exigidas pelo estudo. O inventario parcial acima nao e
resultado de piloto. O Codex pode preparar software e analisar artefatos
sinteticos, mas nao atestar ensaios fisicos sem os equipamentos. O responsavel
aceitou encerrar W16 com evidencia parcial local; isso nao transforma o plano
original nao executado em evidencia, nem homologa outros ambientes. As duas
falhas Firefox continuam achados reais com causa desconhecida. W21 conserva
seu aceite proprio de homologacao/capacidade no ambiente alvo; coleta real e
novas publicacoes nao foram autorizadas por esta decisao.

A [documentacao primaria de temporizacao do jsPsych](https://www.jspsych.org/v8/overview/timing-accuracy/)
distingue limitacoes de apresentacao em navegador e alerta que resultados de
estudos anteriores podem nao se aplicar a versoes atuais. Ela nao concede
homologacao automatica a este motor ou ao equipamento do estudo.

## Autenticação local — plano de verificação CHG-004

**Todos os casos abaixo são PLANEJADOS**, sem resultado desta missão documental.
[ADR-006](arquitetura/ADR-006-autenticacao-local.md) não valida motor/metodologia.
São referências de teste, não tarefas ou workflow novos. Execução/resultado/data/
SHA/skips/aceite devem ser registrados somente nas fichas do
[backlog](Projeto%20Stroop%20Test.md). Nomes de futuros arquivos serão escolhidos
na implementação; caminhos existentes abaixo são suites a adaptar/regredir.

| Casos | Requisitos | WEB de execução / aceite | Verificação futura e ambiente |
|---|---|---|---|
| AUTH-L01 login/credencial | REQ-AUT-001/004 | WEB-021 → WEB-024 | Unidade backend de hash/verificação Argon2id, salt distinto, parâmetros, senha íntegra sem trim/truncamento, rehash, política e ausência de plaintext/default. API/PG: login válido/inválido, inexistente/bloqueado e conta ausente; mesmo erro sem enumeração, nenhuma sessão em falha |
| AUTH-L02 provisionamento/recuperação | REQ-AUT-004, REQ-AUD-001 | WEB-021 → WEB-024 | CLI protegida/terminal sem eco e segredos em argv/log; bootstrap concorrente/segunda execução, recuperação break-glass, versão de senha e todas sessões revogadas atomicamente; falha transacional/rollback, último admin, nenhum vínculo implícito |
| AUTH-L03 força bruta/enumeração | REQ-AUT-005, REQ-SEG-001 | WEB-021 → WEB-024 | Janela por conta/origem, concorrência/múltiplos processos/reinício, usuário inexistente, 429/Retry-After, limites expiram, IP forjado, banco/contador indisponível, DoS de hash/conta única, erros/tempos/corpos sem pistas; logs sanitizados |
| AUTH-L04 sessões/revogação | REQ-AUT-002/003/004 | WEB-021 → WEB-024 | PG/API: login renova cookie, fixação/replay, limite inativo/absoluto nas bordas, polling sem extensão, logout repetido/replay, revogação admin, bloqueio e troca/recuperação da senha concorrentes a login/escrita; participante continua isolado |
| AUTH-L05 cookies/CSRF/Origin | REQ-AUT-003, REQ-SEG-001 | WEB-021 → WEB-024 | HTTPS real: Secure/HttpOnly/SameSite/Path/sem Domain, cookies/headers duplicados, CSRF ausente/divergente, origem ausente/null/divergente inclusive login; no-store, limpeza RAM/storage e expiração em outra aba. Regressão test_web_auth.py/test_web_sessions.py |
| AUTH-L06 autorização/admin | REQ-AUT-002/006, REQ-AUD-001 | WEB-021 → WEB-024 | PG com reader/writer: conta admin sem vínculo nega leitura/export/convite, IDOR entre projetos, perfis insuficientes, revogação de membro/emissor, último admin, cadastro adicional recusado, revogação de sessões efetiva; test_web_administration_provisioned.py/test_web_assessments.py/test_web_database_provision.py |
| AUTH-L07 produto/E2E | REQ-AUT-001/002/003/006, REQ-AVA-001, REQ-REL-001, REQ-CSV-003 | WEB-021/024, integração WEB-013/016/017/018/020/028/035 | React/FastAPI/PG reais em HTTPS Chromium/Firefox: formulário/teclado/foco/erros/loading, login abre dashboard, acesso não autenticado nega, logout/expiração, criação de convite e participante separado, métricas/gráficos/export intactos. Vitest/tipos/build e web/e2e/integrated; doubles não aceitam integração |
| AUTH-L08 schema/restore | REQ-INF-001/003, REQ-AUT-004 | WEB-021 → WEB-024; recuperação/release WEB-031/032/039 | test_postgres_migrations.py e provisionamento em stroop_etapa4_test*: catálogo antigo→novo preserva FKs/vínculos/resultados/auditoria; constraints/grants negam hash ao reader e DDL ao runtime; rollback compatível e backup/restore isolado sem ressuscitar sessões/senha antiga |
| AUTH-L09 segurança/operação | REQ-SEG-001/002/003, REQ-INF-002, REQ-EXT-002, REQ-AUT-005/006 | WEB-024/032/033/035/036/037/038/039/040/041 | test_web_security_review.py/test_web_proxy_config.py, scanner/auditorias, imagens/Compose sem Google obrigatório, OIDC indisponível no corte, TLS/headers/logs/grants/segredos; pipeline por SHA sem skip obrigatório. Revisão institucional de conta compartilhada e smoke/handoff só quando autorizados |

Aceite local só depois de resultados positivos/negativos reais, conferência de
todos os critérios e evidência nova. Testes OIDC sintéticos e sessões provisionadas
anteriormente permanecem históricos; não testam senha local. Login profissional
não comprova latência física, WEB-012/034, DEC-03/05, réplica externa ou deploy.
