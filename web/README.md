# Interface WEB

Base React/TypeScript com navegacao por historico, orientacoes, acesso da equipe,
estados de carregamento/erro e cliente HTTP. O estado e o aceite ficam no
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

`npm test` executa Vitest: cliente HTTP em Node e ciclo de vida do host em DOM.
Playwright executa navegacao, historico/foco, loading/login, erro/retry e logout
em Chromium e Firefox. Somente a rede desses testes e interceptada, com fixtures
inequivocamente sinteticas; producao nao possui respostas simuladas. Nao executar
esses testes contra coleta real. `npm run preview` serve o build local em 4173.
`dist/`, `node_modules/`, traces e resultados de teste nao sao versionados.

## Organizacao e fronteiras

- `src/App.tsx`: telas e navegacao; `src/styles.css`: apresentacao responsiva,
  foco visivel e movimento reduzido, sem fontes ou recursos externos.
- `src/api/client.ts`: endpoints fixos, cookies same-origin, no-store, CSRF
  em RAM, validacao de resposta, timeout/cancelamento e erros sanitizados.
- `src/experiment/ExperimentHost.tsx`: recipiente de DOM imperativo com montagem
  e limpeza; o motor nao depende de renderizacoes React por quadro. Pratica e
  bloco principal sao entregas seguintes, conforme o protocolo aprovado.
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
