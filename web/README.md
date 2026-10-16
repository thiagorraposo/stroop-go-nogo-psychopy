# Interface web planejada

Diretorio reservado para a interface React/TypeScript e o motor de tarefa
jsPsych. Nesta preparacao estrutural existe apenas documentacao; nenhuma tela,
pacote npm ou funcionalidade web foi implementada.

O navegador sera responsavel pela apresentacao dos estimulos e captura temporal
do teclado. O backend validara os resultados recebidos e calculara as metricas
oficiais. A implementacao seguira o [roadmap](../docs/ROADMAP_WEB.md) e o
[ADR-001](../docs/arquitetura/ADR-001-evolucao-web.md).

Separar a tarefa experimental das telas de navegacao e do cliente da API ao
implementar os primeiros modulos. Criar configuracoes, dependencias fixadas e
testes apenas nas etapas que os utilizarem.
