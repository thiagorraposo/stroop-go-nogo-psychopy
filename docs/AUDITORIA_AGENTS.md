# Auditoria das instrucoes AGENTS.md

Data: 2026-09-01.

## Regra de descoberta

O `AGENTS.md` da raiz governa todo o repositorio. Em um subdiretorio, seu
`AGENTS.md` e herdado e complementado pelo arquivo mais proximo. Nao existe
`AGENTS.override.md` nesta baseline; se um vier a existir, ele substituira o
`AGENTS.md` do mesmo diretorio no escopo correspondente.

## Inventario auditado

| Arquivo | Escopo e arquivos governados | Heranca | Especializacao resultante |
|---|---|---|---|
| `AGENTS.md` | repositorio inteiro | nenhuma | workflow, seguranca, arquitetura vigente, validacao e Git |
| `condicoes/AGENTS.md` | `condicoes/**` | raiz | CSVs-fonte, compatibilidade com `.psyexp` e paradigma |
| `dashboard/AGENTS.md` | `dashboard/**` | raiz | Streamlit, fronteiras de leitura, UX e testes sinteticos |
| `docs/AGENTS.md` | `docs/**` | raiz | fontes canonicas e destino de cada tipo de decisao |
| `scripts/AGENTS.md` | `scripts/**` | raiz | validacao, imutabilidade do CSV, persistencia e CLIs |
| `tests/AGENTS.md` | `tests/**` | raiz | `unittest`, isolamento e proibicao de dados reais |

Nao ha instrucao aninhada em `assets/` ou `data/`: nao existe diferenca de
dominio que justifique mais contexto. As regras da raiz sao suficientes.

## Problemas encontrados antes da otimizacao

- Privacidade, linguagem clinica e registro de alteracoes eram repetidos em
  quase todos os niveis.
- A raiz continha o contrato completo de 21 colunas e regras detalhadas ja
  mantidas em documentos canonicos.
- Termos como “futuro” e “testes futuros” estavam desatualizados: SQLite,
  Streamlit e a suite ja existem.
- Nao havia comandos verificaveis, definicao de conclusao, protocolo das etapas
  nem regra explicita para Git manual.
- `docs/AGENTS.md` enviava UX para `UX_DECISIONS.md`, enquanto a raiz enviava UX
  junto com metodologia para `DECISOES_DO_EXPERIMENTO.md`.
- `scripts/AGENTS.md` dizia que scripts deveriam analisar apenas `data/`, embora
  testes existentes usem caminhos temporarios validos e o importador aceite um
  caminho informado pela CLI.
- `dashboard/AGENTS.md` repetia filtros e limites permanentes sem registrar a
  obrigacao de preservar o launcher publico.
- Nao havia regra contra antecipar etapas, instalar dependencias ou executar
  versionamento sem autorizacao.

## Resultado

- Regras transversais aparecem uma vez na raiz.
- Contratos detalhados sao referenciados por documento canonico.
- Cada arquivo aninhado contem somente diferencas reais do dominio.
- O conflito de UX foi resolvido: metodologia vai para
  `DECISOES_DO_EXPERIMENTO.md`; interface, para `UX_DECISIONS.md`.
- Estados e percentuais ficam exclusivamente em `WORKFLOW_EVOLUCAO.md`.
- As antigas fases em `PLANO_DE_IMPLEMENTACAO_DASHBOARD.md` permanecem como
  historico; nao governam o novo progresso.

## Hierarquia resultante

```text
AGENTS.md
├── condicoes/AGENTS.md
├── dashboard/AGENTS.md
├── docs/AGENTS.md
├── scripts/AGENTS.md
└── tests/AGENTS.md
```

Nao foram criadas sobreposicoes. Em cada ramo, a instrucao aninhada complementa
a raiz sem relaxar seguranca, dados, workflow ou Git.

## Tamanho apos a otimizacao

| Escopo | Linhas | Palavras | Bytes |
|---|---:|---:|---:|
| raiz | 79 | 545 | 4.263 |
| `condicoes/` | 12 | 84 | 623 |
| `dashboard/` | 15 | 118 | 852 |
| `docs/` | 13 | 99 | 722 |
| `scripts/` | 15 | 116 | 816 |
| `tests/` | 14 | 104 | 726 |
| **total armazenado** | **148** | **1.066** | **8.002** |

Uma sessao em um subdiretorio carrega a raiz e no maximo uma especializacao:
entre 4.886 e 5.115 bytes nesta hierarquia. Regras criticas estao na raiz, antes
das especializacoes, e o volume fica abaixo do limite pratico de contexto do
Codex CLI. O pequeno aumento total em relacao aos arquivos anteriores substitui
repeticoes de prompts futuros por workflow, comandos, conclusao e Git verificaveis.
