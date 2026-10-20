# Interface WEB

Base React/TypeScript com navegacao por historico, orientacoes, acesso da equipe,
estados de carregamento/erro, cliente HTTP e execucao local jsPsych. O estado e o aceite ficam no
[roadmap](../docs/ROADMAP_WEB.md); protocolo e unidades seguem o
[contrato HTTP](../docs/desenvolvimento/CONTRATO_API_WEB.md).

## Executar e validar

Requer Node 24.15.0 ou posterior na linha 24, ou Node 26+. Dependencias exatas
e resolucao completa estao em `package.json`/`package-lock.json`.
Na raiz do repositorio:

```bash
cd web
npm ci
npm run dev
```

O servidor escuta somente `http://127.0.0.1:5173`. A navegacao funciona sem
backend. A area profissional consulta `/api/v1/auth/me`; autenticar/encerrar
sessao requer API servida na mesma origem HTTPS, com o proxy e as configuracoes
apropriadas. Vite isolado nao configura OIDC nem a integracao de sessao.
Nao trocar URLs relativas por origens externas nem habilitar CORS para contornar
esse requisito. Integracao completa de coleta e tratada pela etapa propria.

```bash
npm test
npm run typecheck
npm run build
npx --no-install playwright install --no-remove chromium firefox
npm run test:browser
```

`npm test` executa Vitest: cliente HTTP, ambiente, ciclo de vida e pratica com relogio controlado.
Playwright executa navegacao, historico/foco, loading/login, erro/retry e logout
em Chromium e Firefox, alem de quatro feedbacks, tecla mantida, repeticao e interrupcao da pratica. Somente a rede dos testes HTTP e interceptada, com fixtures
inequivocamente sinteticas; producao nao possui respostas simuladas. Nao executar
esses testes contra coleta real. `npm run preview` serve o build local em 4173.
`dist/`, `node_modules/`, traces e resultados de teste nao sao versionados.

## Campanha local W16

Campanha local W16: `npm run test:w16` usa a sessao grafica disponivel, Chrome
instalado e Firefox do Playwright, um worker, dez tentativas por navegador e
Escape separado, sem retries. Requer os binarios existentes; nao instala nada.
Leva cerca de 30 minutos. Usa teclado sintetico e API double; o motor jsPsych,
relogio e quadros sao reais. Mantenha a janela em foco durante a campanha.
A captura opt-in e ativada so nesse servidor local (porta 4186). Artefatos
`timing.json`/`summary.json` por tentativa e `results.json` ficam em
`test-results/w16/`, ignorado pelo Git. Preserve o diretorio antes de repetir,
pois o runner limpa o output da campanha. Invalidacoes do principal falham depois
da exportacao; falhas anteriores ao principal ficam em `results.json` e no
contexto de erro, sem inventar trilha de um bloco nao iniciado. Nao ha substituicao
silenciosa de tentativas. Este comando mede somente
o comportamento observavel por software no ambiente descrito, sem certificar
teclado fisico, todas as combinacoes suportadas ou recebimento no servidor.

## Organizacao e fronteiras

- `src/App.tsx`: telas e navegacao; `src/styles.css`: apresentacao responsiva,
  foco visivel e movimento reduzido, sem fontes ou recursos externos.
- `src/api/client.ts`: endpoints fixos, cookies same-origin, no-store, CSRF
  em RAM, validacao de resposta, timeout/cancelamento e erros sanitizados.
- `src/experiment/ExperimentHost.tsx`: recipiente de DOM imperativo com montagem
  e limpeza; o motor nao depende de renderizacoes React por quadro.
- `src/components/PracticePreparation.tsx`: filtro de ambiente, confirmacao e
  teste de teclado, inicio/repeticao e descarte de treino interrompido.
- `src/experiment/practice*.ts`: plugin jsPsych e runtime monotono com quatro
  condicoes-fonte, contagem, HUD e feedback; treino fica somente em RAM.
- `src/experiment/main*.ts`: motor principal e plugin jsPsych; calibracao de
  quadro na contagem, origem monotona unica, observacoes contiguas, HUD e gates
  temporais. Resultado completo fica em RAM; interrupcao descarta toda a serie.
- `src/experiment/summary.ts` e `src/components/ResultSummary.tsx`: metricas
  locais, mediana sem quantizacao, exibicao conforme Python e finalizacao com
  descarte de RAM. Nao oferecem download participante.
- `src/experiment/protocol.ts`: consome `../condicoes/web_protocol.json`
  compartilhado com a API e os CSVs-fonte de pratica/principal. Nenhum parametro metodologico
  e derivado de exemplos da interface. A sessao usa bootstrap e ordem da API, com
  confirmacao do inicio antes do motor.
- `src/**/*.test.*` e `e2e/`: testes de logica/DOM e navegador.

Nenhum resultado ou token e persistido por JavaScript. Segredos OIDC permanecem
no servidor. O acesso profissional valida cadastro/perfil pelo backend; a UI
nao confere autorizacao por conta propria.

Versoes e requisitos de Node foram consultados no registro npm em 2026-10-16.
Referencias primarias: [React](https://react.dev/learn/build-a-react-app-from-scratch),
[Vite](https://vite.dev/guide/), [Vitest](https://vitest.dev/guide/) e
[Playwright](https://playwright.dev/docs/test-configuration).
Resultados observados e limites de validacao ficam em
[PROGRESS.md](../docs/PROGRESS.md); o teste da interface nao certifica latencia
fisica nem valida todos os sistemas e equipamentos previstos para a pesquisa.

O filtro de user-agent e uma verificacao conservadora, sem prova de teclado
fisico ou homologacao. Ha confirmacao explicita e teste de pressionar/soltar
Espaco. Nao se exige desempenho minimo; repetir descarta o resumo anterior.

Os testes `@timing` executam em serie e sem traces para reduzir interferencia
no proprio ensaio de tempo real; os demais testes de navegador podem executar
em paralelo. Isso nao altera os limites temporais aplicados pelo motor.

Fixtures de paridade ficam em `../tests/fixtures/web_results_summary.json`,
carregadas apenas nos testes. O servidor de desenvolvimento permite somente
as pastas explicitas web/condicoes/fixtures; nao expor a raiz do repositorio.
O serializador CSV de servidor fica em `stroop/domain/web_export.py`; a rota
profissional autorizada foi implementada em W14.


Integracao sintetica HTTPS real (W13): com PostgreSQL descartavel ja iniciado,
configure `TEST_DATABASE_URL` para database cujo nome comece por
`stroop_etapa4_test_` e execute `npm run test:integration` nesta pasta. O harness
**recria o schema desse banco de teste**; nunca aponte para dados de pesquisa.
Exige dependencias Python da raiz em `.venv`, Node, navegadores Playwright e
OpenSSL. Usa portas locais 4373/4381, certificado efemero e proxy HTTPS somente
para testes. Encerra apenas processos que iniciou e remove certificado/chave.
Nao usa `.env`, nao altera VPS e nao comprova OIDC externo ou TLS de producao.

Os testes isolados usam doubles explicitamente em `e2e/support/`; os testes de
`e2e/integrated/` exercitam HTTP/API/PostgreSQL reais. Falhas de transporte podem
ser injetadas mantendo a gravacao e as respostas do backend reais. Convites e
cookies sinteticos nao devem aparecer em logs/traces nem ser versionados.
`ParticipantRun` coordena dados em RAM, recuperacao de recibo e reenvio; a trava
Web Locks impede motores concorrentes entre abas da mesma origem/perfil.

Painel profissional (W15): a area `/equipe` consulta projetos autorizados e
carrega todas as paginas do resultado filtrado antes de apresentar totais. Os
filtros combinados W15A sao enviados ao servidor; a exibicao permite ainda
selecionar instrumento/plataforma no conjunto carregado. Cursor ou ID repetido invalida a
consulta para evitar agregacao parcial/duplicada. Uma falha exige atualizar a
consulta; resultados parciais nao sao exibidos como completos.

Os cards Stroop reproduzem precisao media/mediana, mediana dos RTs por avaliacao,
participantes unicos e totais de erros. Sem hits, o RT e ausente; nao conta como
zero. Graficos mostram datas de inicio, precisao por visita, distribuicao de
RTs medianos e erros. Filtrar um participante num unico projeto mostra evolucao por visita. O detalhe
conserva metricas/tentativas e proveniencia, inclusive campos ausentes do legado.
Datas sem fuso nao recebem conversao implicita. Instrumentos adicionais exibem
suas proprias metricas no detalhe; a demonstracao sintetica registrada tem
cards/graficos/tabela proprios, sem graficos Stroop ou CSV inventado.

O download individual explicito usa CSV oficial W14; o botao `Exportar visao
filtrada` gera separadamente o CSV agregado W15C, ambos reautorizados no servidor
em cada clique. Apenas essas acoes solicitadas pelo profissional criam arquivo; consultas
ficam em RAM e sao descartadas na saida, expiracao, troca de projeto ou logout.
O navegador nao guarda dados em storage JavaScript. A area e limpa em pagehide;
restauracao de BFCache exige revalidar o acesso por recarga.

Coexistencia do MVP: Streamlit e seus launchers permanecem disponiveis para
importacao local autenticada, administracao operacional e exportacao agregada
historica. Esses recursos nao sao removidos nem implicitamente migrados ao
painel WEB. O painel WEB oferece detalhe, CSV oficial por avaliacao e CSV
agregado da visao filtrada; nao transmite nomes/iniciais pessoais do legado,
filtros por nome de participante/avaliador ou personalizacao de instrumentos.
Nao ha interpretacao clinica, normativa ou comparacao entre instrumentos.

Seguranca da pagina (W17): `security-headers.json` e a baseline testada no proxy
HTTPS sintetico, a ser consumida no empacotamento W19. Scripts/estilos/conexoes
sao restritos a mesma origem, sem unsafe-inline ou unsafe-eval. Os motores usam
propriedades CSS diretas; testes verificam pratica e principal sem violacoes.
A previa Vite e destinada a desenvolvimento e nao atesta headers de producao.

## Importar CSV pela equipe

Em `/equipe`, perfis `importacao` e `administracao` vinculados podem importar
um CSV registrado no projeto ativo selecionado. O navegador envia uma copia
com nome substituido por `NAO_COLETADO` e iniciais vazias; o original nao muda.
Limite de 5 MiB/10.000 registros. Em caso de resposta perdida, consulte o
estado ou reenvie explicitamente a mesma operacao. Contrato, estados e erros em
[CONTRATO_API_WEB.md](../docs/desenvolvimento/CONTRATO_API_WEB.md).

## Preparar uma sessao pela equipe

Em `/equipe`, entre com sua conta previamente cadastrada, selecione um projeto
ativo ao qual esteja vinculado e use `Preparar sessao` (perfil de coleta/importacao
ou administracao). Preencha `Codigo do participante` e `Visita da sessao` com
codigos pseudonimizados de 1–64 letras ASCII, numeros, ponto, hifen ou sublinhado.
O avaliador e a conta autenticada, fixada pelo servidor. Use somente sessoes
sinteticas enquanto os gates de pesquisa real permanecerem pendentes.

`Gerar convite` mostra o codigo uma unica vez, os dados da sessao e a expiracao
UTC. Entregue-o por canal apropriado. `Abrir pratica em outra aba` abre `/pratica`,
onde o participante informa o codigo; ele nunca integra o endereco. O participante
segue orientacoes, verificacao de teclado, pratica e principal. Recebimento
somente e confirmado apos recibo do servidor; os resultados podem ser consultados
no projeto e exportados no CSV oficial autorizado.

Trocar projeto, sair ou recarregar apaga o codigo exibido. Ele nao pode ser
recuperado. Uma resposta perdida pode ter criado a sessao; nao ha reenvio
automatico nem revogacao sem identificador conhecido. Informe o responsavel
antes de emitir outro convite nesse caso. `Preparar outra sessao` limpa a tela,
sem revogar o anterior. `Revogar convite` requer confirmacao do servidor; apos
confirmacao impede resgate/continuidade, preservando resultados ja concluidos.

## Consultar com filtros combinados

O seletor `Projeto` continua definindo a preparacao de sessoes. Em `Filtrar
resultados`, `Projetos da consulta` permite combinar ate 20 projetos autorizados.
Use Ctrl/Cmd ou Shift e as setas nos campos de multisselecao. Codigo igual em
projetos diferentes representa participantes distintos nos totais; o detalhe
e o CSV individual usam sempre o projeto da linha.

Escolha datas inclusivas, participantes, visitas, avaliadores tecnicos, versoes,
plataformas e instrumento, depois `Aplicar filtros`. As opcoes vem somente de
projetos autorizados no periodo/instrumento; campos vazios nao restringem.
Valores do mesmo campo combinam por OU e campos diferentes por E. O resumo
mostra os filtros aplicados; editar a selecao so modifica os resultados depois
de aplicar. `Limpar filtros` retorna ao projeto de preparacao, sem restricoes
adicionais. A selecao de exibicao continua mostrando um instrumento por vez.

O periodo usa a data da avaliacao: WEB em UTC, legado na data civil originalmente
registrada. Sem converter horarios legados em UTC. Identificadores de avaliadores
legados sem mapa aparecem como ausencia de identificacao tecnica.

O navegador so mostra totais apos completar todas as paginas/projetos, ate 5.000
avaliacoes por consulta. Acima disso, restrinja o periodo/projetos. Cada faceta
possui limite 200 por projeto; excesso pede periodo/instrumento mais restrito,
sem esconder opcoes por truncamento. Mudanca no conjunto durante paginacao ou
falha de acesso em qualquer projeto limpa o agregado; use `Atualizar consultas`.
A consistencia do CSV agregado e verificada para todos os projetos numa unica
transacao de leitura; snapshots expiram em 15 minutos. Falha ou expiracao exige
recarregar a consulta completa. O CSV agregado possui esquema proprio por
instrumento, nao e importavel como tentativas e permanece separado do CSV
oficial individual disponivel no detalhe autorizado.


## Tabela, detalhe e evolucao descritiva

A tabela Stroop apresenta projeto, avaliador tecnico, precisao total/Go/No-Go,
contagens das quatro respostas e RT mediano. O detalhe inclui IDs de sessao e
avaliacao, projeto, avaliador, inicio/conclusao, versoes/protocolo e tempos
observados quando disponiveis. Dados historicos ausentes ficam identificados,
sem criar fuso, identificacao de avaliador ou proveniencia WEB.

A comparacao de omissoes/comissoes identifica cada projeto. `Participante para
evolucao` seleciona a dupla projeto+codigo; visitas repetidas permanecem como
avaliacoes distintas em ordem de inicio e ID. Precisao (%) e RT mediano (s)
ficam em figuras separadas, com tabela alternativa. Ausencia de hits nao e RT
zero; precisao com denominador ausente aparece como ausencia.

O instrumento demonstrativo sintetico possui visao propria de `demo_total`
(count) e `demo_mean` (unit), por avaliacao, mantendo valores negativos quando
existirem e sem transformar unidades em percentuais. Outros codigos conservam
tabela neutra das metricas disponiveis. Selecionar instrumento preserva a
separacao de conjuntos; a UI nao consulta detalhe de cada linha para montar
cards, tabelas ou graficos. A exportacao agrega somente o instrumento e a
plataforma selecionados, com uma linha por avaliacao autorizada.

O perfil `administracao` tambem recebe a area **Administracao** para cadastrar
identidades Google verificadas, atualizar perfil/e-mail auxiliar/estado e
criar projetos e vinculos explicitos. Identidade usa `iss` + `sub`; e-mail nao
autoriza. Uma pessoa sem cadastro solicita acesso pelo canal institucional com
os proprios identificadores apresentados no retorno OIDC, sem autocadastro. O
ultimo admin ativo e protegido sob concorrencia; bloqueios e revogacoes sao
revalidados pelo backend e nao removem resultados. A area de resultados continua
exigindo vinculo de projeto inclusive para administradores globais.
