# ADR-002 — Hospedagem WEB na VPS existente

Nota de 2026-11-04: decisão histórica preservada. [ADR-004](ADR-004-replanejamento-plataforma.md)
consolida direção atual e substitui orientações antigas de backlog/comandos/Git;
não revoga regras metodológicas ou mapa explícito de legado.

Data: 2026-10-16. Decisao operacional aprovada pelo usuario na sessao.
Complementa o [ADR-001](ADR-001-evolucao-web.md), sem mudar a stack ou o
monolito modular. Estado e aceite no [roadmap WEB](../ROADMAP_WEB.md).

## Contexto e decisao

O usuario aprovou os itens 1–19 da proposta consolidada: protocolo desktop,
acesso por projeto, convites de uso unico, minimizacao de dados, coexistencia
com os adaptadores atuais e execucao autonoma com commits locais validados.
Informou que a finalidade e coleta de dados por seu grupo de pesquisa, que o
publico sao os participantes da pesquisa sem restricao demografica nova, e
que assume as responsabilidades de protocolo, validacao, operacao e incidentes.

A hospedagem WEB sera em **VPS ja adquirida**, com dominio ja existente.
Nenhum provedor, hostname, IP, credencial, sistema operacional ou capacidade
foi informado nesta decisao. Nao presumir OCI, ARM64 ou franquia gratuita.
As especificacoes OCI/Always Free anteriores permanecem historico do legado;
nao sao requisito de infraestrutura da versao WEB.

Manter Docker Compose e Nginx, com frontend/API/banco internos e somente o
proxy publicado em HTTPS. Preparar imagens e configuracao portaveis; escolher
plataforma da imagem e limites de recursos com base na VPS efetivamente
verificada na homologacao autorizada. Nao criar recursos ou contratar servicos.

## Operacao e limites aprovados

- Backups diarios criptografados, 30 geracoes; perda maxima alvo de 24 horas
  e recuperacao alvo em ate quatro horas, ambas sujeitas a ensaios reais.
- Medir e documentar capacidade e limite de concorrencia no ambiente alvo;
  nenhum minimo de simultaneidade foi contratado ou prometido.
- Pilotos e testes sinteticos autorizados. Medicoes manuais e aceite final
  ficam com o usuario responsavel; aprovacao da proposta nao comprova execucao.
- Preservar PsychoPy, Streamlit, historico e CLIs. Gestao/importacao legadas
  continuam disponiveis; nao retirar componentes nem introduzir instrumentos
  reais sem seus contratos proprios.
- O Codex executa escolhas tecnicas rotineiras, dependencias necessarias,
  testes, correcoes, documentacao, subagentes e commits locais autonomamente.
  Push, merge e producao exigem autorizacao especifica sobre entrega preparada;
  W22 continua sendo executada pelo usuario.

## Consequencias e dependencias externas

Desenvolvimento e testes locais nao dependem de credenciais da VPS ou dominio.
Homologacao e producao exigem informacoes reais do host, DNS/TLS, OIDC,
destino externo de backup, custodia das chaves e evidencias de operacao.
Nenhum desses recursos foi acessado ou configurado nesta decisao.

Uso de dados reais exige as configuracoes e textos especificos de pesquisa
sob responsabilidade do usuario; nao inferir consentimentos aplicaveis ou
restricoes demograficas a partir da expressao "qualquer pessoa". Os contratos
de acesso/dados e suas finalidades serao especificados em W03. Nao instalar
barreira automatica por idade, sexo ou perfil clinico sem requisito aprovado.
