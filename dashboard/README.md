# Dashboard local

Planejamento, estado e aceite: [backlog canonico](../docs/Projeto%20Stroop%20Test.md).
Operacao do desenvolvimento: [protocolo Codex CLI](../docs/WORKFLOW_CODEX_CLI.md).


Dashboard Streamlit autenticado para visualizar resultados descritivos do
experimento Stroop Go/No-Go importados para SQLite.

O acesso usa Google OIDC e exige cadastro previo por `iss` + `sub` no
PostgreSQL. Perfis, bootstrap e configuracao sem secrets versionados estao em
[`docs/AUTENTICACAO_E_PERMISSOES.md`](../docs/AUTENTICACAO_E_PERMISSOES.md).

O registro de visões em `dashboard/instrumentos.py` também permite validar
instrumentos adicionais sem misturar métricas. A tela sempre seleciona um
instrumento por vez; o contrato e o adaptador demonstrativo estão em
[`docs/MULTIPLOS_INSTRUMENTOS.md`](../docs/MULTIPLOS_INSTRUMENTOS.md).

Aviso fixo exibido na interface:

> Resultados descritivos. Este dashboard não representa avaliação clínica ou diagnóstico.

## Objetivo

- consultar avaliações já importadas para SQLite;
- aplicar filtros por metadados da sessão;
- visualizar métricas agregadas, gráficos, tabela de avaliações e detalhe por avaliação;
- exportar manualmente apenas a visão agregada filtrada que está visível.

O dashboard não modifica CSV bruto nem altera o SQLite. O login redireciona ao
Google Identity; a area de importacao autorizada envia o CSV selecionado somente
ao processador local da aplicacao e ao PostgreSQL configurado.

A infraestrutura Docker da Etapa 3 empacota este ponto de entrada e fornece
`DATABASE_URL`, mas a camada de acesso continua SQLite nesta etapa. A troca do
backend do dashboard pertence a uma etapa posterior do workflow.

## Instalação

Em um ambiente Python local:

```bash
python3 -m pip install -r dashboard/requirements.txt
```

## Execução

```bash
streamlit run dashboard/app.py
```

`dashboard/app.py` permanece como ponto de entrada e e usado tambem por
`scripts/run_dashboard.py` e pelos atalhos da raiz.

Antes de iniciar, configure `.streamlit/secrets.toml`, `AUTH_DATABASE_URL` e as
migrations PostgreSQL. Sem login, nenhuma leitura do SQLite ou area protegida e
executada.

## Estrutura interna

- `app.py`: composicao da interface Streamlit e ponto de entrada;
- `auth.py`: validacao de claims, perfis, bloqueio e auditoria PostgreSQL;
- `data_access.py`: conexao SQLite somente leitura, validacao do schema e carga;
- `transformations.py`: filtros, agregacoes, calculos puros e exportacao em memoria;
- `components.py`: cards, graficos, tabela e detalhe visual reutilizaveis.

As dependencias seguem em direcao ao ponto de entrada: acesso a dados e
transformacoes nao importam Streamlit; componentes dependem apenas das
transformacoes; `app.py` compoe todas as camadas. A API historicamente importada
de `dashboard.app` permanece reexportada para compatibilidade.

## Banco esperado

Banco padrão:

```text
database/stroop_results.sqlite3
```

O banco deve ser criado previamente pelo importador local. O dashboard lê apenas SQLite e abre o arquivo em modo somente leitura.

Tabelas esperadas:

- `assessments`;
- `assessment_metrics`;
- `trial_results`.

Se o banco não existir, estiver vazio ou tiver schema incompatível, a interface mostra uma mensagem clara.

## Filtros

- período por `assessment_date`;
- `project`;
- `participant_id`;
- `participant_name`;
- `visit`;
- `evaluator`;
- `test_code`;
- `test_version`.

## Métricas e visualizações

Cards principais:

- total de avaliações;
- participantes únicos;
- precisão média;
- precisão mediana;
- tempo de reação mediano;
- total de omissões;
- total de comissões.

Gráficos:

- avaliações por data;
- precisão por visita;
- distribuição do tempo de reação;
- omissões e comissões por projeto;
- evolução de um participante ao longo das visitas.

Tabela de avaliações:

- `assessment_date`;
- `project`;
- `participant_id`;
- `participant_name`;
- `visit`;
- `evaluator`;
- `test_version`;
- `accuracy`;
- `accuracy_go_trials`;
- `accuracy_no_go_trials`;
- `omission_errors`;
- `commission_errors`;
- `response_time`.

Detalhe da avaliação:

- metadados da sessão;
- métricas completas;
- contagem de `hit`, `omission`, `correct_rejection` e `commission`;
- tabela de tentativas.

## Exportação

O botão de download gera CSV apenas da visão agregada filtrada e visível. O
callback revalida expiracao, cadastro, bloqueio e perfil no clique. A exportação
é manual e não modifica o SQLite nem CSVs brutos.

## Limites metodológicos

Os resultados são descritivos e exploratórios. A interface não apresenta interpretação de saúde, classificação individual, comparação normativa, percentil ou recomendação clínica.

## Privacidade

- Use `participant_id` pseudonimizado como identificador principal.
- `participant_name` é dado pessoal local e deve ser tratado com cuidado.
- Não use screenshots públicas com dados reais.
- Não versione banco SQLite, exports ou arquivos de coleta.
- O dashboard é local e não deve expor dados fora do ambiente da máquina.
