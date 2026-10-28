# Transicao, cobertura e manutencao WEB

Este documento orienta a operacao das funcionalidades implementadas e a
coexistencia com o fluxo local. O estado formal e os aceites permanecem no
[roadmap WEB](../ROADMAP_WEB.md); release publicada e evidencias operacionais
ficam no [registro da VPS](DEPLOY_WEB_VPS.md), na
[homologacao](HOMOLOGACAO_WEB.md) e no [registro de alteracoes](../REGISTRO_DE_ALTERACOES.md).
Este guia nao concede homologacao, aceite de implantacao ou liberacao para
dados reais por sua propria existencia.

## Matriz de recursos e continuidade

| Necessidade | Caminho WEB implementado | Continuidade e limite |
|---|---|---|
| Execucao Stroop Go/No-Go | Tutorial, convite, teclado, pratica e principal no navegador | PsychoPy Builder permanece disponivel; motor WEB tem protocolo e validacao proprios |
| Preparacao de coleta | Profissional vinculado informa projeto, pseudonimo e visita; emissao/revogacao de convite | Sem conta Google de participante; nao importar identidade civil para a WEB |
| Confirmacao de resultado | Recibo do servidor, recuperacao e reenvio do mesmo resultado mantido em RAM | Sem retomada de principal, resultado parcial ou armazenamento offline; fechar pagina pode perder envio pendente |
| Consulta e filtros | Projetos autorizados, periodo, participantes por codigo, visitas, avaliadores tecnicos, versoes, plataformas e instrumento | Consulta completa antes de agregar; restringir filtros quando atingir limites apresentados pela interface |
| Analise descritiva | Cards Stroop, tabela, detalhe, datas, precisao, RT, erros e evolucao por projeto+participante | Instrumentos separados; sem diagnostico, norma ou comparacao psicometrica |
| CSV oficial Stroop | Download individual autorizado no detalhe | Tentativas no contrato oficial; nome mascarado/iniciais vazias na WEB; arquivo local original permanece intacto |
| CSV agregado | Exportacao da visao filtrada, uma linha por avaliacao | Esquema por instrumento; nao serve de entrada ao importador de tentativas |
| Importacao CSV | Upload autenticado, minimizacao no navegador, validacao e auditoria por operacao | Original fica local; duplicata rejeitada sem sobrescrever; CLIs e importacao local permanecem disponiveis |
| Historico no mesmo PostgreSQL | Consulta somente apos mapa legado explicitamente autorizado | Nome de projeto coincidente nao concede acesso; nao ha migracao automatica de SQLite ou de outro banco |
| Historico fora do banco WEB | Importacao explicita de CSV oficial permitido para projeto escolhido | Sem sincronizacao automatica entre bancos; operador deve verificar proveniencia e duplicatas antes de importar |
| Contas e permissoes | Administracao de identidade Google verificada, perfil, estado, projetos e vinculos | Vinculo e necessario inclusive para admin consultar dados; o ultimo admin ativo e protegido |
| Dados identificaveis legados | Nomes e iniciais sao mascarados na consulta/exportacao WEB | Campos locais nao sao removidos do CSV ou banco original; nao existe filtro WEB por nome |
| Outros instrumentos registrados | Consulta de metricas e exportacao agregada; demonstracao sintetica tem visualizacoes proprias | Nao cria tarefa experimental adicional ou interpretacao clinica; nao mistura formulas Stroop com outros instrumentos |
| Operacao local | Launchers, importadores, diagnostico e Streamlit preservados | Continuam seguindo o backlog e procedimentos legados; coexistencia nao implica copia automatica de novas coletas WEB |

Uso pela equipe e participantes no [guia do usuario](GUIA_DO_USUARIO.md).
Contratos canonicos: [HTTP](../desenvolvimento/CONTRATO_API_WEB.md),
[CSV](../experimento/CSV_UNIFICADO.md),
[modelo de dados](../dados/MODELO_DE_DADOS.md) e
[escopo do historico](../arquitetura/ADR-003-escopo-legado-web.md).

## Preservar rastreabilidade do historico

Antes de disponibilizar registros antigos, o responsavel identifica o banco,
o projeto e a autorizacao para aquele conjunto. O operador provisiona o mapa
legado para projetos WEB de forma explicita; nao atribui dados por coincidencia
de rotulos. Desativar mapa, vinculo ou projeto bloqueia consulta pela WEB sem
apagar as avaliacoes.

Ao importar CSV, selecione conscientemente o projeto de destino e mantenha o
original sob custodia local. A copia minimizada enviada nao altera o arquivo
fonte. Preserve o identificador da operacao ate confirmar a importacao; perda
de resposta exige consultar estado ou reenviar a mesma operacao. Uma avaliacao
ja existente nao deve ser reimportada com outro identificador para contornar
a protecao de duplicatas.

No detalhe, confira ID da avaliacao, origem/plataforma, versoes, metadados e
tentativas. Campos historicos ausentes continuam ausentes: nao inventar fuso,
avaliador tecnico ou sessao WEB para registros PsychoPy. O CSV agregado nao
substitui o CSV de tentativas nem preserva todos os elementos do detalhe.

## Coexistencia e retorno operacional

Manter PsychoPy, Streamlit, fontes, launchers e bancos existentes. Nao ha
retirada de componente ou exclusao de dados autorizada por este guia.
A abertura local do dashboard continua por `abrir_dashboard.bat` ou
`bash abrir_dashboard.sh`, conforme o
[guia de instalacao](INSTALACAO_MULTIPLATAFORMA.md).

Uma falha de candidato deve seguir o [runbook WEB](WEB_RECUPERACAO.md) e o
[procedimento da VPS](DEPLOY_WEB_VPS.md): preservar volumes, registrar imagens
aceitas, validar backup/restauracao e retornar somente a aplicacao compativel.
Nao restaurar backup antigo sobre novas coletas nem executar `down -v`.

O rollback temporario para o dashboard legado preservado nao torna novas
coletas WEB visiveis no legado. Se ele for necessario, o operador comunica
essa limitacao, mantem o banco WEB e reconcilia dados apenas por procedimento
explicitamente autorizado. Para manter o retorno por mais tempo, revalidar
tambem a configuracao de renovacao TLS conforme o registro de implantacao.

## Rotina de manutencao

O responsavel pelo repositorio responde pelo produto, infraestrutura,
habilitacao de pesquisa, acesso e incidentes. Operadores devem conhecer o
[tratamento de dados](../seguranca/TRATAMENTO_DE_DADOS.md) e as
[regras de acesso](../seguranca/ACESSO_WEB.md); configuracoes, chaves e backups
permanecem fora do Git e dos canais de suporte.

| Momento | Acao do operador | Evidencia minima sem dados pessoais |
|---|---|---|
| Monitoramento recorrente | Conferir saude, disco, TLS, falhas e idade do backup conforme runbook | Horario, estado e alerta; sem cookies, payloads ou identificadores de participantes |
| Backup agendado | Conferir geracao criptografada e copia externa autorizada, com chave separada | Resultado, data, tamanho e checksum; falha exige acao do responsavel |
| Restauracao periodica | Restaurar isoladamente e validar migrations, integridade e contagens | Resultado do ensaio e duracao; nao usar banco operacional como destino |
| Mudanca de equipe | Conferir perfil/vinculos e revogar acessos sem necessidade vigente | Decisao e operacao administrativa; resultados concluidos preservados |
| Antes de atualizar | Registrar release/digests, backup restauravel, compatibilidade de schema/grants e retorno | Manifesto do candidato e verificacoes aprovadas |
| Depois de atualizar ou reiniciar | Conferir HTTPS, readiness, portas internas, login e fluxo sintetico | Versao efetiva, resultado do smoke e contagens preservadas |
| Falha ou incidente | Conter a falha, preservar dados e acionar responsavel pelo canal institucional | Horario, codigo fechado do erro, impacto e acao; sem copiar logs integrais |

Comandos e detalhes de agenda permanecem nas fontes operacionais:
[Docker WEB](WEB_DOCKER.md), [recuperacao](WEB_RECUPERACAO.md),
[hardening](HARDENING_PRODUCAO.md) e [implantacao VPS](DEPLOY_WEB_VPS.md).
O resultado local de um ensaio nao garante capacidade, RPO ou RTO da VPS;
usar as evidencias do ambiente alvo registradas na homologacao.

## Empacotar uma release completa

Use um commit identificado e um arquivo completo das fontes versionadas,
gerado por `git archive`, em vez de montar a release copiando somente API,
frontend e o Compose principal. O arquivo inclui as dependencias operacionais
indiretas, como `compose.restore-test.yaml`, usado pelo teste de restauracao.
Omiti-lo pode deixar a aplicacao saudavel enquanto o ensaio agendado de
recuperacao falha. Preserve tambem migrations, scripts, arquivos de condicoes
e contratos exigidos pelo pacote. Nao inclua worktree, `.env`, dados, exports,
logs ou chaves na transferencia.

Por exemplo, na raiz, apos validar e commitar o candidato:

```bash
(set -C; git archive --format=tar HEAD > /DESTINO-EXTERNO/release.tar)
git rev-parse HEAD
sha256sum /DESTINO-EXTERNO/release.tar
```

Registre o commit e checksum junto ao manifesto das imagens, transfira e
confira a integridade antes de extrair em novo diretorio de release. A release
deve conservar caminhos relativos e conter `compose.web.yaml` e
`compose.restore-test.yaml`; configuracoes preenchidas e secrets sao externos.
Teste a rotina de backup/restauracao a partir desse pacote extraido, nao
apenas do checkout de desenvolvimento. Depois de publicar, mantenha a release
anterior para retorno e registre a versao efetivamente ativa. Detalhes de
destino e troca de trafego seguem o procedimento da VPS.

## Revisao pelo responsavel antes do aceite

O responsavel deve percorrer o guia usando somente dados sinteticos, conferir
se consegue preparar e revogar convite, concluir uma sessao, localizar seu
recibo, filtrar, detalhar e exportar resultados, importar CSV e administrar
acessos conforme o perfil. A revisao operacional inclui localizar backup,
evidencia de restauracao, monitoramento e procedimento de retorno.

Registrar o que foi realmente executado e quaisquer limitacoes nos documentos
de evidencia; o aceite formal continua no roadmap. Liberacao para coleta real
continua dependendo dos requisitos especificos da pesquisa definidos pelo
responsavel e das configuracoes descritas nas regras de acesso, mesmo quando
a infraestrutura estiver publicada. Os limites temporais conhecidos ficam na
validacao WEB e nao sao removidos por atualizar documentacao ou infraestrutura.
