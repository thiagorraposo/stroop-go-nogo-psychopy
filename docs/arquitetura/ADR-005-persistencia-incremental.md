# ADR-005 — Participação por projeto e persistência incremental

Data: 2026-11-05. Decisão técnica validada pelo responsável. Receptor backend
implementado em M2; worker e integração temporal permanecem em M3/M4.
Após apresentação da proposta versionada em `270377b`, o responsável respondeu
“valido”, aprovando a estratégia, os limites de perda e a matriz de invalidação.
Essa resposta satisfaz a exigência de validação documental anterior ao código;
não constitui evidência dos ensaios técnicos/temporais ainda planejados. Estado, bloqueios e aceite somente no
[backlog](../Projeto%20Stroop%20Test.md), DEC-01/02 e WEB-005.

## Contexto e decisão de produto

Um participante pseudonimizado pertence a um projeto e pode ter várias visitas
e avaliações. Convite prepara uma avaliação, sem agenda autônoma ou cadastro
central longitudinal. UUIDs estáveis e vínculos explícitos permitem evolução
aditiva futura, sem correlacionar pessoas por pseudônimo entre projetos.
O [modelo](../dados/MODELO_DE_DADOS.md) é a fonte das entidades e invariantes.

O responsável rejeitou preservar todas as tentativas apenas em RAM até o final.
Dados recebidos devem sobreviver à interrupção, identificados como incompletos
ou inválidos. Isso não autoriza retomar bloco nem produzir resultado parcial.
D2 e os gates aprovados permanecem no [protocolo](../experimento/PROTOCOLO_WEB.md).

## Estratégia validada em 2026-11-05

1. Criar a sessão no resgate, antes da prática, com vínculos e protocolo fixados.
   Antes do principal, confirmar conectividade, autorização, prazo e prontidão
   do receptor/worker. Sem confirmação, não iniciar. Não alongar contagem ou
   trecho experimental para esperar rede; aguardar em tela de preparação.
2. Preparar um Dedicated Worker da mesma origem antes da contagem. Ao encerrar
   cada tentativa principal, depois de registrar o fim real, entregar uma cópia
   pequena e imutável ao worker. A transição experimental seguinte mantém seu
   agendamento original: nenhuma espera de HTTP, hash ou serialização JSON no
   caminho de apresentação/teclado. Tentativa ainda em andamento não é declarada
   completa nem recebe timestamps fabricados.
3. Worker serializa e envia fora da thread do motor, usando cookie HttpOnly e
   CSRF somente em RAM. Um envio em voo; agrupar as tentativas completas pendentes
   em prefixo contíguo. Fila limitada às 16 posições do bloco, sem descarte de
   observações. Retry do mesmo conteúdo em 1, 2, 4 e depois 8 s, respeitando
   Retry-After e prazo absoluto. 401/403/410 encerram envio; 409 divergente exige
   falha de integridade, sem substituição. A perda de transporte não autoriza
   pausar ou estender o bloco; se os gates não forem violados, conservar fila
   pendente e tentar enviar ao terminar, dentro da validade da sessão.
4. Servidor confirma somente depois do commit, com prefixo contíguo e hash;
   cliente mantém dados sem confirmação e consulta o recibo em erro incerto.
   Checkpoint só confirma armazenamento parcial, nunca sucesso experimental.
   Recepção, replay, expiração, conclusão e concorrência têm sua fonte única no
   [contrato HTTP alvo validado](../desenvolvimento/CONTRATO_API_WEB.md).
5. Ao terminar integralmente, enviar complete e esperar recibo oficial em tela
   de envio, fora do trecho cronometrado. Só então apresentar resultado recebido.
   Interrupção comprometendo o protocolo encerra a execução; tentar entregar
   observações completas pendentes e aviso, sem depender do evento de fechamento.
   Nova sessão começa com prática. Nunca reconstruir motor a partir do prefixo.
6. Persistir observações separadas de resultados oficiais; sessão expirada sem
   conclusão é incompleta mesmo se nenhum aviso chegar. Canal profissional
   autorizado distingue ausência de observação, prefixo recebido e invalidação,
   sem incluir parciais nas métricas/CSV oficiais. Dados brutos já recebidos
   permanecem preservados conforme política de retenção institucional aplicável.

A escolha de worker é inferência de engenharia: a [documentação primária MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)
explica execução em outra thread, mensagens copiadas e acesso a fetch. Isso
reduz trabalho na thread do motor, mas não prova ausência de impacto temporal.
Não usar Service Worker, armazenamento persistente JS, cache, arquivo local ou
beacon de fechamento como garantia. Se o worker não puder operar, bloquear início;
não degradar silenciosamente para final-only.

## Limitações e riscos residuais

- Copiar mensagens, callbacks, coleta de lixo, CPU, rede e agendamento do SO
  podem afetar quadros mesmo com worker. A fronteira entre tentativas não é
  intervalo livre: a próxima fixação começa imediatamente. Não acrescentar
  pausas nem tratar os 950 ms como autorização para alongar o protocolo.
- Queda pode perder a tentativa em curso e todo sufixo sem commit confirmado.
  Com rede saudável, a unidade pretendida é uma tentativa completa; não existe
  limite garantido de uma tentativa de perda. Offline prolongado ou falha antes
  do primeiro commit pode ainda perder todas as tentativas. A estratégia reduz
  exposição, não promete perda zero nem funcionamento offline.
- Resposta perdida pode ocultar commit existente; consulta/replay confirma sem
  duplicar. Recibo não substitui backup/replicação/restauração. Falha catastrófica
  do servidor ou configuração sem durabilidade pode perder dados confirmados;
  prontidão operacional depende dos ensaios próprios, sem tocar produção aqui.
- Eventos de fechamento/energia podem não entregar abort; expiração registra
  incompletude sem atribuir causa falsa. Servidor valida coerência declarada,
  não ausência física de interrupção, fraude ou latência real do equipamento.
- Falha de rede isolada não é prova de violação metodológica. Não interromper
  um bloco íntegro só por falta de ACK; se houver violação D2/D5, invalidar.
- Preservação parcial amplia superfície de acesso/retenção: mesmos projetos,
  papéis restritos, minimização, no-store, logs sem conteúdo e DEC-03 continuam
  obrigatórios. Nenhuma tabela longitudinal global ou dado nominal é necessário.

## Validação anterior à implementação

A resposta “valido” do responsável em 2026-11-05 aprovou a estratégia, a janela
residual de perda e a matriz de invalidação do protocolo apresentadas em
`270377b`. Revisão e aprovação documentais não são ensaio do worker ou do banco.
A revisão
técnica deve fechar schema aditivo, contratos e tratamento de invalidação tardia,
sem delegar ao desenvolvedor escolhas científicas. Se houver efeito metodológico
novo ou pausa proposta, obter decisão e versionamento antes de implementar.
Preservar versões atuais nesta entrega documental; futura versão de app registra
mudança de transporte, sem alterar versão experimental silenciosamente.

Depois da aprovação documental, e antes de aceitar o comportamento implementado,
exigir os ensaios sintéticos planejados abaixo nas tarefas do backlog:

| Cenário | Evidência que a implementação deverá produzir |
|---|---|
| Participante/visita | Duas visitas e várias avaliações na mesma visita; concorrência sem duplicar vínculo; mesmo pseudônimo em dois projetos isolado; FK rejeita cruzamento |
| Convite | UUIDs distintos, código de uso único, resgate concorrente, revogação, prazo e negações de acesso/CSRF; reemissão não altera sessão antiga |
| Recepção | Perda antes do primeiro ACK, prefixo confirmado e queda no meio; crash pré/pós-commit; consulta após resposta perdida; preservação de prefixo em rollback final |
| Idempotência | Lotes iguais/sobrepostos, lacuna, conteúdo divergente, concorrência e corrida checkpoint/abort/complete; zero duplicação ou sobrescrita |
| Incompletude | Fechamento sem aviso, expiração com 0/N/16 observações, revogação, aborto e aviso tardio; nenhuma promoção automática nem métrica oficial parcial |
| Protocolo | Eventos D2, falhas D5 e prática interrompida; nova sessão com prática completa e sem retomada; falha só de transporte distinguida de falha metodológica |
| Timing e carga | Mesmos gates D5 com transporte ativo, ACK lento/perdido, retries e servidor indisponível; medir callbacks/cópia e quadros nos browsers de referência; sem presumir latência física |
| Segurança | PG real descartável, reader sem DML/writer sem owner, isolamento por projeto em cada operação; sem dados/segredos em armazenamento JS/log/cache |

Na entrega documental original nenhum desses ensaios havia sido executado.
Os ensaios atuais de receptor/banco estão registrados em EV-M2 no backlog. M2 valida
contratos e banco; M3 valida impacto temporal; M4 integra fluxo/motor/UX; M5
revalida exclusão de inválidos nas consultas. Aprovação documental não encerra
esses gates nem autoriza produção.
