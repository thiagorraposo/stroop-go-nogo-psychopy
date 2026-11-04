# Padrao de commits

Este projeto usa Conventional Commits em portugues, com mensagens curtas, objetivas e no imperativo quando fizer sentido.

## Tipos

- `feat:` nova funcionalidade do experimento ou ferramenta auxiliar.
- `fix:` correcao de bug, variavel, rotina, condicao ou saida de dados.
- `docs:` mudancas de documentacao.
- `refactor:` reorganizacao interna sem mudar comportamento experimental.
- `test:` verificacoes, testes ou ajustes de validacao.
- `chore:` tarefas de manutencao, configuracao ou versionamento.

## Exemplos

```text
docs: documenta regras do paradigma stroop go/nogo
fix: corrige mapeamento de resposta no bloco de pratica
feat: adiciona resumo local de desempenho ao script de analise
refactor: organiza nomes de variaveis no builder
test: valida colunas dos csvs de condicoes
chore: estrutura inicial de versionamento do experimento
```

## Regras praticas

- Cada commit deve representar uma mudanca coerente.
- Nao misturar alteracao experimental, documentacao e limpeza ampla no mesmo commit, salvo quando fizerem parte da mesma tarefa.
- Nunca incluir dados de participantes, arquivos em `data/`, logs ou arquivos `*_lastrun.py`.
- Atualizar `docs/REGISTRO_DE_ALTERACOES.md` quando a mudanca alterar comportamento, dados, UX ou estrutura do projeto.

