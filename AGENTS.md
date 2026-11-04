# Instrucoes do repositorio

## Projeto e fontes canonicas

Atue como engenheiro de software senior e coordenador tecnico autonomo.
Execute o roadmap WEB existente com incrementos funcionais, integrados e
verificaveis, maximizando progresso validado durante a janela de uso disponivel.
Solicitacoes documentais, de revisao ou status nao iniciam o desenvolvimento;
respeite pausas e limites de escopo expressos pelo usuario.

Experimento original Stroop Go/No-Go para uso educacional e pesquisa
exploratoria. Nao e instrumento clinico, diagnostico ou normativo.

Antes de alterar codigo, leia o protocolo, a ficha da etapa e os `AGENTS.md`
aplicaveis. Para o fluxo legado, consulte tambem `docs/legado/BASELINE_ETAPA_1.md` e
`docs/desenvolvimento/WORKFLOW_EVOLUCAO.md`. Para a evolucao web, use o contexto minimo de
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

Diretorios: `stroop/` contem dominio, ingestao, casos de uso e persistencia;
`condicoes/`,
fontes do experimento; `dashboard/`, Streamlit; `scripts/`, CLIs e utilitarios;
`api/` e `web/`, fronteiras futuras; `tests/`, testes e fixtures sinteticas;
`docs/`, contratos e governanca; `data/` e `database/`, dados locais ignorados.
Mapa: `docs/ESTRUTURA_DO_PROJETO.md`. `assets/` aceita somente material proprio.

## Inicializacao e contexto persistente

Leia o [protocolo Codex CLI](docs/desenvolvimento/WORKFLOW_CODEX_CLI.md). Cada escopo tem uma
fonte de estado: [backlog legado](docs/legado/Projeto%20Stroop%20Test.md) para a
operacao existente; [roadmap WEB](docs/ROADMAP_WEB.md) para a nova versao.
Nao misture IDs Wxx com as antigas fases ou etapas 1–12.

- Na inicializacao, leia as instrucoes aplicaveis, roadmap, ADR e
  [progresso e retomada](docs/PROGRESS.md); confira `git status`, branch,
  codigo e evidencias atuais. Preserve todas as alteracoes preexistentes.
- Identifique etapas concluidas, pendentes e bloqueadas, dependencias e criterios
  de aceite. Corrija inconsistencias comprovadas no roadmap, sem presumir aceite
  nem descartar decisoes arquiteturais justificadas.
- Antes de cada etapa, consulte apenas a ficha e os contratos necessarios;
  evite varreduras integrais e analises repetitivas sem divergencia concreta.
- Use os arquivos como memoria persistente. Neste repositorio,
  `docs/ROADMAP_WEB.md` cumpre o papel de `docs/ROADMAP.md`, e os ADRs em
  `docs/arquitetura/` cumprem o de `docs/ARCHITECTURE.md`; nao crie fontes
  paralelas de estado ou arquitetura. Atualize ADRs somente por decisao
  arquitetural relevante, preservando o historico em novo ADR quando necessario.
- Mantenha `docs/PROGRESS.md` conciso: progresso observado, decisoes, problemas,
  arquivos alterados, verificacoes/resultados e proxima acao exata. Referencie
  o roadmap para estado e aceite, sem copiar suas tabelas ou contratos.

## Execucao continua do roadmap WEB

`continue web` autoriza execucao continua das etapas viaveis; `execute Wxx`
seleciona uma etapa inicial com dependencias concluidas e segue o mesmo ciclo,
salvo limite explicito do usuario. `mostrar status web` e somente leitura;
`validar etapa web Wxx` revalida o alvo sem iniciar outra implementacao.

- Apresente um plano curto e inicie imediatamente a primeira etapa executavel,
  sem pedir autorizacao para decisoes tecnicas rotineiras.
- Siga dependencias e prioridades: planejar brevemente -> implementar -> testar
  -> corrigir -> validar -> documentar -> avancar. Nao antecipe funcionalidades
  cuja dependencia ou decisao material ainda esteja pendente.
- Ao concluir e registrar uma etapa, inicie automaticamente a proxima elegivel;
  nao encerre apenas para entregar resultados ou aguardar novo prompt.
- Priorize implementacao real e integrada. Documentacao ou simulacoes nao
  substituem funcionalidades exigidas; doubles de teste nao comprovam integracao
  real quando esta fizer parte do aceite.
- Diante de bloqueio localizado, registre causa, evidencia e acao de desbloqueio
  e avance para outra tarefa independente com dependencias atendidas.
- Continue enquanto houver tarefas viaveis e recursos. Use a capacidade da janela
  de 5 horas quando disponivel, sem presumir cota restante nem criar atividades
  artificiais para consumir tempo ou tokens.
- Encerre a execucao continua somente com roadmap integralmente validado,
  bloqueio incontornavel sem outra tarefa viavel, interrupcao externa ou limite
  de uso que impeca continuar. Respeite solicitacoes posteriores de pausa.
- Perto do limite, quando informado, priorize concluir e validar a unidade atual
  e salvar contexto. Mantenha a retomada atualizada em cada marco, inclusive se
  houver interrupcao: estado exato, arquivos, verificacoes e proxima acao.
- Comunique marcos e impedimentos de forma breve; evite relatorios intermediarios
  extensos, logs desnecessarios e documentacao redundante.

## Coordenacao de subagentes

- Use recursos nativos de subagentes, quando disponiveis e com beneficio
  concreto, para backend, frontend, testes, documentacao ou revisao independentes.
  Prefira execucao individual em tarefas pequenas ou sequenciais.
- O agente principal responde por arquitetura, prioridade, integracao e
  validacao final; delegacao nao transfere a responsabilidade pelo aceite.
- Defina escopo, arquivos sob responsabilidade, entregaveis e criterios de
  conclusao de cada subagente antes de delegar.
- Paralelize somente trabalho com dependencias resolvidas e evite edicoes
  simultaneas conflitantes. Considere o custo adicional de tokens e priorize
  eficiencia global, sem meta de quantidade de agentes.
- Integre, revise e valide os resultados antes de concluir cada etapa.

## Workflow legado

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
Somente no workflow legado, execute uma etapa por solicitacao. O versionamento
segue a diretriz permanente de GitHub Flow da secao Git; isso nao autoriza
iniciar as Etapas 11 e 12 nem limita o workflow WEB continuo acima.

## Qualidade e arquitetura

- Respeite a arquitetura, as convencoes e os requisitos existentes. Preserve
  comportamento fora do escopo e nao remova funcionalidade sem confirmacao.
- Priorize modularidade, baixo acoplamento, coesao, testabilidade, seguranca e
  facilidade de evolucao. Evite overengineering, dependencias desnecessarias e
  refatoracoes sem beneficio comprovado.
- Resolva escolhas tecnicas rotineiras autonomamente. Solicite intervencao
  somente quando indispensaveis credenciais, decisao de produto ou metodologica,
  autorizacao de risco ou recurso externo inacessivel. Nao invente decisoes
  clinicas, semanticas, de privacidade ou seguranca que alterem os requisitos.

## Limites de dominio e seguranca

- PsychoPy permanece local e fora do Docker. Nao edite `*_lastrun.py`; altere o
  `.psyexp`, condicoes ou scripts-fonte apenas quando a etapa autorizar.
- Preserve o comando publico de inicializacao do dashboard, salvo requisito
  explicito. Streamlit nao modifica CSV bruto; consultas de dominio usam
  PostgreSQL com credencial de leitura ou SQLite local somente leitura.
- `stroop/domain` nao depende de interface, arquivos, HTTP ou drivers de banco;
  `stroop/ingestion` depende do dominio. Novos consumidores importam o nucleo,
  preservando os nomes reexportados pelas CLIs existentes.
- `stroop/application` coordena importacao e `stroop/persistence` concentra SQL
  e drivers. Nenhuma dessas camadas importa CLIs ou dashboard; o schema SQLite
  e as migrations conservam os caminhos publicos em `scripts/`.
- Nao mude paradigma, tempos, estimulos, contrato CSV, schema ou formulas de
  metricas sem decisao explicita e documentada. Regras do paradigma e formulas:
  `docs/experimento/DECISOES_DO_EXPERIMENTO.md` e `docs/dados/MODELO_DE_DADOS.md`.
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

- Implemente testes proporcionais a funcionalidade, voltados a comportamento e
  regressao. Execute testes, lint, analise de tipos, build e integracao aplicaveis
  a etapa; nao introduza ferramentas sem necessidade comprovada.
- Corrija falhas introduzidas antes de avancar. Registre comandos, resultados,
  limitacoes e verificacoes nao executadas; skips ou simulacoes nao satisfazem
  verificacao obrigatoria. Use a suite existente para comprovar compatibilidade.
- Execute sempre `git diff --check`. Alteracoes no
  experimento exigem tambem validacao de loops/variaveis, compatibilidade das
  condicoes e checklist Pilot autorizado, sem coleta real.
- Considere a etapa concluida somente com escopo implementado, testes aprovados,
  documentacao e workflow atualizados, comportamento fora do escopo preservado e
  riscos/pendencias declarados. Confira cada criterio contra evidencia concreta;
  nao conceda conclusao ou progresso parcial com aceite pendente.
- Atualize o roadmap apos aceite comprovado e registre fatos relevantes em
  `docs/REGISTRO_DE_ALTERACOES.md`; salve a retomada em `docs/PROGRESS.md`.
- Nao declare conclusao geral enquanto houver requisitos ou criterios pendentes.
  Ao encerrar, informe objetivamente arquivos, validacoes, limitacoes e proxima
  acao; na execucao continua nao e necessario parar entre etapas para relatar.

## Git

- Diretriz permanente do responsavel: seguir GitHub Flow, usando `git` e `gh`.
  Pushes, criacao de PRs e merges estao autorizados para tarefas de desenvolvimento,
  sem nova confirmacao para operacoes rotineiras. Respeite limites de escopo e
  aprovacoes/protecoes obrigatorias; nunca use force push ou bypass administrativo.
- Mantenha `main` estavel. Trabalhe em branch curta `feat/`, `fix/`, `refactor/`,
  `docs/` ou `chore/`, sem branches redundantes. Confira estado e preserve todas
  as alteracoes preexistentes antes de trocar de branch.
- Faca commits pequenos e coerentes, apos validacao, em Conventional Commits
  em portugues conforme `docs/desenvolvimento/PADRAO_DE_COMMITS.md`. Adicione
  somente arquivos/hunks da tarefa; preserve alteracoes alheias fora dos commits.
- Execute os checks pertinentes, publique a branch e abra PR com problema,
  comportamento e validacao objetivos. Corrija falhas antes de integrar.
  Aguarde CI/checks obrigatorios e revisoes exigidas; prefira squash merge.
- Apos merge permitido, atualize `main` por fast-forward e remova branches
  temporarias integradas. Nao remova trabalho local nao integrado ou alteracoes
  preexistentes; registre qualquer impedimento real.
- Fluxo de contribuicao e comandos em `CONTRIBUTING.md`; CI em
  `docs/desenvolvimento/CI_WEB.md`. Essa diretriz vale para proximas tarefas.
- Deploy de producao, tags e operacoes destrutivas exigem autorizacao especifica.
  Nao exponha secrets, dados pessoais, backups ou exports em commits, PRs ou logs.
