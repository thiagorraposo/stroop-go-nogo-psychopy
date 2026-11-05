# Workflow canônico do Codex CLI

Mensagens abaixo são comandos de trabalho do usuário, não scripts. Fontes:
[AGENTS](../AGENTS.md), [backlog único](Projeto%20Stroop%20Test.md),
[requisitos](REQUISITOS_E_RASTREABILIDADE.md), [arquitetura](ARQUITETURA_WEB.md).
Históricos Wxx/etapas 1–12 não selecionam execução. Esta versão substitui o
protocolo anterior de avanço contínuo entre marcos e PR/merge automático.

## Inicialização mínima

1. Ler AGENTS raiz e os aplicáveis, workflow e Retomada do backlog.
2. Conferir status, branch, remotos, HEAD, upstream e commits locais sem push;
   preservar cada alteração preexistente. Não abrir secrets/dados reais.
3. Ler ficha do marco/tarefa autorizados, dependências/decisões e evidências.
   Consultar requisitos, contrato científico/HTTP e testes apenas do escopo.
4. Verificar divergência concreta antes de repetir inventário. Registrar conflito
   documentação/código sem apagar aprovação histórica nem inferir funcionamento.
5. Apresentar plano breve e executar o trabalho autorizado. Não pedir confirmação
   para escolhas técnicas reversíveis; registrar hipótese quando não for decisão
   científica/de produto/privacidade que exija responsável.

## mostrar status

Somente leitura, inclusive backlog e Git. Informar contagem de entregáveis
aceitos, marco, tarefa em andamento, bloqueios/decisões, prioridade, próxima
executável e risco principal. Separar evidência histórica da executada na sessão;
ciência de teste anterior não é reexecução. Não alterar arquivos, instalar,
fazer commit/fetch/push ou consultar produção implicitamente. Se houver dúvida
sobre estado remoto, informar que não foi atualizado.

## continue o projeto

Autoriza implementação no marco vigente selecionado pelo backlog, salvo escopo
expresso mais restrito. Após M0, a primeira autorização posterior seleciona M1 e
WEB-001. A missão documental original não concedia essa autorização; consultar
o registro da sessão e o marco vigente na Retomada do backlog.

Para reproduzir a base existente em M1, seguir a
[receita local](desenvolvimento/BASELINE_LOCAL.md), com evidência apenas no backlog.

Selecionar tarefa PRONTA ou dependência interna coesa pronta. Verificar decisões
externas antes do trabalho dependente. Mudar para EM_ANDAMENTO quando iniciar.
Implementar comportamento observável preservando legado/contratos; sem funções
antecipadas ou dados reais. Testar e corrigir falhas introduzidas; registrar
comandos, ambiente, resultado, falhas/skips, limites e SHA. Usar EM_VALIDACAO
quando entrega estiver disponível e aceite ainda em conferência.

Atualizar matriz com testes reais e referência à evidência do backlog; conferir
cada critério e só então CONCLUIDA. Registrar branch, commits, push e CI por SHA.
Aprovar marco apenas quando todas tarefas e critérios da ficha forem comprovados.
Continuar automaticamente tarefas independentes autorizadas **dentro do marco**;
não avançar a outro marco sem autorização posterior. Encerrar com próxima ação
exata e estado persistido; nenhuma sessão conclui tarefa só por terminar o turno.

Se bloqueado: causa, evidência, responsável, ação de desbloqueio e dependentes no
backlog; marcar BLOQUEADA apenas quando impedimento concreto impedir a tarefa.
Dependência ainda não concluída mantém PENDENTE. Pode executar outra pronta do
mesmo marco. Credenciais, decisão metodológica/produto material, autorização de
risco ou recurso inacessível são os pontos de intervenção humana indispensáveis.

## validar marco atual

Não implementa funcionalidade nova. Conferir todos critérios/tarefas, executar
verificações proporcionais e registrar data/HEAD/comando/resultado. Distinguir
aprovação local, skips, double, integração real, medição física e Actions. Falta
de ferramenta/evidência obrigatória mantém critério não comprovado, não vira
aceite com ressalva automático. Apontar regressão e abrir correção autorizável;
não apagar conclusão histórica: registrar evidência nova e impacto atual.

Documentação: links relativos/âncoras, IDs/dependências, fonte única, Git diff
--check e revisão de escopo. Código: testes focados e regressão apropriada;
PG real descartável nos critérios transacionais; frontend tipos/build/DOM;
HTTPS/Playwright e medições manuais apenas quando exigidos. Não executar suites
pesadas apenas para validar uma edição documental.

## replanejar

Registrar motivo e evidência, mudança CHG no backlog, requisitos afetados,
componentes/testes a revisar, decisões/ADRs, dependências/prioridades e necessidade
de aprovação externa. Preservar IDs e histórico; não marcar concluído como
pendente sem regressão comprovada ou novo escopo explícito. Arquivar fonte
anterior quando a reorganização for material; deixar ponte de navegação, sem
segundo backlog ativo. Progresso muda só por aceites/alteração rastreada de escopo.
Replanejamento não autoriza implementação por implicação.

## Git e encerramento

GitHub Flow adaptado sem PR/merge automático, conforme [CONTRIBUTING](../CONTRIBUTING.md).
Status/branch/remotos → preservar worktree → fetch quando acessível em sessão de
escrita → conferir base → sincronização ff-only se segura → branch coesa.
Não criar outra branch se a atual for adequada. Base com trabalho não integrado
pode ser preservada com justificativa, sem descartar commits para partir de main.

Depois de validar unidade coerente: diff --check, revisar diff/status, adicionar
somente tarefa, commit Conventional Commits em português e push com upstream.
Push falhou: investigar sem sobrescrever histórico, registrar causa/pendência;
não força, não altera proteção. PR e merge não são automáticos. main não recebe
push direto. Deploy, integração, tags, dados reais e operações destrutivas têm
aprovação específica e não decorrem de commit/push.

No backlog: ID, estado/aceite, branch, SHA real, testes/evidências/data, limitações,
push e CI. Evitar autorreferência de SHA: registrar hash da entrega no fechamento
posterior ou consulta Git inequívoca para o próprio fechamento. Não criar commits
artificiais só para atualizar hash. CI existente dispara PR/main/manual; push de
branch não implica execução. Actions não executado/não verificado é um estado
válido de registro, não equivalente a aprovado. Nunca desabilitar checks para
adaptar fluxo. M8 planeja formalização de CI sem alterar política/proteções agora.

Final: resultado, arquivos, validações, riscos/pendências, branch/commits/push/CI
e próxima tarefa. Na missão documental: parar após M0 validado/versionado/enviado,
sem iniciar React/API/migrations/produção. A autorização final de versionamento
substituiu as proibições iniciais de add/commit/push da missão.

## Compatibilidade de comandos antigos

`mostrar status web` é alias de mostrar status. `continue web`, `execute Wxx`,
`validar etapa atual` e `validar etapa web Wxx` não reiniciam fichas arquivadas:
identificar intenção e mapear tarefa WEB/marco vigente com escopo explícito.
Na ausência de mapeamento seguro, informar referência histórica e pedir apenas a
clarificação indispensável. Nunca retomar antigas ações W22/VPS por um alias.

## Verificação documental reproduzível de M0

Executado na raiz com python3, sem instalar dependências. O bloco abaixo verifica
links locais/âncoras Markdown, IDs/estados/campos, matriz, ciclos técnicos e escopo
somente documental. É procedimento de validação, não utilitário do produto.
Os tamanhos esperados descrevem o catálogo inicial de M0, não progresso; futuras
mudanças de catálogo exigem atualizar asserções com CHG rastreada. Não comprova
correção científica nem detecta sozinho ciclos semânticos de decisões externas;
esses receberam revisão independente. Para implementação, não aplicar a asserção
de escopo exclusivamente Markdown. Também executar `git diff --check`.

```bash
python3 - <<'PY'
from pathlib import Path
import re, subprocess, unicodedata
from urllib.parse import unquote, urlsplit
root=Path.cwd()
files=[root/p for p in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],text=True).splitlines() if p.endswith('.md')]
errors=[];links=0;anchors=0
for p in files:
 s=re.sub(r'^```.*?^```[^\n]*','',p.read_text(),flags=re.M|re.S)
 # Existing docs may use inline code for sample placeholders; real Markdown links still parsed.
 for m in re.finditer(r'\]\(([^)]+)\)',s):
  target=m[1].strip().strip('<>')
  if target.startswith(('http:','https:','mailto:','plugin:','app:')):continue
  url=urlsplit(target); path=unquote(url.path); frag=unquote(url.fragment)
  q=(p.parent/path).resolve() if path else p
  links+=1
  if not q.exists():errors.append(f'{p.relative_to(root)}: missing {target}');continue
  if frag and q.is_file() and q.suffix=='.md':
   anchors+=1
   headings=[];counts={}
   for line in q.read_text().splitlines():
    if re.match(r'^#{1,6} ',line):
     h=re.sub(r'^#{1,6} ','',line).strip().lower()
     h=re.sub(r'<[^>]+>','',h)
     h=''.join(c for c in h if c.isalnum() or c in ' _-')
     h=h.replace(' ','-'); n=counts.get(h,0);counts[h]=n+1;headings.append(h+(f'-{n}' if n else ''))
   explicit=re.findall(r'(?:id|name)=["\']([^"\']+)',q.read_text())
   if frag not in headings+explicit:errors.append(f'{p.relative_to(root)}: missing anchor {target}')
print(f'Markdown: {len(files)} files; {links} relative links; {anchors} anchors; {len(errors)} errors')
for e in errors:print(e)
b=(root/'docs/Projeto Stroop Test.md').read_text();r=(root/'docs/REQUISITOS_E_RASTREABILIDADE.md').read_text()
parts=re.split(r'^### (WEB-\d{3}) — ',b,flags=re.M);tasks={parts[i]:parts[i+1] for i in range(1,len(parts),2)}
ids=re.findall(r'^### (WEB-\d{3}) — ',b,re.M)
reqs=re.findall(r'^### (REQ-[A-Z]+-\d{3})$',r,re.M)
assert len(ids)==len(set(ids))==42,(len(ids),len(set(ids)))
assert len(reqs)==len(set(reqs))==36
assert set(ids)=={f'WEB-{i:03}' for i in range(42)}
allowed={'PENDENTE','PRONTA','EM_ANDAMENTO','BLOQUEADA','EM_VALIDACAO','CONCLUIDA'}
graph={}
for tid,card in tasks.items():
 dep=re.search(r'^- Dependências: (.+)',card,re.M).group(1)
 refs=re.findall(r'WEB-\d{3}',dep);graph[tid]=refs
 for v in refs:assert v in tasks,(tid,v)
 for field in ['Marco:','Prioridade:','Estado:','Dependências:','Responsável:','Critérios:','Evidências:','Riscos/bloqueios:','Referências:']:
  # Task acceptance uses Critérios de aceite, WEB-000 uses Critérios.
  if field=='Critérios:':assert ('Critérios:' in card or 'Critérios de aceite:' in card),tid
  else:assert field in card,(tid,field)
 state=re.search(r'Estado: ([A-Z_]+)',card).group(1);assert state in allowed,(tid,state)
visited=set();active=set()
def visit(t):
 assert t not in active,('cycle',t)
 if t in visited:return
 active.add(t)
 for v in graph[t]:visit(v)
 active.remove(t);visited.add(t)
for t in tasks:visit(t)
traces=re.findall(r'^\| (REQ-[A-Z]+-\d{3}) \| ([^|]+) \| (M\d+) \| (WEB-\d{3}) \|',r,re.M)
assert len(traces)==len(reqs)
assert set(t[0] for t in traces)==set(reqs)
for req,adr,marco,task in traces:
 assert task in tasks,(req,task)
 assert re.search(r'Marco: '+marco+r'\.',tasks[task]),(req,marco,task)
for ref in set(re.findall(r'WEB-\d{3}',r)):assert ref in tasks,ref
for i in range(11):assert re.search(r'^## M'+str(i)+r' — ',b,re.M)
assert len(re.findall(r'^\| R\d\d \|',b,re.M))==10
assert len(re.findall(r'^\| DEC-\d\d \|',b,re.M))==5
print('Structure: 11 milestones; 42 unique tasks; 36 requirements/trace rows; 10 risks; 5 decisions; acyclic task dependencies')
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
assert all(p.endswith('.md') for p in changed),changed
print(f'Scope: {len(changed)} changed/new files, all Markdown; no functional/config/schema change')
if errors:raise SystemExit(1)
PY
```
