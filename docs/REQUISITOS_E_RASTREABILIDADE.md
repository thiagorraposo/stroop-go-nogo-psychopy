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

- Descrição: Identificar profissional por Google OIDC iss+sub e cadastro ativo.
- Justificativa: Preserva identidade verificada e evita autorização por e-mail.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Callback válido cria sessão; assinatura/aud/iss/nonce/state inválidos, expirados ou reutilizados não criam sessão.
- Dependências: WEB-021 e pré-requisitos registrados no backlog.
- Restrições conhecidas: ACESSO_WEB / D1–D6 não alterados; login real em ambiente autorizado.
- Origem: seguranca/AUTENTICACAO_E_PERMISSOES.md e api/auth.py.

### REQ-AUT-002

- Descrição: Autorizar perfis e projetos a cada leitura, escrita e exportação.
- Justificativa: Mantém isolamento de pesquisa e revogação efetiva.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Consulta não escreve; importacao prepara convite; admin sem vínculo não consulta resultados; bloqueio/revogação retiram acesso.
- Dependências: WEB-022 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem novo papel implícito de avaliador.
- Origem: seguranca/AUTENTICACAO_E_PERMISSOES.md e api/auth.py.

### REQ-AUT-003

- Descrição: Separar sessões profissional e participante com cookies seguros e CSRF.
- Justificativa: Evita confusão de credenciais e falsificação de escrita.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Secure/HttpOnly/SameSite e origem/CSRF testados; logout/expiração/replay encerram acesso apropriado.
- Dependências: WEB-023 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem tokens Google ou credenciais em armazenamento do cliente.
- Origem: desenvolvimento/CONTRATO_API_WEB.md e routers api/.

## B. Gestão de participantes

### REQ-PAR-001

- Descrição: Identificar participação por pseudônimo e visita no projeto autorizado.
- Justificativa: Atende identificação sem transmitir nome/iniciais.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Convite/resgate conserva código/visita e rejeita campos nominais; isolamento entre projetos comprovado.
- Dependências: WEB-013 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Pseudônimo não é anonimização nem credencial.
- Origem: seguranca/ACESSO_WEB.md e controles existentes.

### REQ-PAR-002

- Descrição: Participante pseudonimizado por projeto admite múltiplas visitas e avaliações com vínculos estáveis, sem cadastro longitudinal central.
- Justificativa: Evita confundir metadados de sessão com cadastro global.
- Prioridade: P0. Estado da especificação: **Confirmado** (DEC-01, 2026-11-05).
- Aceite verificável: UUIDs e vínculos conforme modelo canônico; várias visitas e avaliações por visita sem duplicação/cruzamento de projetos; evolução longitudinal aditiva sem reescrever resultados. Diretriz aprovada; comportamento ainda requer implementação/ensaios.
- Dependências: WEB-005 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem nomes/identificador pessoal global, agenda separada ou correlação automática; schema novo só após aprovação da estratégia definitiva e tarefa autorizada.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

### REQ-PAR-003

- Descrição: Não impor filtros demográficos nem coletar idade/sexo sem requisito aprovado.
- Justificativa: Preserva finalidade e elegibilidade sob responsabilidade científica.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Formulários/payloads não coletam idade/sexo e não calculam norma; textos de elegibilidade só os aprovados.
- Dependências: WEB-014 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Responsável define elegibilidade/consentimento DEC-03.
- Origem: experimento/DECISOES_DO_EXPERIMENTO.md e PROTOCOLO_WEB.md (D1–D6).

## C. Gestão de avaliações

### REQ-AVA-001

- Descrição: Permitir que avaliador vinculado prepare avaliação e emita/revogue convite.
- Justificativa: Materializa início do fluxo principal.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Criação via React retorna convite uma vez; resgate único; revogação/expiração impedem execução sem apagar resultado anterior.
- Dependências: WEB-013 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Projeto synthetic até liberação específica DEC-05.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

### REQ-AVA-002

- Descrição: Preparar avaliação por convite único vinculado a participante/visita/projeto, sem módulo separado de agendamento.
- Justificativa: O código atual não representa agendamento independente.
- Prioridade: P1. Estado da especificação: **Confirmado** (DEC-01, 2026-11-05).
- Aceite verificável: Convite único, prazo, acesso e resgate único; reemissão cria sessão distinta e mantém vínculos/execuções anteriores; nenhuma unicidade artificial impede várias avaliações na mesma visita.
- Dependências: WEB-005 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não introduzir agendamento nem nova entidade por inferência.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md e decisão do responsável de 2026-11-05.

### REQ-AVA-003

- Descrição: Distinguir sessão iniciada, interrompida, enviada e avaliação recebida.
- Justificativa: Impede declarar sucesso sem persistência confirmada.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: UI só diz recebido após recibo; reload de running invalida; sessão abortada não aparece como resultado oficial.
- Dependências: WEB-015 e pré-requisitos registrados no backlog.
- Restrições conhecidas: D2 proíbe retomar principal interrompido.
- Origem: experimento/DECISOES_DO_EXPERIMENTO.md e PROTOCOLO_WEB.md (D1–D6).
- Impacto CHG-003: REQ-UX-010/WEB-015 refinam estados visuais sem alterar transições/recibos ou permitir retomada.

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

### REQ-REL-002

- Descrição: Exibir detalhe descritivo com métricas, tentativas e proveniência.
- Justificativa: Permite análise e auditoria de cada avaliação.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Detalhe mostra unidades, quatro respostas e metadados técnicos sem nomes/iniciais; no-hit correto e acessibilidade básica verificados.
- Dependências: WEB-019 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Sem diagnóstico, norma ou interpretação clínica.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.
- Impacto CHG-003: REQ-UX-006/011 e WEB-019 mantêm precisão no painel profissional e revisam somente UI compartilhada/acessibilidade.

### REQ-REL-003

- Descrição: Administrar contas, projetos e vínculos no React sem apagar coletas.
- Justificativa: Retira dependência operacional de UI legada.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: CRUD permitido testado, negação por papel, último administrador protegido inclusive sob concorrência, sem exclusão de dados.
- Dependências: WEB-018 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Administração não herda escopo de resultados.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md.

## H. Importação e exportação

### REQ-CSV-001

- Descrição: Manter CSV de 21 campos como intercâmbio complementar compatível.
- Justificativa: Preserva análise e histórico sem fazer CSV banco operacional.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Roundtrip sintético conserva colunas, unidades, classificação e metadados admitidos; prática não vira resultado oficial.
- Dependências: WEB-026 e pré-requisitos registrados no backlog.
- Restrições conhecidas: CSV local nominal não deve ser transmitido à WEB.
- Origem: experimento/CSV_UNIFICADO.md.

### REQ-CSV-002

- Descrição: Minimizar importação no navegador e validar novamente no servidor.
- Justificativa: Protege dados nominais e evita confiar apenas na UI.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Cópia RAM usa NAO_COLETADO/iniciais vazias; API rejeita nominal, excesso de tamanho/linhas e CSV inválido; UUID recupera estado sem duplicar.
- Dependências: WEB-025 e pré-requisitos registrados no backlog.
- Restrições conhecidas: 5 MiB/10000 registros dedicados; original local inalterado.
- Origem: desenvolvimento/CONTRATO_API_WEB.md e routers api/.

### REQ-CSV-003

- Descrição: Exportar detalhe e conjunto filtrado com reautorização e proteção de células.
- Justificativa: Mantém portabilidade sem vazar escopo ou fórmulas de planilha.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: CSV agregado corresponde à consulta filtrada; acesso revogado nega download; conteúdo potencialmente executável é neutralizado conforme contrato.
- Dependências: WEB-020 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Exportações explícitas e não versionadas.
- Origem: desenvolvimento/CONTRATO_API_WEB.md e routers api/.
- Impacto CHG-003: REQ-UX-006/WEB-020 exigem paridade das exportações após alteração de apresentação, sem remover colunas/métricas.

## I. Administração e auditoria

### REQ-AUD-001

- Descrição: Registrar eventos técnicos e alterações de acesso sem payload pessoal.
- Justificativa: Rastreia operação sem ampliar exposição.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Eventos de login/acesso/gestão/importação têm ação/resultado/ID e não contêm cookies, código de convite, nomes ou corpo experimental.
- Dependências: WEB-024 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não imprimir dados em logs para depurar.
- Origem: seguranca/ACESSO_WEB.md e controles existentes.

### REQ-AUD-002

- Descrição: Preservar histórico por mapa explícito de autorização, sem vínculo por nome.
- Justificativa: Evita apropriação de dados criando projeto de nome coincidente.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Colisão de código sem mapa nega; mapa autorizado permite; desativação retira acesso; nenhuma coleta é reescrita.
- Dependências: WEB-027 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Configurar mapa real exige autorização de dados.
- Origem: arquitetura/ADR-003-escopo-legado-web.md.

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

### REQ-SEG-002

- Descrição: Aprovar finalidade, informação/consentimento aplicáveis, retenção e tratamento institucional.
- Justificativa: Requisito para uso real sob responsabilidade do projeto.
- Prioridade: P0. Estado da especificação: **Pendente de decisão**.
- Aceite verificável: DEC-03 tem responsáveis, política aplicável, procedimentos de acesso/exclusão/incident response e aprovação institucional necessária registrada.
- Dependências: WEB-033 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Não inventar base legal, prazo ou autorização ética.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

### REQ-SEG-003

- Descrição: Separar ensaio sintético de coleta real e impedir liberação implícita.
- Justificativa: Evita converter validação técnica em autorização de pesquisa.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Projetos continuam synthetic até DEC-05 e WEB-040; mudança de modo exige decisão específica, teste de barreira e trilha.
- Dependências: WEB-041 (após WEB-036 e DEC-05) e pré-requisitos registrados no backlog.
- Restrições conhecidas: Disponibilidade de VPS/domínio não autoriza coleta/deploy.
- Origem: Auditoria de código em AUDITORIA_REPLANEJAMENTO.md.

## K. Infraestrutura e implantação

### REQ-INF-001

- Descrição: Operar PostgreSQL atrás da API com migrations versionadas e papéis mínimos.
- Justificativa: Protege histórico e reduz alcance do runtime.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Banco descartável aplica catálogo imutável, writer/reader e owner separados; leituras realmente read-only e schema compatível com rollback.
- Dependências: WEB-007 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Nenhuma migration nesta fase nem dados reais sem aprovação.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

### REQ-INF-002

- Descrição: Empacotar em Docker Compose/Nginx/HTTPS com somente proxy exposto.
- Justificativa: Reutiliza VPS e isola serviços.
- Prioridade: P1. Estado da especificação: **Confirmado**.
- Aceite verificável: Build reproduzível, saúde, TLS, headers, limites e rejeição de fontes/secrets aprovados em pilha exclusiva; sem deploy automático.
- Dependências: WEB-029 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Infraestrutura operacional inalterada nesta execução.
- Origem: Missão de replanejamento do proprietário em 2026-11-04.

### REQ-INF-003

- Descrição: Comprovar backup, réplica externa, restauração e rollback antes da publicação.
- Justificativa: Reduz perda/interrupção e testa recuperabilidade.
- Prioridade: P0. Estado da especificação: **Confirmado**.
- Aceite verificável: Restauração isolada confere dados/schema e retorno compatível; réplica/agenda/alerta ensaiados; comparar RPO 24h/RTO 4h com medidas reais.
- Dependências: WEB-031 e pré-requisitos registrados no backlog.
- Restrições conhecidas: Objetivos históricos ADR-002, não garantias; produção requer autorização.
- Origem: arquitetura/ADR-002-hospedagem-vps.md.

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

## Matriz de rastreabilidade

Cada linha é o vínculo principal; relações complementares aparecem nas fichas.
Testes com caminho são existentes; resultados atuais só estão comprovados quando
a linha aponta para uma evidência datada no backlog. Referências PLANEJADAS são
verificações ainda sem resultado de aceite; não inventam testes.
Evidência e aceite são consultados por WEB no backlog, sem duplicar estado.
Vínculos sem evidência datada permanecem planejados, mesmo quando o componente
já existe ou participa da regressão geral. WEB-000 é exclusivamente documental.

| Requisito | Decisão | Marco | Tarefa | Componente | Teste/verificação | Evidência → aceite |
|---|---|---|---|---|---|---|
| REQ-AUT-001 | ADR-004 | M6 | WEB-021 | `api/auth.py, api/google_oidc.py` | `tests/test_web_oidc_callback.py` | PLANEJADA; consultar WEB-021 no backlog |
| REQ-AUT-002 | ADR-004 | M6 | WEB-022 | `stroop/domain/auth.py, stroop/persistence/web_sessions.py` | `tests/test_web_auth.py` | ACEITA em EV-M6-022/023 no backlog; PG/API e HTTPS, OIDC externo separado |
| REQ-AUT-003 | ADR-004 | M6 | WEB-023 | `api/auth.py, api/sessions.py` | `tests/test_web_sessions.py` | ACEITA em EV-M6-022/023 no backlog; dez casos HTTPS e regressão PG |
| REQ-PAR-001 | ADR-004 | M4 | WEB-013 | `api/sessions.py, web/src/participant/` | `tests/test_web_sessions.py` | PLANEJADA; consultar WEB-013 no backlog |
| REQ-PAR-002 | ADR-004/005 | M2 | WEB-005 | `Modelo lógico e formulário de sessão` | `Revisão documental DEC-01 em 2026-11-05; ensaios PLANEJADOS` | Aceite documental em EV-M2-005-R2; receptor/banco em EV-M2, worker/timing da fixture em EV-M3-011; integração de produto permanece M4 |
| REQ-PAR-003 | ADR-004 | M4 | WEB-014 | `web/src/components/, api/models.py` | `tests/test_web_security_review.py` | PLANEJADA; consultar WEB-014 no backlog |
| REQ-AVA-001 | ADR-004 | M4 | WEB-013 | `web/src/App.tsx, api/sessions.py` | `tests/test_web_sessions.py` | PLANEJADA; consultar WEB-013 no backlog |
| REQ-AVA-002 | ADR-004/005 | M2 | WEB-005 | `Contrato HTTP e modelo lógico` | `Revisão documental DEC-01 em 2026-11-05; ensaios PLANEJADOS` | Aceite documental em EV-M2-005-R2; receptor/banco em EV-M2, worker/timing da fixture em EV-M3-011; integração de produto permanece M4 |
| REQ-AVA-003 | ADR-004 | M4 | WEB-015 | `web/src/participant/ParticipantRun.ts, api/results.py` | `tests/test_web_results.py` | PLANEJADA; consultar WEB-015 no backlog |
| REQ-EXP-001 | ADR-004 | M3 | WEB-009 | `condicoes/, web/src/experiment/` | `tests/test_fase3_condicoes_tempos.py`, `web/src/experiment/environment.test.ts`, `practice.test.ts`, `main.test.ts` | EXECUTADA em WEB-009; EV-M3-009/010 no backlog |
| REQ-EXP-002 | ADR-004 | M3 | WEB-010 | `web/src/experiment/main-engine.ts, ExperimentHost.tsx` | `web/src/experiment/main.test.ts`, `practice.test.ts`, `ExperimentHost.test.tsx`, `web/e2e/main.spec.ts`, `practice.spec.ts` | Evidências e falhas em EV-M3-009/010; consultar aceite WEB-010 no backlog |
| REQ-EXP-003 | ADR-004 | M3 | WEB-011 | `web/src/experiment/environment.ts, web/pilots/` | `web/pilots/web011.spec.ts, web/src/transport/checkpoint-queue.test.ts, web/src/experiment/main.test.ts` | ENGENHARIA TESTADA; campanha WEB-011 aceita em EV-M3-011; suporte em revisão EV-M3-012, sem latência física ou integração M4 presumida |
| REQ-INT-001 | ADR-004 | M2 | WEB-006 | `stroop/domain/web_results.py, api/results.py` | `tests/test_web_results.py, tests/test_web_sessions.py, tests/test_web_checkpoints.py` | EXECUTADA em WEB-006; EV-M2 no backlog |
| REQ-INT-002 | ADR-004 | M2 | WEB-007 | `stroop/persistence/web_sessions.py, web_checkpoints.py` | `tests/test_web_checkpoints.py, tests/test_web_sessions.py, tests/test_web_database_provision.py, tests/test_postgres_migrations.py` | EXECUTADA em WEB-007; EV-M2-007/008 no backlog |
| REQ-INT-003 | ADR-004/005 | M2 | WEB-005 | `ParticipantRun.ts e modelo lógico` | `ADR-005 e matriz de falhas validados pelo responsável em 2026-11-05` | Aceite documental em EV-M2-005-R2; receptor/banco em EV-M2, worker/timing da fixture em EV-M3-011; integração de produto permanece M4 |
| REQ-MET-001 | ADR-004 | M2 | WEB-008 | `stroop/domain/stroop.py, web_results.py` | `tests/test_nucleo_compartilhado.py, tests/test_web_export.py, tests/test_web_checkpoints.py` | EXECUTADA em WEB-008; EV-M2-007/008 no backlog |
| REQ-MET-002 | ADR-004 | M2 | WEB-008 | `stroop/domain/stroop.py, web/src/dashboard/analysis.ts` | `tests/test_web_results.py, web/src/dashboard/analysis.test.ts` | EXECUTADA em WEB-008; EV-M2-007/008 no backlog |
| REQ-MET-003 | ADR-004 | M5 | WEB-019 | `web_assessments, api/assessments.py` | `tests/test_web_assessments.py` | PLANEJADA; consultar WEB-019 no backlog |
| REQ-REL-001 | ADR-004 | M5 | WEB-017 | `web/src/components/, api/assessments.py` | `tests/test_web_assessments.py` | PLANEJADA; consultar WEB-017 no backlog |
| REQ-REL-002 | ADR-004 | M5 | WEB-019 | `web/src/components/, web/src/dashboard/` | `tests/test_web_results.py` | PLANEJADA; consultar WEB-019 no backlog |
| REQ-REL-003 | ADR-004 | M5 | WEB-018 | `api/administration.py, web/src/api/administration.ts` | `tests/test_web_administration_provisioned.py` | PLANEJADA; consultar WEB-018 no backlog |
| REQ-CSV-001 | ADR-004 | M7 | WEB-026 | `stroop/ingestion/stroop_csv.py, api/assessments.py` | `tests/test_csv_unificado.py` | PLANEJADA; consultar WEB-026 no backlog |
| REQ-CSV-002 | ADR-004 | M7 | WEB-025 | `web/src/imports/minimize.ts, api/imports.py` | `tests/test_web_imports.py` | PLANEJADA; consultar WEB-025 no backlog |
| REQ-CSV-003 | ADR-004 | M5 | WEB-020 | `api/assessments.py, web/src/api/aggregate.ts` | `tests/test_web_aggregate_export.py` | PLANEJADA; consultar WEB-020 no backlog |
| REQ-AUD-001 | ADR-004 | M6 | WEB-024 | `stroop/persistence/auth.py, api/transport.py` | `tests/test_web_security_review.py` | PLANEJADA; consultar WEB-024 no backlog |
| REQ-AUD-002 | ADR-003 + ADR-004 | M7 | WEB-027 | `scripts/migrations/0007_web_legacy_project_links.sql` | `tests/test_web_assessments.py` | PLANEJADA; consultar WEB-027 no backlog |
| REQ-AUD-003 | ADR-004 | M0 | WEB-000 | `docs/Projeto Stroop Test.md e REQUISITOS_E_RASTREABILIDADE.md` | `Validação documental reproduzível no workflow (EV-M0)` | EV-M0 real; aceite documental em WEB-000 no backlog |
| REQ-SEG-001 | ADR-004 | M6 | WEB-024 | `api/transport.py, web/deploy/` | `tests/test_web_security_review.py` | PLANEJADA; consultar WEB-024 no backlog |
| REQ-SEG-002 | ADR-004 | M9 | WEB-033 | `docs/seguranca/` | `PLANEJADO: revisão do responsável DEC-03` | PLANEJADA; consultar WEB-033 no backlog |
| REQ-SEG-003 | ADR-004 | M10 | WEB-041 | `stroop/persistence/web_sessions.py, política de operação` | `PLANEJADOS: testes research em WEB-041` | PLANEJADA; consultar WEB-041 no backlog |
| REQ-INF-001 | ADR-002 + ADR-004 | M2 | WEB-007 | `scripts/migrations/, provision_web_database.py` | `tests/test_web_database_provision.py, tests/test_postgres_migrations.py` | Aceite em EV-M2-007/008; consultar WEB-007 no backlog |
| REQ-INF-002 | ADR-002 + ADR-004 | M8 | WEB-029 | `compose.web.yaml, Dockerfile.api, Dockerfile.web` | `tests/test_web_proxy_config.py` | ACEITA em EV-M8-029/031 no backlog; build/Compose HTTPS sintético real |
| REQ-INF-003 | ADR-002 + ADR-004 | M8 | WEB-031 | `scripts/backup_postgres.py, deploy/` | `tests/test_web_backup_replication.py` | PLANEJADA; consultar WEB-031 no backlog |
| REQ-EXT-001 | ADR-004 | M1 | WEB-003 | `stroop/, api/, web/` | `tests/test_nucleo_compartilhado.py, tests/test_casos_uso_importacao.py, tests/test_multiplos_instrumentos.py` | EV-M1 real em WEB-003; fronteiras/contratos revalidados em 2026-11-04 |
| REQ-EXT-002 | ADR-004 | M8 | WEB-030 | `scripts/verify_web_ci.py, .github/workflows/web.yml` | `tests/test_verify_web_ci.py` | PLANEJADA; consultar WEB-030 no backlog |
| REQ-EXT-003 | ADR-004 | M1 | WEB-004 | `AGENTS.md, docs/WORKFLOW_CODEX_CLI.md` | `Receita BASELINE_LOCAL.md; scripts/verify_web_ci.py integration; ensaio de retomada WEB-004` | EV-M1 real em WEB-004; percurso local/retomada revalidados em 2026-11-04 |
| REQ-UX-001 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-042 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-002 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-042 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-003 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-043 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts, web/src/experiment/protocol.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-004 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-043 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-005 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-043 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-006 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-044 | `web/src/experiment/summary.ts, stroop/domain/stroop.py, web/src/participant/ParticipantRun.ts` | `web/src/experiment/summary.test.ts, tests/test_nucleo_compartilhado.py e tests/test_web_export.py; PLANEJADO: integração WEB-016/019/020` | Regressão de métricas/CSV executada em EV-M3-044; integração real WEB-016/019/020 ainda PLANEJADA |
| REQ-UX-007 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M3 | WEB-042 | `web/src/experiment/main-engine.ts, web/src/experiment/practice-engine.ts, web/src/styles.css` | `web/src/experiment/main.test.ts, practice.test.ts, presentation.test.ts; web/e2e/presentation.spec.ts; main.spec.ts/practice.spec.ts` | IMPLEMENTADO/TESTADO; aceite do escopo WEB-042/043 em EV-M3-042/043; regressão consolidada WEB-044 em EV-M3-044; validações WEB-011/034 continuam próprias |
| REQ-UX-008 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M4 | WEB-014 | `web/src/App.tsx, web/src/experiment/practice-engine.ts, docs/experimento/COPY_DAS_TELAS.md, web/src/components/PracticePreparation.tsx, web/src/components/ParticipantFlow.tsx` | `PLANEJADO: practice.test.ts, web/e2e/practice.spec.ts e integração real` | PLANEJADO; evidência/aceite futuro em WEB-014; sem SHA de implementação |
| REQ-UX-009 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M4 | WEB-014 | `web/src/App.tsx, web/src/experiment/ExperimentHost.tsx, web/src/participant/ParticipantRun.ts, web/src/components/PracticePreparation.tsx, web/src/components/ParticipantFlow.tsx` | `PLANEJADO: ExperimentHost.test.tsx, web/e2e/practice.spec.ts e integração real` | PLANEJADO; evidência/aceite futuro em WEB-014; sem SHA de implementação |
| REQ-UX-010 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M4 | WEB-015 | `web/src/participant/ParticipantRun.ts, web/src/components/ResultSummary.tsx, api/results.py` | `PLANEJADO: ParticipantRun.test.ts, ResultSummary.test.tsx e web/e2e/integrated/` | PLANEJADO; evidência/aceite futuro em WEB-015; sem SHA de implementação |
| REQ-UX-011 | ADR-004/005; CHG-003; D3/D4 revisadas pelo proprietário | M5 | WEB-019 | `web/src/styles.css, web/src/App.tsx, web/src/components/, web/src/dashboard/` | `PLANEJADO: componentes Vitest, teclado/árvore acessível e E2E M5; cobertura experimental WEB-044` | Cobertura experimental M3 conferida em EV-M3-044; restante e aceite M5 WEB-019 PLANEJADOS |

Estados de evidência UX: **PLANEJADO** (critério sem execução), **IMPLEMENTADO**
(código disponível), **TESTADO** (comandos/resultados/SHA registrados), **ACEITO**
(todos os critérios conferidos na ficha WEB). Esses rótulos não substituem os
estados canônicos das tarefas nem dão crédito parcial. Evidência e aceite são
referências à ficha do backlog; a matriz não mantém um segundo painel.

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
