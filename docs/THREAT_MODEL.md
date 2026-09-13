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
