# Dashboard

Esta pasta esta reservada para um dashboard Streamlit local futuro.

## Objetivo

O dashboard devera permitir consulta descritiva de avaliacoes do experimento Stroop Go/No-Go, com filtros, visao geral, tabela de sessoes e detalhe de avaliacao.

## Fonte de dados prevista

A fonte padrao sera um banco SQLite local gerado por script futuro de validacao e importacao. O dashboard deve ler apenas esse banco e nunca modificar CSVs brutos em `data/`.

## Filtros previstos

- periodo;
- projeto;
- `participant_id`;
- iniciais;
- visita;
- avaliador;
- teste;
- versao do teste.

## Metricas previstas

- `accuracy`;
- `accuracy_go_trials`;
- `accuracy_no_go_trials`;
- `omission_errors`;
- `omission_errors_percentage`;
- `commission_errors`;
- `response_time`;
- totais tecnicos de tentativas, hits e rejeicoes corretas.

## Limites metodologicos

Os resultados sao descritivos e exploratorios. O dashboard nao deve apresentar diagnostico, comparacao normativa, escore clinico, percentil clinico, recomendacao de avaliacao clinica ou alegacao individual sobre capacidades cognitivas.

## Estado atual

Nenhuma aplicacao funcional e criada nesta etapa. Esta pasta contem apenas documentacao e regras persistentes para implementacao futura.
