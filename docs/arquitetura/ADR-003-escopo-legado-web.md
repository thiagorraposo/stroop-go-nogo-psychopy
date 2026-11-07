# ADR-003 — Vinculo explicito para consulta de dados legados pela WEB

Nota de 2026-11-04: decisão histórica preservada. [ADR-004](ADR-004-replanejamento-plataforma.md)
consolida direção atual e substitui orientações antigas de backlog/comandos/Git;
não revoga regras metodológicas ou mapa explícito de legado.

Data: 2026-10-16. Decisao tecnica de autorizacao para W14; implementacao e
aceite permanecem no [roadmap](../ROADMAP_WEB.md).

## Contexto

Avaliacoes WEB possuem `web_assessments.project_id`. Avaliacoes locais possuem
somente `assessments.project`, um rotulo textual historico. A API permite criar
projetos e gerir vinculos profissionais. Associar automaticamente o rotulo
legado ao codigo de um projeto novo permitiria obter acesso a dados existentes
criando um codigo coincidente. Autenticacao e vinculo ao projeto novo nao
comprovam autorizacao sobre a coleta antiga.

## Decisao

A migration aditiva `0007_web_legacy_project_links.sql` cria um mapa explicito
entre um rotulo legado e um projeto WEB. O mapa inicia vazio, sem consultar ou
migrar coletas. Cada rotulo legado pertence a no maximo um projeto WEB; um
projeto pode reunir rotulos explicitamente autorizados. A desativacao do mapa,
do projeto, do usuario ou do vinculo profissional impede o acesso.

Somente a operacao autorizada provisiona o mapa. Nao criar uma rota de escrita
para ele nem preencher por coincidencia de nomes/codigos. A aplicacao de uma
migration nao concede por si acesso a nenhum dado legado. Configuracao real e
acoes no host continuam sujeitas ao workflow operacional do usuario.

As consultas usam credencial dedicada de leitura (`API_READ_DATABASE_URL`) e
transacao somente leitura; autenticacao e limites de frequencia continuam na
conexao propria. Ausencia de configuracao de leitura gera indisponibilidade
fechada, sem fallback para a credencial de escrita. Os grants de producao devem
permitir somente SELECT nas tabelas necessarias, incluindo o mapa.

## Consequencias

Preserva o acesso profissional ao legado exigido pelo produto mediante escopo
explicito, sem reescrever avaliacoes ou alterar o dashboard local. Novos projetos
nao herdam dados por nome. Os testes devem comprovar colisao de codigos sem
acesso, mapa explicito com acesso, desativacao, acesso cruzado e mascaramento de
nome/iniciais. Exportacao permanece exclusiva de profissionais vinculados.

## Referencias

- [Acesso WEB](../seguranca/ACESSO_WEB.md).
- [Contrato HTTP](../desenvolvimento/CONTRATO_API_WEB.md).
- [Arquitetura modular](ADR-001-evolucao-web.md).
