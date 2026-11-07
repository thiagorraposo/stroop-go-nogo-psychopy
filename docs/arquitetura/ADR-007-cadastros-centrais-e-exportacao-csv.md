# ADR-007: Cadastros centrais de pacientes e avaliadores, preparação completa e CSV exclusivo para exportação

- **Status:** Aceito (direção arquitetural aprovada pelo proprietário em 2026-11-07; implementação planejada em M4, M5, M7, M8, M9 e M10)
- **Data:** 2026-11-07
- **Decisores:** Proprietário do repositório / responsável pelo produto e infraestrutura
- **Rastreabilidade:** `CHG-005`, `DEC-01` (revisada), `DEC-03`, `R05`, `R06`, `R07`, `R12`, `R13`, `WEB-045`, `WEB-046`, `WEB-047`, `WEB-017`–`WEB-020`, `WEB-025`–`WEB-028`, `WEB-033`, `WEB-035`

## Contexto e problema

Até `CHG-004`, a plataforma Stroop Web operava sob a premissa original de `DEC-01` (2026-10-16):

1. Os participantes eram representados apenas por códigos pseudonimizados locais a cada projeto (`web_project_participants(project_id, participant_id)`), digitados manualmente pelo operador na preparação da sessão (`SessionInvitation.tsx`), sem nome completo (`participant_name`), sem iniciais (`initials`) e sem entidade global de paciente.
2. O avaliador responsável pela sessão (`evaluator_id`) era preenchido automaticamente pelo identificador técnico da conta autenticada (`urn:stroop:local:<uuid>` após `ADR-006`), sem cadastro nominal de avaliadores responsáveis separado da conta compartilhada de login da equipe.
3. O produto incluía uma tela e endpoints de importação manual de arquivos CSV (`CsvImportPanel.tsx`, `POST/GET /api/v1/projects/{project_id}/imports/{operation_id}`) que mascaravam `participant_name` para `NAO_COLETADO` no navegador antes do envio.

Para atender à operação real do grupo de pesquisa, o proprietário determinou o replanejamento funcional e de UX da plataforma (`CHG-005`) com o fluxo profissional integrado:

**Login da equipe → Dashboard → Pacientes/Avaliadores → Preparar avaliação → Executar teste → Armazenar resultados → Consultar, analisar e exportar.**

O sistema passa a concentrar o cadastro de pacientes e avaliadores, a preparação completa das avaliações (recuperando os campos pertinentes do formulário original do PsychoPy Builder `stroop_go_nogo_ptbr.psyexp`), a execução experimental, o armazenamento estruturado e a análise/exportação avançada, eliminando a necessidade de planilhas externas de de-para ou upload manual de CSV no produto.

## Decisão

### 1. Revisão formal de `DEC-01`: identidade central de pacientes e avaliadores

1. **Cadastro central de pacientes (`web_patients`):**
   - Cada paciente possui um identificador interno único e imutável gerado pelo sistema (`id UUID`) e um código estável legível gerado automaticamente (`participant_code`, formato `PAT-YYYYMMDD-NNNNNN` ou compatível com `^[A-Za-z0-9_-]{2,64}$`), eliminando a digitação manual de IDs pelo operador.
   - Atributos de domínio autorizados a partir do formulário original do PsychoPy (`formulario_sessao` / `inicializacao_sessao` em `stroop_go_nogo_ptbr.psyexp`):
     - `full_name` (`participant_name`): obrigatório no cadastro central, texto após `strip()` com `2 <= len <= 120`.
     - `initials` (`initials`): opcional (`0 <= len <= 16`), informado ou derivado como auxílio visual/conferência.
     - `notes_or_disambiguation` / metadados de conferência autorizados sem inventar campos clínicos ou demográficos (sem idade, sexo, diagnóstico, CPF ou contato não previstos no formulário original).
     - `active` (booleano para inativação lógica sem exclusão destrutiva), `created_at`, `updated_at`, `created_by_principal_id`.
   - **Reutilização transversal:** o mesmo paciente (`web_patients.id`) pode participar de múltiplos projetos (`web_project_participants`), múltiplas visitas (`web_participant_visits`), diferentes instrumentos (`test_code`/`test_version`), sessões (`web_participant_sessions`) e avaliações (`assessments`/`web_assessments`).
   - **Separação entre identidade nominal e resultados experimentais:** a tabela de resultados e tentativas científicas permanece referenciando chaves estáveis e códigos de participação, mantendo a identidade nominal (`web_patients.full_name`, `initials`) segregada em tabela cadastral própria com controle explícito de acesso e exportação.

2. **Cadastro central de avaliadores responsáveis (`web_evaluators`):**
   - Cada avaliador possui `id UUID` interno único, código estável gerado automaticamente pelo sistema (`evaluator_code`, ex.: `EVA-NNNNNN`), `full_name` (`2 <= len <= 120`), `initials` opcional, estado `active` (`true`/`false`) e timestamps de auditoria.
   - **Distinção estrita entre autenticação e identificação do avaliador:** a conta local compartilhada (`ADR-006`, `web_Repeat`/`web_professional_accounts`) autentica o acesso da equipe à aplicação (`principal_id` na auditoria técnica de segurança), enquanto o avaliador responsável (`evaluator_uuid` / `evaluator_code` / nome cadastrado em `web_evaluators`) identifica o profissional que preparou e conduziu cada avaliação. Não é criada uma conta de login individual para cada avaliador nesta versão.

3. **Prevenção de duplicidade, tratamento de homônimos e CRUD seguro:**
   - Antes de criar ou selecionar paciente ou avaliador, a aplicação pesquisa cadastros existentes por nome normalizado (case/accent-insensitive), iniciais e código, exibindo correspondências candidatas com informações mínimas de confirmação (código gerado, nome completo, iniciais, projetos/visitas vinculados e data de cadastro).
   - O sistema nunca unifica dois registros automaticamente apenas por coincidência de nome (homônimos são permitidos mediante confirmação explícita de "Cadastrar novo homônimo" pelo operador).
   - Inativação lógica (`active = false`) impede novas seleções por padrão sem remover nem alterar avaliações, sessões ou resultados históricos. Exclusão física de paciente ou avaliador com qualquer vínculo histórico é bloqueada no banco (`RESTRICT`) e no domínio.
   - Alterações cadastrais e correções de vínculo são registradas em trilha de auditoria (`web_registry_audit_events`) com valores anteriores/novos (ou referências técnicas), timestamp e conta operadora.

4. **Procedimento verificável para registros pseudonimizados anteriores:**
   - Registros históricos criados sob a regra anterior de `DEC-01` (pseudônimos por projeto sem nome nominal ou com `NAO_COLETADO`) permanecem íntegros e consultáveis.
   - Não há reconciliação automática por coincidência de código ou texto. Qualquer vinculação de um `web_project_participants` legado a um cadastro central `web_patients` ou `web_evaluators` exige ação administrativa explícita, auditada e reversível (`web_legacy_entity_links`).

### 2. Formulário completo de preparação da avaliação

Na preparação da avaliação (`Preparar avaliação`):

1. O profissional seleciona um paciente existente (com busca/autocomplete) ou realiza o cadastro imediato no fluxo, sem digitar IDs internos manualmente.
2. Seleciona um avaliador responsável ativo existente (ou cadastra novo avaliador autorizado).
3. Seleciona o projeto ativo (`project`), o instrumento registrado (`test_code`, padrão `stroop_go_nogo_ptbr`) e informa a visita (`visit`) e confirmação de iniciais (`initials`, pré-preenchida do cadastro do paciente quando existente).
4. Exibe tela/etapa de **resumo para conferência** (paciente, código automático, iniciais, avaliador responsável, projeto, instrumento e visita) antes de emitir o convite/iniciar a sessão.
5. Metadados técnicos (`assessment_id`, `session_id`, `invitation_id`, `assessment_date`, `started_at`, `test_version`, `protocol_id`, `app_version`) permanecem gerados exclusivamente pelo sistema.
6. O fluxo experimental subsequente (convite de uso único, sessão de 30 min, prática, interrupção D2, persistência incremental `ADR-005` e recibo final) permanece inalterado.

### 3. Retirada da importação CSV do produto e exportação CSV avançada

1. **Retirada da importação CSV do produto (`M7`):**
   - Os dados operacionais passam a ser cadastrados, coletados e armazenados diretamente na plataforma WEB.
   - A tela `Importar CSV` (`CsvImportPanel.tsx`), comandos visíveis de importação no dashboard e os endpoints de upload CSV no modo produto (`POST/GET /api/v1/projects/{project_id}/imports/{operation_id}`) são retirados do fluxo operacional do usuário.
   - Módulos Python de validação/ingestão (`services/csv_ingestion.py`, `persistence/sqlite_ingestor.py`) e CLIs locais permanecem isolados no repositório exclusivamente para compatibilidade técnica histórica, testes de contrato e migração técnica excepcional sob autorização específica.

2. **Exportação CSV avançada e catálogo de filtros (`M5`):**
   - O CSV consolida-se como funcionalidade de **exportação** para análise externa (R, Python, SPSS, JASP, Excel/LibreOffice).
   - O painel oferece catálogo completo de filtros combinados (paciente/ID, avaliador responsável, projeto, instrumento, versão, visita, período, status da sessão/avaliação, condição experimental, tipo de resposta/erro, faixas de precisão e RT, busca textual, multisseleção e ordenação).
   - A exportação permite escolher o nível de granularidade (`pacientes`, `avaliacoes`, `tentativas`, `metricas`, além do CSV oficial de 21 colunas do Stroop), selecionar colunas autorizadas, pré-visualizar contagem e amostra antes do download, exportar metadados dos critérios aplicados e optar entre modo desidentificado (padrão seguro com códigos estáveis) e modo nominal (restrito a perfil autorizado e quando o projeto possuir habilitação institucional `DEC-03`).
   - Todas as exportações aplicam proteção contra *CSV formula injection* e separam estritamente avaliações válidas oficiais de observações parciais/interrompidas.

### 4. Arquitetura de informação e UX administrativa sem alterar o motor experimental

1. A interface profissional é organizada nos módulos: **Visão geral (Dashboard)**, **Pacientes**, **Avaliadores**, **Preparar avaliação**, **Avaliações e histórico**, **Resultados e análises**, **Exportações** e **Administração/configurações**.
2. O motor experimental jsPsych (`web/src/experiment/`), a apresentação `stroop-web-outline/1.0.0` (`CHG-003`), as dez cores, o estímulo central, o HUD de progresso/cronômetro, a ausência de precisão ao vivo e os gates temporais D5 permanecem intocados.

## Alternativas consideradas

1. **Manter apenas pseudônimos manuais por projeto (`DEC-01` original):** rejeitado pelo proprietário porque obriga a equipe a manter planilhas externas paralelas, propicia erros de digitação de `participant_id` entre visitas/testes e impede a gestão integrada de pacientes e avaliadores na plataforma.
2. **Criar uma conta de login individual para cada avaliador:** descartado nesta versão pelo proprietário (Seção 3.1 e Seção 5 da missão `CHG-005`); a equipe utiliza uma única conta local compartilhada para autenticação de acesso (`ADR-006`) e identifica o avaliador responsável separadamente no cadastro central e em cada avaliação.
3. **Manter upload CSV aberto na UI do produto:** descartado pelo proprietário (Seção 8 da missão `CHG-005`); manter entrada manual por CSV cria dupla fonte de verdade e contorna o cadastro central de pacientes, avaliadores e preparação de sessão.

## Consequências

- **Positivas:** fluxo clínico/pesquisa ponta a ponta sem planilhas paralelas; eliminação de erros de digitação de IDs; rastreabilidade longitudinal de pacientes e avaliadores entre múltiplos projetos, visitas e instrumentos; análises e exportações CSV flexíveis em múltiplas granularidades.
- **Riscos e mitigações:**
  - *Armazenamento de nomes completos no PostgreSQL (`R05`, `R07`, `R13`):* exige segregação lógica entre tabela cadastral (`web_patients`) e resultados científicos, exportação desidentificada por padrão, backup criptografado e bloqueio de coleta real até aprovação institucional/LGPD (`DEC-03` / `WEB-033`).
  - *Conta local compartilhada (`R12`):* a atribuição do avaliador na sessão é declarada por seleção cadastral, não por credencial individual de login; a auditoria registra tanto a conta técnica autenticada quanto o `evaluator_id` selecionado.
  - *Homônimos sem documento civil (`R13`):* como o formulário original do PsychoPy não coleta CPF ou data de nascimento, o sistema apresenta código estável gerado, iniciais e histórico de projetos/visitas para confirmação humana explícita, sem fusão automática.
