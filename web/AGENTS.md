# Interface WEB

Herda as instrucoes da raiz. Fontes: [roadmap](../docs/ROADMAP_WEB.md),
[protocolo](../docs/experimento/PROTOCOLO_WEB.md) e
[contrato HTTP](../docs/desenvolvimento/CONTRATO_API_WEB.md).

- React controla navegacao, formularios e ciclo de vida. O motor jsPsych
  controla seu DOM, teclado e relogio monotono dentro de `ExperimentHost`;
  nao depender de renderizacoes React por quadro nem medir RT pela rede.
- Fontes de condicoes e snapshot aprovados governam tempos/cores/ordem. Nao
  transformar exemplos visuais, mocks ou fixtures em protocolo de coleta.
- Cliente HTTP usa caminhos relativos fixos sob mesma origem HTTPS e cookies
  HttpOnly; CSRF fica somente em RAM. Nao guardar resultados/credenciais em
  localStorage, sessionStorage, IndexedDB, service worker, arquivo ou URL.
- Nao incluir secrets em bundle, variaveis `VITE_*`, logs, mensagens de erro
  ou traces versionados. Erros publicos sao fechados e seguros em portugues.
- Dependencias diretas possuem versao exata; atualizar `package.json` e
  `package-lock.json` juntos, com necessidade comprovada e fonte primaria.
- Validar `npm ci`, `npm test`, `npm run typecheck`, `npm run build` e
  `npm run test:browser` conforme escopo. Testes de navegador usam somente
  dados sinteticos; mocks HTTP nao concedem aceite da integracao real W13.
- Registrar navegador/versao/SO observados, sem inferir suporte universal nem
  equivalencia temporal. Evidencia fisica e homologacao continuam gates proprios.
