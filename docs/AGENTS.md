# Documentacao

Escopo: `docs/`. Herda todas as regras da raiz.

- Use o [indice](README.md) e agrupe documentos em `experimento/`, `dados/`,
  `seguranca/`, `operacao/`, `desenvolvimento/`, `arquitetura/` ou `legado/`.
  Roadmap WEB, progresso, registro e mapa estrutural permanecem nesta raiz.
- Escreva em portugues, de forma objetiva, e use links relativos para fontes
  canonicas em vez de duplicar contratos ou estados.
- Registre metodo em `experimento/DECISOES_DO_EXPERIMENTO.md`, interface em
  `experimento/UX_DECISIONS.md`, arquitetura em `arquitetura/ADR-*.md` e fatos datados em
  `REGISTRO_DE_ALTERACOES.md`. Altere documentacao arquitetural somente diante
  de decisao relevante, justificando motivo e impacto; preserve os ADRs anteriores.
- Estado legado fica em [Projeto Stroop Test.md](legado/Projeto%20Stroop%20Test.md);
  estado da evolucao web fica somente em [ROADMAP_WEB.md](ROADMAP_WEB.md).
  Nao misture IDs Wxx, etapas legadas 1–12 e fases historicas de implementacao.
- Leia e aplique o [protocolo Codex CLI](desenvolvimento/WORKFLOW_CODEX_CLI.md). Documentos
  auxiliares referenciam as fontes canonicas, sem copiar fichas, tabelas de
  estado, pesos, dependencias ou criterios de aceite.
- [PROGRESS.md](PROGRESS.md) e a memoria concisa de retomada: registre marcos,
  decisoes, problemas/bloqueios com evidencia, arquivos alterados, comandos e
  resultados de validacao e a proxima acao. Atualize a cada marco ou impedimento,
  mantendo contexto suficiente para compactacao, interrupcao ou fim de cota.
  Referencie IDs do roadmap sem criar outra contabilidade de progresso.
- Use `ROADMAP_WEB.md` e `arquitetura/ADR-*.md` nos papeis dos nomes genericos
  `ROADMAP.md` e `ARCHITECTURE.md`; nao crie documentos paralelos. Ajuste o
  roadmap somente com evidencia, preservando decisoes e aceite ainda pendente.
- Ao mudar regras operacionais, alinhe instrucoes, protocolo e trechos de
  retomada do roadmap/README, sem alterar o estado das etapas por presuncao.
- Exemplos devem ser sinteticos e nao podem conter nomes, IDs ou metadados reais.
- Ao criar ou renomear documentos, valide todos os links relativos afetados.
