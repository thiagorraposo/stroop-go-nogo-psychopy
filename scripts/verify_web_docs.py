"""Valida governança documental canônica sem dependências ou acesso a dados de coleta."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PROTECTED_PARTS = {'data', 'database', 'backup', 'backups', 'production-secrets'}
TASK_STATES = {'PENDENTE', 'PRONTA', 'EM_ANDAMENTO', 'BLOQUEADA', 'EM_VALIDACAO', 'CONCLUIDA'}


class DocumentError(ValueError):
    """Inconsistência verificável no catálogo canônico."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise DocumentError(message)


def sequence(ids: list[str], prefix: str, start: int, width: int) -> None:
    require(bool(ids), f'Catálogo vazio: {prefix}')
    require(len(ids) == len(set(ids)), f'IDs duplicados: {prefix}')
    expected = {f'{prefix}{i:0{width}d}' for i in range(start, start + len(ids))}
    require(set(ids) == expected, f'Sequência com lacuna ou renumeração: {prefix}')


def validate_catalog(backlog: str, requirements: str) -> dict[str, int]:
    """Calcula contagens das fichas e confere referências, grafo e painel vigente."""
    cards = list(re.finditer(r'^### (WEB-\d{3}) — [^\n]+\n(.*?)(?=^#{2,3} |\Z)', backlog, re.M | re.S))
    ids = [match[1] for match in cards]
    sequence(ids, 'WEB-', 0, 3)
    tasks = {match[1]: match[2] for match in cards}
    milestones = re.findall(r'^## (M\d+) — ', backlog, re.M)
    sequence(milestones, 'M', 0, 1)
    reqs = re.findall(r'^### (REQ-[A-Z]+-\d{3})\s*$', requirements, re.M)
    require(bool(reqs) and len(reqs) == len(set(reqs)), 'Requisitos vazios ou duplicados')
    for group in {req.rsplit('-', 1)[0] for req in reqs}:
        sequence([req for req in reqs if req.startswith(group + '-')], group + '-', 1, 3)
    risks = re.findall(r'^\| (R\d{2}) \|', backlog, re.M)
    decisions = re.findall(r'^\| (DEC-\d{2}) \|', backlog, re.M)
    sequence(risks, 'R', 1, 2)
    sequence(decisions, 'DEC-', 1, 2)
    for kind, values in ((r'WEB-\d{3}', ids), (r'REQ-[A-Z]+-\d{3}', reqs),
                         (r'R\d{2}', risks), (r'DEC-\d{2}', decisions)):
        references = set(re.findall(r'\b' + kind + r'\b', backlog + '\n' + requirements))
        require(references <= set(values), f'Referências inexistentes: {sorted(references - set(values))}')
    for row in re.findall(r'^\| (?:R\d{2}|DEC-\d{2}) \|.*$', backlog, re.M):
        state = row.rstrip(' |').rsplit('|', 1)[1].strip()
        allowed = {'ABERTO', 'MITIGADO', 'ENCERRADO'} if row.startswith('| R') else {'PENDENTE', 'APROVADA', 'REJEITADA'}
        require(state in allowed, f'Estado inválido no registro: {row.split("|")[1].strip()}')
    graph = {}
    task_milestones = {}
    accepted = Counter()
    totals = Counter()
    for tid, card in tasks.items():
        for field in ('Marco:', 'Prioridade:', 'Complexidade:', 'Estado:', 'Dependências:',
                      'Responsável:', 'Evidências:', 'Riscos/bloqueios:', 'Referências:'):
            require(field in card, f'{tid}: campo ausente {field}')
        require('Critérios:' in card or 'Critérios de aceite:' in card, f'{tid}: critérios ausentes')
        state = re.search(r'Estado: ([A-Z_]+)', card)
        require(state and state[1] in TASK_STATES, f'{tid}: estado inválido')
        milestone = re.search(r'Marco: (M\d+)\.', card)
        require(milestone and milestone[1] in milestones, f'{tid}: marco inválido')
        task_milestones[tid] = milestone[1]
        totals[milestone[1]] += 1
        accepted[milestone[1]] += state[1] == 'CONCLUIDA'
        dependencies = re.search(r'^- Dependências: (.+)', card, re.M)
        graph[tid] = re.findall(r'WEB-\d{3}', dependencies[1])
        require(set(graph[tid]) <= set(tasks), f'{tid}: dependência inexistente')
    active: set[str] = set()
    visited: set[str] = set()

    def visit(tid: str) -> None:
        require(tid not in active, f'Ciclo de dependências em {tid}')
        if tid in visited:
            return
        active.add(tid)
        for dependency in graph[tid]:
            visit(dependency)
        active.remove(tid)
        visited.add(tid)

    for tid in tasks:
        visit(tid)
    traces = re.findall(r'^\| (REQ-[A-Z]+-\d{3}) \| ([^|]+) \| (M\d+) \| (WEB-\d{3}) \|([^\n]+)', requirements, re.M)
    require(Counter(trace[0] for trace in traces) == Counter(reqs), 'Matriz deve ter uma linha por requisito')
    for req, decision, milestone, task, tail in traces:
        require(task in tasks and task_milestones[task] == milestone, f'{req}: tarefa/marco incompatíveis')
        require(bool(decision.strip()) and len(tail.split('|')) >= 4, f'{req}: cadeia de rastreabilidade incompleta')
        require(all(cell.strip() for cell in tail.strip('|').split('|')), f'{req}: célula de rastreabilidade vazia')
    panel = backlog.split('## Painel visual de acompanhamento', 1)
    require(len(panel) == 2, 'Painel de progresso ausente')
    panel = panel[1].split('## Ordem, caminho crítico e paralelismo', 1)[0]
    count = sum(accepted.values())
    progress = re.search(r'Progresso atual: \*\*(\d+)/(\d+) entregáveis aceitos', backlog)
    require(progress and tuple(map(int, progress.groups())) == (count, len(ids)), 'Progresso atual diverge das fichas')
    global_row = re.search(r'\*\*(\d+) de (\d+) · ([\d,]+)%\*\*\s*\|\s*\*\*(\d+)\*\*', panel)
    require(global_row, 'Contadores globais do painel ausentes')
    require((int(global_row[1]), int(global_row[2]), int(global_row[4])) == (count, len(ids), len(ids) - count), 'Contadores globais divergem das fichas')
    percent = f'{count / len(ids) * 100:.1f}'.replace('.', ',')
    require(global_row[3] == percent, 'Percentual global incorreto')
    bar_percent = re.search(r'^Aceites\s+([█░]+)\s+([\d,]+)%', panel, re.M)
    require(bar_percent and bar_percent[2] == percent, 'Percentual da barra global incorreto')
    require(abs(bar_percent[1].count('█') / len(bar_percent[1]) - count / len(ids)) <= 1 / len(bar_percent[1]), 'Barra global incoerente')
    milestone_rows = re.findall(r'^\| \[(M\d+)\]\([^\n]+$', panel, re.M)
    require(Counter(milestone_rows) == Counter(milestones), 'Painel deve conter todos os marcos uma vez')
    for row in re.findall(r'^\| \[M\d+\]\([^\n]+$', panel, re.M):
        milestone = re.search(r'\[(M\d+)\]', row)[1]
        cells = row.split('|')
        counts = re.search(r'\*\*(\d+)/(\d+)\*\*', cells[3])
        require(counts and tuple(map(int, counts.groups())) == (accepted[milestone], totals[milestone]), f'{milestone}: totais do painel incorretos')
        require((cells[3].count('🟩'), cells[3].count('⬜')) == (accepted[milestone], totals[milestone] - accepted[milestone]), f'{milestone}: quadrados do painel incorretos')
    return {'marcos': len(milestones), 'tarefas': len(ids), 'requisitos': len(reqs),
            'riscos': len(risks), 'decisões': len(decisions), 'aceitos': count}


def markdown_anchors(source: str) -> set[str]:
    counts: Counter[str] = Counter()
    anchors = set(re.findall(r'(?:id|name)=["\']([^"\']+)', source))
    for heading in re.findall(r'^#{1,6} (.+)$', source, re.M):
        heading = re.sub(r'<[^>]+>', '', heading.strip().lower())
        slug = ''.join(char for char in heading if char.isalnum() or char in ' _-').replace(' ', '-')
        anchors.add(slug + (f'-{counts[slug]}' if counts[slug] else ''))
        counts[slug] += 1
    return anchors


def readable_markdown(root: Path, path: Path) -> bool:
    """Confere o destino resolvido antes de ler Markdown, inclusive por symlink."""
    resolved_root = root.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(resolved_root):
        return False
    return not any(part in PROTECTED_PARTS or part.startswith('.env')
                   for part in resolved.relative_to(resolved_root).parts)


def validate_links(root: Path) -> dict[str, int]:
    result = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root)
    names = sorted({name for name in result.decode().split('\0') if name.endswith('.md')})
    # Nunca ler dados/coletas, backups ou arquivos de ambiente, mesmo se versionados.
    files = [root / name for name in names if readable_markdown(root, root / name)]
    errors = []
    links = anchors = 0
    for path in files:
        source = re.sub(r'^```.*?^```[^\n]*', '', path.read_text(encoding='utf8'), flags=re.M | re.S)
        for target in re.findall(r'\]\(([^)]+)\)', source):
            target = target.strip().strip('<>')
            url = urlsplit(target)
            if url.scheme:
                continue
            local = unquote(url.path)
            destination = (path.parent / local).resolve() if local else path
            links += 1
            if not destination.exists():
                errors.append(f'{path.relative_to(root)}: link inexistente {target}')
            elif url.fragment and destination.is_file() and destination.suffix == '.md':
                anchors += 1
                if not readable_markdown(root, destination):
                    errors.append(f'{path.relative_to(root)}: âncora em caminho protegido ou fora do repositório')
                    continue
                if unquote(url.fragment) not in markdown_anchors(destination.read_text(encoding='utf8')):
                    errors.append(f'{path.relative_to(root)}: âncora inexistente {target}')
    require(not errors, '\n'.join(errors))
    return {'documentos': len(files), 'links': links, 'âncoras': anchors}


def validate_stable_ids(root: Path, backlog: str, requirements: str) -> None:
    """A expansão pode acrescentar IDs; os já versionados em HEAD permanecem."""
    catalogs = (
        ('docs/Projeto Stroop Test.md', backlog, (
            r'^### (WEB-\d{3}) — ', r'^## (M\d+) — ',
            r'^\| (R\d{2}) \|', r'^\| (DEC-\d{2}) \|')),
        ('docs/REQUISITOS_E_RASTREABILIDADE.md', requirements, (r'^### (REQ-[A-Z]+-\d{3})\s*$',)),
    )
    for path, current, patterns in catalogs:
        previous = subprocess.check_output(['git', 'show', f'HEAD:{path}'], cwd=root, text=True)
        for pattern in patterns:
            removed = set(re.findall(pattern, previous, re.M)) - set(re.findall(pattern, current, re.M))
            require(not removed, f'IDs versionados removidos: {sorted(removed)}')


def main() -> int:
    try:
        backlog = (ROOT / 'docs/Projeto Stroop Test.md').read_text(encoding='utf8')
        requirements = (ROOT / 'docs/REQUISITOS_E_RASTREABILIDADE.md').read_text(encoding='utf8')
        counts = validate_catalog(backlog, requirements)
        validate_stable_ids(ROOT, backlog, requirements)
        counts.update(validate_links(ROOT))
    except (DocumentError, OSError, subprocess.CalledProcessError) as error:
        print(f'FALHA documental: {error}')
        return 1
    print('Documentação válida: ' + '; '.join(f'{value} {key}' for key, value in counts.items()) + '; dependências sem ciclos.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
