"""Regressões do catálogo documental com textos e Git exclusivamente sintéticos."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.verify_web_docs import DocumentError, validate_catalog, validate_links, validate_stable_ids


def catalog(total=2):
    tasks = []
    for number in range(total):
        tasks.append(f'''### WEB-{number:03} — Entrega sintética

- Marco: M0. Prioridade: P0. Complexidade: P. Estado: {'CONCLUIDA' if number == 0 else 'PENDENTE'}.
- Dependências: {'nenhuma' if number == 0 else 'WEB-000'}.
- Responsável: sintético.
- Critérios: verificáveis.
- Evidências: sintéticas.
- Riscos/bloqueios: R01.
- Referências: REQ-UX-001.
''')
    backlog = f'''Progresso atual: **1/{total} entregáveis aceitos**.

## Painel visual de acompanhamento

| **1 de {total} · {100 / total:.1f}%** | **{total - 1}** |

Aceites   {'█' * (20 // total)}{'░' * (20 - 20 // total)}   {100 / total:.1f}%

| [M0](#m0) | Sintético | 🟩{'⬜' * (total - 1)} **1/{total}** | Pendente |

## Ordem, caminho crítico e paralelismo

## M0 — Sintético

{''.join(tasks)}
## Registro

| R01 | Sintético | ABERTO |
| DEC-01 | Sintético | PENDENTE |
'''.replace(f'{100 / total:.1f}%', f'{100 / total:.1f}'.replace('.', ',') + '%')
    requirements = '''### REQ-UX-001

- Descrição: sintética.

| REQ-UX-001 | DEC-01 | M0 | WEB-000 | Componente | Teste planejado | Evidência planejada |
'''
    return backlog, requirements


class WebDocsTests(unittest.TestCase):
    def test_contagens_calculadas_aceitam_expansao_sem_mudar_validador(self):
        for total in (2, 4):
            with self.subTest(total=total):
                result = validate_catalog(*catalog(total))
                self.assertEqual(result['tarefas'], total)
                self.assertEqual(result['aceitos'], 1)

    def test_rejeita_ciclo_dependencia_desconhecida_ids_duplicados_e_estado(self):
        backlog, requirements = catalog()
        mutations = [
            backlog.replace('Dependências: nenhuma', 'Dependências: WEB-001'),
            backlog.replace('Dependências: WEB-000', 'Dependências: WEB-999'),
            backlog.replace('### WEB-001', '### WEB-000'),
            backlog.replace('Estado: PENDENTE', 'Estado: APROVADA'),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(DocumentError):
                validate_catalog(mutation, requirements)

    def test_rejeita_matriz_incompleta_tarefa_de_outro_marco_e_requisito_sem_linha(self):
        backlog, requirements = catalog()
        mutations = [
            requirements.replace('| Componente |', '| |'),
            requirements.replace('| M0 |', '| M1 |'),
            requirements + '\n### REQ-UX-002\n',
            requirements + requirements,
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(DocumentError):
                validate_catalog(backlog, mutation)

    def test_rejeita_denominador_percentual_quadrados_e_barra_incoerentes(self):
        backlog, requirements = catalog()
        mutations = [
            backlog.replace('1/2 entregáveis', '1/3 entregáveis'),
            backlog.replace('50,0%', '60,0%'),
            backlog.replace('🟩⬜', '🟩🟩'),
            backlog.replace('██████████░░░░░░░░░░', '████████████████████'),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(DocumentError):
                validate_catalog(mutation, requirements)

    def test_ids_ja_versionados_nao_podem_sumir_na_expansao(self):
        previous = ['### WEB-000 — Sintético\n', '### REQ-UX-001\n']
        with patch('scripts.verify_web_docs.subprocess.check_output', side_effect=previous):
            validate_stable_ids(Path('/synthetic'), previous[0] + '### WEB-001 — Novo\n', previous[1])
        with patch('scripts.verify_web_docs.subprocess.check_output', side_effect=previous):
            with self.assertRaises(DocumentError):
                validate_stable_ids(Path('/synthetic'), '### WEB-001 — Novo\n', previous[1])

    def test_ancora_nao_le_destino_protegido_inclusive_link_codificado_e_symlink(self):
        with tempfile.TemporaryDirectory(prefix='stroop-synthetic-docs-') as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '--quiet'], cwd=root, check=True)
            protected = root / 'data' / 'synthetic.md'
            protected.parent.mkdir()
            protected.write_text('# Sintético\n', encoding='utf8')
            alias = root / 'alias.md'
            alias.symlink_to(protected)
            page = root / 'Fonte.md'
            original_read = Path.read_text
            reads = []

            def read(path, *args, **kwargs):
                reads.append(path.resolve())
                return original_read(path, *args, **kwargs)

            for link in ('data/synthetic.md#sintético', '%64ata/synthetic.md#sintético', 'alias.md#sintético'):
                page.write_text(f'# Fonte\n\n[link]({link})\n', encoding='utf8')
                reads.clear()
                with self.subTest(link=link), patch.object(Path, 'read_text', read):
                    with self.assertRaisesRegex(DocumentError, 'caminho protegido'):
                        validate_links(root)
                self.assertNotIn(protected.resolve(), reads)

    def test_links_e_ancoras_locais_com_git_descartavel(self):
        with tempfile.TemporaryDirectory(prefix='stroop-synthetic-docs-') as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '--quiet'], cwd=root, check=True)
            page = root / 'Fonte.md'
            page.write_text('# Olá mundo\n\n[link](Fonte.md#olá-mundo)\n', encoding='utf8')
            self.assertEqual(validate_links(root)['âncoras'], 1)
            for link in ('Ausente.md', 'Fonte.md#ausente'):
                page.write_text(f'# Olá mundo\n\n[link]({link})\n', encoding='utf8')
                with self.subTest(link=link), self.assertRaises(DocumentError):
                    validate_links(root)


if __name__ == '__main__':
    unittest.main()
