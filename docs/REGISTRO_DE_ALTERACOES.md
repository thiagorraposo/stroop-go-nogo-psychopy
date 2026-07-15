# Registro de alteracoes

Formato: entradas incrementais com data, tipo de mudanca e resumo.

## 2026-07-15

- `feat`: criado fluxo multiplataforma para configurar `.venv`, instalar dependencias, importar o CSV oficial mais recente e iniciar o dashboard local em Windows, Linux e macOS.
- `feat`: adicionados atalhos `setup.bat`, `setup.sh`, `abrir_dashboard.bat` e `abrir_dashboard.sh`, sem dependencia de `.desktop` ou shell especifico na logica Python.
- `test`: adicionadas validacoes estaticas para deteccao do sistema, Python da venv, selecao do CSV mais recente, ausencias de CSV e venv, comando Streamlit e preservacao de `data/`.
- `docs`: documentada instalacao multiplataforma, uso manual, armazenamento local e limite descritivo nao clinico dos resultados.
- `feat`: implementada Fase 8 com dashboard Streamlit local em `dashboard/app.py`, lendo apenas o SQLite padrao `database/stroop_results.sqlite3` em modo somente leitura.
- `feat`: adicionados filtros por periodo, projeto, `participant_id`, `participant_name`, visita, avaliador, teste e versao, com cards, graficos, tabela agregada, detalhe por avaliacao e download manual da visao filtrada.
- `test`: adicionados testes do dashboard com SQLite temporario para conexao, banco ausente, schema, leitura das tres tabelas, tabela agregada, filtros, cards, detalhe, linguagem proibida e ausencia de escrita no banco.
- `docs`: atualizada documentacao do dashboard, plano e camada de dados para marcar a Fase 8 como implementada tecnicamente e pendente de validacao manual com banco real.

## 2026-07-09

- `feat`: adicionada rotina `resultados` apos `principal_loop`, com resumo descritivo do bloco principal em painel central claro, indicador circular de precisao, mediana de RT dos hits e contagens por tipo de resposta.
- `fix`: ajustado o fluxo para que `resultados` seja a tela final e grave o CSV oficial ao finalizar, evitando depender da rotina antiga `fim`.
- `fix`: removida importacao local de `visual` e `event` no Code Component de `resultados`, evitando `UnboundLocalError` no script gerado pelo Builder.
- `fix`: alterado o CSV oficial para exportar apenas tentativas do bloco principal, mantendo a pratica somente para feedback e HUD local.
- `test`: adicionadas validacoes estaticas para Flow, formulas, textos obrigatorios, navegacao por clique/Espaco/Enter, sintaxe dos Code Components, escrita no encerramento e ausencia de linhas extras no CSV pela tela de resultados.
- `docs`: documentadas formulas, limites de interpretacao e decisao de UX da tela final de resultados.
- `feat`: implementada Fase 7 com importacao do CSV unificado para SQLite local em `scripts/importar_csv_sqlite.py` e schema em `scripts/db_schema.sql`.
- `test`: adicionados testes com CSVs temporarios para importacao valida, cabecalho invalido, duplicidade, `--force`, metricas, rollback, validacao de RT e coerencia de resposta.
- `docs`: criada documentacao `docs/IMPORTACAO_SQLITE.md` e atualizados README, modelo de dados e arquitetura para marcar SQLite local como implementado e pendente de validacao manual com CSV real em Pilot.
- `feat`: atualizada versao para `0.2.2`, com bloco principal balanceado em 8 tentativas congruentes e 8 incongruentes, preservando pratica 2/2 e protocolo curto 4 + 16.
- `fix`: removido texto instrucional visivel do `trial_principal`, mantendo apenas estimulo central, cronometro, precisao e progresso durante o bloco principal.
- `test`: atualizadas validacoes de condicoes, versao, cores oficiais, pares incongruentes e ausencia de texto instrucional no bloco principal.
- `docs`: sincronizadas decisoes e validacao de condicoes com a distribuicao 8/8 e a limpeza da tela principal.

## 2026-07-06

- `feat`: atualizada versao para `0.2.1`, com formulario incluindo `participant_name` local, fullscreen padrao, fundo escuro mantido e centralizacao dos componentes de estimulo.
- `fix`: ajustado o contrato do CSV unificado para 21 colunas, inserindo `participant_name` apos `participant_id` e mantendo `participant_id` como nome-base do arquivo.
- `test`: atualizadas validacoes automatizadas para `participant_name`, tela cheia, ausencia de tamanho fixo e alinhamento central do cartao e do estimulo.
- `docs`: sincronizada a documentacao de formulario, CSV unificado, dados e decisoes com `participant_name` e a versao `0.2.1`.

- `fix`: substituido o uso de variaveis globais diretas do HUD por `hud_state`, evitando `SyntaxError` por declaracao `global` tardia no script gerado pelo Builder.
- `fix`: declarados contadores do HUD como globais nos Code Components de pratica e bloco principal, evitando `UnboundLocalError` ao atualizar precisao e cronometro no `run()`.
- `fix`: corrigidas cores dos cartoes de estimulo para literal constante, evitando geracao de `setColor(#F8FAFC, ...)` invalido no `lastrun.py`.
- `fix`: corrigida a cor de fundo do tema escuro no `.psyexp` para lista RGB numerica, evitando geracao de `color=[#0B1020]` invalido no `lastrun.py`.
- `feat`: atualizada versao para `0.2.0`, com protocolo curto de 4 tentativas de pratica e 16 tentativas principais, bloco principal de cerca de 1 minuto, HUD de precisao, cronometro principal e tema escuro com cartao claro para estimulos.
- `test`: atualizadas validacoes automatizadas para condicoes 4/16, tempos 300/2000/500 ms na pratica, 300/2500/950 ms no principal, HUD, cronometro, tema escuro e preservacao do CSV canonico.
- `docs`: documentados protocolo curto, duracao exclusiva do bloco principal, precisao ao vivo como decisao de UX e tema escuro.
- `fix`: alterado o nome do CSV oficial para usar `participant_id` como nome-base do arquivo gerado em `data/`.
- `feat`: adicionada primeira fase da interface visual pre-pratica com abertura, tutorial unico, introducao a pratica e lembrete rapido automatico.
- `test`: adicionada validacao automatica do Flow pre-pratica, remocao de telas antigas duplicadas, navegacao por clique/teclado e preservacao do formulario.
- `docs`: registradas decisoes de UX da interface pre-pratica e checklist Pilot correspondente.
- `feat`: implementada Fase 3 com 10 cores oficiais, pratica de 10 tentativas, bloco principal de 60 tentativas e perfil temporal de 2,0 segundos por tentativa.
- `test`: adicionada validacao automatica de balanceamento das condicoes, renderizacao por `ink_color_display`, preservacao do CSV unificado e tempos do `.psyexp`.
- `docs`: atualizada validacao de condicoes para documentar balanceamento, duracao aproximada de 2 minutos do bloco principal e checklist Pilot da Fase 3.
- `fix`: corrigido `.gitignore` para manter `data/` local e versionar somente `data/README.md`.
- `fix`: alterado o nome do CSV oficial para usar o `assessment_id` como nome-base do arquivo gerado em `data/`.
- `fix`: removida importacao local redundante de `os` no componente `formulario_sessao`, evitando `UnboundLocalError` no inicio da execucao gerada pelo PsychoPy.
- `feat`: implementada exportacao unificada em CSV oficial `_trials.csv`, com uma linha por tentativa real, metadados de sessao, pratica e bloco principal no mesmo arquivo.
- `test`: atualizado `scripts/analisar_stroop.py` para validar o contrato do CSV unificado e calcular metricas descritivas do bloco principal; criados testes automatizados em memoria para os quatro tipos de resposta e casos invalidos.
- `docs`: criado `docs/CSV_UNIFICADO.md` e atualizada a documentacao da camada de dados para registrar o CSV unificado como fonte oficial futura.
- `fix`: movida a execucao do formulario de sessao para `Begin Experiment`, evitando acesso a `expInfo` antes de sua criacao pelo PsychoPy.
- `fix`: corrigida leitura dos campos do formulario de sessao para aceitar retorno em lista ou dicionario do `psychopy.gui.Dlg`, evitando falso erro em `participant_id` valido.
- `feat`: implementado formulario local de sessao no PsychoPy com metadados canonicos, validacao de `participant_id` e nome de arquivo sem identificadores digitados.
- `docs`: criado `docs/FORMULARIO_DE_SESSAO.md` com regras, mapeamento para CSV e checklist manual de Pilot.
- `docs`: definida arquitetura futura de dados e dashboard local em `docs/DADOS_E_DASHBOARD.md`, `docs/MODELO_DE_DADOS.md` e `docs/PLANO_DE_IMPLEMENTACAO_DASHBOARD.md`.
- `docs`: criada estrutura documental de `dashboard/` com regras persistentes e README, sem implementar Streamlit ou banco.
- `chore`: atualizadas regras de Git e agentes para proteger SQLite, bancos locais, exports e dados reais.
- `docs`: criada especificacao visual e funcional futura em `docs/ESPECIFICACAO_VISUAL_E_FLUXO.md`.
- `docs`: criado copy sugerido das telas em `docs/COPY_DAS_TELAS.md`.
- `docs`: atualizadas decisoes de UX e decisoes metodologicas sem alterar `.psyexp`, condicoes, scripts, dados ou exportacao.

## 2026-07-05

- `test`: documentada validacao estatica de loops, variaveis e CSVs de condicoes em `docs/VALIDACAO_CONDICOES.md`, sem alterar o paradigma ou arquivos de coleta.
- `refactor`: organizada a estrutura do projeto com separacao entre experimento, condicoes, scripts, documentacao, testes, assets e dados locais.
- `docs`: criados READMEs locais, `AGENTS.md` por diretorio e `docs/ESTRUTURA_DO_PROJETO.md`.
- `chore`: movido `analisar_stroop.py` para `scripts/analisar_stroop.py` sem alterar a logica de analise.
- `chore`: preservados os nomes dos CSVs em `condicoes/` porque sao referenciados diretamente pelo `.psyexp`.
- `chore`: criada estrutura inicial de versionamento profissional com `.gitignore`, `AGENTS.md`, documentos de governanca e pastas auxiliares.
- `docs`: documentadas regras de privacidade, padrao de commits e decisoes iniciais do experimento.
- `chore`: preservada a pasta `condicoes/` como pasta local de CSVs de condicoes, em vez de duplicar conteudo em `conditions/`.
