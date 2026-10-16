# Threat model

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
| Abuso de requisicoes e upload | rate/connection limits, 5 MiB, UTF-8/CSV, validacao antes da escrita e temporario descartado | Limite por IP nao impede botnet; monitorar sem capturar payload |
| CSV malicioso | extensao, tamanho, encoding, estrutura, nome aleatorio, `0600`, sem execucao e transacao | Conteudo valido ainda pode conter dados excessivos; protocolo deve minimizar campos |
| Vazamento por erros e logs | detalhes ocultos, mensagens fechadas e log Nginx sem URI/query/cookies/body | Bibliotecas e host precisam de revisao apos atualizacoes |
| Vazamento por auditoria de rejeicao | somente SHA-256, status e codigo fechado; expurgo em 30 dias | Hash pode permitir correlacao de arquivos identicos; acesso deve ser restrito |
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
[CONTRATO_API_WEB.md](CONTRATO_API_WEB.md), e hospedagem na VPS ja adquirida
com dominio existente em [ADR-002](arquitetura/ADR-002-hospedagem-vps.md).
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
