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
filtros de participante e visita sao enviados ao servidor; instrumento e
plataforma selecionam o conjunto carregado. Cursor ou ID repetido invalida a
consulta para evitar agregacao parcial/duplicada. Uma falha exige atualizar a
consulta; resultados parciais nao sao exibidos como completos.

Os cards Stroop reproduzem precisao media/mediana, mediana dos RTs por avaliacao,
participantes unicos e totais de erros. Sem hits, o RT e ausente; nao conta como
zero. Graficos mostram datas de inicio, precisao por visita, distribuicao de
RTs medianos e erros. Filtrar participante mostra evolucao por visita. O detalhe
conserva metricas/tentativas e proveniencia, inclusive campos ausentes do legado.
Datas sem fuso nao recebem conversao implicita. Instrumentos adicionais exibem
suas proprias metricas no detalhe, sem graficos Stroop ou CSV inventado.

O download explicito usa CSV oficial W14, reautorizado no servidor em cada
clique. Apenas essa acao solicitada pelo profissional cria arquivo; consultas
ficam em RAM e sao descartadas na saida, expiracao, troca de projeto ou logout.
O navegador nao guarda dados em storage JavaScript. A area e limpa em pagehide;
restauracao de BFCache exige revalidar o acesso por recarga.

Coexistencia do MVP: Streamlit e seus launchers permanecem disponiveis para
importacao local autenticada, administracao operacional e exportacao agregada
historica. Esses recursos nao sao removidos nem implicitamente migrados ao
painel WEB. O painel WEB oferece detalhe e CSV oficial por avaliacao; nao
transmite nomes/iniciais pessoais do legado, nao oferece exportacao agregada,
filtros por nome de participante/avaliador ou personalizacao de instrumentos.
Filtros por periodo/versao e exportacao agregada continuam no Streamlit neste
MVP. Nao ha interpretacao clinica, normativa ou comparacao entre instrumentos.
