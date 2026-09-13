# Múltiplos instrumentos

Esta etapa define a extensão do sistema para instrumentos diferentes sem misturar
suas métricas. O contrato comum reutiliza `assessments` para metadados da sessão
e `assessment_metrics` para resultados calculados. `test_code` e `test_version`
identificam o instrumento e sua versão em todas as avaliações.

## Adaptadores

Os adaptadores ficam em `scripts/instrumentos.py` e retornam uma avaliação
normalizada com metadados, métricas e, quando aplicável, tentativas. Cada
adaptador valida seu próprio cabeçalho, campos, unidades, valores ausentes e
fórmulas antes de qualquer gravação.

O adaptador `stroop_go_nogo_ptbr` preserva integralmente o CSV de 21 colunas, as
quatro regras de resposta, as fórmulas e as tentativas em `trial_results`. O
adaptador `instrumento_sintetico_demo` é somente uma prova técnica, sem
interpretação clínica: aceita duas métricas demonstrativas e não cria linhas em
`trial_results`.

Um novo instrumento deve:

1. definir um `test_code` estável e versões suportadas;
2. declarar seu cabeçalho e validar todos os campos antes da persistência;
3. documentar cada métrica, unidade, fórmula e regra de ausência;
4. retornar metadados comuns e métricas normalizadas;
5. adicionar testes sintéticos de coexistência e de rejeição de métricas de
   outro instrumento;
6. receber uma visão em `dashboard/instrumentos.py` antes de aparecer no
   dashboard.

Não se deve usar uma métrica de outro instrumento nem preencher
`trial_results` com colunas que não representem tentativas do Stroop. Dados
brutos específicos de instrumentos futuros exigem decisão e armazenamento
próprios antes de serem incorporados.

## Dashboard

O dashboard filtra por um único instrumento por vez. Cards, gráficos, tabela,
detalhe e exportação usam os códigos registrados na visão selecionada. Assim,
avaliações de testes diferentes não entram na mesma média, gráfico ou arquivo
exportado. A visão demonstrativa exibe somente suas métricas e não apresenta
detalhe de tentativas.

## Limites

Os instrumentos previstos no backlog ainda dependem da confirmação de campos,
unidades, repetições, fórmulas, interpretação e dados permitidos. Esta etapa não
inventa regras para DASS-21, TUG, Digit Span, EEG ou bateria frontal. O
instrumento demonstrativo existe apenas para validar a arquitetura com dados
inequivocamente sintéticos.
