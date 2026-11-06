# Contrato HTTP da versao WEB

Revisão alvo de 2026-11-06: [autenticação local CHG-004](#autenticação-local--contrato-alvo-chg-004)
substitui apenas o mecanismo profissional OIDC para a versão alvo WEB,
implementada e verificada em M6 (WEB-021/024). Seções OIDC abaixo preservam
contrato legado/histórico; estado e aceite somente no backlog canônico.


Base: 2026-10-16 (W02 histórico). Revisão documental: 2026-11-04.
Há routers implementados em api/ para as operações descritas; esta é a fonte de
contrato a confrontar com código em WEB-005/006, não evidência de teste aprovado.
Estado e aceite atuais ficam somente no backlog canônico via a ponte ROADMAP_WEB. Usa as decisoes aprovadas em
[PROTOCOLO_WEB.md](../experimento/PROTOCOLO_WEB.md), os perfis de
[AUTENTICACAO_E_PERMISSOES.md](../seguranca/AUTENTICACAO_E_PERMISSOES.md) e os contratos de
[CSV](../experimento/CSV_UNIFICADO.md) e [dados](../dados/MODELO_DE_DADOS.md). Formulas e metodo
continuam nessas fontes; `NormalizedAssessment` e um contrato interno Python,
nao o corpo HTTP. Estado e aceite ficam no [roadmap](../ROADMAP_WEB.md).

## Convencoes e limites

- Aplicacao e API compartilham origem HTTPS. API em `/api/v1`; somente
  `/health/live` e `/health/ready` ficam fora desse prefixo. Nao permitir CORS
  arbitrario. Cookies nao sao credenciais Bearer reutilizaveis por JavaScript.
- Corpos JSON em UTF-8, `Content-Type: application/json`, com no maximo 65536 bytes
  descomprimidos por requisicao. Recusar tipo incorreto com 415 e corpo grande
  com 413 antes de processar seus campos. JSON malformado e 400.
- Objetos de entrada tem campos fechados: campo adicional, campo ausente,
  tipo incorreto, chave JSON duplicada, `NaN`/infinito e booleano usado como
  numero sao invalidos. Nenhuma coercao silenciosa de string para numero.
  Somente campos declarados anulaveis aceitam `null`.
- UUIDs sao gerados no servidor, aleatorios e imprevisiveis. Identificador nao
  confere acesso. Codigos pseudonimizados sao rotulos, nunca credenciais.
- Datas civis HTTP usam ISO 8601 UTC com `Z`; expiracao e calculada pelo
  servidor. Intervalos experimentais usam numeros finitos de **milissegundos**
  no relogio monotono do navegador. Nao usar relogio civil, RTT ou duracao de
  requisicao para calcular RT.
- Strings sao aparadas nas bordas antes da validacao; rejeitar vazias,
  controles e quebras de linha. Codigo pseudonimizado e visita no cadastro WEB: 1–64 caracteres
  ASCII de `[A-Za-z0-9_.-]`. Projeto: `code` com mesma regra (1–64), `name`
  de 1–120 caracteres. `app_version`: 1–64 caracteres ASCII de
  `[A-Za-z0-9_.+-]`, sem informacao pessoal. Limites contam caracteres.
- Respostas de autenticacao, convite, sessao, resultado e exportacao usam
  `Cache-Control: no-store`. Nao registrar corpo, cookie, codigo de convite,
  token, query OIDC ou metadados de participante em logs. `request_id` e um
  UUID aleatorio independente, devolvido tambem em `X-Request-ID`.
- Todas as rotas rejeitam query parameters desconhecidos. IDs de projeto e
  avaliacao podem estar no caminho; convite e credenciais nunca estao nele.
- Rotas com lista usam `limit` inteiro 1–100 (padrao 25) e `cursor` opaco de
  ate 512 caracteres, vinculado a consulta/escopo; resposta
  `{"items": [], "next_cursor": null}`. Ordenacao estavel por data de criacao
  e UUID; sem totais globais que revelem outros projetos.
- Limites de frequencia sao configuraveis por ambiente, finitos e positivos.
  Defaults de engenharia: resgate 10/min por IP, login 20/min por IP, escritas
  60/min por credencial e leituras 120/min por credencial. Resposta 429 inclui
  `Retry-After` em segundos; o proxy deve obter IP somente de origem confiavel.
  Os limites podem ser ajustados conforme a medicao operacional, sem mudar o
  protocolo experimental.
- `user_id` e um identificador opaco e estavel da identidade composta por
  emissor OIDC e `sub`; clientes devem apenas devolve-lo sem interpretar sua
  codificacao. Ele nao contem e-mail nem substitui autorizacao.

## Autenticacao, cookies e CSRF

O profissional continua usando Google OIDC, cadastro previo, identidade
`iss` + `sub`, bloqueio e perfis `consulta`, `importacao` e `administracao`.
Assinatura, emissor, audiencia, nonce e expiracao sao verificados no servidor;
claims, e-mail ou perfil enviados pelo navegador nao autorizam operacoes.
O e-mail e auxiliar e nao aparece nos metadados de avaliacao.

Cookies opacos e separados: `__Host-stroop_professional` e
`__Host-stroop_participant`, sempre `Secure`, `HttpOnly`, `SameSite=Lax`,
`Path=/`, sem `Domain`. Valores com pelo menos 256 bits de entropia; guardar
somente seu hash no servidor. Tokens Google nunca sao devolvidos ao frontend.
Sessao profissional tem expiracao absoluta de 8 horas, limitada tambem pela
validade da identidade validada; expirada, exige novo login. Revalidar cadastro,
bloqueio, perfil e vinculo a cada operacao, inclusive exportacao. Sessao do
participante dura exatamente 30 minutos desde resgate, sem renovacao deslizante.

Cada sessao tem token CSRF independente, devolvido em JSON no bootstrap e
enviado em `X-CSRF-Token` nas escritas. Validar o token e `Origin` igual a
origem configurada. Nao colocar token CSRF em URL, log ou armazenamento duravel.
Requisicoes sem `Origin` ou com origem divergente sao recusadas em escritas do
navegador. Falha CSRF e 403 `csrf_failed`; cookies profissional e participante
nao substituem um ao outro.

`POST /participant/redeem` ainda nao possui sessao: exigir `Origin` correto e
JSON, sem aceitar formulario simples, e aplicar rate limit. A resposta cria
cookie/token participante. Login OIDC usa `state` aleatorio de uso unico,
nonce e PKCE vinculados a uma transacao de curta duracao; callback e a excecao
ao header CSRF, protegido por essa transacao. Nao aceitar `return_to` externo;
o destino apos login e fixo e local.

### Operacoes profissionais

Todos os caminhos desta tabela tem prefixo `/api/v1`.

Compatibilidade operacional opt-in: `OIDC_CALLBACK_PATH=/oauth2callback` usa
esse caminho absoluto no login e na troca do codigo, ativando um alias para
o mesmo handler de callback. Somente esse caminho legado e o padrao
`/api/v1/auth/callback` sao aceitos; nenhuma URL arbitraria ou redirecionamento
intermediario e permitido. Sem a opcao, o alias retorna404.

No callback, metadados opcionais da resposta Google nao definem identidade,
dominio autorizado ou permissoes. Se presente, `iss` deve ser exatamente
`https://accounts.google.com`. Parametros duplicados/desconhecidos e mistura de
`code` com `error` continuam rejeitados; cookie/state, expiracao, uso unico,
PKCE, nonce e ID token verificado permanecem obrigatorios no sucesso.
Referencia: [resposta de autorizacao Google](https://developers.google.com/identity/openid-connect/reference#authenticationuriparameters).

| Metodo e caminho | Entrada / resultado de sucesso | Autorizacao |
|---|---|---|
| `GET /auth/login` | Sem corpo/query; 303 para Google, cria transacao OIDC de 10 min | Publica, com rate limit |
| `GET /auth/callback` | Query OIDC `code` e `state`, ou `error` e `state`; metadados Google opcionais `scope`, `authuser`, `prompt`, `hd`, `iss`; apos validar, 303 para aplicacao e cookie profissional novo. Identidade verificada sem cadastro recebe 401 sem sessao, mostrando somente seu proprio `iss`/`sub` | Transacao OIDC valida; cadastro previo ativo |
| `POST /auth/logout` | Corpo `{}`; 204 e remocao do cookie/sessao profissional | Sessao profissional e CSRF; repeticao sem cookie continua 204 apos validar origem |
| `GET /auth/me` | 200 com `user_id` opaco (`iss` + `sub`), `role`, `expires_at`, `csrf_token` | Profissional ativo |
| `GET /projects` | Lista paginada de `id`, `code`, `name`, `active`, `created_at`; sem corpo | Profissional; somente projetos vinculados, admin pode listar todos |
| `POST /projects` | `{"code":"PROJETO_SINTETICO","name":"Projeto sintetico"}`; 201 com objeto do projeto | `administracao` + CSRF; `code` unico, duplicado 409 |
| `GET /projects/{project_id}/members` | Lista paginada de `user_id`, `active`; nao devolve tokens/e-mails | `administracao` |
| `PUT /projects/{project_id}/members/{user_id}` | `{"active":true}`; 200 com `user_id`, `active`; ativa/desativa vinculo, idempotente | `administracao` + CSRF; usuario profissional deve existir |
| `POST /projects/{project_id}/invitations` | Metadados abaixo; 201 com convite e codigo uma unica vez | `importacao`/`administracao`, projeto ativo e vinculo |
| `POST /projects/{project_id}/invitations/{invitation_id}/revoke` | `{}`; 204; repeticao continua 204 | Mesmo requisito da criacao; convite e sessao ainda ativos sao invalidados |
| `GET /projects/{project_id}/assessments` | Lista paginada completa, filtros combinados e limites descritos abaixo | Qualquer perfil com vinculo, inclusive administracao |
| `GET /projects/{project_id}/assessments/options` | Facetas autorizadas por projeto, periodo e instrumento; sem nomes/iniciais | Qualquer perfil com vinculo ativo |
| `GET /projects/{project_id}/assessments/{assessment_id}` | 200 com detalhe/metricas recalculadas e tentativas, no formato abaixo | Mesmo escopo da lista |
| `GET /projects/{project_id}/assessments/{assessment_id}/export` | 200 `text/csv; charset=utf-8`, 21 colunas oficiais, 16 linhas principais | Mesmo escopo da lista; revalidar antes do download |
| `POST /projects/{project_id}/imports/{operation_id}` | CSV UTF-8 minimizado em `text/csv`; 200 com estado da operacao | Perfil `importacao`/`administracao`, projeto ativo e vinculo; CSRF/origem |
| `GET /projects/{project_id}/imports/{operation_id}` | Sem corpo/query; 200 com estado auditado | Mesmo perfil e vinculo ativo; reautoriza projeto |
| `POST /assessments/export` | CSV agregado de uma linha por avaliacao, contrato fechado por instrumento | Qualquer perfil vinculado aos projetos; CSRF/origem e reautorizacao no clique |
| `GET /admin/users` | Lista paginada de `{user_id,issuer,subject,email,role,active}`; acesso exclusivo da area de administracao | `administracao`; e-mail auxiliar restrito a admins |
| `POST /admin/users` | Corpo fechado `{issuer,subject,role,email?}`; 201 cadastra identidade Google, sem senha/autocadastro | `administracao` + CSRF/origem; `iss`/`sub` sao a identidade |
| `PUT /admin/users/{user_id}` | Corpo fechado `{role,active,email}`; atualiza perfil, estado e e-mail auxiliar | `administracao` + CSRF/origem; 409 protege a ultima conta admin |

`GET /admin/users` usa os parametros paginados assinados `limit`/`cursor` e
ordena por perfil e identidade. As escritas de conta reutilizam os casos de uso
autorizados e registram o resultado sem e-mail nem claims no log/auditoria.
Nao ha exclusao ou autocadastro. Um profissional autenticado sem cadastro pode
encaminhar seu proprio `iss` e `sub` por canal institucional; e-mail nao concede
acesso. Administradores criam projetos pelas operacoes existentes e concedem
vinculos explicitamente; a administracao global nao herda acesso a resultados.
Bloqueio e revogacao preservam dados e sao revalidados em cada operacao.

### Importacao CSV WEB (W15E)

O `operation_id` e UUID aleatorio criado pelo navegador. O cliente envia a
copia minimizada do CSV oficial registrado ou do instrumento demo registrado;
`participant_name` deve ser exatamente `NAO_COLETADO` e `initials` vazio. A
interface cria essa copia em memoria, preserva o arquivo selecionado e nao envia
nome de arquivo. Clientes alternativos que transmitam nome ou iniciais sao
recusados pela API. Projeto no caminho e a unica associacao; o rotulo legado da
coluna `project` nunca cria vinculo nem mapa.

O endpoint dedicado aceita somente `text/csv` opcionalmente com
`charset=utf-8`, corpo de 1 a 5 MiB e ate 10.000 registros de dados. Os outros
endpoints mantem o limite JSON de 65.536 bytes. O servidor grava temporariamente
com permissao `0600`, valida pelo mesmo ingestao de instrumento do fluxo Python,
remove temporarios em sucesso/erro e nao registra payload, nome, caminho local
ou dados nominais. NUL, UTF-8 invalido, CSV vazio, formato/schema invalidos ou
arquivo nao minimizado resultam em estado `rejeitado` (`invalid_csv`).

Resposta de sucesso ou reconsulta:

```json
{"operation_id":"UUID","status":"recebido|validado|importado|rejeitado","error_code":null,"assessment_id":"UUID ou null","created_at":"ISO-8601 UTC","updated_at":"ISO-8601 UTC"}
```

Uma repeticao com o mesmo UUID e hash e idempotente; UUID reutilizado com outro
projeto, identidade ou conteudo retorna `409 state_conflict`. Duplicata global
de `assessment_id` fica `rejeitado` com `duplicate_assessment`, sem sobrescrita.
Estado e hash SHA-256 ficam na auditoria restrita. A gravacao da avaliacao e a
mudanca para `importado` compartilham transacao. Se houver falha antes do commit,
a reconsulta pode mostrar `validado`; o cliente deve consultar ou solicitar
explicitamente reenvio da mesma copia e UUID, nunca repetir automaticamente.

### Filtros profissionais combinados (W15A)

A listagem aceita `start_date` e `end_date` em YYYY-MM-DD, ambos inclusivos
sobre `assessment_date`; inicio posterior ao fim e datas invalidas retornam422.
A data WEB e o dia UTC do inicio; o legado conserva a data civil registrada,
sem converter horarios sem fuso. `test_code` seleciona um instrumento por igualdade
(1–64 caracteres ASCII de codigo). Estes parametros, `limit` e `cursor` sao unicos.

`participant_id`, `visit`, `evaluator_id`, `test_version` e `platform` podem se
repetir ate 100 vezes por campo. Valores do mesmo campo combinam por OU; campos
diferentes combinam por E. Ausencia significa sem restricao. Codigos/visitas
historicos de consulta aceitam 1–512 caracteres sem controles ou valor composto
somente de espacos; nao altera a emissao WEB, que permanece 64 caracteres ASCII. Avaliador
usa identificacao tecnica opaca de ate 512 caracteres ASCII seguros;
`LEGADO_NAO_MAPEADO` seleciona ausencia de identidade tecnica sem divulgar o
rotulo original. Versoes aceitam 1–64 caracteres ASCII de codigo, incluindo `+`; plataformas
sao `web` e `psychopy`. Valores sao deduplicados/ordenados antes de vincular cursor.

O cursor HMAC de avaliacoes e vinculado ao profissional, projeto e filtros
canonicos e contem fingerprint dos metadados do conjunto autorizado. Cada pagina
reautoriza o acesso numa transacao READ ONLY/REPEATABLE READ. Alteracao desse
conjunto entre paginas retorna409 `state_conflict`, exigindo nova consulta
integral. Tokens anteriores a este contrato nao sao reutilizaveis (422), sem
alteracao do formato de resposta `items`/`next_cursor`. Limite de 100 por pagina e
5.000 avaliacoes no conjunto de cada projeto; exceder retorna422, sem truncar.
O navegador limita o agregado a20projetos/5.000 avaliacoes; falha em qualquer
pagina/projeto descarta o agregado e pede recuperacao explicita. A leitura de
listagem e paginada por projeto; a exportacao agregada compara snapshots de todos
os projetos numa unica transacao antes de gerar o arquivo. Resultados concluidos
nao sao alterados pela interface.

Cada pagina tambem retorna `X-Assessment-Snapshot`, token opaco HMAC vinculado
ao profissional, projeto, filtros e fingerprint completo (metadados, tentativas
principais Stroop e metricas genericas), valido por 15 minutos. O navegador
mantem o token apenas em RAM e exige consistencia entre todas as paginas antes
de habilitar exportacao. `POST /assessments/export` recebe corpo fechado
`{projects:[{project_id,snapshot}],filters,view:{test_code,platform?}}`;
`projects` aceita 1–20 projetos distintos e filtros seguem o contrato acima.
`view` registra somente `stroop_go_nogo_ptbr` ou `instrumento_sintetico_demo` e,
opcionalmente, `web`/`psychopy`. A API valida os tokens e, numa unica transacao
READ ONLY/REPEATABLE READ, reautoriza cada vinculo, reconta ate 5.000 avaliacoes
e compara os fingerprints antes de selecionar instrumento/plataforma. Mudanca
retorna409 `state_conflict`; acesso revogado retorna404. O CSV usa esquema fixo
por instrumento, UTF-8 sem BOM, virgulas, aspas CSV e CRLF; metadados sao
limitados a IDs tecnicos, projeto, visita, avaliador tecnico, inicio, plataforma,
instrumento e versoes. Texto de celula potencialmente formulavel e escapado;
metricas ausentes ficam vazias e valores numericos nao sao arredondados. Nome
estatico termina em `_avaliacoes.csv`, resposta usa `no-store` e nao persiste no
servidor. Este CSV agregado nao pertence ao contrato oficial de tentativas,
nao e aceito pelo importador oficial e nao altera o download individual de 21
colunas.

`GET .../assessments/options` aceita somente os parametros unicos `start_date`,
`end_date`, `test_code`. Responde objeto fechado com arrays de strings
`participant_id`, `visit`, `evaluator_id`, `test_version`, `platform`, `test_code`.
Opcoes sao distintas, ordenadas e autorizadas no contexto selecionado. Limite
de 200 valores por faceta/projeto; excesso retorna422 e pede periodo/instrumento
mais restrito, sem truncar silenciosamente. Nao le nomes/iniciais nem devolve
rotulos de avaliadores legados. Facetas nao concedem autorizacao a resultados:
listagem, detalhe e download reautorizam cada solicitacao.

Admin conserva o poder administrativo global de projetos/vinculos; acesso a
dados de pesquisa e convites exige vinculo inclusive para administradores.
Ausencia de vinculo/objeto fora do projeto responde 404, sem confirmar sua existencia.
Perfil `consulta` em escrita responde 403 depois de resolver escopo permitido.
Os vinculos concedem consulta compartilhada no projeto; o criador do convite
continua sendo o avaliador, e nao um limite de visibilidade aos colegas.
Nao criar cadastro publico, senha propria ou elevacao de perfil por convite.

Criacao de convite (dados integralmente sinteticos):

```json
{"participant_id":"P_SINTETICO","visit":"V_SINTETICA"}
```

```json
{
  "invitation_id":"00000000-0000-4000-8000-000000000010",
  "session_id":"00000000-0000-4000-8000-000000000020",
  "code":"CODIGO_SINTETICO_NAO_UTILIZAVEL",
  "expires_at":"2026-10-17T13:00:00Z",
  "state":"issued"
}
```

`project_id` vem do caminho. O servidor fixa o projeto, codigo pseudonimizado,
visita e avaliador (`user_id` estavel do criador), junto ao protocolo. Nao aceitar
`participant_name`, `initials`, idade, sexo, CPF, contato ou avaliador no corpo.
Convite real usa codigo opaco com pelo menos 128 bits de entropia, sensivel a
maiusculas, de ate 128 caracteres ASCII seguros; hash no banco e comparacao
segura. E utilizavel uma unica vez durante 24 horas da criacao. O codigo so e
mostrado na resposta de criacao e e entregue fora da aplicacao pelo profissional;
nao criar link contendo esse codigo. Nova criacao gera convite/sessao distintos,
sem reutilizar automaticamente a execucao anterior.

## Sessao participante e estados

**Convite:** `issued` -> `redeemed`, `expired` ou `revoked`. Resgate e atomico;
dois resgates concorrentes nao criam duas credenciais. Convite expirado responde
410; desconhecido/revogado responde 404; ja resgatado responde 409, sem emitir
nova credencial. Perda da resposta de resgate exige novo convite: nao e possivel
recuperar com codigo ja consumido. O operador deve revogar o convite anterior
quando ainda aplicavel. Nao relaxar uso unico para simular idempotencia.

**Sessao:** `preparing` -> `running` -> `completed`. `preparing` e `running`
podem ir a `aborted` ou `expired`; estados terminais nao voltam a ficar ativos.
`session_id` identifica essa tentativa operacional; `assessment_id` so nasce
na transacao de conclusao valida. Pratica, expiracao e abortamento nao criam
linhas de avaliacao, metricas ou tentativas parciais oficiais.

O resgate ativa a sessao em `preparing`, fixa `activated_at`,
`expires_at=activated_at+30min` e uma permutacao aleatoria sem reposicao das
16 condicoes principais. A ordem e persistida no servidor e nunca e sorteada
novamente em consulta, retry ou reload. Pratica usa pool proprio de quatro
condicoes; cada rodada sorteia uma permutacao completa local, sem enviar treino
no resultado. Apenas uma rodada completa, sem limiar, libera o botao principal
no frontend; a API nao consegue certificar que uma pessoa fez esse treino.

| Metodo e caminho, sob `/api/v1` | Entrada e sucesso | Estado/regras |
|---|---|---|
| `POST /participant/redeem` | `{"code":"CODIGO_SINTETICO_NAO_UTILIZAVEL"}`; 201 com `session_id`, `state`, `activated_at`, `expires_at`, `csrf_token`, e cookie participante | Convite valido e nao consumido; nao recebe cookie profissional como autorizacao |
| `GET /participant/session` | Sem corpo/query; 200 com bootstrap descrito abaixo | Credencial participante. Em `running` devolve estado/expiracao e `can_resume:false`, sem nova autorizacao para iniciar. Em `completed` devolve recibo/resumo. Em `aborted` 409; expirada 410 |
| `POST /participant/start` | `{"app_version":"web-0.1.0"}`; 200 com `session_id`, `state:"running"`, `started_at`, `expires_at` | CSRF; transicao atomica antes da primeira fixacao principal. `app_version` fixada no primeiro inicio |
| `POST /participant/abort` | `{"reason":"focus_lost"}`; 200 com `session_id`, `state:"aborted"` | CSRF; somente sessao propria `preparing`/`running`; repeticao apos abortamento devolve o mesmo estado |
| `POST /participant/complete` | Corpo fechado abaixo; primeira conclusao 201, retry identico 200 com mesmo recibo | CSRF; somente `running` nao expirada, ou `completed` para comparacao idempotente |

`GET /participant/session` em completed conserva o recibo JSON e fornece
`X-CSRF-Token` e `X-Session-Expires-At` nos headers, para finalizar com seguranca.
`POST /participant/logout` recebe `{}` sem query, exige Origin e CSRF quando ha
cookie participante e responde 204; sem cookie e idempotente, mantendo a
validacao de Origin. Invalida a credencial no servidor e remove o cookie
HttpOnly/Secure/SameSite=Lax. Preparacao ou execucao sao abortadas com
`user_cancelled`; resultados concluidos sao preservados. Finalizar no cliente
aguarda essa confirmacao; falha permite tentar novamente sem anunciar saida.

`abort.reason` e uma enumeracao fechada: `focus_lost`, `visibility_hidden`,
`escape`, `reload`, `page_closed`, `timing_invalid`, `user_cancelled`.
Nao aceitar texto livre. O frontend tenta comunicar interrupcao quando possivel;
fechamento/recarga podem impedir o aviso. Sem entrega, o servidor expira a sessao
no prazo original. Nunca reconstruir o principal pelo bootstrap nem concluir
um subconjunto. Revogacao do convite/sessao pelo profissional bloqueia novas
operacoes do participante; nao apaga avaliacao ja concluida.

`start` repetido com o mesmo corpo durante `running` devolve o recibo original,
sem alterar instante, ordem ou prazo; corpo diferente responde 409. Essa
idempotencia permite retry de uma chamada cuja resposta se perdeu **antes**
de o motor executar. O frontend da mesma pagina mantem em RAM se comecou e
nunca usa o retry para repetir estimulos. Ao carregar uma pagina com sessao
`running`, deve abortar com `reload` e exigir novo convite; nao existe retomada
apos reload. O servidor nao prova pelo HTTP se um estimulo ja foi apresentado:
esse limite deve ser testado no fluxo de frontend, sem prometer prova fisica.

### Bootstrap de preparacao

Objeto devolvido por `GET /participant/session` em `preparing`:

- `session_id`, `state`, `activated_at`, `expires_at`, `csrf_token`.
- `protocol_id="stroop_go_nogo_ptbr/0.2.2-web.1"`,
  `test_code="stroop_go_nogo_ptbr"`, `test_version="0.2.2-web.1"`,
  `platform="web"`. O protocolo e um snapshot imutavel servidor/condicoes,
  independente da versao do aplicativo. Mudanca de tempos/condicoes exige nova
  identidade de protocolo; atualizar o app nao reinterpreta sessoes existentes.
- `protocol`: dados de apresentacao necessarios ao motor, correspondentes ao
  [protocolo aprovado](../experimento/PROTOCOLO_WEB.md): tempos numericos em ms, contagem,
  cores, regra/HUD, politica de interrupcao e repeticao de pratica. Testes
  verificarao correspondencia ao snapshot; nao duplicar decisoes neste contrato.
- `practice_conditions`: exatamente quatro objetos com `condition_id` 1–4,
  `word`, `ink_color`, `ink_color_display`, `condition`, `correct_response`.
- `main_conditions`: exatamente 16 objetos com os mesmos campos, em ordem
  de apresentacao, acrescentando `trial_number` sequencial 1–16. Aqui
  `condition_id` e o `trial_number` da linha do CSV-fonte principal; no treino
  usa o CSV-fonte de pratica. Os namespaces sao separados pelo bloco.

`condition` e `congruent|incongruent`; `correct_response` e `space|null`.
Os campos de cor logica e visual sao distintos; o CSV continua usando a cor
logica. A API deriva a condicao das fontes e a cor visual da paleta efetiva
do Builder, registrada em `../experimento/UX_DECISIONS.md`, nao do cliente. O Builder substitui
os hexadecimais historicos de `ink_color_display` dos CSVs-fonte; preservar a
paleta efetivamente exibida ao montar o snapshot WEB.
Exemplo sintetico de um item de `main_conditions` (o bootstrap real possui 16):

```json
{"trial_number":1,"condition_id":9,"word":"AZUL","ink_color":"gray","ink_color_display":"#808080","condition":"incongruent","correct_response":null}
```

O bootstrap nao precisa expor nome, identificadores de participante/projeto,
e-mail ou avaliador para executar a tarefa. A credencial ja fixa esses dados.
Em `running`, `GET /participant/session` continua fornecendo CSRF para permitir
abortamento, mas devolve somente estado, IDs tecnicos, prazo e `can_resume:false`.

## Conclusao: schema, tempo e consistencia

`POST /participant/complete` aceita **somente**:

| Campo | Tipo e regra |
|---|---|
| `protocol_id` | String identica ao snapshot da sessao |
| `test_version` | String identica a variante fixada |
| `platform` | Literal `web` |
| `app_version` | String identica a fixada em `start` |
| `frame_period_ms` | Numero finito entre 4 e 50 inclusive, medido pelo motor antes do principal |
| `trials` | Lista com exatamente 16 objetos, ordenados por `trial_number` |

Cada objeto de `trials` aceita **somente** os seguintes campos, todos presentes:

| Campo | Tipo e regra |
|---|---|
| `trial_number` | Inteiro 1–16, sequencial na ordem apresentada |
| `condition_id` | Inteiro 1–16, igual a condicao atribuida pelo servidor nessa posicao |
| `key_pressed` | `null` ou literal `space` |
| `reaction_time_ms` | `null` sem resposta; numero finito estritamente positivo com resposta |
| `trial_start_ms` | Numero finito nao negativo, inicio da fixacao relativo ao comeco principal |
| `stimulus_onset_ms` | Numero finito, inicio observado do estimulo/janela |
| `stimulus_offset_ms` | Numero finito, retirada observada do estimulo/fim da janela |
| `trial_end_ms` | Numero finito, fim do intervalo da tentativa |
| `key_at_ms` | `null` sem resposta; numero finito com resposta, no mesmo relogio relativo |

O cliente nao envia metadados de pessoa, classificacao, `correct`,
`error_type`, palavra/cor, contagens ou metricas. O servidor consulta a ordem
fixada, deriva as classificacoes e recalcula o resultado pelo nucleo.

Validacao atomica antes de qualquer escrita de avaliacao:

1. Credencial, CSRF, estado, revogacao e prazo; protocolo, plataforma e versoes
   exatas. Nao confiar em `session_id` ou `assessment_id` fornecidos no corpo.
2. Exatamente 16 tentativas, numeros 1–16 unicos e ordenados, cada `condition_id`
   correspondente a ordem persistida; cada linha-fonte principal aparece uma
   unica vez. Assim se preservam balanceamento, cores e condicoes do snapshot.
3. Primeiro `trial_start_ms=0`. Para cada tentativa, tempos estritamente
   crescentes: inicio < onset < offset < fim. O fim de uma tentativa coincide
   com inicio da seguinte; esses limites sao o mesmo registro de transicao.
   Todos os instantes sao no maximo 60100 ms; nao aceitar duracao negativa,
   salto de relogio ou novo zero em cada tentativa.
4. Para a tentativa `i` iniciada em `s`, conferir inicio nominal `(i-1)*3750`,
   onset `s+300`, offset `s+2800` e fim `s+3750`, com desvio absoluto de ate
   `frame_period_ms` em cada transicao. Conferir tambem duracao observada do
   estimulo de 2500 ms com desvio de ate um quadro. O ultimo fim deve estar
   entre 59900 e 60100 ms. Igualdade na tolerancia e aceita. Os numeros
   derivam do snapshot e os gates sao os do protocolo; nao alterar o criterio
   para acomodar maquina que falhou.
5. Sem resposta: `key_pressed`, `reaction_time_ms` e `key_at_ms` todos `null`.
   Com resposta: todos presentes, `key_pressed="space"`,
   `stimulus_onset_ms < key_at_ms < stimulus_offset_ms` e
   `0 < reaction_time_ms < 2500`. A diferenca
   `key_at_ms-stimulus_onset_ms` deve corresponder ao RT informado com
   tolerancia numerica de 0,001 ms, sem quantizar RT antes de validar. Fim
   exclusivo e RT positivo prevalecem mesmo dentro da tolerancia numerica.
6. Classificar somente a primeira nova pressao valida. Repeticoes/tecla mantida
   devem ser filtradas pelo motor; o corpo nao e um historico bruto de teclado.
   O servidor rejeita incoerencia observavel, mas nao pode provar ausencia de
   eventos omitidos ou fraude de temporizacao a partir de declaracao do cliente.

Os tempos sao relativos ao inicio **local** do principal, depois da confirmacao
de `start`, sem incluir rede, pratica ou contagem. `started_at` e horario civil
da autorizacao pelo servidor, nao instante fisico do primeiro quadro. O motor
registra o instante observado de cada transicao; responder nao encerra cedo a
tentativa. Na normalizacao converter `reaction_time_ms/1000` uma unica vez
para segundos, preservando precisao para as formulas; arredondar somente para
exibicao/exportacao conforme os contratos canonicos.

Sessao com payload invalido nao grava avaliacao nem tentativas. Erro de schema
ou consistencia e 422 e nao muda `running`: pode corrigir apenas serializacao
do registro original, sem refazer a tarefa ou fabricar timestamps. Se o motor
detectar violacao temporal/interrupcao, deve abortar com razao fechada e exigir
nova sessao. Validacao de consistencia nao certifica latencia fisica: a medicao
de W16 continua necessaria.

### Corpo sintetico completo

Este exemplo usa uma ordem aleatoria sintetica fixada previamente no servidor;
e valido somente para sessao com essa mesma ordem. Contem 16 tentativas sem
resposta (oito omissoes e oito rejeicoes corretas), sem RT inventado:

```json
{
  "protocol_id":"stroop_go_nogo_ptbr/0.2.2-web.1",
  "test_version":"0.2.2-web.1",
  "platform":"web",
  "app_version":"web-0.1.0",
  "frame_period_ms":16.666667,
  "trials":[
    {"trial_number":1,"condition_id":9,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":0,"stimulus_onset_ms":300,"stimulus_offset_ms":2800,"trial_end_ms":3750,"key_at_ms":null},
    {"trial_number":2,"condition_id":1,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":3750,"stimulus_onset_ms":4050,"stimulus_offset_ms":6550,"trial_end_ms":7500,"key_at_ms":null},
    {"trial_number":3,"condition_id":10,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":7500,"stimulus_onset_ms":7800,"stimulus_offset_ms":10300,"trial_end_ms":11250,"key_at_ms":null},
    {"trial_number":4,"condition_id":2,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":11250,"stimulus_onset_ms":11550,"stimulus_offset_ms":14050,"trial_end_ms":15000,"key_at_ms":null},
    {"trial_number":5,"condition_id":11,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":15000,"stimulus_onset_ms":15300,"stimulus_offset_ms":17800,"trial_end_ms":18750,"key_at_ms":null},
    {"trial_number":6,"condition_id":3,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":18750,"stimulus_onset_ms":19050,"stimulus_offset_ms":21550,"trial_end_ms":22500,"key_at_ms":null},
    {"trial_number":7,"condition_id":12,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":22500,"stimulus_onset_ms":22800,"stimulus_offset_ms":25300,"trial_end_ms":26250,"key_at_ms":null},
    {"trial_number":8,"condition_id":4,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":26250,"stimulus_onset_ms":26550,"stimulus_offset_ms":29050,"trial_end_ms":30000,"key_at_ms":null},
    {"trial_number":9,"condition_id":13,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":30000,"stimulus_onset_ms":30300,"stimulus_offset_ms":32800,"trial_end_ms":33750,"key_at_ms":null},
    {"trial_number":10,"condition_id":5,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":33750,"stimulus_onset_ms":34050,"stimulus_offset_ms":36550,"trial_end_ms":37500,"key_at_ms":null},
    {"trial_number":11,"condition_id":14,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":37500,"stimulus_onset_ms":37800,"stimulus_offset_ms":40300,"trial_end_ms":41250,"key_at_ms":null},
    {"trial_number":12,"condition_id":6,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":41250,"stimulus_onset_ms":41550,"stimulus_offset_ms":44050,"trial_end_ms":45000,"key_at_ms":null},
    {"trial_number":13,"condition_id":15,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":45000,"stimulus_onset_ms":45300,"stimulus_offset_ms":47800,"trial_end_ms":48750,"key_at_ms":null},
    {"trial_number":14,"condition_id":7,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":48750,"stimulus_onset_ms":49050,"stimulus_offset_ms":51550,"trial_end_ms":52500,"key_at_ms":null},
    {"trial_number":15,"condition_id":16,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":52500,"stimulus_onset_ms":52800,"stimulus_offset_ms":55300,"trial_end_ms":56250,"key_at_ms":null},
    {"trial_number":16,"condition_id":8,"key_pressed":null,"reaction_time_ms":null,"trial_start_ms":56250,"stimulus_onset_ms":56550,"stimulus_offset_ms":59050,"trial_end_ms":60000,"key_at_ms":null}
  ]
}
```

Para um hit sintetico na segunda tentativa, substituir somente
`key_pressed="space"`, `reaction_time_ms=512`, `key_at_ms=4562`.
Para uma comissao na primeira, usar `space`, `681`, `981`. Esses exemplos
exercitam as quatro classificacoes com as condicoes recebidas.

## Persistencia, idempotencia e consulta

Conclusao valida executa uma unica transacao: bloquear sessao, revalidar acesso/
prazo/estado, validar payload e ordem, normalizar, recalcular metricas no nucleo,
inserir avaliacao/tentativas/metricas e vincular `assessment_id`, hash e recibo
ao estado `completed`. Falha em qualquer ponto provoca rollback completo.
Restricoes unicas em `session_id` e vinculo de avaliacao impedem duplicidade
entre processos. Nenhuma chamada HTTP grava no CSV local do PsychoPy.

Idempotencia de `complete` e implicita por sessao e hash SHA-256 do corpo
canonico validado: propriedades ordenadas, UTF-8, sem espacos, listas preservando
ordem, numeros finitos em representacao decimal normalizada (`1` e `1.0`
equivalem; `-0` equivale a `0`). A implementacao deve definir uma unica funcao
canonizadora e fixtures Python/TypeScript; nao usar o hash dos bytes brutos nem
comparar arredondamentos de RT. Nao e necessario header de idempotencia do cliente.
Referencia implementada: `stroop/domain/web_results.py::canonical_payload` usa
decimal normalizado sem expoente; vetores compartilhados em
[`web_result_canonical.json`](../../tests/fixtures/web_result_canonical.json).
RT cuja conversao para segundos nao seja representavel como numero positivo
finito no nucleo e rejeitado, preservando ausencia versus medida.
Depois de `completed`, payload identico devolve o mesmo recibo/ID com 200;
payload diferente devolve 409 `result_conflict`. Requisicao malformada continua
400/422. Duas conclusoes simultaneas identicas produzem uma avaliacao; duas
diferentes produzem um sucesso e um conflito.

Credencial participante vencida nao permite ler nem reenviar, mesmo se a
avaliacao foi concluida. Antes do prazo, `GET /participant/session` com
`completed` pode recuperar recibo de uma resposta perdida. Depois dele, o
profissional vinculado consulta o resultado persistido. Ausencia de resposta
HTTP nao significa ausencia de commit; em erro de rede/503, reenviar o mesmo
corpo original em RAM ate o prazo. Exibir “salvo” somente apos recibo de sucesso
ou consulta confirmada. Nao usar localStorage, sessionStorage, IndexedDB, cache
de service worker ou arquivo para persistir resultado/credencial no navegador.
Recarregar/fechar pode perder resultado ainda nao confirmado; nao prometer
recuperacao offline. O cookie HttpOnly de sessao e a unica persistencia tecnica
necessaria, com prazo fixo; nenhum token e copiado para armazenamento JS.

Recibo de conclusao sem hits (JSON sintetico):

```json
{
  "session_id":"00000000-0000-4000-8000-000000000020",
  "assessment_id":"00000000-0000-4000-8000-000000000030",
  "state":"completed",
  "completed_at":"2026-10-16T13:02:00Z",
  "platform":"web",
  "test_code":"stroop_go_nogo_ptbr",
  "test_version":"0.2.2-web.1",
  "protocol_id":"stroop_go_nogo_ptbr/0.2.2-web.1",
  "app_version":"web-0.1.0",
  "summary":{"accuracy":50,"response_time_seconds":null,"total_trials":16,"hits":0,"omission_errors":8,"commission_errors":0,"correct_rejections":8}
}
```

Participante recebe somente o resumo da propria execucao. Ausencia de hits e
`null` no HTTP e `—` na interface. Preservar o sentinel historico `0.0` de
`response_time` no banco/nucleo legado: o adaptador HTTP consulta a contagem de
hits para distinguir ausencia de medida, sem apresentar zero como RT medido.
Nao alterar formulas ou arredondar antes de calcular a mediana.

Lista profissional devolve por item: `assessment_id`, `participant_id`, `visit`,
`evaluator_id`, `created_at`, `started_at`, `platform`, `test_code`,
`test_version`, `protocol_id`, `app_version` e `summary`. Detalhe acrescenta
`project_id`, `session_id`, `completed_at`, `metrics` (codigos/unidades do
[modelo canonico](../dados/MODELO_DE_DADOS.md)), `frame_period_ms` e 16 `trials` com os
campos recebidos e as classificacoes/cor/palavra derivadas do snapshot.
Avaliacoes locais existentes podem ter `platform="psychopy"`, sem
`protocol_id`, `session_id`, `app_version`, tempos observados ou periodo de
quadro (`null`); nao inventar proveniencia WEB para essas linhas. Consulta WEB
de linhas legadas deve ocultar nome/iniciais, inclusive na serializacao interna
que chega ao navegador. Acesso WEB nao amplia transmissao de dados pessoais.
Avaliador legado sem correspondencia de identidade WEB recebe
`evaluator_id=null`; seu CSV usa `LEGADO_NAO_MAPEADO`, sem expor o rotulo antigo.
Horarios legados sem fuso permanecem sem fuso; nao atribuir UTC implicitamente.
No legado, a quantidade de tentativas segue o protocolo original; instrumentos
sem tentativas retornam lista vazia, sem fabricar registros Stroop.

O `summary` profissional Stroop e fechado com onze campos: `accuracy`,
`accuracy_go_trials`, `accuracy_no_go_trials`, `total_go_trials`,
`total_no_go_trials`, `response_time_seconds`, `total_trials`, `hits`,
`omission_errors`, `commission_errors`, `correct_rejections`. As precisões
profissionais Go/No-Go sao percentuais do nucleo recalculado por pagina, sem
consulta de detalhe por linha. Cada precisao e `null` quando nao ha tentativas
do respectivo tipo; RT e `null` sem hits. Contagens conservam zero quando zero
foi observado. O detalhe preserva a mesma ausencia para as metricas com
denominador zero, inclusive percentual de omissoes sem Go. Isso nao altera
formulas do nucleo, CSV, nem o recibo do participante de sete campos.

Instrumentos adicionais conservam `summary: {"metrics": {codigo: numero}}`
e unidades/rotulos no detalhe. A demonstracao registrada
`instrumento_sintetico_demo` usa `demo_total` (`count`) e `demo_mean` (`unit`),
sem classificacoes Stroop ou tentativas inventadas. A apresentacao WEB mostra
cada instrumento separadamente; valores ausentes nao recebem zero nem unidade
presumida para codigos desconhecidos. A listagem e o detalhe nao divulgam
caminho/nome de arquivo fonte ou campos nominais de participantes.

Escopo legado exige vinculo operacional explicito em `web_legacy_project_links`,
conforme [ADR-003](../arquitetura/ADR-003-escopo-legado-web.md); coincidencia entre
rotulo legado e codigo de projeto novo nao concede acesso. O mapa inicia vazio,
nao e escrito pela API e nao altera as coletas existentes.

Exportacao profissional da coleta WEB usa somente as 21 colunas oficiais, sem
acrescentar IDs tecnicos/versao do aplicativo: metadados fixados no servidor,
`participant_name=NAO_COLETADO`, `initials` vazio, cor logica, classificacoes
recalculadas e RT em segundos/vazio. `project` usa codigo estavel do projeto;
`evaluator` usa identificador tecnico estavel, nunca e-mail/nome.
`assessment_date` e a data e `started_at` e o horario civil de inicio no fuso
UTC; exibicao local pode converter sem alterar o instante. Nome de download
segue codigo do teste e timestamp, sem participante. A rota de exportacao
legada via WEB tambem deve mascarar nome/iniciais; isso nao reescreve arquivos
ou banco locais. `Content-Disposition` usa nome gerado no servidor; CSV deve
escapar delimitadores e neutralizar campos textuais que iniciem formula em
planilhas, preservando os rotulos pseudonimizados permitidos.

CSV de 21 colunas e o contrato oficial do Stroop. Outros instrumentos sem
contrato compativel conservam consulta/detalhe, mas essa exportacao recebe 422;
nao converter metricas arbitrarias em tentativas desta tarefa.

## Erros seguros e precedencia

Corpo uniforme (exemplo sintetico):

```json
{"error":{"code":"invalid_result","message":"Resultado inconsistente com o protocolo."},"request_id":"00000000-0000-4000-8000-000000000040"}
```

`message` e texto fixo seguro; nao devolver valores enviados, stack, SQL,
conexao, e-mail, claims, token, cookie ou detalhe que revele projeto alheio.
Nao retornar o corpo padrao de validacao que reflita a entrada. Logs usam
categoria fixa e `request_id`. Respostas OIDC com falha encerram a transacao e
usam mensagem fixa; query do callback nunca e incluido em log ou redirecionado.

| HTTP | Codigos e condicao |
|---|---|
| 400 | `invalid_json`, `invalid_oidc_state`: sintaxe/transacao invalida |
| 401 | `authentication_required`: sem credencial ou profissional com sessao vencida |
| 403 | `permission_denied`, `account_blocked`, `csrf_failed`: credencial reconhecida, operacao proibida |
| 404 | `not_found`: objeto desconhecido/fora do escopo, codigo invalido ou revogado |
| 409 | `state_conflict`, `invitation_used`, `result_conflict`, `duplicate_project`: conflito de estado/unicidade |
| 410 | `invitation_expired`, `session_expired`: prazo conhecido expirado |
| 413 | `body_too_large`: limite de corpo |
| 415 | `unsupported_media_type`: escrita sem JSON |
| 422 | `invalid_request`, `invalid_result`: campos/tipos/limites ou consistencia invalidos |
| 429 | `rate_limited`: limite de frequencia, com `Retry-After` |
| 503 | `service_unavailable`: banco/dependencia indispensavel indisponivel, sem detalhes internos |

Ordem de resolucao: limites de transporte/rate -> credencial/CSRF -> escopo ->
estado/prazo -> schema/consistencia -> transacao. Nunca devolver conflito ou
prazo de uma sessao/avaliacao alheia. Cookie participante reconhecido, mas
expirado, recebe 410; cookie ausente/desconhecido recebe 401. Em sessao terminal
`aborted`, operacoes de inicio/conclusao respondem 409; `abort` em `completed`
responde 409 e nao apaga resultado. Prazo esgotado nao reabre nem muda uma
avaliacao ja concluida; apenas bloqueia seu canal de acesso participante.

## Health e mapa de validacao

`GET /health/live`: 200 `{"status":"ok"}` enquanto processo responde;
nao depende de banco, OIDC ou dados. `GET /health/ready`: 200
`{"status":"ready"}` somente com configuracao valida, conexao de banco e
migrations obrigatorias presentes; caso contrario 503 com erro uniforme.
Sem autenticar, executar escrita, devolver configuracao ou iniciar migracoes
nessas rotas. Configuracao obrigatoria invalida deve impedir inicializacao
segura; prontidao nao mascara falha de configuracao com dados ficticios.

| Cenario | Evidencia exigida na implementacao |
|---|---|
| Criacao e resgate | Vinculo/perfil revalidados, metadados fixados, codigo em corpo e consumo atomico; concorrencia produz uma credencial |
| Preparacao e pratica | Snapshot consistente com condicoes; ordem principal imutavel/permutacao16; pratica nunca aparece na conclusao |
| Inicio/retry/reload | Uma transicao de inicio; recibo original no retry antes motor; reload em running interrompe e nao retoma |
| Quatro respostas | Hits/omissoes/rejeicoes/comissoes derivados; RT em ms normalizado uma vez; ausencia de hits vira null no HTTP |
| Janela e temporalidade | RT zero/negativo, fim exato, precoce/tardio, tecla mantida/repeat no motor; gates de um quadro e 100 ms, sem alegar validacao fisica |
| Resultado invalido | 15/17 tentativas, duplicata, ordem/condicao/versao adulterada, campo extra, `NaN`, origem de relogio errada e metrica enviada: 422, sem avaliacao |
| Conclusao/reenvio | Identico retorna mesmo ID; diferente 409; perda de resposta/503 apos commit nao duplica; corrida sob transacao e restricoes unicas |
| Rollback | Falha entre avaliacao, tentativas e metricas nao deixa linha parcial nem estado completed |
| Expiracao | 24 h para convite e 30 min desde resgate, limite final exclusivo; start/complete nao renovam prazo; sem avaliacao parcial |
| Interrupcao | Foco/aba/Escape/reload/fechamento; aviso perdido leva a expiracao; sessao abortada nao conclui; sem retomada principal |
| Acesso negativo | Sem cookie 401, perfil 403, projeto cruzado 404, bloqueio imediato, CSRF/origem incorretos 403, convites vazados/reutilizados limitados |
| Exportacao | Autorizacao nova no download, 21 colunas e 16 tentativas, dados minimizados, RT/ausencia corretos, nome seguro |
| Operacao | Configuracao invalida, readiness/banco indisponivel 503, 64 KiB/415/rate limit, erro sem reflexao ou segredo |

W05 implementa transporte/configuracao/health; W06 autenticacao/autorizacao;
W07 ciclo e migrations aditivas; W08 recebimento atomico; W09–W13 cliente,
motor e integracao; W14 consulta/exportacao profissional; W16 coleta evidencia
temporal real. A aprovacao do contrato nao substitui os testes, o banco real
ou os navegadores exigidos por essas etapas.


## Contrato alvo validado — persistência incremental (2026-11-05)

Esta seção especifica o contrato aprovado em DEC-02. O receptor backend foi
implementado em M2; resultados dos ensaios e SHA ficam em EV-M2 no
[backlog](../Projeto%20Stroop%20Test.md#ev-m2--receptor-incremental-e-banco-sintético-2026-11-05).
As seções anteriores preservam os corpos integrais de start/complete. O cliente
experimental ainda envia somente ao final: worker/fila e gates de prontidão e
timing pertencem a M3/M4. O responsável validou expressamente
esta estratégia e a matriz metodológica em 2026-11-05, após apresentação de
`270377b`, conforme [ADR-005](../arquitetura/ADR-005-persistencia-incremental.md).
Contrato alvo aprovado não é evidência de implementação ou integração.
O modelo de vínculos está no [modelo canônico](../dados/MODELO_DE_DADOS.md).
Não alterar prazos, cookies, OIDC, CSRF, grants ou escopo por projeto.

### Convites e vínculos

Preservar UUID único de convite, código secreto aleatório de pelo menos 256 bits,
hash no servidor, exibição única, expiração absoluta de 24 h e resgate atômico de
uso único. UUID identifica; código autoriza resgate, pseudônimo nunca autoriza.
Emissão exige perfil importação/administração e vínculo ativo com projeto ativo;
revogação bloqueia convite/sessão e preserva registros recebidos. Sessão de 30 min
não é renovada pelos checkpoints. Manter rate limit, código somente no corpo,
HTTPS, no-store e ausência de segredo em logs/URL. IDs de participante/visita
são resolvidos no servidor na preparação, sem confiar em associações do cliente.
Compatibilidade do corpo atual por rótulos deve ser preservada com resolução
unívoca; UUIDs internos não mudam as 21 colunas do CSV.

### Recepção incremental

- `POST /participant/session/checkpoints`: cookie participante + CSRF/Origin;
  corpo fechado `{protocol_id,test_version,platform,app_version,frame_period_ms,
  trials}`. `trials` contém de 1 a 16 registros completos com os mesmos campos,
  tipos e unidades da conclusão atual; posições consecutivas em ordem crescente.
  Não confiar em projeto/participante/sessão enviados no corpo. Limite 64 KiB.
- Em running, o servidor aceita novo trecho somente se estende o prefixo
  confirmado sem lacunas; sobreposição exige conteúdo canônico idêntico.
  Conferir ordem/snapshot e continuidade temporal com o prefixo anterior.
  Recebimento preservável não significa validade: falha temporal observável é
  registrada e impede conclusão oficial. Corpo malformado/extra/inseguro: 422,
  sem gravar o lote. Trecho fora da ordem: 409 `state_conflict`.
- Transação bloqueia sessão, revalida acesso/prazo, grava lote e recibo, então
  confirma commit. Resposta 200 fechada: `{session_id,confirmed_through,
  prefix_hash,received_at}`; prefixo é contíguo, 0–16, hash SHA-256 calculado
  pelo servidor pela canonização já definida, abrangendo proveniência e lista
  ordenada de observações. `received_at` é UTC; não mede RT.
- Idempotência por sessão/posição e hash canônico, com restrição única no banco.
  Repetição idêntica não cria observação nova; retorna o prefixo confirmado
  atual. Conteúdo diferente para posição já recebida: 409 `result_conflict`,
  sem sobrescrever. Uma corrida divergente impede resultado válido até revisão;
  não escolher silenciosamente a versão conveniente. Recibo só é sucesso após
  commit durável conforme configuração PostgreSQL validada.
- `GET /participant/session` acrescenta objeto fechado `checkpoint` com
  `confirmed_through`, `prefix_hash`, `received_at` (hash/data nulos no prefixo 0).
  Permite consultar recebimento após resposta perdida; não devolve tentativas
  para reconstrução/retomada do principal. Credencial expirada/revogada não
  consulta nem envia. Profissional autorizado pode conferir estado no projeto.
  Em aborted, retorna 200 com metadados da sessão, `can_resume:false`, CSRF e
  checkpoint, sem tentativas; start/complete continuam proibidos. Em completed,
  mantém recibo e headers de CSRF/prazo, acrescentando checkpoint; se invalidada,
  acrescenta `valid_for_result:false` e suprime o resumo com `summary:null`.
- Checkpoint pode chegar após `abort`, antes do vencimento e sem revogação,
  somente para preservar o prefixo já observado: nunca muda estado terminal,
  nunca autoriza novo start/complete. Após completed, só replay idêntico de
  observações existentes; qualquer acréscimo/divergência é 409. Expiração ou
  revogação bloqueiam nova escrita; nada recebido é apagado por essa razão.

### Conclusão, interrupção e concorrência

`complete` conserva o corpo integral atual, suas validações e seu recibo oficial.
Na mesma transação, confronta cada posição recebida, insere eventual sufixo
faltante, valida integralidade/ordem/gates e materializa avaliação/métricas.
Prefixo recebido pode sobreviver a rollback da conclusão; **nenhuma avaliação
oficial parcial** sobrevive. Divergência não sobrescreve observações. Complete
é permitido só em running válida, dentro do prazo, sem marca de interrupção,
com confirmação local de encerramento de todas as tentativas. Retry de envio
após término íntegro é transporte, não nova execução experimental.

`abort`, checkpoint e complete serializam pelo mesmo bloqueio de sessão.
Interrupção conhecida antes do encerramento principal proíbe o cliente de
solicitar complete; abort vencedor impede complete. Complete já confirmado
não é apagado por aviso tardio: evidência posterior de violação exige registro
de invalidação auditável e exclusão dos resultados válidos, preservando linhas e
recibo históricos. O contrato alvo validado prevê
`POST /participant/session/invalidate`, corpo fechado `{reason,event_at_ms}`:
razão enumerada D2/D5, tempo monotônico finito do evento (nulo quando não
observável), mesma credencial/CSRF/Origin e prazo. É idempotente por sessão,
retorna 200 `{session_id,valid_for_result:false}` após commit, inclusive se
complete já venceu; preserva recibo e observações. Não reabre sessão nem aceita
novo resultado. Evento posterior ao término íntegro não invalida o bloco.
Após vencimento/revogação, canal participante permanece bloqueado; revisão
profissional vinculada ao projeto registra invalidação auditável por operação
`POST /projects/{project_id}/sessions/{session_id}/invalidate`, mesmo corpo,
perfil importação/administração e CSRF. Consultas profissionais de resultado
acrescentam `valid_for_result` e motivo, omitem inválidos por padrão de listas,
resumos e exportações oficiais; acesso direto autorizado ao histórico mostra a
marca sem resultado utilizável. Invalidação não é reversível pela API. Nenhum
resultado pode continuar válido apenas porque a corrida favoreceu complete. Servidor não consegue provar que o
cliente notificou todos os eventos. Falta de aviso não autoriza conclusão por
quantidade de checkpoints ou tempo decorrido.

Sessão sem conclusão válida ao fim do prazo é incompleta; expiração lógica deve
ser respeitada imediatamente nas leituras e escritas, mesmo antes de uma rotina
idempotente materializar o estado. Conservar motivo observado; sem aviso,
registrar causa desconhecida. Não criar resultado automaticamente com prefixo 16.
Nova execução exige novo convite/sessão e prática; mesma visita pode ser usada
sem misturar observações de sessões diferentes.

### Inspeção profissional de recebimento

`GET /projects/{project_id}/sessions/{session_id}` exige profissional ativo,
vínculo e projeto ativo; usa exclusivamente a credencial de leitura. Retorna
objeto fechado com `session_id`, `state`, `expires_at`, `complete`,
`valid_for_result`, `abort_reason`, `revoked`, `invalidation` e `checkpoint`.
`invalidation` é nulo ou `{reason,source,event_at_ms,recorded_at}`; `checkpoint`
tem os mesmos três campos da consulta participante. Sem conclusão, validade é
sempre falsa; prazo vencido em preparing/running aparece como expired, sem
fabricar motivo. Não devolve observações brutas, métricas ou credenciais.
Rejeita corpo/query e usa os mesmos erros seguros e no-store. Este canal não
concede retomada nem exportação parcial; a interface de inspeção pertence a M4/M5.

### Identificação visual complementar de D3/D4 — 2026-11-05

Variante visual `stroop-web-outline`, versão `1.0.0`, definida no protocolo.
Snapshot compartilhado `condicoes/web_protocol.json` passa a incluir seção
`visual` e `hud.live_accuracy=false`; tempos/cores/resposta permanecem.
`test_version` e `protocol_id` continuam identificando o protocolo cognitivo;
`app_version=web-<versão do pacote>+visual.1.0.0` distingue a apresentação usando
os metadados já fixados em start/conclusão/recibo. Não acrescentar campos ao
payload fechado, schema ou CSV de 21 colunas. Recibos/resultados antigos mantêm
app_version original; não atribuir versão visual com base só em test_version.

## Autenticação local — contrato alvo CHG-004

Decisão de 2026-11-06, [ADR-006](../arquitetura/ADR-006-autenticacao-local.md),
implementada e verificada em M6 (WEB-021/024); estado, evidências e aceite ficam
somente no [backlog canônico](../Projeto%20Stroop%20Test.md).
Para a versão alvo WEB, esta seção substitui o mecanismo OIDC profissional das
seções anteriores, preservadas como contrato legado/histórico.
Demais payloads experimentais, CSV, convites, recibos e prazos participantes ficam intactos.

### Login, identidade e sessão

- `POST /api/v1/auth/login`: JSON fechado `{username,password}`. `username`:
  1–64 ASCII `[A-Za-z0-9_.-]`, aparado e convertido para minúsculas; unicidade
  usa a mesma normalização. `password`: string de 15–128 caracteres Unicode,
  sem aparar/normalizar/truncar (exceção explícita à convenção geral de strings).
  Limite de corpo específico 4 KiB, UTF-8/JSON; sem query/formulário simples.
  `Origin` único exatamente igual ao configurado obrigatório, inclusive antes
  da sessão: proteção de login CSRF; sem origem, null ou divergente → 403
  `csrf_failed`. Não reutilizar token CSRF de sessão anterior para login.
- Sucesso 200 fechado `{user_id,role,expires_at,csrf_token}`, formato de `/me`;
  emite cookie profissional novo aleatório de pelo menos 256 bits, guardado por
  hash no servidor, nunca no corpo. Invalidar sessão profissional anterior do
  mesmo navegador; impedir fixação. Destino frontend fixo/local: dashboard.
- Usuário inexistente, senha incorreta, conta bloqueada: mesmo 401
  `authentication_required`, mensagem genérica “Usuário ou senha inválidos.”,
  sem `registration_request`, iss/sub ou dicas de cadastro; nenhum cookie novo.
  Limitação: 429 `rate_limited` com `Retry-After`; indisponibilidade: 503
  `service_unavailable`. Envelope fechado existente e no-store em todos os casos.
  Corpo inválido mantém 400/413/415/422 das convenções; erros nunca refletem entrada.
- `GET /api/v1/auth/me`: conserva campos `{user_id,role,expires_at,csrf_token}`;
  `user_id` opaco/estável representa principal técnico local e não codificação
  Google obrigatória. Cliente não interpreta nem escolhe identidade/perfil.
  Sem sessão válida, expirada/revogada ou conta bloqueada → 401. APIs protegidas
  mantêm 401/403/404 e autorização por objeto/projeto; nenhum redirect HTML em API.
- Cookie `__Host-stroop_professional`: Secure, HttpOnly, SameSite=Lax, Path=/,
  sem Domain; `Max-Age`/`Expires` não excedem limite servidor. Teto absoluto
  **8 horas**, sem extensão por atividade, e inatividade **30 minutos** no
  servidor desde login/última operação autenticada autorizada. `/me`/polling
  automático não renova atividade; definir testes de fronteira e concorrência.
  `expires_at` devolve o menor prazo efetivo; frontend revalida quando necessário,
  limpa RAM em 401/logout e não decide validade. Horário do cliente não prorroga.
- `POST /api/v1/auth/logout` mantém `{}`/204, Origin e CSRF e invalidação efetiva
  no banco, inclusive replay em outra aba; repetição sem cookie continua 204
  após validar Origin. Todas as escritas autenticadas conservam X-CSRF-Token
  e Origin exatos. Sem localStorage/sessionStorage/IndexedDB ou senha persistida.

### Alteração e revogação

- `POST /api/v1/auth/password`: sessão ativa, Origin e CSRF, JSON fechado
  `{current_password,new_password}`; strings com os limites acima, 4 KiB no total.
  Senha atual inválida → 401 genérico e rate limit como login. Nova senha fora
  da política → 422 genérico sem eco. Sucesso 204 **após commit** do novo hash/
  versão e revogação de todas as sessões, inclusive corrente; apaga cookie e
  frontend exige novo login. Sem criação de sessão automática pela troca.
- `POST /api/v1/admin/users/{user_id}/sessions/revoke`: `{}`, 204 após revogar
  todas as sessões do principal explicitamente indicado; administração ativa,
  Origin/CSRF e rate limit de escrita. Alvo fora do contrato/inexistente → 404;
  perfil insuficiente → 403. Revogar a própria conta encerra sessão corrente.
  Idempotente quanto a sessões já revogadas; não altera vínculos ou dados.
- Bootstrap e recuperação são procedimentos administrativos protegidos fora do
  HTTP público, conforme [segurança](../seguranca/AUTENTICACAO_E_PERMISSOES.md#autenticação-local--especificação-alvo-chg-004).
  API não expõe endpoint de recuperação pública nem cadastro. Bloqueio de conta
  e rotação/recuperação impedem uso de sessão antiga em todas as operações.
- Gestão mantém perfis/vínculos e proteção do último admin. `GET /admin/users`
  alvo retorna identidade técnica opaca, role e active, sem hash/senha e sem
  exigir issuer/subject Google; campos legados de exibição ficam documentados
  como históricos. `PATCH /admin/users/{id}` preserva role/active e valida último
  admin; negar criação de contas adicionais com 403 `permission_denied` no
  `POST /admin/users` alvo. Não remover recursos históricos nem habilitar
  ampliação multiusuário por esta decisão. Ajustar clientes/testes juntos.
- No corte alvo, `GET /auth/login`, callback e alias `/oauth2callback` deixam de
  emitir sessões OIDC e retornam 404; nenhuma configuração Google é obrigatória.
  Código/DDL legado permanecem até retirada especificamente autorizada.

Defaults de antiabuso e política de senha estão na especificação de segurança;
rate limit de leituras/escritas continua distinto do login. Convites mantêm
24 h, participante 30 min absolutos, CSRF e cookies separados. Rotação de senha
revoga sessões profissionais; autorização do emissor bloqueado/perfil/vínculo
revogado continua revalidada em convites/sessões participantes. Não declarar
que trocar senha, por si, revoga convites: exposição de convites exige sua
revogação explícita. Testar a distinção em AUTH-L04/L06/L07.
