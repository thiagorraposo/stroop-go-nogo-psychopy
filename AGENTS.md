# Instrucoes do repositorio

## Projeto e fontes canonicas

Experimento original Stroop Go/No-Go para uso educacional e pesquisa
exploratoria. Nao e instrumento clinico, diagnostico ou normativo.

Antes de alterar codigo, leia o protocolo, a ficha da etapa e os `AGENTS.md`
aplicaveis. Para o fluxo legado, consulte tambem `docs/BASELINE_ETAPA_1.md` e
`docs/WORKFLOW_EVOLUCAO.md`. Para a evolucao web, use o contexto minimo de
`docs/ROADMAP_WEB.md` e `docs/arquitetura/ADR-001-evolucao-web.md`; nao refaca a
inspecao completa sem divergencia concreta. Contratos nao devem ser duplicados.

Operacao existente: PsychoPy local -> CSV oficial -> importador -> SQLite local
ou PostgreSQL -> dashboard Streamlit autenticado. Arquitetura alvo: monolito
modular com nucleo Python reutilizavel e futuros adaptadores web/HTTP.
Pontos de entrada preservados:

- experimento: `stroop_go_nogo_ptbr.psyexp` no PsychoPy Builder;
- dashboard publico: `abrir_dashboard.bat` ou `bash abrir_dashboard.sh`;
- launcher: `python scripts/run_dashboard.py`;
- importador: `python scripts/importar_csv_sqlite.py CAMINHO.csv`;
- diagnostico somente leitura: `python scripts/doctor.py`;
- testes: `.venv/bin/python -m unittest discover -s tests -v` (Linux/macOS).

Diretorios: `stroop/` contem dominio e ingestao reutilizaveis; `condicoes/`,
fontes do experimento; `dashboard/`, Streamlit; `scripts/`, CLIs e utilitarios;
`api/` e `web/`, fronteiras futuras; `tests/`, testes e fixtures sinteticas;
`docs/`, contratos e governanca; `data/` e `database/`, dados locais ignorados.
Mapa: `docs/ESTRUTURA_DO_PROJETO.md`. `assets/` aceita somente material proprio.

## Workflow por etapas

Leia o [protocolo Codex CLI](docs/WORKFLOW_CODEX_CLI.md). Cada escopo tem uma
fonte de estado: [backlog legado](docs/Projeto%20Stroop%20Test.md) para a
operacao existente; [roadmap WEB](docs/ROADMAP_WEB.md) para a nova versao.
`continue web` executa uma unica etapa web elegivel; `execute Wxx` seleciona
uma etapa com dependencias concluidas; `mostrar status web` e somente leitura.
Nao misture IDs Wxx com as antigas fases ou etapas 1–12.

Os comandos legados continuam regidos pelo backlog legado. O usuario executara e
validara diretamente as Etapas 11 e 12; o Codex nao as inicia por meio de
`continue o projeto`. Nessas etapas, atua apenas em consultas e revisoes
documentais solicitadas pelo usuario, sem alterar o estado sem evidencias de
aceite. Para etapas sob execucao do Codex, `continue o projeto` autoriza somente
a primeira etapa nao concluida do backlog; `mostrar status` e somente leitura;
`validar etapa atual` revalida etapas do Codex ou revisa evidencias fornecidas
para as Etapas 11 e 12, sem avancar.
Siga integralmente o protocolo para os tres comandos. Nao acesse ou configure
OCI por iniciativa do Codex; decisoes materiais cabem ao usuario.
Neste workflow, nao execute `git add`, `git commit`, `git tag` ou `git push`.

- Execute somente a etapa explicitamente solicitada e pare antes da seguinte.
- Consulte estado e criterios no roadmap do escopo selecionado; nao antecipe
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
  explicito. Streamlit nao modifica CSV bruto; consultas de dominio usam
  PostgreSQL com credencial de leitura ou SQLite local somente leitura.
- `stroop/domain` nao depende de interface, arquivos, HTTP ou drivers de banco;
  `stroop/ingestion` depende do dominio. Novos consumidores importam o nucleo,
  preservando os nomes reexportados pelas CLIs existentes.
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
