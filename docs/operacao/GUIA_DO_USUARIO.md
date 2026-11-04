# Guia do usuario

## Escolher o fluxo

A versao WEB permite preparar convites, executar a tarefa no navegador e
consultar resultados por projeto. O fluxo local PsychoPy e Streamlit continua
disponivel. O estado de liberacao da WEB fica no [roadmap](../ROADMAP_WEB.md);
a versao publicada e seus limites ficam no [registro da VPS](DEPLOY_WEB_VPS.md).
Use somente dados sinteticos enquanto a liberacao aplicavel a pesquisa nao
estiver registrada. Publicar a pagina nao libera automaticamente coleta real.

Os resultados sao descritivos, sem diagnostico, norma, percentil clinico ou
equivalencia psicometrica entre PsychoPy e navegador. Consulte os limites da
[validacao WEB](../VALIDACAO_WEB.md).

## Participar pela WEB

1. Abra o endereco informado pela equipe e selecione **Iniciar tutorial**.
2. Leia a regra: pressione **Espaco** quando palavra e cor das letras forem
   iguais; quando forem diferentes, aguarde sem pressionar.
3. Selecione **Ir para a pratica** e informe o codigo de convite fornecido pela
   equipe. O participante nao precisa de conta Google.
4. Use computador Windows ou Linux, teclado fisico e Chrome, Edge ou Firefox
   atualizado. Confirme o teclado e pressione e solte Espaco para verifica-lo.
   A verificacao de ambiente nao certifica precisao fisica do equipamento.
5. Selecione **Comecar pratica**. Sao quatro tentativas com feedback. Ao final,
   escolha **Repetir pratica** ou **Comecar tarefa**. O principal dura cerca de
   um minuto; mantenha a aba em foco e evite interrupcoes.
6. Aguarde **Resultado recebido pela equipe** antes de finalizar. O resumo
   local, sozinho, nao confirma que os dados chegaram ao servidor.
7. Selecione **Finalizar** para encerrar o acesso. Depois, pode fechar a pagina.

Use uma unica aba para a tarefa. Escape, perda de foco ou outra interrupcao
podem invalidar o bloco; o principal interrompido nao e retomado nem gera
avaliacao parcial. Comunique a interrupcao a equipe para orientar nova sessao.

Se aparecer **Reenviar resultado**, mantenha a pagina aberta e use esse botao:
o mesmo resultado pode ser enviado sem repetir a tarefa, enquanto o acesso
estiver valido. Fechar ou recarregar pode perder um resultado ainda nao
confirmado, pois ele fica somente na memoria da pagina. **Sair sem confirmacao**
encerra esse acesso sem garantir recebimento. A equipe pode consultar o projeto
para verificar o que foi efetivamente gravado antes de preparar outra sessao.

## Entrar como profissional

Abra **Area da equipe** (`/equipe`) e escolha **Entrar com Google** usando sua
conta previamente cadastrada. Quem nao tem cadastro deve solicitar acesso ao
responsavel. Identidade Google e perfil sao verificados pelo servidor; e-mail
auxiliar nao concede permissao. Mesmo administradores precisam de vinculo
ativo ao projeto para acessar seus resultados.

O perfil **Consulta** acessa resultados e exportacoes autorizados. **Coleta e
importacao** tambem prepara sessoes e importa CSV. **Administracao** permite
gerenciar contas, projetos e vinculos, alem das operacoes de dados permitidas
por seu vinculo. Ao terminar, use **Encerrar sessao** e aguarde a confirmacao.

## Preparar convite

1. Selecione o projeto ativo no campo **Projeto** e localize **Preparar sessao**.
2. Informe **Codigo do participante** e **Visita da sessao**. Use pseudonimos
   definidos pela pesquisa, sem nome ou iniciais. Ambos aceitam de 1 a 64
   letras ASCII, numeros, ponto, hifen ou sublinhado. Exemplo sintetico:
   `SINTETICO_001`, visita `PILOTO_01`.
3. Clique em **Gerar convite**. O servidor fixa o projeto, participante, visita
   e sua conta como avaliador responsavel.
4. Entregue o codigo de uso unico por canal apropriado e confira a expiracao
   UTC mostrada na tela. **Abrir pratica em outra aba** abre a pagina onde o
   participante digita o codigo; ele nao e incluido no endereco.

O codigo aparece uma unica vez. Recarregar, sair ou trocar projeto apaga sua
exibicao, sem recuperacao posterior. Nao o coloque em URL, screenshot ou log.
**Preparar outra sessao** limpa a tela sem revogar o convite anterior.
**Revogar convite** so esta concluido depois da confirmacao do servidor;
resultados ja concluidos sao preservados.

Se a criacao nao for confirmada, a sessao pode ter sido criada sem que o codigo
chegasse a tela. Nao emita outra automaticamente: informe o responsavel e siga
a orientacao exibida. Um codigo consumido nao pode ser compartilhado entre
participantes nem reutilizado para repetir um principal interrompido.

## Consultar e exportar resultados

Em **Filtrar resultados**, escolha projetos, periodo, codigos de participantes,
visitas, avaliadores tecnicos, versoes, plataformas e instrumento; depois use
**Aplicar filtros**. Em multisselecao, use Ctrl/Cmd ou Shift e as setas. Opcoes
do mesmo campo combinam por OU; campos diferentes combinam por E. Campos
vazios nao restringem. **Limpar filtros** retorna ao projeto de preparacao.

O periodo e inclusivo: avaliacoes WEB usam a data UTC de inicio; registros
legados conservam a data civil original. Codigo igual em projetos diferentes
nao representa automaticamente a mesma pessoa. A consulta aceita ate 20
projetos e 5.000 avaliacoes completas; se exceder, restrinja os filtros.

Cards, graficos e tabela usam o conjunto completo carregado e um instrumento
por vez. Consulte o detalhe para conferir metadados, metricas e tentativas.
**Participante para evolucao** seleciona projeto e codigo para acompanhar
visitas, mantendo avaliacoes repetidas separadas. RT sem acertos e ausencia de
dado, sem substituir por zero. As visualizacoes nao oferecem interpretacao
clinica ou comparacao normativa.

Ha duas exportacoes diferentes:

- No detalhe Stroop, o CSV oficial individual contem as tentativas e preserva
  o [contrato de 21 colunas](../experimento/CSV_UNIFICADO.md), com nome mascarado
  e iniciais vazias.
- **Exportar visao filtrada** gera uma linha por avaliacao do instrumento e
  plataforma selecionados. Esse CSV agregado nao serve para importar tentativas.

Cada download revalida sua permissao. Se o acesso mudar, os dados mudarem
ou a consulta expirar, atualize a consulta completa antes de tentar novamente.
Arquivos baixados ficam sob custodia do profissional; nao os envie a canais
publicos. A WEB nao revela nomes/iniciais de participantes do historico.

## Importar CSV pela WEB

1. Selecione o projeto de destino e localize **Importar CSV**, disponivel aos
   perfis de coleta/importacao e administracao com vinculo ativo.
2. Escolha o CSV oficial do instrumento registrado, em UTF-8, ate 5 MiB e
   10.000 registros. Nao use o CSV agregado do painel.
3. Clique em **Minimizar e importar CSV**. Antes do envio, o navegador cria
   uma copia com nome `NAO_COLETADO` e iniciais vazias. O original permanece
   no dispositivo sem alteracao.
4. Aguarde **Importacao concluida** e consulte o resultado no projeto.

Avaliacao duplicada e rejeitada sem substituir dados. Se o envio nao for
confirmado, use **Consultar estado** e, quando indicado, **Reenviar a mesma
copia**. Preserve a pagina e o identificador da operacao ate resolver a
incerteza; iniciar uma nova operacao nao e a recuperacao da anterior.

Dados ja existentes no banco legado requerem um vinculo explicitamente
provisionado pelo operador para aparecerem na WEB. Criar um projeto de nome
igual nao concede acesso ao historico. Consulte a
[transicao e matriz de cobertura](TRANSICAO_WEB.md).

## Administrar contas e projetos

Com perfil de administracao, abra **Administracao** para cadastrar a identidade
Google verificada, ajustar perfil/e-mail auxiliar/estado, criar projetos e
atribuir vinculos. Use os identificadores retornados pelo login da propria
pessoa, pelo canal institucional; nao deduza identidade pelo e-mail. O ultimo
administrador ativo e protegido contra bloqueio ou rebaixamento concorrente.

Bloqueios e revogacoes impedem novas operacoes e podem invalidar sessoes ainda
abertas emitidas pelo profissional. Eles nao apagam resultados concluidos.
A atribuicao de vinculo a projeto e uma acao explicita; administrador global
nao recebe acesso a dados de pesquisa automaticamente.

## Ajuda rapida da WEB

- Login sem acesso: confira conta cadastrada, perfil, estado e vinculo com o
  responsavel. Nao envie senha, cookies ou codigos Google para suporte.
- Nenhum resultado: confira projeto, filtros e eventual mapa do historico;
  nao reimporte apenas para tentar tornar um registro visivel.
- Resultado ainda sem confirmacao: mantenha a pagina aberta e use a acao de
  reenvio oferecida. Consulte a equipe antes de repetir a tarefa.
- Acesso expirado ou revogado: solicite orientacao; nao reutilize convite
  consumido e nao tente retomar principal interrompido.
- Falha na consulta ou exportacao: atualize a consulta completa. Erro 429
  indica limite de requisicoes; aguarde antes de tentar novamente.
- Incidente: informe ao responsavel horario aproximado e mensagem exibida,
  sem dados de participantes, convites ou capturas identificaveis.

## Fluxo local preservado

O experimento PsychoPy gera um CSV oficial. O launcher importa esse CSV para
SQLite local, ou o importador explicito usa PostgreSQL. O Streamlit consulta
os resultados sem modificar o CSV bruto.

```text
PsychoPy -> data/*_trials.csv -> SQLite local -> dashboard Streamlit
```

O projeto e educacional e exploratorio. Ele nao e instrumento clinico, nao produz diagnostico e nao oferece comparacao normativa.

## Configurar o fluxo local PsychoPy e Streamlit

Se voce recebeu o projeto como ZIP, siga primeiro o
[guia por ZIP](USO_POR_ZIP_GITHUB.md). Em resumo:

- Windows: instale Python, execute `setup.bat` e depois `abrir_dashboard.bat`.
- Linux/macOS: instale Python, execute `bash setup.sh` e depois `bash abrir_dashboard.sh`.

O PsychoPy deve ser instalado separadamente do ambiente usado pelo dashboard.

## Executar o experimento

1. Abra o PsychoPy.
2. Entre na interface Builder.
3. Abra `stroop_go_nogo_ptbr.psyexp`.
4. Antes de uma coleta, rode o experimento em modo Pilot e confira instrucoes, pratica, respostas e tela de resultados.
5. Para a execucao desejada, preencha apenas os campos solicitados pelo formulario local.
6. Ao final, confirme que um CSV unificado com sufixo `_trials.csv` foi criado em `data/`.

Nao mova o `.psyexp` sozinho para outra pasta: ele depende dos arquivos versionados em `condicoes/` e da estrutura do projeto.

## Abrir o dashboard

Depois que houver um CSV oficial em `data/`:

- Windows: execute `abrir_dashboard.bat`.
- Linux/macOS: execute `bash abrir_dashboard.sh`.

O launcher usa o CSV `*_trials.csv` modificado mais recentemente, importa a avaliacao para `database/stroop_results.sqlite3` e inicia o Streamlit. Se a avaliacao ja estiver no banco, ela nao e duplicada.

Para escolher outro CSV ou reimportar uma avaliacao, consulte a
[instalacao multiplataforma](INSTALACAO_MULTIPLATAFORMA.md). O CSV de origem
nunca e alterado pelo launcher ou pelo dashboard.

## Encerrar

Feche a aba do navegador e encerre o processo do dashboard no terminal com `Ctrl+C`. Em operação PostgreSQL, os dados importados permanecem no banco; no fallback local, permanecem no SQLite.

## Cuidado com dados pessoais

No fluxo local, os dados ficam no computador do usuario, dentro de `data/` e
`database/`, ou no PostgreSQL explicitamente configurado. Na WEB, os resultados
confirmados ficam no banco do servidor. Pastas, bancos e exportacoes nao devem
ser publicados nem enviados junto com contribuicoes ao projeto. Nao coloque
dados reais em screenshots, issues publicas, mensagens de suporte ou exemplos
de documentacao.

Use `participant_id` como identificador tecnico. `participant_name` e informacao pessoal local e nao deve aparecer em nomes de arquivo, capturas publicas ou logs compartilhados.

## Ajuda rapida

- Python nao abre: reinstale uma versao compativel e confira o `PATH`.
- Setup informa ambiente gerenciado: use o script de setup, sem instalar pacotes globalmente.
- Streamlit ausente: execute o setup novamente e use o launcher do projeto.
- Banco ausente: gere um CSV oficial e abra o dashboard novamente.
- Nenhum CSV encontrado: confirme o sufixo `_trials.csv` dentro de `data/`.
- Cabecalho incompativel: use o CSV oficial sem edicao manual e consulte `../experimento/CSV_UNIFICADO.md`.

Para instrucoes detalhadas de Download ZIP e solucao de problemas, consulte o
[guia por ZIP](USO_POR_ZIP_GITHUB.md). Operadores da WEB devem seguir a
[transicao e manutencao](TRANSICAO_WEB.md) e o [runbook de recuperacao](WEB_RECUPERACAO.md).
