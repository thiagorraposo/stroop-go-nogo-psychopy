# Instrucoes do repositorio

## Projeto e fontes canonicas

Experimento original Stroop Go/No-Go para uso educacional e pesquisa
exploratoria. Nao e instrumento clinico, diagnostico ou normativo.

Antes de alterar codigo, leia `docs/BASELINE_ETAPA_1.md`,
`docs/WORKFLOW_EVOLUCAO.md`, a documentacao citada pela etapa e todos os
`AGENTS.md` aplicaveis. Contratos detalhados ficam na documentacao, nao devem ser
duplicados aqui.

Arquitetura vigente: PsychoPy local -> CSV oficial local -> importador -> SQLite
local -> dashboard Streamlit local. Pontos de entrada:

- experimento: `stroop_go_nogo_ptbr.psyexp` no PsychoPy Builder;
- dashboard publico: `abrir_dashboard.bat` ou `bash abrir_dashboard.sh`;
- launcher: `python scripts/run_dashboard.py`;
- importador: `python scripts/importar_csv_sqlite.py CAMINHO.csv`;
- diagnostico somente leitura: `python scripts/doctor.py`;
- testes: `.venv/bin/python -m unittest discover -s tests -v` (Linux/macOS).

Diretorios: `condicoes/` contem fontes do experimento; `dashboard/`, a interface
Streamlit; `scripts/`, importacao e utilitarios; `tests/`, testes e fixtures
sinteticas; `docs/`, contratos e governanca; `data/` e `database/`, dados locais
ignorados. `assets/` aceita somente material proprio.

## Workflow por etapas

- Execute somente a etapa explicitamente solicitada e pare antes da seguinte.
- Consulte o estado e os criterios em `docs/WORKFLOW_EVOLUCAO.md`; nao antecipe
  infraestrutura, migracoes ou funcionalidades de etapas posteriores.
- Antes de editar, inspecione o estado atual e apresente um plano curto.
- Preserve todo comportamento fora do escopo. Prefira mudancas pequenas,
  incrementais e verificaveis; nao remova funcionalidade sem confirmacao.
- Atualize o estado/progresso do workflow somente quando todos os criterios da
  etapa estiverem comprovados. Registre mudancas relevantes em
  `docs/REGISTRO_DE_ALTERACOES.md`.
- Interrompa e solicite decisao diante de ambiguidade clinica, semantica,
  arquitetural, metodologica, de privacidade ou seguranca que altere o resultado.

## Limites de dominio e seguranca

- PsychoPy permanece local e fora do Docker. Nao edite `*_lastrun.py`; altere o
  `.psyexp`, condicoes ou scripts-fonte apenas quando a etapa autorizar.
- Preserve o comando publico de inicializacao do dashboard, salvo requisito
  explicito. Streamlit nao modifica CSV bruto; no estado vigente, abre SQLite
  somente leitura.
- Nao mude paradigma, tempos, estimulos, contrato CSV, schema ou formulas de
  metricas sem decisao explicita e documentada. Regras do paradigma e formulas:
  `docs/DECISOES_DO_EXPERIMENTO.md` e `docs/MODELO_DE_DADOS.md`.
- Nao copiar identidade, textos, pontuacao ou alegacoes proprietarias; nao criar
  diagnostico, norma, percentil clinico ou equivalencia psicometrica.
- Use somente dados inequivocamente sinteticos em testes e documentacao. Nao
  abra, copie, imprima, registre em log ou versione dados identificaveis.
- `participant_name` e `initials` sao dados locais potencialmente identificaveis.
  Nunca os use em nomes de arquivo, screenshots, exemplos publicos ou logs.
- Nao modificar coletas existentes. Nao versionar `data/`, SQLite, backups,
  exports, logs, temporarios, credenciais ou secrets; respeite `.gitignore`.
- Nao instalar ou atualizar dependencias sem necessidade comprovada pela etapa.

## Validacao e conclusao

- Execute os testes aplicaveis e sempre `git diff --check`. Alteracoes no
  experimento exigem tambem validacao de loops/variaveis, compatibilidade das
  condicoes e checklist Pilot autorizado, sem coleta real.
- Considere a etapa concluida somente com escopo implementado, testes aprovados,
  documentacao e workflow atualizados, comportamento fora do escopo preservado e
  riscos/pendencias declarados.
- Na entrega, liste arquivos alterados, comandos e resultados, riscos, decisoes
  pendentes e confirme que a proxima etapa nao foi iniciada.

## Git

- O versionamento e manual. Nao execute `git add`, `git commit`, `git tag` ou
  `git push` sem solicitacao explicita.
- Preserve alteracoes preexistentes do usuario e nao use comandos destrutivos.
- Ao final de cada etapa, sugira exatamente uma mensagem Conventional Commits em
  portugues conforme `docs/PADRAO_DE_COMMITS.md`; nao execute o commit.
