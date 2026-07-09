# AGENTS.md

## Objetivo do projeto

Este projeto e um experimento original Stroop Go/No-Go desenvolvido em PsychoPy, para fins educacionais e de pesquisa exploratoria.

## Limites eticos e de propriedade

- Nao copiar identidade visual, logotipos, textos proprietarios, pontuacao normativa, diagnosticos ou alegacoes clinicas de plataformas como CogniFit.
- O experimento pode se inspirar em paradigmas publicos, mas deve manter interface e textos proprios.
- Nao alegar validacao clinica, equivalencia psicometrica ou diagnostico sem estudo apropriado.

## Regras para alteracoes

- Antes de mudancas relevantes, inspecionar os arquivos atuais e explicar o plano.
- Fazer alteracoes incrementais.
- Nao reescrever o experimento inteiro quando uma correcao localizada for suficiente.
- Nao alterar arquivos de dados ja coletados.
- Nao editar `*_lastrun.py`; corrigir o `.psyexp`, CSVs de condicoes ou scripts-fonte.
- Nao remover funcionalidades existentes sem explicar e confirmar.

## Regras de dados

- `data/` e local e nunca deve ser versionada.
- Os CSVs finais precisam ser consistentes, uma linha por tentativa do bloco principal, com `block` em `main`.
- Manter somente um CSV unificado por execucao futura.
- Campos finais esperados no CSV unificado oficial: `project`, `participant_id`, `participant_name`, `initials`, `visit`, `evaluator`, `assessment_id`, `assessment_date`, `started_at`, `test_code`, `test_version`, `block`, `trial_number`, `word`, `ink_color`, `condition`, `correct_response`, `key_pressed`, `reaction_time`, `correct`, `error_type`.
- O CSV unificado oficial deve ser uma linha por tentativa real do bloco principal, com `block` em `main`, `condition` em `congruent` ou `incongruent` e sem colunas `_raw`; a pratica nao deve gerar linhas no CSV oficial.
- A arquitetura de dados futura e: PsychoPy -> CSV bruto unificado -> script de importacao -> SQLite local -> dashboard Streamlit local.
- Nao versionar SQLite, bancos locais, CSVs reais, exports, backups, credenciais ou arquivos temporarios.
- Toda metrica nova deve ter formula documentada antes da implementacao.
- Manter rastreabilidade entre `assessment_id`, `source_file` e dados por tentativa.
- `participant_id` e o identificador principal; `participant_name` e dado pessoal local que nao deve aparecer em nomes de arquivo, screenshots, exemplos publicos ou logs; `initials` sao opcionais e potencialmente identificaveis.
- Nao coletar nome completo, CPF, e-mail, endereco, telefone, idade ou sexo nesta versao.

## Regras do paradigma

- Congruente + Espaco = `hit`.
- Congruente sem resposta = `omission`.
- Incongruente sem resposta = `correct_rejection`.
- Incongruente + Espaco = `commission`.
- Nao mudar essas regras sem registrar a decisao em documentacao.

## Regras de documentacao

- Toda mudanca relevante deve atualizar `docs/REGISTRO_DE_ALTERACOES.md`.
- Decisoes metodologicas ou de UX devem ser registradas em `docs/DECISOES_DO_EXPERIMENTO.md`.
- Commits devem seguir o padrao definido em `docs/PADRAO_DE_COMMITS.md`.

## Estrutura canonica

- `.psyexp` principal permanece na raiz do projeto.
- `condicoes/` e o nome canonico para CSVs de condicoes; nao criar pasta duplicada `conditions/`.
- `scripts/` concentra scripts auxiliares.
- `docs/` concentra documentacao metodologica, historico e governanca.
- `assets/` armazena apenas assets proprios do projeto.
- `dashboard/` fica reservado para dashboard Streamlit local futuro.
- `tests/` fica reservado para validacoes futuras.
- `data/` e local; somente `data/README.md` pode ser versionado.

## Regras de validacao

- Apos alterar o experimento, validar variaveis usadas em rotinas e loops.
- Confirmar que CSVs de condicoes tem colunas compativeis.
- Testar em modo Pilot antes de coletar dados reais.
- Nao alegar validacao clinica, equivalencia psicometrica ou diagnostico sem estudo apropriado.
