# ADR-008: Paridade operacional, transição do legado e simplificação em três eixos (CHG-006)

- **Status:** Aceito (aprovado na governança de transição M7 em 2026-11-08)
- **Data:** 2026-11-08
- **Decisores:** Proprietário do repositório / responsável pelo produto e infraestrutura
- **Rastreabilidade:** `CHG-005`, `CHG-006`, `ADR-003`, `ADR-004`, `ADR-007`, `WEB-025`, `WEB-026`, `WEB-027`, `WEB-028`

## Contexto e problema

Historicamente, o experimento Stroop Go/No-Go dependia de múltiplos instrumentos operacionais desconectados:
1. **PsychoPy Builder (`stroop_go_nogo_ptbr.psyexp`):** runner local em Python/Desktop que executava a tarefa e gravava CSVs brutos em disco local, exigindo configuração prévia de Python e digitação manual de identificadores.
2. **Dashboard Streamlit (`dashboard/app.py`):** interface analítica em Python/Streamlit que consumia arquivos CSVs locais e bancos SQLite/PostgreSQL legados, provendo análise descritiva em tela única reativa.
3. **Planilhas manuais e uploads fragmentados:** a equipe precisava associar manualmente participantes a visitas e importar CSVs via upload na interface ou CLIs.

Com a consolidação da plataforma WEB modular e a introdução dos cadastros centrais de pacientes e avaliadores (`ADR-007` / `CHG-005`), tornou-se necessária a definição formal da transição operacional (`M7` / `WEB-028`), garantindo total paridade com as facilidades do Streamlit e do PsychoPy Runner, sem descontinuar fisicamente ferramentas legadas nem quebrar coletas anteriores.

## Decisão

A plataforma Stroop Web adota a **arquitetura de fluxo em 3 eixos operacionais** (`CHG-006`), proporcionando fluidez superior à soma dos sistemas legados:

```
                      ┌──────────────────────────────────────────────┐
                      │          PLATAFORMA STROOP WEB               │
                      └──────────────────────┬───────────────────────┘
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      ▼                                      ▼                                      ▼
┌───────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────┐
│          EIXO 1           │  │          EIXO 2           │  │          EIXO 3           │
│   APLICAÇÃO DIRETA EM     │  │     ANÁLISE REATIVA EM    │  │  EXPORTAÇÃO AVANÇADA E    │
│      UMA ÚNICA ETAPA      │  │     TELA ÚNICA (ESTILO    │  │       INTERCÂMBIO         │
│   (ESTILO PSYCHOPY RUNNER)│  │         STREAMLIT)        │  │       CIENTÍFICO          │
├───────────────────────────┤  ├───────────────────────────┤  ├───────────────────────────┤
│ • Seleção de paciente e   │  │ • Visão geral integrada:  │  │ • Retirada total de       │
│   avaliador cadastrados   │  │   KPIs, gráficos e tabela │  │   upload CSV no produto   │
│ • Modalidade Presencial:  │  │ • Filtros reativos e      │  │ • CSV canônico 21 colunas │
│   botão "Iniciar Agora"   │  │   multi-seleção imediata  │  │ • 5 granularidades        │
│ • Modalidade Remota:      │  │ • Detalhamento de sessões │  │ • Roundtrip 100% testado  │
│   link de convite único   │  │ • Preservação de métricas │  │ • Vínculo explícito de    │
│ • 100% motor jsPsych D5   │  │   oficiais sem distorção  │  │   entidades legadas       │
└───────────────────────────┘  └───────────────────────────┘  └───────────────────────────┘
```

### 1. Eixo 1 — Aplicação direta em 1 etapa (estilo PsychoPy Runner)
- **Preparação unificada:** o profissional prepara a avaliação selecionando o paciente cadastrado (com autocomplete) e o avaliador responsável ativo em formulário de etapa única, eliminando erros de digitação de IDs.
- **Dupla modalidade de condução:**
  - *Presencial ("Iniciar Agora"):* abre diretamente o ambiente experimental no navegador do avaliador para aplicação assistida em laboratório/consultório.
  - *Remota:* emite link/código de uso único (expiração de 30 min) para envio ao participante.
- **Preservação científica estrita:** apresentação com contorno branco `stroop-web-outline/1.0.0` (`CHG-003`), 16 tentativas do bloco principal, ausência de feedback de precisão em tempo real e gates temporais D5 (estímulo 500 ms, resposta 400 ms, feedback de treino 800 ms).

### 2. Eixo 2 — Análise reativa em tela única (estilo Streamlit)
- **Fluidez em tela única:** o módulo *Dashboard / Visão Geral* e o módulo *Resultados e Análises* consolidam a facilidade analítica instantânea característica do Streamlit:
  - KPIs agregados (total de avaliações, participantes, média/mediana de precisão e tempo de reação, erros de comissão e omissão).
  - Distribuição de respostas, precisão por visita e contagem temporal.
  - Visualização detalhada de tentativas e metadados com navegação acessível por teclado.
- **Filtragem reativa:** painel de filtros combinados (período, visitas, avaliadores, instrumentos, plataformas e status de validação) com atualização imediata sem recarregar a aplicação.

### 3. Eixo 3 — Exportação avançada, intercâmbio e compatibilidade histórica
- **CSV exclusivamente para exportação:** retirada total da tela de importação CSV (`CsvImportPanel.tsx`) e bloqueio dos endpoints de upload de avaliações no modo produto (`POST/GET /api/v1/projects/{project_id}/imports/{operation_id}` retornando `410 Gone`), garantindo fonte única de verdade no fluxo web.
- **Exportação multi-granularidade:** cinco níveis estruturados (`pacientes`, `avaliacoes`, `tentativas`, `metricas`, `stroop_21_colunas`), com suporte a modo desidentificado seguro e modo nominal autorizado, protegidos contra injeção de fórmulas CSV.
- **Compatibilidade e roundtrip:** comprovado roundtrip do CSV exportado com `analisar_stroop.py` e o importador SQLite oficial (`import_csv`), preservando as 12 métricas oficiais.
- **Vínculo explícito de legados:** procedimento auditado (`web_legacy_entity_links` e `web_registry_audit_events`) para associar registros pseudonimizados anteriores aos cadastros centrais, proibindo qualquer fusão automática por coincidência textual.

### 4. Preservação física e política de descontinuação
- Os launchers locais (`abrir_dashboard.bat`, `abrir_dashboard.sh`), scripts Python (`scripts/analisar_stroop.py`, `scripts/importar_csv_sqlite.py`) e o código fonte do dashboard Streamlit permanecem **100% preservados no repositório**, sem remoção física de arquivos.
- A substituição do uso operacional pelo produto WEB ocorre de forma segura e progressiva, mantendo os componentes locais disponíveis como contingência e referência metodológica.

## Consequências

- **Positivas:**
  - Fim da fragmentação entre ferramentas desktop e web.
  - Redução drástica da carga cognitiva do operador e eliminação de digitação manual de IDs.
  - Rastreabilidade longitudinal perfeita de pacientes e avaliadores.
  - Garantia de paridade funcional completa com Streamlit e PsychoPy.
- **Salvaguardas:**
  - Nenhuma perda de dados legados ou alteração em coletas reais existentes.
  - Auditoria estrita em qualquer associação de legados.
  - Total isolamento de ingestão legado para suites técnicas internas.
