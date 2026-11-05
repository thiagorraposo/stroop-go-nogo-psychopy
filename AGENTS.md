# Instruções para agentes

## Missão e fontes canônicas

Plataforma Web modular para aplicação, gerenciamento e análise de avaliações
cognitivas, começando pelo Stroop Go/No-Go. React/TypeScript/Vite, FastAPI,
PostgreSQL, jsPsych e infraestrutura WEB já existem: reutilizar e revalidar,
sem presumir migração do zero nem equivalência com PsychoPy.

Experimento original Stroop Go/No-Go para uso educacional e pesquisa
exploratoria. Nao e instrumento clinico, diagnostico ou normativo. A nova
versao WEB sera usada para coleta de dados por um grupo de pesquisa do qual o
responsavel pelo repositorio participa; seu publico inclui os participantes da
pesquisa em geral. O responsavel pelo repositorio responde pelo produto e pela
infraestrutura. A hospedagem prevista e uma VPS ja adquirida e o dominio ja
existe; disponibilidade desses recursos nao autoriza publicar, configurar
servicos externos ou fazer deploy sem instrucao explicita.

Estado, marcos M0–M10, tarefas WEB, aceite, progresso, riscos, bloqueios e próxima
ação ficam **somente** em [docs/Projeto Stroop Test.md](docs/Projeto%20Stroop%20Test.md).
Inicialização: ler este arquivo, [workflow](docs/WORKFLOW_CODEX_CLI.md), backlog e
AGENTS aplicáveis; conferir Git/branch/remotos/evidências. Depois ler apenas ficha,
requisitos e contratos necessários. Não repetir auditoria sem divergência concreta.
[Arquitetura](docs/ARQUITETURA_WEB.md), [requisitos/matriz](docs/REQUISITOS_E_RASTREABILIDADE.md)
e [auditoria](docs/AUDITORIA_REPLANEJAMENTO.md) têm responsabilidades distintas.
ROADMAP_WEB e PROGRESS são endereços de navegação; arquivos em docs/legado são
históricos congelados, sem execução/progresso concorrentes. Não transferir 87%.

## Escopo e comandos

- `mostrar status`: somente leitura; consultar backlog/Git e distinguir evidências históricas/atuais.
- `continue o projeto`: autoriza tarefas prontas do marco vigente, dependências satisfeitas; implementar, testar, validar e registrar. Encerrar no limite do marco, sem avançar outro implicitamente.
- `validar marco atual`: conferir critérios/testes e registrar; não implementar funções novas.
- `replanejar`: revisar impactos, requisitos/decisões/dependências e preservar histórico; não implementar por implicação.

A missão documental de 2026-11-04 termina em M0 após validação/commit/push.
Implementação requer autorização posterior. Aliases antigos não retomam Wxx,
VPS ou etapas 11/12: consultar o workflow vigente. Decisões técnicas reversíveis
são autônomas; bloqueio localizado não impede tarefas independentes autorizadas.
Subagentes só com benefício concreto e escopo/arquivos/entregáveis claros;
principal integra e confere aceite. Não paralelizar edições conflitantes.

## Fronteiras e proteção

- Preservar código fora do escopo, dados, secrets e alterações preexistentes.
  Nunca abrir dados identificáveis, .env operacional ou backups para investigar.
  Apenas fixtures inequivocamente sintéticas; não versionar logs/exports/coletas.
- Domínio sem UI/IO/HTTP/driver; ingestão depende do domínio; casos de uso e
  persistência não importam CLIs/dashboard. Reutilizar fórmulas Python oficiais.
- Método: [decisões](docs/experimento/DECISOES_DO_EXPERIMENTO.md) e
  [protocolo](docs/experimento/PROTOCOLO_WEB.md); campos/fórmulas:
  [modelo](docs/dados/MODELO_DE_DADOS.md); payloads:
  [contrato HTTP](docs/desenvolvimento/CONTRATO_API_WEB.md). Não duplicar contratos.
- Não alterar paradigma, tempos, estímulos, regras, métricas, CSV ou validade
  científica sem decisão documentada do responsável. Versão local e WEB distintas.
  Medição do browser/gates não provam latência física ou equivalência psicométrica.
- PsychoPy exclusivamente referência histórica/metodológica da plataforma;
  não editar *_lastrun.py. Streamlit segue preservado na transição; sua retirada
  exige autorização. Preservar launchers/CLIs e não modificar coletas existentes.
- Motor jsPsych controla DOM/teclado/relógio fora do render React. Não criar
  armazenamento de resultado/credencial no cliente ou retomada contrária a D2.
- Não reduzir OIDC, CSRF, cookies seguros, grants ou acesso por projeto. Migrations
  existentes imutáveis; novas alterações de schema só na tarefa autorizada.
- Decisões metodológicas, operações destrutivas, migrações/dados reais, credenciais
  sensíveis, produção/deploy, merge main, tags e reescrita de histórico exigem
  autorização específica. VPS/domínio existentes não a concedem.

## Validação e continuidade

Para cada tarefa: ler fonte → verificar dependências → executar → testar →
conferir todos critérios → registrar evidência/data/SHA → atualizar vínculos,
estado e próxima ação no backlog → registrar mudança relevante no histórico.
Documento/código/push não provam conclusão funcional. Skips/doubles não substituem
integração real. Não inventar CI aprovada. Testes proporcionais e suites existentes;
PG descartável com prefixo stroop_etapa4_test; frontend Vitest/tipos/build e
navegadores/HTTPS quando exigidos. Sempre git diff --check; documentos também
exigem links e consistência. Não instalar/atualizar dependência incidentalmente.

## GitHub Flow adaptado

main estável; branch coesa docs/feat/fix/refactor/test/chore por marco ou entrega.
Antes: status/branch/remotos, preservar alterações locais, fetch quando acessível,
conferir main/origin; sincronizar só com fast-forward seguro e base apropriada.
Reutilizar branch adequada. Não descartar trabalho para obter árvore limpa.

Commits e pushes autônomos autorizados após unidade coerente validada, Conventional
Commits em português, staging só de arquivos/hunks da tarefa. Primeiro push com
upstream; sem push direto em main, force push, bypass ou exclusão remota.
**Não criar PR automaticamente e não executar merge automático.** Integração à
main exige autorização específica e proteções/revisões vigentes; não alterá-las.
Se houver bloqueio de envio, preservar commits, registrar causa e pendência.

CI existente permanece ativa; push pode disparar workflows conforme gatilhos.
Distinguir teste local e Actions por SHA, falhou/não executado/não verificado.
No fechamento registrar branch, commits reais, resultado do push, CI, limitações
e próxima tarefa. [Contribuição](CONTRIBUTING.md) e workflow detalham operações.
