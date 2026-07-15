# Dashboard local

Dashboard Streamlit local para visualizar resultados descritivos do experimento Stroop Go/No-Go importados para SQLite.

Aviso fixo exibido na interface:

> Resultados descritivos. Este dashboard não representa avaliação clínica ou diagnóstico.

## Objetivo

- consultar avaliações já importadas para SQLite;
- aplicar filtros por metadados da sessão;
- visualizar métricas agregadas, gráficos, tabela de avaliações e detalhe por avaliação;
- exportar manualmente apenas a visão agregada filtrada que está visível.

O dashboard não modifica CSV bruto, não altera o SQLite e não envia dados para servidor externo.

## Instalação

Em um ambiente Python local:

```bash
python3 -m pip install -r dashboard/requirements.txt
```

## Execução

```bash
streamlit run dashboard/app.py
```

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

O botão de download gera CSV apenas da visão agregada filtrada e visível. A exportação é manual e não modifica o SQLite nem CSVs brutos.

## Limites metodológicos

Os resultados são descritivos e exploratórios. A interface não apresenta interpretação de saúde, classificação individual, comparação normativa, percentil ou recomendação clínica.

## Privacidade

- Use `participant_id` pseudonimizado como identificador principal.
- `participant_name` é dado pessoal local e deve ser tratado com cuidado.
- Não use screenshots públicas com dados reais.
- Não versione banco SQLite, exports ou arquivos de coleta.
- O dashboard é local e não deve expor dados fora do ambiente da máquina.
