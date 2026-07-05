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
- Os CSVs finais precisam ser consistentes, uma linha por tentativa, e permitir distinguir `practice` e `main` pela coluna `block`.
- Manter somente um CSV unificado por execucao futura.
- Campos finais esperados: `participant`, `session`, `block`, `trial_number`, `word`, `ink_color`, `condition`, `correct_response`, `key_pressed`, `reaction_time`, `correct`, `error_type`.

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
- `tests/` fica reservado para validacoes futuras.
- `data/` e local; somente `data/README.md` pode ser versionado.

## Regras de validacao

- Apos alterar o experimento, validar variaveis usadas em rotinas e loops.
- Confirmar que CSVs de condicoes tem colunas compativeis.
- Testar em modo Pilot antes de coletar dados reais.
- Nao alegar validacao clinica, equivalencia psicometrica ou diagnostico sem estudo apropriado.
