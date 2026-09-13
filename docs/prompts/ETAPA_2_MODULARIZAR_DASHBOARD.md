# Etapa 2 — Modularizar o dashboard

> Documento historico, substituido para fins de planejamento, estado e aceite.
> As instrucoes, estados, criterios e referencias antigas abaixo nao governam
> execucoes atuais, nem autorizam validacao com dados reais. Consulte o
> [backlog canonico](../Projeto%20Stroop%20Test.md) e o
> [protocolo Codex CLI](../WORKFLOW_CODEX_CLI.md).


Leia os `AGENTS.md` aplicaveis, a
[baseline](../BASELINE_ETAPA_1.md), o
[workflow](../WORKFLOW_EVOLUCAO.md), `dashboard/README.md` e os testes atuais do
dashboard. Inspecione `dashboard/app.py` e apresente um plano curto antes de
editar.

## Objetivo

Modularizar `dashboard/app.py`, separando interface Streamlit, acesso SQLite,
transformacoes de dados e componentes visuais, sem mudar comportamento publico.

## Escopo

- Criar a menor estrutura modular suficiente dentro de `dashboard/`.
- Manter SQLite em modo somente leitura.
- Preservar interface, textos, filtros, graficos, tabelas, detalhes, exportacao,
  metricas e tratamento de erros existentes.
- Preservar `dashboard/app.py` como ponto de entrada e os atalhos/launcher atuais.
- Adaptar os 73 testes existentes e adicionar apenas testes de regressao ou de
  fronteira necessarios para comprovar a separacao.
- Atualizar documentacao, registro de alteracoes e, ao concluir, o estado deste
  workflow.

## Fora do escopo

- PsychoPy, `.psyexp`, condicoes e geracao do CSV.
- Mudancas de formulas, metricas, schema ou dados locais.
- Docker, PostgreSQL, suporte a multiplos testes, upload, autenticacao ou API.
- Instalacao/atualizacao de dependencias e qualquer trabalho da Etapa 3.

## Implementacao esperada

- Dependencias entre modulos em uma direcao clara, sem ciclos.
- Consultas e validacao SQLite isoladas da renderizacao Streamlit.
- Transformacoes e calculos puros testaveis sem iniciar o Streamlit.
- Componentes visuais compostos pela aplicacao, mantendo o resultado atual.
- Compatibilidade de importacao e inicializacao comprovada pelos testes.

## Validacoes

```bash
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

Execute verificacoes adicionais focadas nos novos modulos sem abrir dados reais
ou iniciar servidor interativo. A baseline minima e 73 testes aprovados.

## Criterios de aceite

- As quatro responsabilidades estao separadas e documentadas.
- SQLite continua somente leitura e nenhum CSV bruto e acessado pelo dashboard.
- Interface e comando publico de inicializacao permanecem compativeis.
- Todos os testes passam; novos testes cobrem as fronteiras criadas.
- Nao houve mudanca no experimento, metricas, schema ou dependencias.

## Saida final

Relate estrutura resultante, arquivos, comandos/resultados, contagem de testes,
riscos e decisoes pendentes. Somente com todos os criterios comprovados, marque a
Etapa 2 como concluida e o progresso como 12% em
`../WORKFLOW_EVOLUCAO.md`.

Confirme que a Etapa 3 nao foi iniciada, pare e aguarde revisao. Sugira exatamente
uma mensagem Conventional Commits, sem executar versionamento.
