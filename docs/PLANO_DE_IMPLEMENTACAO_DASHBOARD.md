# Plano de implementacao da camada de dados e dashboard

Data: 2026-07-06.

Este plano descreve fases futuras. Nenhuma fase e implementada nesta etapa.

## Fase 1 - Formulario da sessao no PsychoPy

Status: implementada tecnicamente no `.psyexp`; considerar concluida somente apos aprovacao do checklist manual em modo Pilot descrito em `docs/FORMULARIO_DE_SESSAO.md`.

Escopo:

- adicionar campos `project`, `participant_id`, `participant_name`, `initials`, `visit` e `evaluator`;
- gerar `assessment_date` automaticamente com data e hora local;
- garantir que metadados aparecam no CSV unificado futuro;
- nao alterar regras do Stroop;
- validar preenchimento de campos obrigatorios.

Arquivos provaveis:

- `stroop_go_nogo_ptbr.psyexp`
- `docs/DECISOES_DO_EXPERIMENTO.md`
- `docs/REGISTRO_DE_ALTERACOES.md`

Riscos:

- inserir campos que exponham dados pessoais desnecessarios;
- depender de data digitada manualmente;
- quebrar nomes de variaveis exportadas.

Criterios de aceite:

- campos obrigatorios nao podem ficar vazios;
- `assessment_date` e gerada pelo sistema;
- `participant_name` e local, com trim e validacao de tamanho;
- `initials` permanece opcional;
- nenhuma regra do paradigma e alterada.

Testes necessarios:

- execucao Pilot com campos validos;
- tentativa de execucao com campos obrigatorios vazios;
- revisao do CSV local gerado em `data/`.

Commit sugerido:

`feat: adiciona metadados da sessao ao experimento`

## Fase 2 - CSV unificado e resumo tecnico

Status: implementada tecnicamente; considerar concluida somente apos aprovacao do checklist manual em modo Pilot descrito em `docs/CSV_UNIFICADO.md` e no registro da implementacao.

Escopo:

- garantir apenas um CSV por execucao;
- incluir pratica e principal via coluna `block`;
- garantir todas as colunas de tentativa;
- calcular metricas sem dados clinicos;
- validar com execucoes ficticias.

Arquivos provaveis:

- `stroop_go_nogo_ptbr.psyexp`
- `scripts/analisar_stroop.py`
- `tests/test_csv_unificado.py`
- `docs/CSV_UNIFICADO.md`
- `docs/REGISTRO_DE_ALTERACOES.md`

Riscos:

- duplicar linhas por tentativa;
- perder dados do bloco principal;
- alterar tempos ou classificacao sem intencao.

Criterios de aceite:

- um CSV bruto unificado por execucao;
- colunas finais presentes;
- `block` usa `main` nas execucoes oficiais atuais;
- metricas sao descritivas e reproduziveis.

Testes necessarios:

- Pilot com respostas de todos os tipos;
- validacao estatica do CSV;
- comparacao manual de classificacoes.

Commit sugerido:

`feat: consolida exportacao unificada do experimento`

## Fase 3 - Script de validacao e importacao

Status: pendente.

Escopo:

- criar script Python em `scripts/`;
- validar CSV antes de importar;
- impedir duplicidade de importacao;
- gerar banco SQLite local;
- importar `assessments`, `assessment_metrics` e `trial_results`;
- registrar erros sem alterar o CSV original.

Arquivos provaveis:

- `scripts/importar_stroop.py`
- `scripts/README.md`
- `scripts/AGENTS.md`
- `docs/MODELO_DE_DADOS.md`
- `docs/REGISTRO_DE_ALTERACOES.md`
- `.gitignore`

Riscos:

- modificar CSV bruto;
- sobrescrever banco existente sem confirmacao;
- misturar erros de validacao com dados validos;
- permitir importacao duplicada silenciosa.

Criterios de aceite:

- CSV invalido nao e importado como valido;
- duplicidade e bloqueada ou exige confirmacao;
- banco SQLite fica local e ignorado;
- erros sao claros e auditaveis.

Testes necessarios:

- CSV valido ficticio;
- CSV incompleto;
- CSV com duplicidade;
- CSV com `error_type` incompativel;
- reexecucao do importador no mesmo arquivo.

Commit sugerido:

`feat: cria importador local para sqlite`

## Fase 4 - Dashboard Streamlit

Status: implementada tecnicamente na Fase 8; pendente de validacao manual com banco real.

Escopo:

- criar aplicacao local em `dashboard/`;
- ler apenas SQLite local;
- implementar filtros;
- criar visao geral, tabela de sessoes e detalhe de avaliacao;
- permitir exportacao somente da visao filtrada;
- exibir aviso explicito de resultados descritivos e nao clinicos.

Filtros previstos:

- periodo;
- projeto;
- `participant_id`;
- `participant_name`;
- visita;
- avaliador;
- teste;
- versao do teste.

Visao geral:

- total de avaliacoes;
- participantes unicos;
- precisao media;
- precisao mediana;
- tempo mediano de resposta;
- omissoes;
- comissoes.

Graficos:

- avaliacoes por periodo;
- precisao por visita;
- distribuicao de tempo de reacao;
- omissoes e comissoes por projeto;
- evolucao de um participante ao longo das visitas.

Arquivos provaveis:

- `dashboard/app.py`
- `dashboard/README.md`
- `dashboard/AGENTS.md`
- `docs/DADOS_E_DASHBOARD.md`
- `docs/REGISTRO_DE_ALTERACOES.md`

Riscos:

- expor dados sensiveis em prints ou exports;
- sugerir interpretacao clinica;
- modificar banco ou CSVs brutos pelo dashboard;
- filtros ambiguos.

Criterios de aceite:

- dashboard roda localmente;
- nao precisa de internet;
- le apenas SQLite;
- filtros operam conforme documentado;
- aviso nao clinico e visivel;
- exportacao nao altera dados originais.

Testes necessarios:

- banco ficticio local;
- filtros combinados;
- detalhe de avaliacao;
- exportacao filtrada;
- verificacao de que CSV bruto nao foi alterado.

Commit sugerido:

`feat: cria dashboard local de resultados`

## Fase 8 - Dashboard interativo local

Status: implementada tecnicamente em 2026-07-15; pendente de validacao manual com banco SQLite real importado.

Escopo implementado:

- aplicacao Streamlit local em `dashboard/app.py`;
- leitura do banco padrao `database/stroop_results.sqlite3` em modo somente leitura;
- tratamento de banco ausente, banco vazio e schema invalido;
- filtros por periodo, projeto, `participant_id`, `participant_name`, visita, avaliador, teste e versao;
- cards de total de avaliacoes, participantes unicos, precisao media, precisao mediana, tempo de reacao mediano, total de omissoes e total de comissoes;
- graficos de avaliacoes por data, precisao por visita, distribuicao do tempo de reacao, omissoes e comissoes por projeto e evolucao de participante por visita;
- tabela agregada filtravel de avaliacoes;
- detalhe da avaliacao com metadados, metricas completas, tentativas e contagem dos quatro tipos de resposta;
- download manual em CSV apenas da visao agregada filtrada e visivel;
- testes automatizados com SQLite temporario, sem dados reais.

Arquivos:

- `dashboard/app.py`;
- `dashboard/README.md`;
- `dashboard/requirements.txt`;
- `tests/test_dashboard.py`;
- `docs/DADOS_E_DASHBOARD.md`;
- `docs/PLANO_DE_IMPLEMENTACAO_DASHBOARD.md`;
- `docs/REGISTRO_DE_ALTERACOES.md`;
- `README.md`.

Checklist manual pendente:

1. Importar pelo menos um CSV real para SQLite.
2. Rodar `streamlit run dashboard/app.py`.
3. Confirmar abertura do dashboard.
4. Testar filtros.
5. Conferir cards principais.
6. Conferir graficos.
7. Conferir tabela de avaliacoes.
8. Conferir detalhe de uma avaliacao.
9. Conferir aviso nao clinico.
10. Conferir exportacao da visao filtrada.

## Fase 5 - Testes e validacao

Status: pendente.

Escopo:

- teste com pelo menos tres execucoes ficticias;
- teste de filtros;
- teste de importacao duplicada;
- teste de dados incompletos;
- teste de execucao repetida do mesmo participante;
- teste de preservacao dos CSVs brutos;
- revisao manual no PsychoPy Pilot.

Arquivos provaveis:

- `tests/`
- `docs/VALIDACAO_CONDICOES.md`
- `docs/DADOS_E_DASHBOARD.md`
- `docs/REGISTRO_DE_ALTERACOES.md`

Riscos:

- usar dados reais como fixtures;
- validar apenas caminho feliz;
- deixar banco ou export gerado ser versionado.

Criterios de aceite:

- fixtures nao contem dados pessoais reais;
- testes cobrem importacao valida, invalida e duplicada;
- CSVs brutos permanecem imutaveis;
- resultados do dashboard batem com metricas calculadas.

Testes necessarios:

- validacao automatizada de CSV;
- validacao de schema SQLite;
- comparacao de metricas;
- revisao manual do fluxo em Pilot.

Commit sugerido:

`test: valida camada local de dados e dashboard`
