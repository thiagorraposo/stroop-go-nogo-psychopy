# Threat model

Revisão alvo CHG-004, 2026-11-06: referências OIDC abaixo preservam o código
atual/histórico. Para a versão alvo WEB, aplicar
[autenticação local](AUTENTICACAO_E_PERMISSOES.md#autenticação-local--especificação-alvo-chg-004)
e [ADR-006](../arquitetura/ADR-006-autenticacao-local.md). Estado/riscos no backlog.


Escopo: preparacao para exposicao futura do dashboard autenticado. Este modelo
nao transforma o experimento em instrumento clinico e nao autoriza dados reais
ou deploy. Deve ser revisto na Etapa 11 diante do host, DNS, certificado,
firewall e destino de backup efetivos.

## Ativos e fronteiras

Ativos principais: dados pseudonimizados das avaliacoes, identificadores
locais, perfis OIDC, auditorias, credenciais PostgreSQL/OIDC, chave de backup e
backups criptografados. Google Identity e fronteira externa de autenticacao;
Nginx e a unica entrada publica futura; dashboard e PostgreSQL sao fronteiras
internas; host, operador, pesquisador responsável e CEP permanecem fora do
software.

## Ameacas e controles

| Ameaca | Controle implementado | Risco residual / responsavel |
|---|---|---|
| Acesso sem cadastro ou privilegio excessivo | OIDC, chave `iss` + `sub`, perfis no PostgreSQL e revalidacao de expiracao/bloqueio em cada operacao | Comprometimento da conta Google; administrador deve bloquear e responder ao incidente |
| Exposicao direta do banco ou Streamlit | somente Nginx publica 80/443; redes separadas e backend interno | Firewall e regras OCI devem ser confirmados na Etapa 11 |
| Interceptacao de sessao | TLS obrigatorio, HSTS, CORS/XSRF do Streamlit, cookies OIDC e secrets externos | Certificado, hostname e redirect URI reais ainda nao existem |
| Abuso de requisicoes e upload | rota CSV dedicada 5 MiB/10.000 registros, concorrencia limitada, validacao UTF-8/CSV e temporario `0600` descartado | Limite por IP nao impede botnet; monitorar sem capturar payload |
| CSV malicioso ou identificavel | copia minimizada no navegador; API rejeita nome/iniciais, valida esquema, nome/path fornecido nao e usado, sem execucao e transacao atomica | Cliente alternativo pode transmitir dados antes da rejeicao; limite de transporte e minimizacao nao substituem governanca de coleta |
| Vazamento por erros e logs | detalhes ocultos, mensagens fechadas e log Nginx sem URI/query/cookies/body | Bibliotecas e host precisam de revisao apos atualizacoes |
| Vazamento por auditoria de rejeicao | somente SHA-256, status e codigo fechado; expurgo em 30 dias | Hash pode permitir correlacao de arquivos identicos; acesso deve ser restrito |
| Falha de resposta/duplicacao de upload WEB | UUID idempotente, estado/hash auditados, avaliacao e auditoria na mesma transacao, consulta explicita e sem retry automatico | Reenvio explicito depende de manter a copia minimizada somente em RAM durante a sessao |
| Escalada no container | UIDs dedicados, raiz somente leitura, capabilities removidas, `no-new-privileges`, PIDs/CPU/memoria limitados | Kernel e daemon Docker continuam parte da base confiavel |
| Ransomware/perda do banco | backup diario AES-256-GCM, checksum, 30 geracoes e restore mensal isolado | Destino externo so sera definido na Etapa 11 |
| Roubo da chave junto ao backup | ferramenta recusa chave dentro da arvore de backups | Custodia institucional e rotacao da chave continuam operacionais |
| Retencao excessiva | prazos provisorios, expurgo separado e decisao final pelo protocolo/pesquisador/CEP | Confirmacao institucional pendente antes de dados reais |
| Dependencia vulneravel | imagens multi-arquitetura e dependencias diretas fixadas | Fixacao nao corrige CVE; revisar e atualizar com teste periodico |

## Suposicoes e exclusoes

- o operador protege o host e nao expõe o socket Docker;
- secrets possuem acesso minimo e nao entram em Git, imagem ou backup;
- somente usuarios previamente cadastrados acessam operacoes;
- nao ha garantia contra administrador malicioso, host comprometido ou captura
  de tela pelo usuario autorizado;
- exportacoes baixadas passam à custodia do usuario e da instituicao;
- disponibilidade, regras OCI, ARM64 efetivo e dimensionamento final pertencem
  a Etapa 11.

Aceitar dados reais exige confirmar institucionalmente finalidade, base legal,
papéis dos agentes, protocolo/CEP, identificadores permitidos, retencao,
atendimento aos titulares e resposta a incidentes. Consulte
[tratamento de dados](TRATAMENTO_DE_DADOS.md) e
[resposta a incidentes](RESPOSTA_A_INCIDENTES.md).

## Extensao WEB aprovada em 2026-10-16

As secoes anteriores registram o hardening legado. Esta extensao especifica
ameacas e controles alvo da API/navegador, **a implementar e verificar** nas
etapas WEB; nao lhes atribui o estado de controles ja implementados. Regras
de acesso ficam em [ACESSO_WEB.md](ACESSO_WEB.md), transporte em
[CONTRATO_API_WEB.md](../desenvolvimento/CONTRATO_API_WEB.md), e hospedagem na VPS ja adquirida
com dominio existente em [ADR-002](../arquitetura/ADR-002-hospedagem-vps.md).
As antigas referencias a OCI/ARM64/hostname inexistente descrevem preparacao
legada, sem impor esse provedor nem negar a existencia do dominio atual.

Novas fronteiras: participante sem OIDC -> navegador/motor -> API -> PostgreSQL;
profissional -> Google OIDC -> API com autorizacao por projeto. O navegador e
nao confiavel: timestamps e respostas declaradas permitem validar consistencia,
nao provar identidade civil, participacao efetiva, latencia fisica ou ausencia
de fraude. A chave codigo-pessoa continua fora do sistema.

| Ameaca WEB | Controle exigido | Risco residual / responsavel |
|---|---|---|
| Consulta/exportacao cruzada por UUID, filtro ou admin | Vinculo de projeto tambem para admin; conferir projeto real do objeto a cada operacao e devolver 404 fora do escopo | Admin pode conceder vinculos explicitamente; responsavel controla concessoes e revisa acessos |
| Codigo vazado ou adivinhado | Codigo opaco forte, hash no servidor, sem URL/log, 24 h, rate limit e revogacao | Primeiro portador pode resgatar; profissional entrega por meio adequado e revoga exposicao |
| Replay e corrida no resgate | Consumo atomico unico, credencial distinta, sem reemitir cookie por codigo consumido | Resposta perdida exige novo convite; nao usar identidade civil como atalho |
| Roubo/fixacao de sessao e CSRF | Cookies opacos separados, Secure/HttpOnly/SameSite, renovacao no login, CSRF e origem nas escritas, state/nonce/PKCE no OIDC | Host ou navegador comprometido permanece fora da garantia; operador responde ao incidente |
| Profissional bloqueado ou vinculo revogado durante coleta | Revalidar acesso e emissor nas operacoes; invalidar convites/sessoes ativos; prazo participante de 30 min sem renovacao | Dados ja apresentados ou exportados nao podem ser retirados remotamente |
| Manipulacao de condicoes, RT ou metricas | Snapshot e ordem imutaveis, campos fechados, validacao de 16 tentativas/janelas/tempos; recalculo no nucleo e transacao unica | Payload coerente pode ser fabricado; medicao de software nao certifica equivalencia fisica |
| Reenvio duplicado ou resultado conflitante | Sessao + hash canonico, restricao unica e recibo; conflito 409; rollback integral | Perda de RAM antes de confirmar pode perder resultado; nao prometer recuperacao offline |
| Interrupcao silenciosa por reload/foco/aba | Motor invalida principal, tentativa de abortamento e expiracao no servidor; sem retomada/parcial | Browser pode nao transmitir fechamento; prazos e validacao nao recuperam exposicao |
| Identificacao indevida em dados remotos | Pseudonimo/projeto/visita/avaliador tecnico; recusar nome/iniciais/CPF/contato/idade/sexo; mascarar legado no adaptador WEB | Pseudonimo ainda correlaciona visitas; responsavel custodia mapa externo |
| Vazamento por erro, cache, analytics ou export | Erros fechados, logs sem entradas, no-store, sem persistencia JS; exportacao reautorizada/minimizada e nome seguro | Exportacao autorizada passa a custodia institucional; captura de tela nao e impedida |
| Ativar coleta real sem requisitos especificos | Projeto sintetico por padrao; habilitacao real depende de aviso/requisitos registrados pelo responsavel | Software nao concede aprovacao etica nem determina consentimento; responsabilidade do usuario |
| Perda da VPS/banco/chave | Backups diarios criptografados, destino separado, 30 geracoes e ensaios de restauracao | RPO de 24 h/RTO de 4 h sao objetivos a medir; host/chaves/destino exigem configuracao operacional |

Somente proxy HTTPS publica a aplicacao; API, dashboard legado e banco permanecem
internos. Ausencia atual de credenciais/hostname de producao nao impede testar
esses limites com identidades, banco e origem sinteticos. Antes da operacao,
o responsavel configura TLS/OIDC/firewall, backup externo e custodia de chave,
valida capacidade/recuperacao e fornece textos/requisitos da pesquisa.
Os controles WEB exigem os testes negativos e de concorrencia das etapas
correspondentes; esta matriz nao comprova sua execucao.

## Revisao WEB integrada — W17, 2026-10-16

Escopo adicional: frontend React, motor jsPsych, API FastAPI, cookies separados
profissional/participante e PostgreSQL. Fontes de autorizacao e minimizacao:
[acesso WEB](ACESSO_WEB.md) e [contrato HTTP](../desenvolvimento/CONTRATO_API_WEB.md).
VPS e dominio foram adquiridos; nenhuma configuracao real de host, DNS, TLS ou
OIDC foi validada por esta revisao local. Referencias antigas a OCI nao definem
provedor atual; prevalece [ADR-002](../arquitetura/ADR-002-hospedagem-vps.md).

| Ameaca WEB | Controle observado/correcao | Evidencia e limite |
|---|---|---|
| Confusao entre sessao profissional e participante | Cookies __Host separados, hashes e HMAC com dominios distintos; Origin/CSRF exatos e escopo revalidado | Testes negativos, logout e replay reais; navegador nao declara privilegios |
| Acesso cruzado ou heranca por nome legado | Membership ativo inclusive admin; mapa legado operacional explicito; SELECT por coluna e READ ONLY | W14/W15: consulta/exportacao negadas apos revogacao, sem nome/iniciais |
| Duplicacao/resultado parcial | Lock transacional, ordem persistida, validacao/recalculo servidor e recibo idempotente | Concorrencia backend e falhas de rede antes/depois do commit em HTTPS real |
| XSS/inclusao de dados como documento | React trata texto; sem HTML arbitrario. API impoe nosniff, CSP default-src none/frame-ancestors none/base-uri none/form-action none, XFO DENY, no-referrer e CORP same-origin em sucesso/erro/CSV | Testes ASGI verificam headers, inclusive substituicao de valores fracos. CSP da pagina frontend pertence ao proxy W19 e precisa de teste proprio |
| Framing HTTP ambiguo | Recusa Content-Length com Transfer-Encoding, TE duplicado/invalido, comprimento divergente e corpo acima64KiB | Testes no limite ASGI; nao alegar que substituem validacao do parser/proxy publico |
| Abuso por cookies aleatorios | Somente hash de credencial emitida cria contador participante; leitura/escrita e profissional sao separados | Variar16 operacoes com oito cookies inventados resulta401 e zero contadores; proxy deve limitar volume por IP/conexao antes da API |
| Nonce OIDC invalido | Unicode fora do contrato produz falha fechada de OIDC | Teste negativo evita TypeError500; loginGoogle externo continua gate de homologacao |
| Vazamento em resposta/log/storage | Erros fechados e request_id; no-store; sem log de path/query/body/cookies. CSRF/resultados em RAM; limpeza/logout/expiracao/BFCache | Testes de logs/erros, navegador e CSV. Comprometimento de host/conta/captura de tela permanecem externos |

### Pendencias operacionais de seguranca

- W19 deve aplicar CSP de pagina compativel com bundle local/jsPsych, TLS,
  HSTS, protecao de enquadramento, limites por IP/conexao e roteamento de mesma
  origem. Headers da API sao politica para respostas de dados, nao politica
  suficiente para servir HTML da aplicacao.
- W18 deve automatizar verificacoes de dependencias/secrets e testes negativos.
  Dependencias fixadas, por si so, nao comprovam ausencia de vulnerabilidades.
- W21 deve testar OIDC/redirect/certificados e configuracao efetiva no ambiente
  alvo; nao existem credenciais reais disponiveis nesta validacao.
- Pesquisador/operador responde por elegibilidade, informacao/consentimento,
  prazos finais de retencao e acesso institucional antes de dados reais.

Nao executar ataques ou scanners contra VPS/dominio como decorrencia destes
testes locais. Risco operacional nao resolvido continua visivel no roadmap;
nenhuma configuracao futura e descrita como protecao ja implantada.

Baseline da pagina WEB: `web/security-headers.json` restringe scripts, estilos,
imagens, fontes e conexoes a propria origem, sem unsafe-inline/unsafe-eval;
proibe frames, objetos e workers, restringe base/form e desabilita permissoes
nao usadas. O proxy de teste HTTPS consome esse arquivo; a integracao ao proxy
operacional pertence a W19. A manipulacao de propriedades CSS pelo motor nao
e uma permissao geral de HTML inline, conforme a
[documentacao de style-src](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src).
Os testes de CSP precisam passar no bundle real; a previa Vite de desenvolvimento
na porta4173 nao constitui hospedagem com essa politica de producao.

## Ameaças da autenticação local — CHG-004

| Ameaça | Controle alvo planejado | Risco residual / verificação |
|---|---|---|
| Banco/hash exposto ou senha reutilizada | Argon2id/salt/custo, política de senha, grants e backups protegidos | Hash não elimina quebra offline; AUTH-L01/L08, rotação por incidente |
| Enumeração/força bruta/DoS | Mensagens/corpos genéricos, hash fictício, limites por conta/origem e concorrência | Conta única pode sofrer negação de acesso; AUTH-L03/L09 e revisão WEB-024 |
| Login CSRF/fixação/replay ou sessão antiga | Origin no login, nova sessão, CSRF autenticado, inatividade/teto e revogação efetiva | Comprometimento de host/browser permanece externo; AUTH-L04/L05 |
| Recuperação/rotação concorrente ou abuso de admin | Operador protegido, confirmação/auditoria, transação de senha e revogação; projetos explícitos | Credencial administrativa comprometida amplia alcance; AUTH-L02/L06 |
| Compartilhamento e saída de profissional | Custódia, troca de senha/revogação global e revisão DEC-03 | Sem autoria ou revogação individual; R12 permanece aberto, WEB-033/039 |
| Corte/rollback/restore ressuscita acesso | Schema aditivo testado, invalidação de sessões, redefinição de senha restaurada | Exigir AUTH-L08/L09/WEB-032; sem reativação automática de OIDC |

Todos os controles locais são PLANEJADOS. Acesso por projeto e separação do
participante não mudam. Nenhum scanner/ataque contra produção foi autorizado.
