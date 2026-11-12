# Requisitos e rastreabilidade

Especificação de 2026-11-04, derivada da missão e da [auditoria](AUDITORIA_REPLANEJAMENTO.md).
Estado da especificação: Confirmado = direção explícita ou contrato aprovado;
Proposto = hipótese a avaliar; Pendente de decisão = precisa responsável externo.
Nenhum estado de especificação significa requisito implementado ou aceito.
Estados de execução e progresso existem somente no [backlog](Projeto%20Stroop%20Test.md).
P0 = integridade/segurança/risco impeditivo; P1 = operação MVP; P2 = extensão opcional.
Dependências referem-se às tarefas canônicas (incluindo suas dependências transitivas).
Uma decisão pode concluir uma tarefa de definição com alternativa rejeitada;
qualquer implementação nova precisa de tarefa/critério explícito no backlog.

Origens e contratos são referências documentais e de código; não são alegação
de teste aprovado. As regras completas ficam nas fontes científicas vinculadas,
sem nova cópia de fórmulas aqui. Modelo e método preservam suas fontes em subpastas.

## A. Gestão de usuários e autenticação

### REQ-AUT-001

- Descrição: Autenticar profissional por usuário e senha locais no backend, com conta administrativa única inicial e sem cadastro público/Google obrigatório.
- Justificativa: Decisão do proprietário retira dependência externa; não amplia múltiplas contas nesta versão.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-004/ADR-006, 2026-11-06).
- Aceite verificável: Login válido abre dashboard com sessão nova; inválido/inexistente/bloqueado nega genericamente; logout e acesso não autenticado negam conforme contrato, integração React/FastAPI/PG/HTTPS real AUTH-L01/L07.
- Dependências: WEB-021 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Evidência OIDC histórica não cobre login local; aceite local comprovado em M6 (WEB-021/024), sem dispensar integração de produto M4/M5.
- Origem: Decisão explícita do proprietário nesta missão; ADR-006 e contrato HTTP alvo.

### REQ-AUT-002

- Descrição: Autorizar perfis e projetos a cada leitura, escrita e exportação.
- Justificativa: Mantém isolamento de pesquisa e revogação efetiva.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Consulta não escreve; importacao prepara convite; admin sem vínculo não consulta resultados; bloqueio/revogação retiram acesso.
- Dependências: WEB-022 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem novo papel implícito de avaliador.
- Origem: seguranca/AUTENTICACAO_E_PERMISSOES.md e api/auth.py.
- Impacto CHG-004: mantém perfis, último admin e vínculos explícitos; conta local não herda projetos. Regressão AUTH-L06 concluída em WEB-021/024 preserva aceite histórico de WEB-022.

### REQ-AUT-003

- Descrição: Separar sessões profissional e participante com cookies seguros e CSRF.
- Justificativa: Evita confusão de credenciais e falsificação de escrita.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Secure/HttpOnly/SameSite e origem/CSRF testados; logout/expiração/replay encerram acesso apropriado.
- Dependências: WEB-023 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem credenciais em armazenamento durável do cliente; alvo local exige inatividade, teto absoluto e revogação após rotação, AUTH-L04/L05, sem alterar sessão participante.
- Origem: desenvolvimento/CONTRATO_API_WEB.md e routers api/.
- Impacto CHG-004: AUTH-L04/L05 comprovados para sessão local em WEB-021/024 (Origin inclusive login, inatividade 30 min, teto 8 h e rotação/revogação), preservando aceite histórico de WEB-023.

### REQ-AUT-004

- Descrição: Proteger senha, provisionamento, alteração e recuperação administrativa da conta local.
- Justificativa: Credencial passa a ser responsabilidade da aplicação e do operador.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-004/ADR-006).
- Aceite verificável: Argon2id/salt/custo e verificação segura, sem plaintext/hardcode/default/segredo versionado; bootstrap protegido sem cadastro público, recuperação auditada, rotação revoga todas sessões na mesma transação e resiste a login concorrente; AUTH-L01/L02/L04/L08.
- Dependências: WEB-021 e pré-requisitos registrados no backlog; controles técnicos em WEB-021/024.
- Restrições conhecidas: Schema aditivo, grants mínimos e histórico preservado; procedimento real só autorizado posteriormente.
- Origem: Missão documental do proprietário de 2026-11-06; ADR-006 e segurança.

### REQ-AUT-005

- Descrição: Impedir enumeração e limitar força bruta no login local sem vazamento ou bypass.
- Justificativa: Senha local introduz superfície de abuso própria.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-004/ADR-006).
- Aceite verificável: Limites por conta/origem confiável persistentes/concorrentes, erros genéricos, hash fictício, 429/Retry-After e falha fechada; logs sem senha/hash/token/usuário tentado; AUTH-L03/L09.
- Dependências: WEB-021 e pré-requisitos registrados no backlog; controles técnicos em WEB-021/024.
- Restrições conhecidas: Custo de hash e DoS da conta única avaliados em WEB-024; defaults na especificação de segurança.
- Origem: Missão documental do proprietário de 2026-11-06; ADR-006 e segurança.

### REQ-AUT-006

- Descrição: Explicitar privilégios e limitações de auditoria da conta administrativa compartilhada.
- Justificativa: Conta técnica compartilhada não permite atribuição individual ou revogação por pessoa.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-004/ADR-006).
- Aceite verificável: Admin sem vínculo não acessa dados; custódia/troca na mudança de equipe e revogação global documentadas/testadas; DEC-03 avalia adequação institucional antes de dados reais; AUTH-L06/L07/L09.
- Dependências: WEB-033 e pré-requisitos registrados no backlog; controles técnicos em WEB-021/024.
- Restrições conhecidas: Direção de produto aprovada, adequação institucional PENDENTE; não declarar auditoria individual nem uso real autorizado.
- Origem: Missão documental do proprietário de 2026-11-06; ADR-006 e segurança.

## B. Gestão de participantes

### REQ-PAR-001

- Descrição: Identificar participação por pseudônimo e visita no projeto autorizado.
- Justificativa: Atende identificação sem transmitir nome/iniciais.
- Prioridade: P0. Estado da especificação: **Confirmado** (histórico M4 aceito; evoluído por CHG-005/DEC-01 revisada).
- Aceite verificável: Convite/resgate conserva código/visita e rejeita campos nominais; isolamento entre projetos comprovado.
- Dependências: WEB-013 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Pseudônimo não é anonimização nem credencial.
- Origem: seguranca/ACESSO_WEB.md e controles existentes.
- Impacto CHG-005: Preserva o aceite histórico de `WEB-013`/`WEB-016` e o isolamento da sessão do participante (que continua sem expor dados nominais no bootstrap/motor), passando o código `participant_id` a ser gerado automaticamente pelo cadastro central de pacientes (`REQ-PAR-004`, `WEB-045`/`WEB-046`).

### REQ-PAR-002

- Descrição: Participante pseudonimizado por projeto admite múltiplas visitas e avaliações com vínculos estáveis, sem cadastro longitudinal central.
- Justificativa: Evita confundir metadados de sessão com cadastro global.
- Prioridade: P0. Estado da especificação: **Confirmado** (DEC-01 histórica aceita em M2/M4; substituída pela revisão formal de DEC-01 em CHG-005, 2026-11-07).
- Aceite verificável: UUIDs e vínculos conforme modelo canônico; várias visitas e avaliações por visita sem duplicação/cruzamento de projetos; evolução longitudinal aditiva sem reescrever resultados. Diretriz aprovada; comportamento ainda requer implementação/ensaios.
- Dependências: WEB-005 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem nomes/identificador pessoal global, agenda separada ou correlação automática; schema novo só após aprovação da estratégia definitiva e tarefa autorizada.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-005: Incompatibilidade formalmente registrada e resolvida pela revisão de `DEC-01` e `ADR-007`: os vínculos `web_project_participants` e `web_participant_visits` são preservados e estendidos aditivamente para referenciar o cadastro central `web_patients` (`REQ-PAR-004`/`005`), sem migração automática de registros pseudonimizados anteriores (`WEB-027`).

### REQ-PAR-003

- Descrição: Não impor filtros demográficos nem coletar idade/sexo sem requisito aprovado.
- Justificativa: Preserva finalidade e elegibilidade sob responsabilidade científica.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Formulários/payloads não coletam idade/sexo e não calculam norma; textos de elegibilidade só os aprovados.
- Dependências: WEB-014 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Responsável define elegibilidade/consentimento DEC-03.
- Origem: experimento/DECISOES_DO_EXPERIMENTO.md e PROTOCOLO_WEB.md (D1–D6).
- Impacto CHG-005: Mantido integralmente; o cadastro central de pacientes (`REQ-PAR-004`) restringe-se a nome completo (`participant_name`), iniciais (`initials`) e nota curta de desambiguação autorizados pelo formulário original do PsychoPy, sem inventar campos clínicos ou demográficos.

### REQ-PAR-004

- Descrição: Manter cadastro centralizado de pacientes com identificador único e código estável gerados automaticamente pelo sistema, nome completo (`participant_name`), iniciais (`initials`), verificação de duplicidade/homônimos e reutilização entre múltiplos projetos, visitas, instrumentos e avaliações.
- Justificativa: Elimina digitação manual de IDs e planilhas externas, permitindo acompanhamento longitudinal íntegro do mesmo paciente em diferentes testes e projetos.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-005; DEC-01 revisada; ADR-007).
- Aceite verificável: Criação gera `id UUID` e `participant_code` automático (`PAT-...`) sem digitação manual; valida `full_name` (2–120 chars) e `initials` (0–16 chars); pesquisa candidatos duplicados por nome normalizado/iniciais/código e bloqueia criação duplicada acidental (`409 duplicate_candidate_found`) exigindo confirmação explícita para homônimos; separa tabela nominal (`web_patients`) das tabelas de resultados científicos (`assessments`); permite vincular o mesmo paciente a múltiplos projetos, visitas, instrumentos e sessões (CAD-01/CAD-02).
- Dependências: WEB-045, WEB-046, WEB-047 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não inventar campos clínicos/demográficos nem unificar homônimos automaticamente; coleta real permanece sujeita a `DEC-03` (`WEB-033`).
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`); `stroop_go_nogo_ptbr.psyexp`.

### REQ-PAR-005

- Descrição: Garantir CRUD administrativo seguro de pacientes com edição auditável, inativação lógica sem exclusão destrutiva de avaliações/resultados e procedimento auditado para correção de vínculos e associação verificável de registros legados.
- Justificativa: Preserva a integridade histórica e longitudinal dos dados científicos diante de correções cadastrais ou desativação de registros.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: Listagem paginada/pesquisável e ficha longitudinal do paciente; edições gravam trilha em `web_registry_audit_events` mantendo intactos UUIDs e vínculos de sessões/avaliações; exclusão é exclusivamente lógica (`active=false`) com `ON DELETE RESTRICT` e ausência de `DELETE` para o writer; associação de registros pseudonimizados anteriores exige confirmação explícita em `WEB-027` sem fusão automática (CAD-01/CAD-02).
- Dependências: WEB-047, WEB-045, WEB-027 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Nenhuma avaliação ou resultado concluído pode ser apagado em cascata.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`).

## C. Gestão de avaliações

### REQ-AVA-001

- Descrição: Permitir que avaliador vinculado prepare avaliação e emita/revogue convite.
- Justificativa: Materializa início do fluxo principal.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Criação via React retorna convite uma vez; resgate único; revogação/expiração impedem execução sem apagar resultado anterior.
- Dependências: WEB-013 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Projeto synthetic até liberação específica DEC-05.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-004: CHG-004 exige login local aceito e vínculo explícito antes de emitir convite; participante continua por convite separado. AUTH-L07 em WEB-013/016, após WEB-024.
- Impacto CHG-005: Preserva o aceite de `WEB-013`/`WEB-016` e estende a preparação em `WEB-045`/`WEB-046` (`REQ-AVA-004`/`005`) para exigir seleção de paciente e avaliador responsável cadastrados, mantendo a distinção entre conta local compartilhada de login e avaliador responsável pela sessão.

### REQ-AVA-002

- Descrição: Preparar avaliação por convite único vinculado a participante/visita/projeto, sem módulo separado de agendamento.
- Justificativa: O código atual não representa agendamento independente.
- Prioridade: P1. Estado da especificação: **Confirmado** (DEC-01, 2026-11-05; estendido por CHG-005 em 2026-11-07).
- Aceite verificável: Convite único, prazo, acesso e resgate único; reemissão cria sessão distinta e mantém vínculos/execuções anteriores; nenhuma unicidade artificial impede várias avaliações na mesma visita.
- Dependências: WEB-005 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não introduzir agendamento nem nova entidade por inferência.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md e decisão do responsável de 2026-11-05.
- Impacto CHG-005: O convite único passa a vincular também `patient_id` (`web_patients`), `evaluator_uuid` (`web_evaluators`), `test_code` e `participant_initials` em `WEB-045`/`WEB-046`, preservando emissão por sessão sem módulo de agenda separado.

### REQ-AVA-003

- Descrição: Distinguir sessão iniciada, interrompida, enviada e avaliação recebida.
- Justificativa: Impede declarar sucesso sem persistência confirmada.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: UI só diz recebido após recibo; reload de running invalida; sessão abortada não aparece como resultado oficial.
- Dependências: WEB-015 e pré-requisitos registrados no backlog.
- Restrições conhecidas: D2 proíbe retomar principal interrompido.
- Origem: experimento/DECISOES_DO_EXPERIMENTO.md e PROTOCOLO_WEB.md (D1–D6).
- Impacto CHG-003: REQ-UX-010/WEB-015 refinam estados visuais sem alterar transições/recibos ou permitir retomada.
- Impacto CHG-005: Mantido integralmente; a área administrativa `Avaliações e histórico` (`WEB-019`) exibe o estado operacional de cada sessão separando estritamente resultados válidos oficiais de sessões em preparação, interrompidas, expiradas ou invalidadas.

### REQ-AVA-004

- Descrição: Manter cadastro centralizado de avaliadores responsáveis com identificador interno único e código estável gerados automaticamente pelo sistema, nome completo, estado ativo/inativo e histórico de avaliações, separado da conta local compartilhada de autenticação.
- Justificativa: Permite identificar com precisão o profissional responsável por cada avaliação em diferentes instrumentos e projetos, sem criar contas individuais de login nesta versão.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: CRUD de `web_evaluators` gera `id UUID` e `evaluator_code` (`EVA-...`) automaticamente; valida `full_name` (2–120 chars) e previne duplicidade acidental (`409 duplicate_candidate_found`); registra no convite e no resultado o vínculo estável do avaliador responsável (`evaluator_uuid` e `evaluator_code`) separadamente da conta autenticada (`issued_by`); inativação lógica (`active=false`) e edições cadastrais preservam todo o histórico de avaliações realizadas; nenhuma conta de login é criada automaticamente (CAD-03).
- Dependências: WEB-045, WEB-046, WEB-047 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Identificação declarada do avaliador na sessão não substitui autenticação individual; limitação registrada em `R12` e sujeita a `DEC-03`.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`).

### REQ-AVA-005

- Descrição: Prover formulário completo de preparação da avaliação recuperando os campos do formulário original do PsychoPy Builder, com seleção/cadastro de paciente e avaliador sem digitação manual de IDs internos e etapa de resumo para conferência antes de iniciar o fluxo experimental.
- Justificativa: Evita dupla digitação e erros manuais de preenchimento, garantindo correspondência integral com os metadados do experimento original.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: Fluxo seleciona ou cadastra paciente e avaliador responsável, seleciona projeto e instrumento (`test_code`), preenche `visit` e `initials` (pré-preenchido do paciente), gera automaticamente `participant_id` e `evaluator` a partir dos cadastros, mantém `assessment_id`/`assessment_date`/`started_at`/`test_version` automáticos no servidor, exibe resumo completo para conferência e, após confirmação explícita, emite o convite único preservando prática, interrupção D2, persistência incremental (`ADR-005`) e recibo (PREP-01).
- Dependências: WEB-046, WEB-045 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Nenhum metadado técnico gerado pelo sistema pode ser transformado em campo editável manual.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`); `stroop_go_nogo_ptbr.psyexp`.

## D. Execução experimental Web

### REQ-EXP-001

- Descrição: Preservar condições, classificação Go/No-Go, tempos, prática e principal aprovados.
- Justificativa: Mantém rastreabilidade metodológica sem equivalência presumida.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Snapshot e condições conferidos; 4 prática 2/2 e 16 principal 8/8, dez cores, HUD, feedback e janela D6 cobertos por regressão.
- Dependências: WEB-009 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Local 0.2.2; WEB 0.2.2-web.1; regras completas só no protocolo.
- Origem: experimento/DECISOES_DO_EXPERIMENTO.md e PROTOCOLO_WEB.md (D1–D6).
- Impacto CHG-003: Apresentação alvo em REQ-UX-001/002/003/005/007 e WEB-042/043; aceite WEB-009 preservado para fontes/tempos/paleta, sem crédito para visual novo. D3 visual revisada pelo proprietário; validação experimental não presumida.

### REQ-EXP-002

- Descrição: Executar motor no navegador com relógio monotônico, separado de renderização React/rede.
- Justificativa: Reduz acoplamento e preserva medição local.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Host limpa listeners; tecla mantida/repeat/fim exclusivo e perda de foco testados; comparativo jsPsych registrado sem mudança semântica.
- Dependências: WEB-010 e pré-requisitos registrados no backlog.
- Restrições conhecidas: performance.now/rAF não comprovam onset físico.
- Origem: arquitetura/ADR-004-replanejamento-plataforma.md.
- Impacto CHG-003: REQ-UX-004/007 e WEB-044 revalidam HUD/relógio/lifecycle sem render React por quadro; aceite WEB-010 preservado para seu escopo histórico.

### REQ-EXP-003

- Descrição: Limitar suporte à matriz desktop aprovada e verificar gates temporais.
- Justificativa: Evita prometer precisão universal.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: M3 registra 10 execuções sintéticas por ambiente selecionado, transições dentro de um quadro e bloco ±100ms; falhas preservadas.
- Dependências: WEB-011 e pré-requisitos registrados no backlog.
- Restrições conhecidas: D1/D5 e DEC-04; piloto automatizado não é latência física.
- Origem: experimento/DECISOES_DO_EXPERIMENTO.md e PROTOCOLO_WEB.md (D1–D6).
- Impacto CHG-003: WEB-011 exige layout final aprovado/testado de WEB-044 e transporte ativo; REQ-UX-001 a REQ-UX-007 e D5 inalterado. DEC-04 aprovada no alcance local de engenharia em 2026-11-05; validação física/metodológica permanece gate M9.

## E. Captura e integridade dos dados

### REQ-INT-001

- Descrição: Capturar ordem/condição, RT e transições e validar contra snapshot da sessão.
- Justificativa: Permite conferir consistência e derivar acerto no servidor.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: 16 condições únicas na ordem esperada; finitos, tipos e unidades validados; payload adulterado ou temporalmente incoerente rejeitado.
- Dependências: WEB-006 e pré-requisitos registrados no backlog.
- Restrições conhecidas: API não pode provar veracidade física do cliente.
- Origem: desenvolvimento/CONTRATO_API_WEB.md e routers api/.

### REQ-INT-002

- Descrição: Persistir conclusão e métricas atomicamente com recibo e idempotência.
- Justificativa: Evita perda parcial/duplicação em falhas de rede.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Falha pré-commit não deixa resultado; replay igual retorna recibo; payload distinto conflita; concorrência não duplica avaliação.
- Dependências: WEB-007 e pré-requisitos registrados no backlog.
- Restrições conhecidas: PostgreSQL real com papéis restritos obrigatório.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md.
- Impacto CHG-003: REQ-UX-010 preserva recibos/idempotência e confirmação somente após commit; WEB-015/016 revalidam UI sem reabrir aceite backend.

### REQ-INT-003

- Descrição: Persistir incrementalmente observações com confirmação e idempotência, preservando sessões incompletas/ inválidas sem retomada ou resultado oficial parcial.
- Justificativa: RAM final-only não garante preservação de tentativas interrompidas.
- Prioridade: P0. Estado da especificação: **Confirmado** (DEC-02; estratégia e matriz validadas em 2026-11-05).
- Aceite verificável: Estratégia ADR-005, contrato HTTP e matriz D2/D5 validados explicitamente antes de implementação; ensaios de perda/recibo/replay/concorrência/expiração e impacto temporal comprovam o comportamento depois do código. RAM final-only rejeitada; riscos residuais informados.
- Dependências: WEB-005 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem offline, localStorage ou retomada implícitos; decisão metodológica se afetar validade.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md e decisão do responsável de 2026-11-05.
- Impacto CHG-003: REQ-UX-010 e WEB-011/015 preservam estratégia ADR-005, parciais e limites residuais, agora com layout final.

### REQ-INT-004

- Descrição: Estruturar a navegação profissional da plataforma em 3 eixos fundamentais inspirados no modelo mental do Streamlit (Eixo 1: Resultados e Análise Unificada; Eixo 2: Aplicação Direta / Nova Avaliação; Eixo 3: Gestão Cadastral e Acessos), eliminando a fragmentação cognitiva em 8 abas isoladas.
- Justificativa: Agiliza a rotina clínica e investigativa, integrando o funil analítico e reduzindo a alternância de contexto do operador.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-006; ADR-008).
- Aceite verificável: Interface da equipe organiza todas as capacidades operacionais nos 3 eixos, provê transições acessíveis e fluidas, garante controle de visibilidade conforme perfil e não interfere no isolamento do motor experimental jsPsych (INT-01).
- Dependências: WEB-049; bases aceitas preservadas no backlog (CHG-007).
- Restrições conhecidas: Acesso restrito a usuários autenticados da equipe; preservação dos componentes de design system já validados.
- Origem: Missão de replanejamento documental do proprietário em 2026-11-08 (`CHG-006`).

- Complemento CHG-007: Base WEB-047 e cobertura documental WEB-028 históricas; integração CHG-007 planejada. Aplicação de filtros explícita; URLs sem segredo; aceite/roteiros no contrato HTTP e UX7, sem SLA universal de 10 segundos.

### REQ-INT-005

- Descrição: Prover painel unificado de resultados e análise em tela única coesa, integrando indicadores (KPIs), catálogo de filtros combinados reativos, visualizações gráficas descritivas, histórico de tentativas e exportação CSV multi-granularidade sobre o recorte ativo.
- Justificativa: Garante paridade de fluidez e reatividade com o Streamlit, assegurando que o mesmo conjunto filtrado se reflita instantaneamente em métricas, gráficos e downloads.
- Prioridade: P1. Estado da especificação: **Confirmado** (CHG-006; ADR-008).
- Aceite verificável: Qualquer alteração nos filtros combinados (paciente, avaliador, visita, projeto, faixas de RT/precisão, condição Go/No-Go) atualiza de forma síncrona KPIs, gráficos, listagem de tentativas e o arquivo gerado pelo hub de exportação CSV, mantendo separação estrita de dados desidentificados vs nominais (DASH-01, EXP-CSV-01).
- Dependências: WEB-052; bases aceitas preservadas no backlog (CHG-007).
- Restrições conhecidas: Não exibir escores normativos, diagnósticos clínicos ou percentis não autorizados pelo protocolo científico.
- Origem: Missão de replanejamento documental do proprietário em 2026-11-08 (`CHG-006`).

- Complemento CHG-007: Base WEB-017/019/020 histórica; integração CHG-007 planejada. Aplicação de filtros explícita; URLs sem segredo; aceite/roteiros no contrato HTTP e UX7, sem SLA universal de 10 segundos.

## F. Cálculo das métricas

### REQ-MET-001

- Descrição: Usar núcleo Python como cálculo oficial das 12 métricas e unidades.
- Justificativa: Evita fórmulas divergentes entre consumidores.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Fixtures sintéticas cobrem classificações, denominadores, mediana dos hits e paridade entre API, CSV e domínio.
- Dependências: WEB-008 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não introduzir norma, score clínico ou nova fórmula.
- Origem: dados/MODELO_DE_DADOS.md e stroop/domain/stroop.py.
- Impacto CHG-003: REQ-UX-006/WEB-044 preservam 12 métricas oficiais apesar da retirada de precisão da UI; regressão real em WEB-016/019/020 sem reabrir WEB-008.

### REQ-MET-002

- Descrição: Distinguir ausência de RT, zero sentinela histórico e arredondamento de apresentação.
- Justificativa: Impede apresentar ausência como resposta instantânea.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Sem hits: persistência legada 0.0, resumo null e UI traço; exportação mantém contrato; diferenças documentadas e testadas.
- Dependências: WEB-008 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Mudança de armazenamento/semântica exige decisão prévia.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md.
- Impacto CHG-003: REQ-UX-006 preserva sentinela/null/traço e arredondamento nos resultados autorizados; remoção de HUD não autoriza alterar representação de ausência.

### REQ-MET-003

- Descrição: Vincular resultados a versão de instrumento, protocolo, app e origem.
- Justificativa: Permite reproduzir cálculo e separar variantes.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Detalhe/exportação técnica permitem identificar snapshot/versão/plataforma; mistura de versões incompatíveis não é silenciosa.
- Dependências: WEB-019 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Nenhuma declaração de equivalência local/WEB.
- Origem: dados/MODELO_DE_DADOS.md e stroop/domain/stroop.py.
- Impacto CHG-003: WEB-019 e WEB-034 devem identificar apresentação anterior/posterior por versão aprovada e SHA; identificação visual complementa D4 conforme aprovação do proprietário no protocolo.

## G. Dashboard e relatórios

### REQ-REL-001

- Descrição: Oferecer painel React com filtros, lista e conjunto autorizado coerente.
- Justificativa: Substitui interface operacional Streamlit.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Filtros e paginação preservam escopo; totais/agregados correspondem ao conjunto filtrado sem vazar outros projetos.
- Dependências: WEB-017 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem totais globais não autorizados.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-004: CHG-004 integra entrada local protegida em WEB-021 e revalida acesso/logout no dashboard em WEB-017 (AUTH-L07), sem alterar filtros/gráficos.
- Impacto CHG-005: Expandido por `REQ-REL-004` e `REQ-REL-005` (`WEB-017`/`WEB-019`) para incluir o catálogo completo de filtros por paciente, avaliador responsável, condição, resposta e métricas, além dos KPIs do Dashboard principal.

### REQ-REL-002

- Descrição: Exibir detalhe descritivo com métricas, tentativas e proveniência.
- Justificativa: Permite análise e auditoria de cada avaliação.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Detalhe mostra unidades, quatro respostas e metadados técnicos sem nomes/iniciais; no-hit correto e acessibilidade básica verificados.
- Dependências: WEB-019 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem diagnóstico, norma ou interpretação clínica.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-003: REQ-UX-006/011 e WEB-019 mantêm precisão no painel profissional e revisam somente UI compartilhada/acessibilidade.
- Impacto CHG-005: O detalhe e as fichas longitudinais (`WEB-019`/`WEB-047`) passam a exibir também os vínculos autorizados do paciente (`participant_code` e cadastro autorizado) e do avaliador responsável (`evaluator_code`/cadastro), mantendo explícitos origem, definição, unidade e tratamento de nulos de cada métrica.

### REQ-REL-003

- Descrição: Administrar contas, projetos e vínculos no React sem apagar coletas.
- Justificativa: Retira dependência operacional de UI legada.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: CRUD permitido testado, negação por papel, último administrador protegido inclusive sob concorrência, sem exclusão de dados.
- Dependências: WEB-018 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Administração não herda escopo de resultados.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md.
- Impacto CHG-004: CHG-004 adapta administração à conta local única e seus vínculos/perfis/bloqueio; sem oferta/criação de contas adicionais agora. Preservar último admin, AUTH-L06/L07 em WEB-018 após WEB-021/024.
- Impacto CHG-005: Integra a área `Administração/configurações` (`WEB-018`) à nova navegação administrativa de 8 módulos, mantendo separada a gestão de conta/projetos do CRUD de `Pacientes` e `Avaliadores` (`WEB-047`).

### REQ-REL-004

- Descrição: Oferecer catálogo completo de filtros combinados na consulta e análise de avaliações e resultados (paciente/código, avaliador responsável, projeto, instrumento, versão, visita, período, status, condição experimental, tipo de resposta/erro, faixas de precisão e tempos de reação, busca textual, seleção múltipla e ordenação).
- Justificativa: Permite exploração analítica flexível e recorte preciso de subconjuntos de pesquisa antes da visualização ou exportação CSV.
- Prioridade: P1. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: Filtros combinam dimensões com semântica determinística, tratam valores ausentes explicitamente (`include_null_rt` quando `hits = 0`), separam resultados oficiais válidos (`status=valid`) de sessões interrompidas/invalidadas e refletem exatamente o mesmo conjunto nos KPIs, tabelas, gráficos e exportações (DASH-01).
- Dependências: WEB-017, WEB-046 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Respeitar estritamente os projetos vinculados à conta autenticada.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`).

### REQ-REL-005

- Descrição: Estruturar a interface administrativa nos módulos Visão geral (Dashboard), Pacientes, Avaliadores, Preparar avaliação, Avaliações e histórico, Resultados e análises, Exportações e Administração/configurações, com KPIs descritivos e visualizações interativas longitudinais e por condição.
- Justificativa: Consolida a plataforma WEB como ambiente único de gestão cadastral, coleta e análise descritiva do grupo de pesquisa.
- Prioridade: P1. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: Dashboard exibe total de pacientes, avaliações por período/instrumento/projeto/status/avaliador, evolução temporal e resumos descritivos das 12 métricas oficiais com origem, definição, unidade e tratamento de nulos explícitos; visualizações interativas cobrem evolução longitudinal por paciente, distribuição de RTs, precisão e erros por condição/projeto/visita/avaliador, sempre com tabela acessível e sem normas clínicas (DASH-01).
- Dependências: WEB-019, WEB-017, WEB-047 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Proibido exibir diagnósticos, escores normativos ou alterar o motor experimental jsPsych.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`).

## H. Importação e exportação

### REQ-CSV-001

- Descrição: Manter CSV de 21 campos como intercâmbio complementar compatível.
- Justificativa: Preserva análise e histórico sem fazer CSV banco operacional.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Roundtrip sintético conserva colunas, unidades, classificação e metadados admitidos; prática não vira resultado oficial.
- Dependências: WEB-026 e pré-requisitos registrados no backlog.
- Restrições conhecidas: CSV local nominal não deve ser transmitido à WEB.
- Origem: experimento/CSV_UNIFICADO.md.
- Impacto CHG-005: O CSV oficial de 21 colunas permanece preservado como formato canônico de **exportação** (`stroop_21_colunas` em `WEB-020` e roundtrip com pipeline Python/CLI em `WEB-026`), deixando de ser formato de entrada manual pelo usuário na plataforma WEB (`REQ-CSV-004`).

### REQ-CSV-002

- Descrição: Minimizar importação no navegador e validar novamente no servidor (substituído no produto WEB pela retirada de upload CSV em CHG-005, mantendo validadores de ingestão apenas para compatibilidade técnica/CLI).
- Justificativa: Protege dados nominais e evita confiar apenas na UI; em CHG-005, os dados operacionais passam a ser produzidos diretamente no sistema.
- Prioridade: P0. Estado da especificação: **Confirmado** (escopo de produto substituído por `REQ-CSV-004` em `CHG-005`, 2026-11-07; validação de ingestão preservada como compatibilidade interna em `WEB-025`/`WEB-026`).
- Aceite verificável: Na revisão de `WEB-025`, o upload CSV de usuário (`CsvImportPanel` e rotas de importação no modo produto) é retirado da aplicação, enquanto os validadores Python de ingestão (`stroop/ingestion/`) continuam testados isoladamente para compatibilidade histórica/CLI.
- Dependências: WEB-025 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Nenhum fluxo operacional do usuário no produto WEB pode depender de upload manual de CSV.
- Origem: desenvolvimento/CONTRATO_API_WEB.md e evolução `CHG-005` (`ADR-007`).

### REQ-CSV-003

- Descrição: Exportar detalhe e conjunto filtrado com reautorização e proteção de células.
- Justificativa: Mantém portabilidade sem vazar escopo ou fórmulas de planilha.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: CSV agregado corresponde à consulta filtrada; acesso revogado nega download; conteúdo potencialmente executável é neutralizado conforme contrato.
- Dependências: WEB-020 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Exportações explícitas e não versionadas.
- Origem: desenvolvimento/CONTRATO_API_WEB.md e routers api/.
- Impacto CHG-003: REQ-UX-006/WEB-020 exigem paridade das exportações após alteração de apresentação, sem remover colunas/métricas.
- Impacto CHG-005: Expandido por `REQ-CSV-005` (`WEB-020`) para suportar múltiplas granularidades, seleção de colunas, pré-visualização, critérios aplicados e distinção entre exportação desidentificada padrão e exportação nominal autorizada.

### REQ-CSV-004

- Descrição: Retirar a importação manual de CSV da interface e do fluxo operacional do produto WEB, consolidando o CSV exclusivamente como funcionalidade de exportação para o usuário.
- Justificativa: Evita entrada paralela de dados que contorne o cadastro central de pacientes e avaliadores e a preparação estruturada da sessão.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: Remoção de `CsvImportPanel.tsx` e de botões/comandos de importação CSV no dashboard; desativação/bloqueio das rotas de upload CSV no modo produto (`404`/`410`); preservação isolada dos módulos internos `stroop/ingestion/` e CLIs apenas para compatibilidade histórica e testes de roundtrip (EXP-CSV-01).
- Dependências: WEB-025, WEB-020 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não apagar dados ou coletas históricas existentes.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`, Seção 8).

### REQ-CSV-005

- Descrição: Prover exportação CSV avançada do subconjunto filtrado com escolha de granularidade (`pacientes`, `avaliacoes`, `tentativas`, `metricas` e `stroop_21_colunas`), seleção de colunas, pré-visualização com contagem de registros, identificação dos critérios aplicados e controle de modo desidentificado vs. nominal autorizado.
- Justificativa: Viabiliza análises estatísticas externas em diferentes níveis de agregação mantendo governança sobre dados nominais e integridade científica.
- Prioridade: P1. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: `POST /api/v1/exports/preview` e `POST /api/v1/exports/download` respeitam todos os filtros ativos, validam colunas por granularidade, exibem contagem e amostra prévia, separam estritamente resultados válidos oficiais de observações parciais/invalidadas, exigem autorização explícita e habilitação `DEC-03` para modo `nominal` (sendo `deidentified` o padrão) e neutralizam *CSV formula injection* (EXP-CSV-01).
- Dependências: WEB-020, WEB-019 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Valores ausentes exportados como vazio `""`, sem arredondamento destrutivo das métricas oficiais.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`, Seção 9).

## I. Administração e auditoria

### REQ-AUD-001

- Descrição: Registrar eventos técnicos e alterações de acesso sem payload pessoal.
- Justificativa: Rastreia operação sem ampliar exposição.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Eventos de login/acesso/gestão/importação têm ação/resultado/ID e não contêm cookies, código de convite, nomes ou corpo experimental.
- Dependências: WEB-024 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não imprimir dados em logs para depurar.
- Origem: seguranca/ACESSO_WEB.md e controles existentes.
- Impacto CHG-004: inclui eventos de login/limitação/provisionamento/rotação/recuperação sem senha/hash; autoria é da conta técnica, não individual (REQ-AUT-006). AUTH-L02/L03/L06/L09 em WEB-024.
- Impacto CHG-005: `web_registry_audit_events` (`WEB-045`/`WEB-047`) registra criação, edição, inativação e correção de vínculo de pacientes e avaliadores identificando tanto a conta técnica operadora quanto o UUID da entidade afetada, sem vazar dados nominais em logs operacionais de texto.

### REQ-AUD-002

- Descrição: Preservar histórico por mapa explícito de autorização, sem vínculo por nome.
- Justificativa: Evita apropriação de dados criando projeto de nome coincidente.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Colisão de código sem mapa nega; mapa autorizado permite; desativação retira acesso; nenhuma coleta é reescrita.
- Dependências: WEB-027 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Configurar mapa real exige autorização de dados.
- Origem: arquitetura/ADR-003-escopo-legado-web.md.
- Impacto CHG-005: Estendido em `WEB-027` (`web_legacy_entity_links`) para cobrir também o procedimento autorizado, verificável e auditado de associação de registros pseudonimizados anteriores a cadastros centrais de pacientes e avaliadores, proibindo reconciliação automática por coincidência de nome ou código.

### REQ-AUD-003

- Descrição: Rastrear tarefa, requisito, teste, evidência e aceite em fonte única.
- Justificativa: Permite continuidade sem memória conversacional.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Todos IDs do backlog/trace resolvem; conclusão tem comando/resultado/data/Git e nenhum critério pendente.
- Dependências: WEB-000 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Progresso não se baseia em tokens/linhas/push.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

## J. Segurança e privacidade

### REQ-SEG-001

- Descrição: Manter controles de transporte, entrada, origem e escopo com negação segura.
- Justificativa: Protege API/SPA contra abuso e vazamentos.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Casos XSS/CSRF/IDOR, JSON ambíguo, limite de corpo, rate limit e erros sanitizados testados; sem fallback de reader para writer.
- Dependências: WEB-024 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não reduzir proteções para simplificar migração.
- Origem: seguranca/ACESSO_WEB.md e controles existentes.
- Impacto CHG-004: inclui revisão final de credencial local, enumeração/força bruta/DoS, expiração e revogação; AUTH-L01–L09, WEB-024.

### REQ-SEG-002

- Descrição: Aprovar finalidade, informação/consentimento aplicáveis, retenção e tratamento institucional.
- Justificativa: Requisito para uso real sob responsabilidade do projeto.
- Prioridade: P0. Estado da especificação: **Pendente de decisão**.
- Aceite verificável: DEC-03 tem responsáveis, política aplicável, procedimentos de acesso/exclusão/incident response e aprovação institucional necessária registrada.
- Dependências: WEB-033 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não inventar base legal, prazo ou autorização ética.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-004: CHG-004/DEC-03 exige avaliação institucional explícita de conta compartilhada, custódia e limites de auditoria (R07/R12), AUTH-L09, WEB-033; decisão ainda não concedida.
- Impacto CHG-005: Com a revisão de `DEC-01` (`ADR-007`), `DEC-03` e `WEB-033` passam a abranger obrigatoriamente a base legal, consentimento/informação, retenção, inativação lógica e controle de exportação nominal dos cadastros centrais de pacientes (`full_name`, `initials`) e avaliadores responsáveis (`R05`, `R07`, `R12`, `R13`) antes de qualquer coleta com pessoas reais.

### REQ-SEG-003

- Descrição: Separar ensaio sintético de coleta real e impedir liberação implícita.
- Justificativa: Evita converter validação técnica em autorização de pesquisa.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Projetos continuam synthetic até DEC-05 e WEB-040; mudança de modo exige decisão específica, teste de barreira e trilha.
- Dependências: WEB-041 (após WEB-036 e DEC-05) e pré-requisitos registrados no backlog.
- Restrições conhecidas: Disponibilidade de VPS/domínio não autoriza coleta/deploy.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md.
- Impacto CHG-005: Em modo `synthetic`, os cadastros de pacientes e avaliadores aceitam apenas fixtures inequivocamente sintéticas e bloqueiam exportação nominal de pesquisa real até a habilitação `research` em `WEB-041` após `DEC-03` e `DEC-05`.
- Impacto CHG-004: exige conta local configurada com privilégios/vínculos explícitos em WEB-041 e aceites separados de research/deploy/coleta/transição; AUTH-L09.

## K. Infraestrutura e implantação

### REQ-INF-001

- Descrição: Operar PostgreSQL atrás da API com migrations versionadas e papéis mínimos.
- Justificativa: Protege histórico e reduz alcance do runtime.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Banco descartável aplica catálogo imutável, writer/reader e owner separados; leituras realmente read-only e schema compatível com rollback.
- Dependências: WEB-007 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Nenhuma migration nesta fase nem dados reais sem aprovação.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-004: exige schema de identidade/credencial/sessão local aditivo e grants/testes AUTH-L08 em WEB-021/024; aceite WEB-007 preservado, sem evidência local nova.

### REQ-INF-002

- Descrição: Empacotar em Docker Compose/Nginx/HTTPS com somente proxy exposto.
- Justificativa: Reutiliza VPS e isola serviços.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Build reproduzível, saúde, TLS, headers, limites e rejeição de fontes/secrets aprovados em pilha exclusiva; sem deploy automático.
- Dependências: WEB-029 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Infraestrutura operacional inalterada nesta execução.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-004: remove Google como dependência alvo de configuração; revalidar imagens/Compose/HTTPS em WEB-032, AUTH-L09; aceite histórico WEB-029 não cobre novo runtime.

### REQ-INF-003

- Descrição: Comprovar backup, réplica externa, restauração e rollback antes da publicação.
- Justificativa: Reduz perda/interrupção e testa recuperabilidade.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Restauração isolada confere dados/schema e retorno compatível; réplica/agenda/alerta ensaiados; comparar RPO 24h/RTO 4h com medidas reais.
- Dependências: WEB-031 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Objetivos históricos ADR-002, não garantias; produção requer autorização.
- Origem: arquitetura/ADR-002-hospedagem-vps.md.
- Impacto CHG-004: mantém réplica externa/RPO/RTO; AUTH-L08 em WEB-031/032/039 inclui hashes protegidos e restore sem ressuscitar sessões/senha antiga.

## L. Manutenibilidade e extensibilidade

### REQ-EXT-001

- Descrição: Manter fronteiras modulares e extensão por instrumento versionado sem antecipar novos testes.
- Justificativa: Permite crescer preservando núcleo e reduzindo custo.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Testes de fronteira negam dependência domínio→UI/IO; instrumento demo permanece técnico; novo instrumento exige contrato separado.
- Dependências: WEB-003 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem microserviços/abstrações universais sem necessidade.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

### REQ-EXT-002

- Descrição: Revalidar pipeline existente local e remotamente quando aplicável sem dispensar testes reais.
- Justificativa: Distingue código escrito de entrega comprovada.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Suite Python/PG sem skips, frontend/tipos/build, navegadores/HTTPS e scanner/auditorias com resultados por SHA; CI não verificada explicitada.
- Dependências: WEB-030 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Push branch atual não dispara verify; sem mudar gatilho nesta fase.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md.
- Impacto CHG-004: integra testes locais/fixtures/locks ao pipeline futuro em WEB-021/032, AUTH-L09; Actions anterior vale somente para seu SHA.

### REQ-EXT-003

- Descrição: Fornecer retomada canônica, branches coesas e runbooks de continuidade.
- Justificativa: Evita investigação repetida e integração não autorizada.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Workflow e AGENTS alinhados; branch/commits/push/CI recuperáveis; instruções locais, produção e recuperação verificáveis.
- Dependências: WEB-004 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem PR/merge/deploy automático; mudanças de escopo registradas.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

## M. Apresentação e experiência do participante — CHG-003

Direção UX confirmada pela solicitação de 2026-11-05. Apresentação e
identificação stroop-web-outline/1.0.0 aprovadas explicitamente pelo proprietário
na revisão D3/D4 de 2026-11-05; DEC-04 não aprovada. Especificação visual detalhada na
[fonte UX](experimento/UX_DECISIONS.md). Nenhum aceite retroativo.

### REQ-UX-001

- Descrição: Contorno branco dos caracteres. Aplicar contorno branco uniforme por token, preservando preenchimento das dez cores e tipografia experimental; avaliar stroke e alternativa compatível.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Dez cores, token, tinta interna e screenshots sintéticos em Chromium/Firefox, sem efeitos decorativos.
- Dependências: WEB-042, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-002

- Descrição: Ausência do fundo retangular. Retirar fundo branco das palavras sem cartão substituto; manter fundo geral e centralização.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Nenhuma caixa de fundo no DOM renderizado; centro/tamanho/fonte conferidos nas resoluções aprovadas.
- Dependências: WEB-042, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-003

- Descrição: Progresso experimental real. Reformular indicador discreto com etapa e tentativas concluídas derivadas do contrato, distinguindo prática e principal.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Sem totais fixos/avanço antecipado/animação; valores 0..total coerentes com eventos reais.
- Dependências: WEB-043, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-004

- Descrição: Cronômetro monotônico discreto. Preservar tempo decorrido do principal e MM:SS, com números tabulares/largura estável e fonte monotônica do motor.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Sem timer React/duplicado/deriva; origem e término preservados; RT independente e alinhamento estável.
- Dependências: WEB-043, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-005

- Descrição: Ausência de precisão em tempo real. Remover precisão agregada, percentuais, barras, rótulos e equivalentes da prática/principal, incluindo árvore acessível.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Sem nó, tooltip, espaço residual ou substituto de acertos/erros/ranking; feedback individual da prática permanece.
- Dependências: WEB-043, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-006

- Descrição: Preservação das métricas científicas. Retirada visual não altera accuracy total/Go/No-Go, omissões, comissões, RT, métricas persistidas, relatórios e CSV.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Paridade das 12 métricas, persistência e exportações; dashboard autorizado conserva precisão e ausência de RT.
- Dependências: WEB-044, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-007

- Descrição: Hierarquia experimental estável. Priorizar palavra no centro, HUD periférico autorizado, sem precisão ou espaço reservado; preservar escala experimental.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Centro não se desloca com HUD; teclado/foco/ambiente preservados; sem scroll e controles distrativos.
- Dependências: WEB-042, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-008

- Descrição: Instruções e prática claras. Melhorar hierarquia Go/No-Go, tecla e confirmação; diferenciar prática/principal sem alterar estratégia ou semântica.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Feedback individual e repetição opcional sem limiar preservados; teclado/foco e confirmação testados.
- Dependências: WEB-014, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-009

- Descrição: Transições previsíveis. Organizar instruções, prática, feedback, preparação e execução, sem mudar durações nem dar desempenho agregado.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Etapas distintas, layout estável e foco correto; nenhum início por tecla mantida ou sem confirmação.
- Dependências: WEB-014, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-010

- Descrição: Encerramento e entrega verdadeiros. Distinguir concluído, aguardando envio, enviando, confirmado, falha, interrompido/inválido conforme ADR-005.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Sem sucesso antes de recibo válido; replay/idempotência e parciais preservados, sem retomada; resultado individual só autorizado.
- Dependências: WEB-015, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-011

- Descrição: Acessibilidade e consistência visual. Reutilizar design system, revisar teclado/foco, contraste não experimental, erros/loading, resolução e perda de foco.
- Justificativa: Integrar UX-01–08 da missão à plataforma existente, reduzindo informação potencialmente distrativa sem inferir benefício científico.
- Prioridade: P0. Estado da especificação: **Confirmado** como direção UX; apresentação experimental aprovada pelo proprietário em D3 revisada; validações funcionais/temporais ainda exigidas.
- Aceite verificável: Sem recolorir estímulos/modificar resposta; sem scroll; componentes compartilhados e métricas administrativas preservados.
- Dependências: WEB-019, CHG-003 e gates do marco no backlog.
- Restrições conhecidas: D1–D6, DEC-02/04, R01/R02/R11; sem equivalência, fórmula nova ou autorização de outro marco.
- Origem: Solicitação do proprietário em 2026-11-05; UX_DECISIONS.md.

### REQ-UX-012

- Descrição: Sistema visual administrativo, usabilidade de cadastros/preparação e acessibilidade das áreas profissionais.
- Justificativa: Garantir experiência profissional coesa, legível e acessível nos módulos de Pacientes, Avaliadores, Preparar avaliação, Dashboard, Resultados e Exportações sem interferir no motor experimental.
- Prioridade: P1. Estado da especificação: **Confirmado** (CHG-005; ADR-007).
- Aceite verificável: Hierarquia histórica dos 8 módulos preservada como base; alvo de três eixos e componentes compartilhados da CHG-007 (REQ-UX-013..016); tabelas pesquisáveis/paginadas com algarismos tabulares; formulários com validação em linha, prevenção de duplicidade e etapa de conferência; estados de loading/vazio/erro explícitos; contraste WCAG AA na área administrativa e navegação completa por teclado com foco visível; zero alteração no motor experimental jsPsych (DASH-01/E2E-FLOW-01).
- Dependências: WEB-047, WEB-046, WEB-019 e gates do marco no backlog.
- Restrições conhecidas: Não alterar estímulos, paleta experimental, HUD, contorno branco ou tempos D5.
- Origem: Missão de replanejamento funcional e UX do proprietário em 2026-11-07 (`CHG-005`, Seção 10); `UX_DECISIONS.md`.
- Impacto CHG-006: A consolidação em 3 eixos fundamentais (`REQ-INT-004`) e o fluxo direto de avaliação (`REQ-SESS-001`) simplificam o design system e a navegação administrativa, mantendo a consistência visual, o foco por teclado e o contraste acessível em um fluxo único e coeso.

## N. Usabilidade e preparação de sessões

### REQ-SESS-001

- Descrição: Prover fluxo sem fricção de aplicação direta e preparação de avaliação em formulário unificado de etapa única estilo PsychoPy Runner, informando Participante, Visita e Projeto com pré-seleções contextuais inteligentes.
- Justificativa: Reduz o tempo de preparação para menos de 10 segundos no consultório, eliminando a navegação obrigatória prévia por telas de cadastro de pacientes.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-006; ADR-008).
- Aceite verificável: Formulário em etapa única aceita seleção com busca instantânea ou digitação de novo nome, preenche visita, seleciona projeto/avaliador responsável contextual e valida em tempo real sem redirecionamentos intermediários (PREP-02).
- Dependências: WEB-054; bases aceitas preservadas no backlog (CHG-007).
- Restrições conhecidas: Manter derivação determinística de iniciais e validação de nomes sem introduzir campos demográficos não autorizados.
- Origem: Missão de replanejamento documental do proprietário em 2026-11-08 (`CHG-006`).

- Complemento CHG-007: Preparação base WEB-046 aceita; fluxo unificado CHG-006/007 planejado. Aplicação de filtros explícita; URLs sem segredo; aceite/roteiros no contrato HTTP e UX7, sem SLA universal de 10 segundos.

### REQ-SESS-002

- Descrição: Disponibilizar modalidades duais de execução imediata da avaliação: modo presencial ("Iniciar Agora neste Dispositivo") e modo remoto ("Gerar Link / QR Code").
- Justificativa: Atende simultaneamente à aplicação clínica direta assistida no consultório/laboratório e à coleta remota ou em dispositivo secundário do participante.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-006; ADR-008).
- Aceite verificável: Modo "Iniciar Agora" oculta o painel da equipe, abre imediatamente a execução experimental no mesmo navegador e, ao término/interrupção com recibo, bloqueia o retorno aos dados confidenciais de outros pacientes exigindo confirmação/credencial da equipe; modo "Gerar Link / QR Code" exibe URL de uso único com botão de cópia e renderiza QR Code dinâmico em alta definição para leitura ótica direta (FLOW-02).
- Dependências: WEB-054; bases aceitas preservadas no backlog (CHG-007).
- Restrições conhecidas: Preservar estritamente o motor jsPsych, a apresentação com contorno branco `stroop-web-outline/1.0.0` e os limites temporais D5.
- Origem: Missão de replanejamento documental do proprietário em 2026-11-08 (`CHG-006`).

- Complemento CHG-007: Convite WEB-013/016/046 aceito; modalidades ADR-008 planejadas. Aplicação de filtros explícita; URLs sem segredo; aceite/roteiros no contrato HTTP e UX7, sem SLA universal de 10 segundos.

### REQ-SESS-003

- Descrição: Orquestrar de forma transparente e atômica no backend e frontend as entidades relacionais de paciente (`web_patients`), avaliador (`web_evaluators`), visita (`web_participant_visits`), vínculo de projeto (`web_project_participants`), sessão (`web_participant_sessions`) e convite (`web_invitations`).
- Justificativa: Elimina a fragmentação do pipeline operacional sem perder a integridade relacional, a auditabilidade e o rigor do modelo de dados PostgreSQL.
- Prioridade: P0. Estado da especificação: **Confirmado** (CHG-006; ADR-008).
- Aceite verificável: Submissão do formulário unificado executa resolução idempotente ou criação transacional do paciente, assegura vínculo ao projeto, gera visita e emite convite assinado em uma única requisição HTTP atômica, retornando identificadores estáveis (`PAT-...`, `EVA-...`) e token de sessão (ORQ-01).
- Dependências: WEB-054; bases aceitas preservadas no backlog (CHG-007).
- Restrições conhecidas: Não permitir bypass de validações cadastrais de homônimos ou restrições de chave estrangeira no banco.
- Origem: Missão de replanejamento documental do proprietário em 2026-11-08 (`CHG-006`).

- Complemento CHG-007: Fundação WEB-045/046 aceita; operação atômica alvo planejada. Aplicação de filtros explícita; URLs sem segredo; aceite/roteiros no contrato HTTP e UX7, sem SLA universal de 10 segundos.

## O. Consolidação profissional e integridade da consulta — CHG-007

### REQ-UX-013

- Descrição: Identidade pública Stroop Test Web. Marca coerente no shell, início, equipe, title/metadados e textos/documentação vigentes, preservando nomes científicos, IDs/versões e histórico.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P1. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Inventário de ocorrências e testes de título/DOM comprovam substituição pública sem troca de test_code, instruções experimentais ou contratos.
- Dependências: WEB-048 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-UX-014

- Descrição: Design system administrativo compartilhado. Tokens e catálogo de responsabilidades UX7-VIS em componentes reutilizáveis, sem estilos concorrentes por módulo ou dependência estética incidental.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P1. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Estados de interação/feedback, tipografia/escala/containers e catálogo completo testados; erros recuperáveis preservam campos; estilos administrativos não mudam estímulos/HUD.
- Dependências: WEB-048 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-UX-015

- Descrição: Sidebar responsiva dos três eixos. Navegação por objetivos ADR-008, desktop expandido/recolhido e drawer móvel, conta/logout previsíveis e contexto preservado.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P1. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Três eixos autorizados no primeiro nível; keyboard/focus/voltar/avançar e logout/revogação não expõem dados; overview/histórico/análise/exportação são experiência única.
- Dependências: WEB-049 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-UX-016

- Descrição: Acessibilidade AA e homologação responsiva profissional. WCAG 2.2 AA aplicável à área profissional completa, cinco larguras e zoom 200%, jornadas funcionais e estados reais.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P0. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: UX7-AA/J1/J2/J3 comprovadas com teclado, foco/leitor de tela, contraste, tabelas equivalentes e sem perda de conteúdo/rolagem global; nenhum aceite só por render/build.
- Dependências: WEB-055 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-REL-006

- Descrição: Consulta aplicada compartilhada e concorrência segura. Um estado normalizado em RAM, rascunho/aplicada, Aplicar explícito, chips e contexto por geração para KPIs/gráficos/tabelas/detalhes/exportação.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P0. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Filtro pendente é indicado e bloqueia download; resposta obsoleta/página falha/snapshot expirado/revogação/logout não publica dados no contexto novo; filtros REQ-REL-004 sem cópias independentes.
- Dependências: WEB-050 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-REL-007

- Descrição: Dicionário de indicadores e integridade de agregação. Referenciar as 12 métricas Python e metadados de numerador/denominador/unidade/população/exclusões/nulos/agregação/fonte/versão, sem nova fórmula científica.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P0. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Média de avaliações distinta de proporção por tentativas; RT ausente preservado; versões incompatíveis estratificadas; quatro contagens de pacientes e visitas/avaliações/tentativas separadas; repetidas sem inferência independente.
- Dependências: WEB-051 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-REL-008

- Descrição: Exploração multigranular interativa e longitudinal. Níveis autorizado institucional/projeto, instrumento/versão, participante/visita, avaliação/tentativa e tempo/grupos; visuais, drill-down, tabelas e exportação na mesma consulta.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P1. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Interações/tabelas UX7-DADOS, distribuição RT/resposta/condição, série por período e longitudinal verificadas com unidades/nulos e identidade correta; escolha de coluna/densidade/página não altera população exportada.
- Dependências: WEB-052 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-REL-009

- Descrição: Volume paginado e completude explícita. Seleção/agregações server-side e paginação estável com teto declarado e medição antes de ampliar; sem infraestrutura nova sem necessidade.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P0. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: 5.000/5.001 e 20/21 projetos testados; limite/erro não produz parcial como total; fingerprints e cancelamento protegem conjunto; EXPLAIN/latência/memória documentados conforme UX7-PERF.
- Dependências: WEB-051 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-REL-010

- Descrição: Qualidade operacional descritiva auditável. Contagens de RT ausente, proveniência incompleta, interrupção/invalidação, avaliador ausente e divergências de versão/plataforma com base e origem rastreáveis.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P1. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Dados operacionais separados de resultados oficiais; nenhum escore clínico ou métrica substitutiva; contagem/base de qualidade confere com fixture e detalhe autorizado.
- Dependências: WEB-051 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-CSV-006

- Descrição: Igualdade da consulta prévia e download. Cinco projeções existentes usam seleção canônica autorizada e token integral; filtros/colunas/modo/versão/projetos e conteúdo vinculados; sem ignorar filtro.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P0. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: EXPORT7 comprova conjuntos lógicos e cardinalidades por projeção, alteração/expiração conflita, token divergente nega, CSV21 íntegro e filtro parcial recusado; amostra é mesma projeção do arquivo.
- Dependências: WEB-053 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

### REQ-CSV-007

- Descrição: Privacidade e escopo integral da exportação. Revalidar todos projetos/cadastro/nominal no servidor, deidentified em amostra e arquivo, DEC-03 institucional, reader sem fallback, auditoria segura e proteção de células.
- Justificativa: Materializar experiência integrada e integridade da CHG-007 antes da candidata, reutilizando a plataforma existente.
- Prioridade: P0. Estado da especificação: **Confirmado** (direção autorizada CHG-007, implementação PLANEJADA).
- Aceite verificável: Revogação nega antes do download; pacientes fora de A não exportam; nominal não vaza em amostra/coluna omitida; multi-projeto não reduz escopo silenciosamente; CSV injection e acesso direto negados conforme contrato.
- Dependências: WEB-053 e dependências/gates da ficha no backlog.
- Restrições conhecidas: D1–D6, domínio Python/CSV canônico e DEC-03/04/05 preservados; somente dados sintéticos na implementação técnica; nenhum deploy implícito.
- Origem: Missão de replanejamento do proprietário em 2026-11-11; ADR-008 complementada; UX7 e contrato HTTP CHG-007.

## Matriz de rastreabilidade

Cada linha é o vínculo principal; relações complementares aparecem nas fichas.
Componentes citados em linhas PLANEJADAS podem ser caminhos propostos; conferir
existência antes de executar e reutilizar equivalentes, sem criar arquivo só pelo nome.
Testes com caminho são existentes; resultados atuais só estão comprovados quando
a linha aponta para uma evidência datada no backlog. Referências PLANEJADAS são
verificações ainda sem resultado de aceite; não inventam testes.
Evidência e aceite são consultados por WEB no backlog, sem duplicar estado.
Vínculos sem evidência datada permanecem planejados, mesmo quando o componente
já existe ou participa da regressão geral. WEB-000 é exclusivamente documental.

| Requisito | Decisão | Marco | Tarefa | Componente | Teste/verificação | Evidência → aceite |
|---|---|---|---|---|---|---|
| REQ-AUT-001 | CHG-004; ADR-006 | M6 | WEB-021 | `api/local_auth.py, api/local_session.py, api/auth.py, api/config.py, web/src/App.tsx, web/src/components/ProfessionalCredentials.tsx` | `tests/test_local_auth.py, tests/test_local_auth_http.py, tests/test_web_security_review.py, web/src/components/ProfessionalCredentials.test.tsx, web/e2e/local-auth/auth.spec.ts, web/e2e/integrated/, scripts/smoke_web_compose.py` | ACEITO em WEB-021/024; EV-M6-021/024 no backlog |
| REQ-AUT-002 | ADR-004; CHG-004/ADR-006 | M6 | WEB-022 | `stroop/domain/auth.py, stroop/persistence/web_sessions.py, stroop/persistence/local_management.py, api/administration.py` | `tests/test_web_auth.py, tests/test_local_auth_http.py, tests/test_web_administration_provisioned.py, web/e2e/administration.spec.ts, web/e2e/integrated/administration.spec.ts, web/e2e/local-auth/auth.spec.ts` | ACEITO histórico EV-M6-022/023; regressão local AUTH-L04/L06/L07 aceita em EV-M6-021/024 |
| REQ-AUT-003 | ADR-004; CHG-004/ADR-006 | M6 | WEB-023 | `api/auth.py, api/local_auth.py, api/local_session.py, api/sessions.py, stroop/persistence/local_auth.py` | `tests/test_web_sessions.py, tests/test_local_auth_http.py, tests/test_web_security_review.py, web/e2e/local-auth/auth.spec.ts, web/e2e/integrated/sessions-security.spec.ts` | ACEITO histórico EV-M6-022/023; mecanismo local AUTH-L04/L05 aceito em EV-M6-021/024 |
| REQ-AUT-004 | CHG-004; ADR-006 | M6 | WEB-021 | `stroop/domain/local_auth.py, stroop/domain/password_blocklist.py, stroop/application/local_auth.py, stroop/persistence/local_auth.py, stroop/security/passwords.py, scripts/gerenciar_conta_local.py`, migrations 0012/0013 | `tests/test_local_auth.py, tests/test_local_auth_http.py, tests/test_postgres_migrations.py, tests/test_web_database_provision.py, web/e2e/local-auth/auth.spec.ts, scripts/smoke_local_auth_restore.py` | ACEITO em WEB-021/024; EV-M6-021-BASE e EV-M6-021/024 no backlog |
| REQ-AUT-005 | CHG-004; ADR-006 | M6 | WEB-021 | `api/local_auth.py, api/transport.py, stroop/persistence/local_auth.py, web/deploy/nginx.conf.template` | `tests/test_local_auth.py, tests/test_local_auth_http.py, tests/test_web_security_review.py, tests/test_web_proxy_config.py` | ACEITO em WEB-021/024; EV-M6-021/024 no backlog |
| REQ-AUT-006 | CHG-004; ADR-006; DEC-03 | M9 | WEB-033 | Política institucional, autorização backend e runbooks | Controles técnicos em `tests/test_local_auth_http.py, web/e2e/local-auth/auth.spec.ts`; PLANEJADO: revisão institucional DEC-03 em WEB-033 | Controles técnicos TESTADOS em EV-M6-021/024; decisão institucional WEB-033 PLANEJADA |
| REQ-PAR-001 | ADR-004; CHG-005/ADR-007 | M4 | WEB-013 | `api/sessions.py, web/src/participant/` | `tests/test_web_sessions.py, web/e2e/integrated/invitations.spec.ts` | ACEITO em WEB-013/016; EV-M4-013/016 no backlog; extensão cadastral em WEB-045/046 |
| REQ-PAR-002 | ADR-004/005; CHG-005/ADR-007 | M2 | WEB-005 | `Modelo lógico e formulário de sessão` | `tests/test_web_sessions.py, web/e2e/integrated/invitations.spec.ts` | Aceite documental em EV-M2-005-R2; receptor/banco em EV-M2 e integração de produto aceita em WEB-013/016; evolução central em WEB-045 |
| REQ-PAR-003 | ADR-004; CHG-005/ADR-007 | M4 | WEB-014 | `web/src/components/, api/models.py` | `tests/test_web_security_review.py, web/e2e/practice.spec.ts, web/e2e/main.spec.ts, web/e2e/integrated/participant.spec.ts` | ACEITO em WEB-014/016; EV-M4-013/016 no backlog |
| REQ-PAR-004 | CHG-005; ADR-007; DEC-01 revisada | M4 | WEB-045 | `scripts/migrations/0014_central_patients_evaluators.sql, stroop/domain/registry.py, stroop/persistence/web_registry.py, api/patients.py` | `tests/test_web_patients.py, tests/test_postgres_migrations.py, tests/test_web_database_provision.py, web/src/components/SessionInvitation.test.tsx, web/e2e/integrated/invitations.spec.ts` | ACEITO em WEB-045/046; EV-M4-045/046 no backlog |
| REQ-PAR-005 | CHG-005; ADR-007 | M5 | WEB-047 | `api/patients.py, web/src/components/PatientsPanel.tsx, stroop/persistence/` | `PLANEJADO: CAD-02 em tests/test_web_patients.py, Vitest e Playwright E2E em WEB-047 e WEB-027` | PLANEJADA; consultar WEB-047 e WEB-027 no backlog |
| REQ-AVA-001 | ADR-004; CHG-004/ADR-006; CHG-005 | M4 | WEB-013 | `web/src/App.tsx, api/sessions.py` | `tests/test_web_sessions.py, tests/test_local_auth.py, web/e2e/integrated/invitations.spec.ts` (AUTH-L06/L07) | ACEITO em WEB-013/016; EV-M4-013/016 no backlog; seleção cadastral aceita em WEB-046 (EV-M4-045/046) |
| REQ-AVA-002 | ADR-004/005; CHG-005/ADR-007 | M2 | WEB-005 | `Contrato HTTP e modelo lógico` | `tests/test_web_sessions.py, web/e2e/integrated/invitations.spec.ts` | Aceite documental em EV-M2-005-R2; receptor/banco em EV-M2 e integração de produto aceita em WEB-013/016 e WEB-045/046 |
| REQ-AVA-003 | ADR-004; CHG-005 | M4 | WEB-015 | `web/src/participant/ParticipantRun.ts, api/results.py` | `tests/test_web_results.py, tests/test_web_checkpoints.py, web/src/participant/ParticipantRun.test.ts, web/e2e/integrated/participant.spec.ts` | ACEITO em WEB-015/016; EV-M4-013/016 no backlog |
| REQ-AVA-004 | CHG-005; ADR-007 | M4 | WEB-045 | `scripts/migrations/0014_central_patients_evaluators.sql, stroop/domain/registry.py, stroop/persistence/web_registry.py, api/evaluators.py` | `tests/test_web_evaluators.py, web/src/components/SessionInvitation.test.tsx, web/e2e/integrated/invitations.spec.ts; PLANEJADO: UI administrativa dedicada em WEB-047` | ACEITO para fundação e preparação em WEB-045/046 (EV-M4-045/046); módulo administrativo dedicado em WEB-047 |
| REQ-AVA-005 | CHG-005; ADR-007 | M4 | WEB-046 | `web/src/components/SessionInvitation.tsx, web/src/api/patients.ts, web/src/api/evaluators.ts, web/src/api/sessions.ts, api/sessions.py, stroop/application/web_sessions.py` | `tests/test_web_sessions.py, web/src/api/sessions.test.ts, web/src/components/SessionInvitation.test.tsx, web/e2e/invitations.spec.ts, web/e2e/integrated/invitations.spec.ts` | ACEITO em WEB-046; EV-M4-045/046 no backlog |
| REQ-EXP-001 | ADR-004 | M3 | WEB-009 | `condicoes/, web/src/experiment/` | `tests/test_fase3_condicoes_tempos.py`, `web/src/experiment/environment.test.ts`, `practice.test.ts`, `main.test.ts` | EXECUTADA em WEB-009; EV-M3-009/010 no backlog |
| REQ-EXP-002 | ADR-004 | M3 | WEB-010 | `web/src/experiment/main-engine.ts, ExperimentHost.tsx` | `web/src/experiment/main.test.ts`, `practice.test.ts`, `ExperimentHost.test.tsx`, `web/e2e/main.spec.ts`, `practice.spec.ts` | Evidências e falhas em EV-M3-009/010; consultar aceite WEB-010 no backlog |
| REQ-EXP-003 | ADR-004 | M3 | WEB-011 | `web/src/experiment/environment.ts, web/pilots/` | `web/pilots/web011.spec.ts, web/src/transport/checkpoint-queue.test.ts, web/src/experiment/main.test.ts` | ENGENHARIA TESTADA; campanha WEB-011 aceita em EV-M3-011; suporte local restrito aceito pelo responsável em EV-M3-012-ACEITE (2026-11-06), sem latência física ou integração M4 presumida |
| REQ-INT-001 | ADR-004 | M2 | WEB-006 | `stroop/domain/web_results.py, api/results.py` | `tests/test_web_results.py, tests/test_web_sessions.py, tests/test_web_checkpoints.py` | EXECUTADA em WEB-006; EV-M2 no backlog |
| REQ-INT-002 | ADR-004 | M2 | WEB-007 | `stroop/persistence/web_sessions.py, web_checkpoints.py` | `tests/test_web_checkpoints.py, tests/test_web_sessions.py, tests/test_web_database_provision.py, tests/test_postgres_migrations.py` | EXECUTADA em WEB-007; EV-M2-007/008 no backlog |
| REQ-INT-003 | ADR-004/005 | M2 | WEB-005 | `ParticipantRun.ts, checkpoint-worker.ts e modelo lógico` | `tests/test_web_checkpoints.py, web/src/transport/checkpoint-queue.test.ts, web/src/participant/ParticipantRun.test.ts, web/e2e/integrated/participant.spec.ts` | Aceite documental em EV-M2-005-R2; receptor/banco em EV-M2, worker/timing em EV-M3-011 e integração de produto aceita em WEB-015/016 (EV-M4-013/016) |
| REQ-INT-004 | CHG-006/007; ADR-008 | M8 | WEB-049 | `web/src/components/ProfessionalDashboard.tsx, web/src/components/UnifiedNavigation.tsx` | PLANEJADO: NAV7; sidebar/3 eixos | Base WEB-047 e cobertura documental WEB-028 históricas; integração CHG-007 planejada; consultar backlog |
| REQ-INT-005 | CHG-006/007; ADR-008 | M8 | WEB-052 | `web/src/components/UnifiedAnalyticsPanel.tsx, web/src/dashboard/analysis.ts` | PLANEJADO: QUERY7/DATA7/ANALYTICS7/EXPORT7 | Base WEB-017/019/020 histórica; integração CHG-007 planejada; consultar backlog |
| REQ-MET-001 | ADR-004 | M2 | WEB-008 | `stroop/domain/stroop.py, web_results.py` | `tests/test_nucleo_compartilhado.py, tests/test_web_export.py, tests/test_web_checkpoints.py` | EXECUTADA em WEB-008; EV-M2-007/008 no backlog |
| REQ-MET-002 | ADR-004 | M2 | WEB-008 | `stroop/domain/stroop.py, web/src/dashboard/analysis.ts` | `tests/test_web_results.py, web/src/dashboard/analysis.test.ts` | EXECUTADA em WEB-008; EV-M2-007/008 no backlog |
| REQ-MET-003 | ADR-004 | M5 | WEB-019 | `web_assessments, api/assessments.py` | `tests/test_web_assessments.py` | PLANEJADA; consultar WEB-019 no backlog |
| REQ-REL-001 | ADR-004; CHG-004/ADR-006; CHG-005 | M5 | WEB-017 | `web/src/components/, api/assessments.py` | `tests/test_web_assessments.py`; PLANEJADO: AUTH-L06/L07 e DASH-01 conforme requisito | PLANEJADA; consultar WEB-017 no backlog |
| REQ-REL-002 | ADR-004; CHG-005 | M5 | WEB-019 | `web/src/components/, web/src/dashboard/` | `tests/test_web_results.py`; PLANEJADO: DASH-01 em WEB-019 | PLANEJADA; consultar WEB-019 no backlog |
| REQ-REL-003 | ADR-004; CHG-004/ADR-006; CHG-005 | M5 | WEB-018 | `api/administration.py, web/src/api/administration.ts` | `tests/test_web_administration_provisioned.py`; PLANEJADO: AUTH-L06/L07 em WEB-018 | PLANEJADA; consultar WEB-018 no backlog |
| REQ-REL-004 | CHG-005; ADR-007 | M5 | WEB-017 | `web/src/components/ResearchFilters.tsx, api/assessments.py, stroop/persistence/` | `PLANEJADO: DASH-01 em tests/test_web_assessments.py, ResearchFilters.test.tsx e web/e2e/integrated/dashboard.spec.ts` | PLANEJADA; consultar WEB-017 no backlog |
| REQ-REL-005 | CHG-005; ADR-007 | M5 | WEB-019 | `web/src/components/ProfessionalDashboard.tsx, web/src/components/ResearchVisualizations.tsx, web/src/components/ResultsTable.tsx` | `PLANEJADO: DASH-01 em Vitest e Playwright E2E em WEB-019` | PLANEJADA; consultar WEB-019 no backlog |
| REQ-CSV-001 | ADR-004; CHG-005/ADR-007; CHG-006/ADR-008 | M7 | WEB-026 | `stroop/ingestion/stroop_csv.py, api/assessments.py, tests/test_web_multi_export.py` | `tests/test_csv_unificado.py, test_web_multi_export.py, test_importar_csv_sqlite.py`; roundtrip 21 colunas e SQLite | ACEITO em WEB-026; roundtrip de exportação canônica e granularidades com analisador Python e SQLite comprovado em EV-M7-026 |
| REQ-CSV-002 | ADR-004; CHG-005/ADR-007 | M7 | WEB-025 | `stroop/ingestion/, api/imports.py` | `tests/test_web_imports.py`; isolamento de ingestão e retirada de UI | ACEITO em WEB-025; ingestão isolada preservada para testes sintéticos e CLI em EV-M7-025 |
| REQ-CSV-003 | ADR-004; CHG-005/ADR-007 | M5 | WEB-020 | `api/assessments.py, web/src/api/aggregate.ts` | `tests/test_web_aggregate_export.py`; PLANEJADO: EXP-CSV-01 em WEB-020 | PLANEJADA; consultar WEB-020 no backlog |
| REQ-CSV-004 | CHG-005; ADR-007; CHG-006/ADR-008 | M7 | WEB-025 | `web/src/components/ProfessionalDashboard.tsx, api/imports.py` | `tests/test_web_imports.py, web/e2e/imports.spec.ts, web/e2e/integrated/imports.spec.ts`; EXP-CSV-01 | ACEITO em WEB-025; ausência de CsvImportPanel na UI e bloqueio 410 no modo produto comprovados em EV-M7-025 |
| REQ-CSV-005 | CHG-005; ADR-007 | M5 | WEB-020 | `api/assessments.py, web/src/components/ExportsPanel.tsx, stroop/application/` | `PLANEJADO: EXP-CSV-01 em tests/test_web_aggregate_export.py, Vitest e Playwright E2E em WEB-020` | PLANEJADA; consultar WEB-020 no backlog |
| REQ-AUD-001 | ADR-004; CHG-004/ADR-006; CHG-005 | M6 | WEB-024 | `stroop/persistence/auth.py, stroop/persistence/local_auth.py, api/transport.py` | `tests/test_web_security_review.py, tests/test_local_auth.py, tests/test_local_auth_http.py` (AUTH-L02/L03/L06/L09) | ACEITO em WEB-024; EV-M6-021/024 no backlog; trilha cadastral em WEB-045/047 |
| REQ-AUD-002 | ADR-003 + ADR-004; CHG-005/ADR-007; CHG-006/ADR-008 | M7 | WEB-027 | `scripts/migrations/0014_central_patients_evaluators.sql, stroop/persistence/web_registry.py, api/administration.py` | `tests/test_web_evaluators.py, tests/test_web_assessments.py`; associação auditada de legados | ACEITO em WEB-027; web_legacy_entity_links e web_registry_audit_events com vínculo explícito e sem merge automático em EV-M7-027 |
| REQ-AUD-003 | ADR-004 | M0 | WEB-000 | `docs/Projeto Stroop Test.md e REQUISITOS_E_RASTREABILIDADE.md` | `Validação documental reproduzível no workflow (EV-M0)` | EV-M0 real; aceite documental em WEB-000 no backlog |
| REQ-SEG-001 | ADR-004; CHG-004/ADR-006 | M6 | WEB-024 | `api/transport.py, api/local_auth.py, web/deploy/` | `tests/test_web_security_review.py, tests/test_web_proxy_config.py, tests/test_local_auth.py, tests/test_local_auth_http.py, web/e2e/local-auth/auth.spec.ts` (AUTH-L01–L09) | ACEITO em WEB-024; EV-M6-021/024 no backlog |
| REQ-SEG-002 | ADR-004; CHG-004/ADR-006; CHG-005/ADR-007 | M9 | WEB-033 | `docs/seguranca/` | `PLANEJADO: revisão do responsável DEC-03 (incluindo cadastros nominais e conta compartilhada)`; AUTH-L09/DEC-03; WEB-033 | PLANEJADA; consultar WEB-033 no backlog |
| REQ-SEG-003 | ADR-004; CHG-004/ADR-006; CHG-005/ADR-007 | M10 | WEB-041 | `stroop/persistence/web_sessions.py, política de operação` | `PLANEJADOS: testes research e barreira de exportação nominal em WEB-041`; AUTH-L09; WEB-041 | PLANEJADA; consultar WEB-041 no backlog |
| REQ-INF-001 | ADR-002 + ADR-004; CHG-004/ADR-006 | M2 | WEB-007 | `scripts/migrations/, provision_web_database.py` | `tests/test_web_database_provision.py, tests/test_postgres_migrations.py, tests/test_local_auth.py, scripts/smoke_local_auth_restore.py` (AUTH-L08) | Aceite em EV-M2-007/008 e incremento local AUTH-L08 comprovado em EV-M6-021/024 |
| REQ-INF-002 | ADR-002 + ADR-004; CHG-004/ADR-006 | M8 | WEB-029 | `compose.web.yaml, Dockerfile.api, Dockerfile.web` | `tests/test_web_proxy_config.py, scripts/smoke_web_compose.py`; consolidação final em WEB-032 | ACEITA em EV-M8-029/031 e revalidada sem Google em EV-M6-021/024; release final em WEB-032 |
| REQ-INF-003 | ADR-002 + ADR-004; CHG-004/ADR-006 | M8 | WEB-031 | `scripts/backup_postgres.py, scripts/smoke_local_auth_restore.py, deploy/` | `tests/test_web_backup_replication.py, scripts/smoke_local_auth_restore.py`; réplica externa/release em WEB-031/032/039 | PARCIAL em EV-M8-029/031 e restore local-auth em EV-M6-021/024; réplica externa pendente em WEB-031 |
| REQ-EXT-001 | ADR-004 | M1 | WEB-003 | `stroop/, api/, web/` | `tests/test_nucleo_compartilhado.py, tests/test_casos_uso_importacao.py, tests/test_multiplos_instrumentos.py` | EV-M1 real em WEB-003; fronteiras/contratos revalidados em 2026-11-04 |
| REQ-EXT-002 | ADR-004; CHG-004/ADR-006 | M8 | WEB-030 | `scripts/verify_web_ci.py, .github/workflows/web.yml` | `tests/test_verify_web_ci.py, scripts/verify_web_ci.py`; candidata final em WEB-032 | ACEITA em EV-M8-030; etapas locais com autenticação local aprovadas em EV-M6-021/024; candidata final em WEB-032 |
| REQ-EXT-003 | ADR-004 | M1 | WEB-004 | `AGENTS.md, docs/WORKFLOW_CODEX_CLI.md` | `Receita BASELINE_LOCAL.md; scripts/verify_web_ci.py integration; ensaio de retomada WEB-004` | EV-M1 real em WEB-004; percurso local/retomada revalidados em 2026-11-04 |
| REQ-UX-001 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-042 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-002 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-042 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-003 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-043 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts, web/src/experiment/protocol.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-004 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-043 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-005 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-043 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-006 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-044 | `web/src/experiment/summary.ts, stroop/domain/stroop.py, web/src/participant/ParticipantRun.ts` | `web/src/experiment/summary.test.ts, tests/test_nucleo_compartilhado.py, tests/test_web_export.py, web/e2e/integrated/invitations.spec.ts, web/e2e/integrated/participant.spec.ts; PLANEJADO: WEB-019/020` | Regressão de métricas/CSV em EV-M3-044 e integração M4 aceita em WEB-016 (EV-M4-013/016); escopo M5 WEB-019/020 PLANEJADO |
| REQ-UX-007 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-042 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts, web/src/styles.css` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-008 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M4 | WEB-014 | `web/src/App.tsx, web/src/experiment/practice-engine.ts, docs/experimento/COPY_DAS_TELAS.md, web/src/components/PracticePreparation.tsx, web/src/components/ParticipantFlow.tsx` | `web/src/experiment/practice.test.ts, web/e2e/practice.spec.ts, web/e2e/participant.spec.ts, web/e2e/integrated/participant.spec.ts` | ACEITO em WEB-014/016; EV-M4-013/016 no backlog |
| REQ-UX-009 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M4 | WEB-014 | `web/src/App.tsx, web/src/experiment/ExperimentHost.tsx, web/src/participant/ParticipantRun.ts, web/src/components/PracticePreparation.tsx, web/src/components/ParticipantFlow.tsx` | `web/src/experiment/ExperimentHost.test.tsx, web/e2e/practice.spec.ts, web/e2e/main.spec.ts, web/e2e/integrated/participant.spec.ts` | ACEITO em WEB-014/016; EV-M4-013/016 no backlog |
| REQ-UX-010 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M4 | WEB-015 | `web/src/participant/ParticipantRun.ts, web/src/components/ResultSummary.tsx, api/results.py` | `web/src/participant/ParticipantRun.test.ts, web/src/api/participant.test.ts, web/e2e/integrated/participant.spec.ts, web/e2e/integrated/complete-results.spec.ts` | ACEITO em WEB-015/016; EV-M4-013/016 no backlog |
| REQ-UX-011 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M5 | WEB-019 | `web/src/styles.css, web/src/App.tsx, web/src/components/, web/src/dashboard/` | `PLANEJADO: componentes Vitest, teclado/árvore acessível e E2E M5; cobertura experimental WEB-044` | Cobertura experimental M3 conferida em EV-M3-044; restante e aceite M5 WEB-019 PLANEJADOS |
| REQ-UX-012 | CHG-005; ADR-007 | M5 | WEB-047 | `web/src/styles.css, web/src/components/ProfessionalDashboard.tsx, web/src/components/PatientsPanel.tsx, web/src/components/EvaluatorsPanel.tsx` | `PLANEJADO: DASH-01 e E2E-FLOW-01 em Vitest e Playwright (teclado, foco, contraste, estados e não regressão experimental) em WEB-047 e WEB-019` | PLANEJADA; consultar WEB-047 e WEB-019 no backlog |
| REQ-SESS-001 | CHG-006/007; ADR-008 | M8 | WEB-054 | `web/src/components/DirectSessionLauncher.tsx, web/src/api/sessions.ts` | PLANEJADO: PREP7; UX7-J2 | Preparação base WEB-046 aceita; fluxo unificado CHG-006/007 planejado; consultar backlog |
| REQ-SESS-002 | CHG-006/007; ADR-008 | M8 | WEB-054 | `web/src/components/DirectSessionLauncher.tsx, web/src/components/QrCodeModal.tsx, web/src/App.tsx` | PLANEJADO: PREP7; isolamento/QR | Convite WEB-013/016/046 aceito; modalidades ADR-008 planejadas; consultar backlog |
| REQ-SESS-003 | CHG-006/007; ADR-008 | M8 | WEB-054 | `api/sessions.py, stroop/application/web_sessions.py, stroop/persistence/web_registry.py` | PLANEJADO: PREP7; API/PG idempotência/rollback | Fundação WEB-045/046 aceita; operação atômica alvo planejada; consultar backlog |

| REQ-UX-013 | CHG-007; ADR-008 complementada | M8 | WEB-048 | `web/index.html, App.tsx, componentes e docs/` | PLANEJADO: COMP7; Vitest e revisão de referências, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-048 no backlog |
| REQ-UX-014 | CHG-007; ADR-008 complementada | M8 | WEB-048 | `web/src/styles.css, web/src/components/` | PLANEJADO: COMP7; Vitest/visual e regressão experimental, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-048 no backlog |
| REQ-UX-015 | CHG-007; ADR-008 complementada | M8 | WEB-049 | `App.tsx, ProfessionalDashboard.tsx, navegação` | PLANEJADO: NAV7; Vitest e Playwright Chromium/Firefox, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-049 no backlog |
| REQ-UX-016 | CHG-007; ADR-008 complementada | M8 | WEB-055 | `web/src/components/, web/e2e/integrated/` | PLANEJADO: UX7-AA; COMP7/NAV7 e três jornadas, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-055 no backlog |
| REQ-REL-006 | CHG-007; ADR-008 complementada | M8 | WEB-050 | `ResearchFilters.tsx, ProfessionalDashboard.tsx, dashboard/, api/` | QUERY7: query.test.ts, AppliedQuery.test.tsx, ResearchFilters.test.tsx; applied-query/research-filters/aggregate-export.spec.ts; integração HTTPS conforme backlog | Implementação em validação; sem aceite integral; consultar EV-M8-050 no backlog |
| REQ-REL-007 | CHG-007; ADR-008 complementada | M8 | WEB-051 | `stroop/domain/, application/, persistence/, api/assessments.py` | PLANEJADO: DATA7; paridade oficial em API/PG sintético, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-051 no backlog |
| REQ-REL-008 | CHG-007; ADR-008 complementada | M8 | WEB-052 | `ResearchVisualizations.tsx, InstrumentVisualizations.tsx, ResultsTable.tsx, dashboard/` | PLANEJADO: ANALYTICS7; Vitest e Playwright com tabela equivalente, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-052 no backlog |
| REQ-REL-009 | CHG-007; ADR-008 complementada | M8 | WEB-051 | `api/assessments.py, stroop/persistence/web_assessments.py, clientes` | PLANEJADO: DATA7; API/PG sintético e benchmark medido, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-051 no backlog |
| REQ-REL-010 | CHG-007; ADR-008 complementada | M8 | WEB-051 | `api/assessments.py, persistência, dashboard/` | PLANEJADO: DATA7/ANALYTICS7; casos legados/parciais sintéticos, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-051 no backlog |
| REQ-CSV-006 | CHG-007; ADR-008 complementada | M8 | WEB-053 | `ExportHubPanel.tsx, api/exports.py, stroop/application/, persistence/web_multi_export.py` | PLANEJADO: EXPORT7; API/PG real sintético e Playwright com CSV parseado, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-053 no backlog |
| REQ-CSV-007 | CHG-007; ADR-008 complementada | M8 | WEB-053 | `api/exports.py, stroop/persistence/web_multi_export.py, domain/web_multi_export.py` | PLANEJADO: EXPORT7; segurança negativa e roundtrip Python/SQLite, conforme VALIDACAO_WEB | PLANEJADA; consultar WEB-053 no backlog |

Estados de evidência (todos os requisitos, inclusive autenticação local): **PLANEJADO** (critério sem execução), **IMPLEMENTADO**
(código disponível), **TESTADO** (comandos/resultados/SHA registrados), **ACEITO**
(todos os critérios conferidos na ficha WEB). Esses rótulos não substituem os
estados canônicos das tarefas nem dão crédito parcial. Evidência e aceite são
referências à ficha do backlog; a matriz não mantém um segundo painel.

## Relações complementares CHG-007

A matriz mantém uma linha principal por requisito. REQ-REL-004/005 e
REQ-CSV-005 preservam a origem/aceite M5; sua extensão integrada é exigida em
WEB-050/051/052/053, sem declarar regressão funcional de toda a entrega histórica.
REQ-UX-012 estende-se a WEB-048/049/054/055; REQ-PAR-005/AVA-005 a WEB-054;
REQ-AUT-002/003 e REQ-AUD-001 à exportação/handoff, REQ-MET-001/002/003 a
WEB-051/052/055. REQ-UX-016 possui implementação distribuída em WEB-048..054 e
aceite transversal em WEB-055. REQ-CSV-007 mantém os gates institucionais
REQ-SEG-002/003 (WEB-033/041), sem os substituir. Testes antigos ou linhas
PLANEJADAS não equivalem a reexecução nesta missão; consultar evidências do backlog.

## Controle de mudança

IDs não são renumerados nem reutilizados. Mudança relevante registra no backlog:
ID e data, motivo/origem, requisito anterior/novo, decisão/ADR, componentes,
testes a revisar, tarefas e dependências impactadas, necessidade e evidência de
aprovação externa. Requisito retirado permanece com motivo e referência de
substituição. Ajustes editoriais não alteram aceite científico.

Ao executar WEB: substituir vínculo PLANEJADO por teste real com caminho/nome,
referenciar evidência canônica no backlog (comando, resultado, data, SHA) e
conferir requisito→teste→aceite. Não copiar resultados nas duas fontes. Se teste
ou contrato mudar, registrar por quê e reavaliar critérios afetados; não reabrir
conclusão histórica sem evidência de regressão ou novo escopo. Novos requisitos
exigem tarefa/critério antes de execução e não concedem crédito retroativo.
