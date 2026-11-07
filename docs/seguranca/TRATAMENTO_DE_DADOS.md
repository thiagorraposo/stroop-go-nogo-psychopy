# Tratamento e retencao de dados

Atualização alvo CHG-004 (2026-11-06): substituir identidade OIDC profissional
por principal técnico local na versão alvo, conforme
[ADR-006](../arquitetura/ADR-006-autenticacao-local.md). Texto OIDC abaixo é
contrato atual/histórico. Hash de senha e sessões são dados sensíveis de acesso,
nunca dados de pesquisa/exportação/logs; backup continua criptografado. Auditoria
local registra conta, ação/resultado e ID técnico, sem autoria individual, com
prazo operacional provisório de 180 dias sujeito a DEC-03, sem alterar política
institucional por esta missão. Conta compartilhada requer avaliação institucional
explícita antes de dados reais; R07/R12 e WEB-033 no backlog.


Politica provisória autorizada em 2026-09-13 para orientar o hardening. Ela nao
substitui protocolo de pesquisa, decisao do pesquisador responsável, parecer do
CEP, base legal, aviso aos titulares ou normas internas. Todos os prazos devem
ser confirmados institucionalmente antes de dados reais.

## Categorias e prazos

| Categoria | Conteudo permitido | Prazo provisorio | Destino ao final |
|---|---|---:|---|
| CSV recebido | arquivo integral em temporario privado | somente durante o processamento | eliminacao imediata, em sucesso ou rejeicao |
| rejeicao de importacao | SHA-256, status e codigo fechado de erro | 30 dias | eliminacao automatizavel |
| logs operacionais | horario, metodo, status, bytes, duracao e ID aleatorio | 30 dias | eliminacao no host |
| auditoria OIDC | `iss`, `sub`, acao, resultado, horario e ID aleatorio | 180 dias | eliminacao automatizavel |
| dados da pesquisa | avaliacoes, metricas, tentativas e identificadores autorizados | minimo de 5 anos apos o termino da pesquisa | eliminar, anonimizar ou reter alem do minimo somente conforme protocolo, pesquisador responsável e CEP |
| backups | copia criptografada do PostgreSQL | 30 geracoes diarias | destruicao da geracao e de eventual replica externa |
| registro formal de incidente | fatos, avaliacao, medidas e comunicacoes necessárias | minimo de 5 anos | destino conforme norma institucional |

Dados da pesquisa permanecem pseudonimizados e com acesso por menor privilegio;
pseudonimizacao nao equivale a anonimização e continua sujeita à LGPD. A chave
de correspondencia, se existir, deve permanecer fora deste sistema e sob
custodia institucional. `participant_name` e `initials` so podem ser mantidos se
o protocolo os autorizar e justificar como necessários.

A LGPD nao define um prazo universal: o termino depende de finalidade,
necessidade, periodo informado, solicitacao aplicavel do titular e determinacao
da ANPD. A conservacao para pesquisa nao justifica guarda indiscriminada e deve
manter vinculo real com a finalidade. Referencias:
[perguntas frequentes da ANPD](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes) e
[guia para fins academicos e pesquisas](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/web-guia-anpd-tratamento-de-dados-para-fins-academicos.pdf).

O minimo de cinco anos segue a responsabilidade de guarda prevista para
pesquisas com participantes na
[Resolucao CNS 510/2016](https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/resolucoes/2016/resolucao-no-510.pdf/view).
A instituicao deve confirmar qual norma e protocolo se aplicam a este estudo.

## Regras operacionais

- nunca usar nome, iniciais, ID de participante ou nome original do arquivo em
  logs, mensagens, paths de temporario, backup, teste ou screenshot;
- nunca registrar corpo, linha, metrica, token, cookie, segredo ou DSN;
- restringir dados e backups aos perfis e operadores que precisam deles;
- manter chave AES-256 separada dos backups e de suas replicas;
- registrar e justificar legalmente qualquer suspensao de eliminacao;
- atender direitos dos titulares somente pelo procedimento institucional, sem
  apagar diretamente registros que estejam sob preservacao obrigatoria;
- revisar prazos ao encerrar a pesquisa, alterar finalidade, receber decisao do
  CEP ou mudar obrigacao legal.

O script de retencao remove apenas auditorias operacionais/OIDC. A eliminacao ou
anonimizacao das tabelas de pesquisa nao foi automatizada porque depende de
decisao humana documentada e nao pode ocorrer por simples variavel de ambiente.

## Extensao WEB aprovada em 2026-10-16

O usuario aprovou os itens 1–19 da proposta da sessao: coleta pelo grupo de
pesquisa ao qual pertence, participantes da pesquisa sem filtro demografico
novo e responsabilidade propria pelo protocolo, validacao, operacao e
incidentes. A hospedagem sera em VPS ja adquirida, com dominio existente,
conforme [ADR-002](../arquitetura/ADR-002-hospedagem-vps.md). Essa aprovacao de
produto nao demonstra aprovacao etica, consentimento aplicavel ou adequacao
institucional de uma coleta concreta.

As secoes anteriores preservam a politica provisoria e o historico do legado,
inclusive a referencia a guarda minima institucional a confirmar. Para a WEB,
nao criar eliminacao automatica de dados de pesquisa nem transformar aquela
referencia em prazo definitivo aprovado: retencao final depende da politica
institucional e do protocolo fornecidos pelo responsavel. Continuam os prazos
provisorios de logs por 30 dias, OIDC por 180 dias e backups por 30 geracoes
diarias, confirmados
pelo usuario para orientar a implementacao.

### Minimizacao e ciclo de dados

Finalidades por campo e matriz de acesso estao em [ACESSO_WEB.md](ACESSO_WEB.md),
sem duplicar regras de autorizacao. O servidor recebe somente pseudonimo,
projeto, visita e avaliador tecnico para contexto da coleta, alem de respostas,
tempos, proveniencia e identificadores operacionais necessarios ao protocolo.
Nao receber nome, iniciais, CPF, contato, idade ou sexo. O mapa codigo-pessoa
fica fora da aplicacao sob responsabilidade do pesquisador. Pseudonimizacao
permite correlacao e nao representa anonimato.

| Estagio/categoria WEB | Tratamento requerido | Prazo/destino |
|---|---|---|
| Entrada de convite | Codigo apenas no corpo, hash no servidor; nenhuma URL ou log com segredo | Resgate em 24 h; depois expira ou e revogado, nunca reutilizavel |
| Credencial participante e dados em memoria | Cookie HttpOnly separado; pratica/resultado somente em RAM, reenvio identico ate o prazo | Sessao de 30 min desde ativacao; interrompida/expirada nao cria avaliacao parcial |
| Resultado antes de confirmar | Nao persistir em armazenamento JS, service worker, arquivo ou cache duravel | Perda de pagina pode perder envio; “salvo” somente apos recibo/consulta confirmada |
| Avaliacao completa | Transacao, classificacao/metricas recalculadas, acesso por projeto | Preservar; nenhuma eliminacao automatica de pesquisa antes de decisao institucional documentada |
| Exportacao WEB | Somente profissional vinculado; CSV de 21 colunas com `participant_name=NAO_COLETADO`, `initials` vazio, nome de arquivo seguro | Download passa a custodia do pesquisador/instituicao; nao manter temporario desnecessario no servidor |
| Logs operacionais WEB | Categorias fechadas, horario/status/duracao e ID aleatorio; sem corpo, metadados de participante, query, cookie ou token | 30 dias, expurgo operacional |
| Auditoria profissional | Identidade tecnica OIDC, acao/resultado fechados, horario e ID aleatorio | 180 dias, expurgo conforme controle existente/ampliado |
| Backups WEB | Copia diaria criptografada, chave e destino separados, acesso minimo | 30 geracoes diarias; remover geracao e eventual replica conforme politica operacional |
| Configuracao de pesquisa | Aviso versionado, requisitos aplicaveis e habilitacao datada pelo responsavel | Preservar versoes relacionadas a coleta conforme politica institucional, sem dados pessoais adicionais do participante |

Os prazos de convite/sessao limitam autenticacao, nao determinam por si o
prazo de guarda de eventos operacionais. Hashes e metadados de convite/sessao
devem ser minimizados e perder poder de acesso imediatamente ao prazo/revogacao;
expurgo de registros operacionais deve respeitar as categorias acima e
preservar somente a proveniencia necessaria da avaliacao concluida. Nao guardar
segredos brutos para permitir recuperacao futura.

Consulta/exportacao WEB de linhas legadas deve mascarar nome/iniciais antes
de serializar ao navegador; a minimizacao nao reescreve CSV bruto ou banco
local existente. Auditar acessos administrativos/alteracoes de vinculo sem
incluir pseudonimo, corpo de resultado ou texto livre. Nao enviar dados de
pesquisa a analytics ou servicos externos por padrao.

### Responsabilidades antes da coleta real

O desenvolvimento e pilotos sinteticos estao autorizados. Cada projeto real
permanece desabilitado ate o responsavel fornecer/configurar aviso/informacoes,
requisitos especificos de elegibilidade e consentimento quando aplicaveis,
confirmacao de atendimento e habilitacao explicita, como definido em
[ACESSO_WEB.md](ACESSO_WEB.md). Nao criar regra etaria/clinica, coletar idade
ou interpretar “qualquer pessoa” como dispensa dos requisitos da pesquisa.
O software nao escolhe base legal, concede aprovacao institucional ou substitui
procedimentos externos. Se houver requisito adicional material, revisar o
respectivo fluxo antes de usa-lo com pessoas reais.

Continuam pendentes para operacao, sob responsabilidade do usuario: textos e
politica definitiva da pesquisa, configuracao segura de OIDC/DNS/TLS no dominio,
destino externo e custodia das chaves de backup, procedimentos de incidentes
e validacoes manuais exigidas. Nenhum desses itens impede implementar e testar
o produto com dados sinteticos. RPO de ate 24 h e RTO de ate 4 h sao objetivos
aprovados, a comprovar em ensaio de recuperacao; nao sao garantias demonstradas.

Os controles WEB desta extensao sao requisitos para as etapas futuras; nao
declarar que ja existem por estarem documentados. Evidencias de autorizacao,
replay/revogacao, minimizacao/exportacao e recuperacao seguem o
[roadmap](../ROADMAP_WEB.md) e o [threat model](THREAT_MODEL.md).

## Evolução CHG-005 — cadastros centrais nominais, inativação lógica e exportação controlada (2026-11-07)

A revisão formal de `DEC-01` ([ADR-007](../arquitetura/ADR-007-cadastros-centrais-e-exportacao-csv.md)) altera a diretriz anterior que mantinha apenas pseudônimos por projeto sem cadastro nominal no servidor. As seções anteriores permanecem como registro histórico das fases `W01`–`W16` e `M1`–`M6`. Para a versão alvo `CHG-005`, aplicam-se as seguintes regras de governança e proteção de dados (LGPD):

1. **Dados cadastrais autorizados e minimização estrita:**
   - `web_patients`: coleta apenas `full_name` (`participant_name`, 2–120 caracteres), `initials` (opcional, 0–16 caracteres) e nota curta de desambiguação operacional, além de `id UUID` e `participant_code` gerados automaticamente pelo sistema.
   - `web_evaluators`: coleta apenas `full_name`, `initials` opcional, `id UUID` e `evaluator_code` gerado automaticamente.
   - Continua proibido coletar CPF, RG, data de nascimento, endereço, telefone, e-mail do participante, diagnóstico clínico ou dados demográficos não previstos no formulário original do PsychoPy (`stroop_go_nogo_ptbr.psyexp`).
2. **Segregação entre identidade nominal e resultados experimentais:**
   - As tabelas científicas (`assessments`, `trials`, `web_assessment_metrics`) armazenam apenas os códigos estáveis (`participant_code` e `evaluator_code`) e os UUIDs de vínculo (`patient_id`, `evaluator_uuid` em `web_assessments`/`web_invitations`), mantendo `full_name` e `initials` isolados nas tabelas cadastrais (`web_patients` e `web_evaluators`).
   - Logs operacionais, mensagens de erro, URLs, nomes de arquivos e artefatos de telemetria continuam proibidos de conter `full_name`, `initials` ou códigos de convite.
3. **Inativação lógica, correção auditável e retenção:**
   - Cadastros de pacientes e avaliadores com vínculos históricos não sofrem exclusão destrutiva (`ON DELETE RESTRICT`); utiliza-se inativação lógica (`active = false`) para impedir novas seleções preservando a integridade longitudinal da pesquisa.
   - Correções de grafia ou de vínculo incorreto geram registro obrigatório em `web_registry_audit_events`.
   - O atendimento a direitos de titulares (retificação, oposição, eliminação/anonimização quando cabível após o prazo legal de guarda da pesquisa) deve ser definido institucionalmente em `DEC-03` (`WEB-033`) antes de habilitar qualquer projeto no modo `research`.
4. **Retirada da importação CSV e controle de exportação:**
   - O recebimento de arquivos CSV pelo usuário é retirado do produto em `M7` (`WEB-025`).
   - Exportações CSV realizadas na plataforma operam por padrão em modo **desidentificado** (`participant_code` / `evaluator_code`); a exportação com nomes completos (`identification_mode = "nominal"`) depende de autorização explícita de perfil e da habilitação `DEC-03` do projeto, sendo auditada em `auth_audit_events`.
5. **Limitação da conta local compartilhada (`R12`):**
   - Enquanto o produto utilizar conta local única compartilhada pela equipe (`ADR-006`), a identificação do avaliador responsável em cada avaliação é declarada por seleção cadastral (`web_evaluators`), não constituindo prova criptográfica de autoria individual do operador autenticado. Essa limitação deve constar expressamente na avaliação institucional `DEC-03` antes de uso com dados reais.
