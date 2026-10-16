# Acesso e minimizacao de dados WEB

Decisoes aprovadas pelo usuario em 2026-10-16, ao aprovar os itens 1–19 da
proposta da sessao. Finalidade: coleta de dados pelo grupo de pesquisa do qual
faz parte. Publico: participantes da pesquisa, podendo ser qualquer pessoa;
nenhum filtro demografico novo no aplicativo. O usuario e responsavel por
protocolo, validacao, operacao, textos e requisitos especificos da pesquisa.

Este documento especifica os controles de W03; nao afirma que autenticacao
HTTP, vinculos ou coleta WEB ja foram implementados. Implementacao e evidencias
seguem o [roadmap WEB](../ROADMAP_WEB.md). Operacoes, payloads, cookies, CSRF,
codigos de erro e prazos estao no [contrato HTTP](../desenvolvimento/CONTRATO_API_WEB.md);
o metodo fica no [protocolo](../experimento/PROTOCOLO_WEB.md).

## Profissionais e autorizacao

Google OIDC autentica; cadastro previo ativo e autorizacao no servidor
determinam acesso. Preservar identidade permanente `iss` + `sub` e os perfis
existentes `consulta`, `importacao` e `administracao`. E-mail e auxiliar,
nao identifica participante nem concede privilegio. Sem autocadastro,
senhas proprias ou acesso por claims que o navegador declarar.

Vinculo ativo a projeto e obrigatorio para consultar dados, exportar e emitir
convites, **inclusive para administradores**. Administracao global permite
gerenciar projetos/vinculos; nao constitui acesso automatico a dados de pesquisa.
Revalidar cadastro, bloqueio, perfil e vinculo em cada operacao, inclusive no
download. Identificadores imprevisiveis e botoes ocultos nao substituem essa
verificacao. O servidor deve consultar o projeto real do objeto solicitado.

| Operacao | consulta | importacao | administracao | Participante |
|---|---|---|---|---|
| Login e propria identidade | Cadastro ativo | Cadastro ativo | Cadastro ativo | Nao usa Google |
| Listar projetos | Somente vinculados | Somente vinculados | Todos para gestao | Nao |
| Criar projetos/gerenciar vinculos | Nao | Nao | Sim, gestao global | Nao |
| Criar/revogar convite | Nao | Vinculo e projeto ativo | Vinculo e projeto ativo | Nao |
| Listar, detalhar e exportar resultados | Vinculo ativo | Vinculo ativo | Vinculo ativo | Nao |
| Resgatar convite/preparar/executar | Codigo e sessao participante separados do login profissional | Igual | Igual | Convite valido e credencial propria |
| Resumo da execucao participante | Somente pelo fluxo participante proprio | Igual | Igual | Somente a propria sessao concluida, durante sua validade |

Integrantes autorizados do mesmo projeto compartilham a consulta de seus
resultados; nao restringir cada profissional apenas as execucoes que criou.
O criador do convite e o avaliador tecnico fixado pelo servidor. O participante
nao escolhe projeto, avaliador, visita ou pseudonimo depois do resgate.
Profissional sem vinculo recebe 404 para objetos do projeto; perfil insuficiente
dentro de escopo permitido recebe 403. Administrador pode atribuir vinculos,
mas essa e uma acao administrativa explicita e auditavel.

Bloquear conta/revogar vinculo nao apaga resultados. Deve impedir novas
operacoes profissionais e invalidar autorizacao dos convites e sessoes ainda
ativos emitidos por essa conta nesse projeto. Antes de resgate, inicio e
conclusao, revalidar projeto ativo, autorizacao do emissor e ausencia de
revogacao. Mudanca de perfil que retire permissao de emitir convite tem o
mesmo efeito para sessoes ainda abertas. Avaliacao concluida permanece
consultavel pelos demais membros autorizados.

## Participantes, codigos e interrupcoes

O convite atende coleta remota ou supervisionada, sem conta Google do
participante. Somente o codigo enviado no corpo de resgate concede acesso;
UUID, pseudonimo, visita ou cookie profissional nao o substituem. O
profissional entrega o codigo por meio externo adequado; nao colocar codigo
em URL, query, analytics, logs ou screenshots.

Codigo e secreto de uso unico, com prazo de 24 horas desde emissao. Resgate
atomico cria credencial participante separada, valida por 30 minutos desde
ativacao, sem prorrogacao por consultas, pratica, inicio ou retries. Guardar
hash dos segredos no servidor. Cookie e opaco, HttpOnly/Secure; escritas usam
CSRF e origem conforme contrato. Nao devolver credencial participante a quem
apenas conhece um codigo ja consumido.

Quem receber codigo vazado antes do titular pode utiliza-lo primeiro; o
software nao autentica a identidade civil de quem o apresenta. Reduzir risco
por entrega controlada, prazo, uso unico, limite de resgates e revogacao pelo
profissional. Identificada exposicao, revogar convite/sessao e emitir outro;
nao reutilizar codigo anterior. Resposta de resgate perdida nao justifica
emitir outra credencial para o mesmo codigo.

A sessao nao e uma avaliacao. Ordem e protocolo sao fixados no servidor;
apenas conclusao integral e valida gera avaliacao. Foco/aba/Escape/recarga
seguem a interrupcao aprovada, sem retomar principal nem exportar parcial.
Aviso de fechamento pode nao chegar: expirar e bloquear conclusao posterior.
Reenvio de resultado mantido em RAM usa mesmo corpo ate o prazo; confirmacao
do servidor antecede “salvo”. Nao persistir resposta ou resultado em
localStorage, sessionStorage, IndexedDB, service worker ou arquivo offline.
Fechar/recarregar pode perder envio ainda nao confirmado.

## Dados permitidos e finalidade

Nao coletar nome, iniciais, CPF, contato, idade ou sexo no navegador/servidor
WEB. Correspondencia codigo-pessoa fica fora deste sistema, sob custodia do
responsavel. Nao inferir anonimato por usar pseudonimo.

| Campo/grupo | Origem e finalidade | Escopo de acesso |
|---|---|---|
| `project_id` e codigo do projeto | Profissional/servidor; delimitar estudo, autorizacao e agrupamento | Membros; admin ve metadados para gestao |
| `participant_id` pseudonimizado | Profissional; relacionar visitas dentro da pesquisa sem identidade civil | Membros do projeto; nao necessario ao motor |
| `visit` | Profissional; distinguir momento da coleta | Membros do projeto; fixado no convite |
| `evaluator_id` | Servidor; conta criadora responsavel pela emissao | Membros do projeto; sem e-mail ou nome no resultado |
| `session_id`, `invitation_id`, estados e prazos | Servidor; uso unico, revogacao, expiracao e rastreabilidade operacional | Somente atores autorizados; IDs nao concedem acesso |
| Hash de codigo/cookie, transacao OIDC e CSRF | Servidor; autenticar e impedir replay/CSRF | Somente backend; segredo nunca vira dado de pesquisa/export |
| `iss`, `sub`, perfil, bloqueio e vinculos | Identidade validada/cadastro; autorizacao e auditoria profissional | Autorizacao/administracao; nao enviados ao participante |
| Protocolo, versao do teste/app e plataforma | Servidor e app; distinguir variante, proveniencia e interpretacao | Motor e membros; nao alterar CSV de 21 colunas |
| Ordem, respostas, tempos monotones e periodo de quadro | Motor; classificacao, metricas e consistencia temporal | Resultado proprio resumido; detalhe somente membros |
| Timestamps civis e hash canonico/recibo | Servidor; identificar execucao e evitar duplicacao no reenvio | Backend/membros; recibo proprio ao participante |
| Logs/auditorias | Codigos fechados e IDs aleatorios; diagnostico operacional e seguranca | Operador autorizado; sem payload ou identificador do participante |

O resultado HTTP participante tem somente seu resumo descritivo e recibo,
sem historico de outras visitas, detalhe de colegas, exportacao ou busca.
Profissionais vinculados consultam detalhe e CSV. O CSV WEB preserva 21 campos:
`participant_name=NAO_COLETADO`, `initials` vazio; demais metadados fixados no
servidor, RT em segundos e classificacoes recalculadas. Consulta/exportacao
WEB de dados legados tambem mascara nome/iniciais; nao altera arquivos locais.
Exportacao baixada passa a custodia do pesquisador/instituicao; sistema nao
controla copias posteriores feitas por usuario autorizado.

## Preparacao sintetica e ativacao de coleta real

Projetos devem distinguir `synthetic` de `research`, com coleta real inicialmente
desabilitada. Testes e desenvolvimento usam somente dados inequivocamente
sinteticos. Uma configuracao de projeto para uso real deve registrar:

- versao do aviso/informacoes aos participantes e texto a apresentar;
- requisitos especificos de elegibilidade e informacao/consentimento aplicaveis,
  fornecidos pelo responsavel, incluindo como sao atendidos no fluxo de pesquisa;
- confirmacao explicita e datada do responsavel, identificada por conta tecnica,
  de que os requisitos de uso real do projeto foram configurados;
- habilitacao explicita de coleta real pelo administrador responsavel.

Sem essas configuracoes, manter projeto em preparacao sintetica e recusar
emissao/resgate para coleta real. O aplicativo nao determina regra legal,
aprovacao etica ou capacidade de consentir. “Qualquer pessoa” nao cria filtro
de 18 anos, coleta de data de nascimento ou regra clinica. Os requisitos de
cada pesquisa sao definidos pelo responsavel, sem novos dados pessoais no
contrato. Se exigirem mudanca material do fluxo/dados, especificar e revisar
esse requisito antes da respectiva coleta, sem bloquear outras implementacoes.
Exibir o aviso configurado antes de executar a tarefa; etapas adicionais de
consentimento dependem do requisito especifico, sem presumir que um clique
substitui procedimento institucional. Nao prometer comprovacao de consentimento
que o software nao registrou.

VPS ja adquirida e dominio existente seguem
[ADR-002](../arquitetura/ADR-002-hospedagem-vps.md). Hostname, credenciais OIDC,
DNS/TLS, destino externo de backup e textos reais sao configuracoes de
homologacao/operacao. Sua ausencia nao bloqueia desenvolvimento e testes
sinteticos locais; acesso/deploy de producao continuam sob autorizacao propria.
Prazos e objetivos de recuperacao estao no
[tratamento de dados](TRATAMENTO_DE_DADOS.md); riscos residuais no
[threat model](THREAT_MODEL.md).

## Cenarios de aceite de acesso

| Cenario | Resultado exigido na implementacao |
|---|---|
| Identidade valida, sem cadastro/conta bloqueada | Recusar operacoes; nenhuma permissao derivada de e-mail ou claims do cliente |
| Consulta tenta emitir convite | 403 no projeto permitido; nao grava convite |
| Conta de outro projeto, inclusive admin sem vinculo de pesquisa | Dados, detalhe, convite e CSV respondem 404; nenhum conteudo/revelacao cruzada |
| Membros diferentes do mesmo projeto | Consulta compartilhada permitida; avaliador original preservado |
| Codigo vazado/usado/expirado/revogado | Uma unica credencial por resgate; usado 409, expirado 410, revogado/desconhecido 404; limite contra tentativas |
| Bloqueio/revogacao apos resgate | Proxima operacao recusa; nenhum novo resultado valido; coleta concluida nao e apagada |
| Cookie/CSRF de outro tipo ou origem incorreta | Cookies profissional/participante nao se substituem; erro 401/403 conforme contrato |
| Pesquisa real sem configuracao | Preparacao sintetica permitida; coleta real permanece desabilitada |
| Aviso/requisitos configurados | Texto correspondente ao projeto apresentado antes da tarefa; sem filtro demografico inventado |
| Resultado/CSV | Participante so proprio resumo; profissionais vinculados recebem exportacao minimizada, reautorizada no download |
| Retry, reload ou prazo final | Mesmo payload nao duplica; diferente conflita; reload nao retoma; sessao expirada nao conclui |

Esta revisao de cenarios fecha a especificacao; evidencias executaveis de
autenticacao, concorrencia, autorizacao e navegador pertencem as etapas
W06–W14. Nao confundir revisao documental com aprovacao de uso real.
