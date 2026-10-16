# API web planejada

Diretorio reservado para o adaptador HTTP Python/FastAPI. Nesta preparacao
estrutural existe apenas documentacao; nenhuma rota, dependencia ou servico foi
criado.

A API consumira o pacote [stroop](../stroop/) e os casos de uso extraidos dos
importadores conforme o [roadmap](../docs/ROADMAP_WEB.md). Transporte HTTP,
autenticacao, configuracao e composicao pertencem a este diretorio; regras do
experimento e formulas pertencem ao nucleo.

Criar arquivos e dependencias somente na etapa correspondente. A organizacao
interna sera definida a partir das rotas reais, com routers e composicao
simples; nao criar camadas vazias. Decisoes em
[ADR-001](../docs/arquitetura/ADR-001-evolucao-web.md).
