# Registro de alteracoes

Formato: entradas incrementais com data, tipo de mudanca e resumo.

## 2026-07-06

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
