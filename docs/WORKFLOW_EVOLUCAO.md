# Workflow de evolucao do projeto

Este e o roteiro canonico das 12 etapas. A baseline tecnica detalhada permanece
em [BASELINE_ETAPA_1.md](BASELINE_ETAPA_1.md); as antigas “fases” documentam o
historico e nao substituem este workflow.

## Arquitetura-alvo

```text
PsychoPy local -> CSV oficial local -> validacao/importacao controlada
                                      -> PostgreSQL
                                      -> camada de servico/API
                                      -> dashboard Streamlit
```

No desenvolvimento, componentes de servidor passam a usar Docker a partir da
Etapa 3. O experimento PsychoPy continua local e fora do Docker. Streamlit
continua sendo o dashboard. A transicao de SQLite para PostgreSQL deve preservar
rastreabilidade, metricas e dados brutos; SQLite permanece a baseline ate a
etapa que autorizar sua substituicao no fluxo correspondente.

## Decisoes fixadas

- Executar uma etapa por sessao/revisao e nao antecipar a seguinte.
- Preservar o paradigma, formulas, contrato CSV e comportamento fora do escopo.
- Usar somente dados sinteticos em desenvolvimento, testes e documentacao.
- Manter PsychoPy local; Docker/PostgreSQL comecam somente na Etapa 3.
- Manter Streamlit e o comando publico de inicializacao ate decisao explicita.
- Fazer versionamento manual; agentes apenas sugerem uma mensagem de commit.
- Decisoes clinicas, semanticas, arquiteturais ou de seguranca nao resolvidas
  interrompem a etapa.

## Etapas, pesos e aceite resumido

| Etapa | Peso | Objetivo e aceite resumido | Estado |
|---|---:|---|---|
| 1. Baseline reproduzivel | 5% | Fluxo, schema, backup, fixtures e testes registrados; integridade comprovada. | Concluida |
| 2. Modularizar dashboard | 7% | Separar interface, SQLite, transformacoes e componentes; preservar UI, leitura somente leitura, launcher e testes. | Concluida |
| 3. Infraestrutura local | 11% | Introduzir Docker para componentes de servidor e PostgreSQL local, sem incluir PsychoPy; configuracao reproduzivel e dados sinteticos. | Concluida |
| 4. Schema e migracoes PostgreSQL | 8% | Modelar e migrar avaliacoes, metricas e tentativas com restricoes, indices, rollback e rastreabilidade testados. | Nao iniciada |
| 5. Importacao para PostgreSQL | 13% | Validar e importar CSV de forma transacional, idempotente e auditavel, preservando formulas e arquivo bruto. | Nao iniciada |
| 6. Camada de servico/API | 8% | Expor operacoes necessarias por contrato versionado, validacao e erros seguros, sem interpretacao clinica. | Nao iniciada |
| 7. Suporte a multiplos testes | 10% | Generalizar contratos e catalogo sem quebrar Stroop; cada teste deve ter schema, versao e validacao explicitos. | Nao iniciada |
| 8. Upload controlado | 10% | Receber arquivos com limites, validacao, rejeicao segura, idempotencia e rastreabilidade; nenhum dado invalido persiste. | Nao iniciada |
| 9. Autenticacao e autorizacao | 8% | Proteger acesso e operacoes por papeis definidos, sessoes seguras e testes de negacao. | Nao iniciada |
| 10. Integracao Streamlit | 7% | Conectar o dashboard a arquitetura de servidor preservando filtros, visualizacoes, privacidade e comando publico acordado. | Nao iniciada |
| 11. Operacao e seguranca | 6% | Validar backups/restauracao, secrets, logs sem PII, observabilidade, atualizacao e checklist de implantacao. | Nao iniciada |
| 12. Implantacao e aceite | 7% | Implantar na VPS aprovada, validar recuperacao, seguranca e operacao, e concluir documentacao de entrega. | Nao iniciada |
| **Total** | **100%** |  |  |

Os objetivos das etapas 3–12 delimitam sequenciamento, nao autorizam escolhas
detalhadas de tecnologia ou semantica. Cada etapa exige prompt proprio aprovado,
baseado em [prompts/TEMPLATE_ETAPA.md](prompts/TEMPLATE_ETAPA.md).

## Estado atual

- Etapa 1: concluida.
- Etapa 2: concluida.
- Etapa 3: concluida.
- Etapa 4: nao iniciada.
- Progresso global: **23%**.
- Baseline da Etapa 1: **73 testes aprovados**.
- Suite atual apos a Etapa 2: **77 testes aprovados**.
- Suite atual apos a Etapa 3: **83 testes aprovados**.

## Atualizacao do progresso

O progresso e a soma dos pesos das etapas integralmente concluidas. Nao existe
credito parcial. Uma etapa so muda para `Concluida` depois que todos os criterios
do prompt forem comprovados, os testes e `git diff --check` passarem, a
documentacao for atualizada e a revisao confirmar que a etapa seguinte nao foi
iniciada. Se houver falha ou decisao pendente material, mantenha `Nao iniciada`
ou registre `Em andamento`, sem somar seu peso.

Somente este documento deve manter estado e percentual globais. Baselines e
registros historicos preservam os resultados da data em que foram produzidos.

## Riscos carregados entre etapas

- Dados locais potencialmente identificaveis exigem minimizacao, controle de
  acesso e proibicao de logs, fixtures e commits.
- O schema SQLite atual depende do importador para varios dominios e unicidades.
- Datas estao em texto e `source_file` nao possui hash de conteudo.
- O importador aceita `practice`, enquanto o CSV oficial atual contem `main`.
- A migracao deve provar paridade de metricas, contagens e rastreabilidade.
- Upload, API e autenticacao ampliam a superficie de ataque e exigem decisoes
  explicitas antes da implementacao.
- O dashboard pode exibir dados pessoais locais; exports e screenshots continuam
  sendo risco operacional.

## Condicao para contratar a VPS

A contratacao nao deve ocorrer antes da conclusao e revisao da Etapa 11. Exige:

- arquitetura local integrada e aprovada com dados exclusivamente sinteticos;
- migracoes, importacao, API, upload, autenticacao e dashboard validados;
- plano comprovado de backup e restauracao;
- gestao de secrets, TLS, controle de acesso, logs sem dados identificaveis,
  atualizacao e rollback documentados;
- estimativa de recursos/custos e aprovacao explicita do responsavel.

A compra, configuracao ou acesso a uma VPS e sempre uma acao externa separada e
requer autorizacao explicita; nao e implicada pela conclusao tecnica das etapas.
