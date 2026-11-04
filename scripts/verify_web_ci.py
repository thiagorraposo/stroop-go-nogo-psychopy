"""Verificacoes WEB reproduziveis; sem dados locais, deploy ou secrets reais."""
from __future__ import annotations

import argparse
from pathlib import Path
import os
import re
import secrets
import string
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
import venv

ROOT = Path(__file__).resolve().parents[1]
GITLEAKS_IMAGE = 'ghcr.io/gitleaks/gitleaks:v8.30.1'
PIP_AUDIT_VERSION = '2.10.1'
SOURCE_SUFFIXES = {'.py', '.ts', '.tsx', '.js', '.mjs', '.json', '.toml', '.yml', '.yaml',
                   '.sql', '.md', '.txt', '.lock', '.sh', '.bat', '.csv', '.psyexp', '.html', '.css',
                   '.conf', '.ini', '.cfg', '.svg', '.http', '.template', '.example', '.dockerignore'}
SOURCE_NAMES = {'Dockerfile', 'Makefile', '.dockerignore', '.gitignore'}
FORBIDDEN_KEY_SUFFIXES = {'.key', '.pem', '.p12', '.pfx'}
EXCLUDED_ROOTS = {'data', 'database', '.git', 'production-secrets', 'node_modules', '.venv', 'venv'}
EXAMPLE_ENVS = {'.env.example', '.env.production.example'}


class SecretFinding(Exception):
    """Gitleaks encontrou um padrao de secret, sem conteudo publico."""


class CheckFailure(Exception):
    """Falha publica sem incluir comandos, credenciais ou conteudo analisado."""


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None,
        quiet: bool = False) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, check=False,
                            stdout=subprocess.DEVNULL if quiet else None,
                            stderr=subprocess.DEVNULL if quiet else None)
    if result.returncode:
        raise CheckFailure('Uma verificacao retornou falha; entrega bloqueada.')


def database_guard(value: str) -> None:
    try:
        uri = urlsplit(value)
        valid = uri.scheme in {'postgresql', 'postgres'} and uri.hostname in {'127.0.0.1', 'localhost', '::1'}
        valid = valid and bool(uri.username) and uri.port is not None and not uri.query and not uri.fragment
        valid = valid and bool(re.fullmatch(r'/stroop_etapa4_test_[A-Za-z0-9_]+', unquote(uri.path)))
    except ValueError:
        valid = False
    if not valid:
        raise CheckFailure('TEST_DATABASE_URL deve apontar explicitamente para PostgreSQL local descartavel stroop_etapa4_test_*.')


def tracked_sources(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise CheckFailure('Nao foi possivel enumerar fontes versionadas.')
    sources = []
    for name in result.stdout.decode('utf8').split('\0'):
        if not name:
            continue
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or any(ord(char) < 32 or ord(char) == 127 for char in name):
            raise CheckFailure('Caminho versionado invalido.')
        if any(part.startswith('.env') and part not in EXAMPLE_ENVS for part in path.parts):
            raise CheckFailure('Arquivo de ambiente operacional versionado; conteudo nao foi aberto.')
        if path.suffix.lower() in FORBIDDEN_KEY_SUFFIXES:
            raise CheckFailure('Arquivo de chave/certificado sensivel versionado; conteudo nao foi aberto.')
        if path.parts[0] in EXCLUDED_ROOTS or any(part in {'node_modules', '__pycache__'} for part in path.parts):
            continue
        full = root / path
        if full.is_symlink():
            raise CheckFailure('Symlink em fonte versionada exige revisao explicita.')
        if full.is_file() and (path.suffix.lower() in SOURCE_SUFFIXES or path.name in EXAMPLE_ENVS
                               or path.name in SOURCE_NAMES or path.name.startswith('Dockerfile.')):
            sources.append(path)
    if not sources:
        raise CheckFailure('Nenhuma fonte versionada foi encontrada.')
    return sources


def scan_sources(root: Path = ROOT) -> None:
    paths = tracked_sources(root)
    with tempfile.TemporaryDirectory(prefix='stroop-ci-sources-') as directory:
        snapshot = Path(directory) / 'source'
        snapshot.mkdir(mode=0o755)
        reports = Path(directory) / 'report'
        reports.mkdir(mode=0o777)
        reports.chmod(0o777)  # Docker rootless pode usar UID diferente; somente metadata efemera.
        for path in paths:
            destination = snapshot / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, destination)
        # Regras oficiais, sem exclusao por pastas, marcadores ou comentarios de fixtures.
        (snapshot / '.gitleaks.toml').write_text('[extend]\nuseDefault = true\n')
        (snapshot / 'report.tmpl').write_text('{{range .}}{{.File}}\t{{.StartLine}}\t{{.RuleID}}{{\"\\n\"}}{{end}}')
        # Sem rede no scanner, sem git/historico/dados locais, sem logs ou relatorios contendo findings.
        result = subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
             '--security-opt', 'no-new-privileges', '--volume', f'{snapshot}:/scan:ro',
             '--volume', f'{reports}:/report:rw',
             GITLEAKS_IMAGE, 'dir', '/scan', '--config', '/scan/.gitleaks.toml', '--redact=100',
             '--no-banner', '--no-color', '--ignore-gitleaks-allow', '--exit-code', '1',
             '--report-format', 'template', '--report-template', '/scan/report.tmpl', '--report-path', '/report/findings.txt'],
             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if result.returncode == 1:
            report = reports / 'findings.txt'
            metadata = report.read_text() if report.is_file() else ''
            count = 0
            for line in metadata.splitlines():
                parts = line.split('\t')
                if len(parts) != 3:
                    continue
                name, line_number, rule = parts
                relative = name.removeprefix('/scan/')
                if Path(relative) in paths and line_number.isdigit() and re.fullmatch(r'[a-zA-Z0-9_-]+', rule):
                    print(f'Secret: {relative}:{line_number} regra={rule}', file=sys.stderr)
                    count += 1
            if not count:
                raise CheckFailure('Scanner nao forneceu metadata valida; entrega bloqueada.')
            raise SecretFinding('Scanner encontrou um padrao de secret; entrega bloqueada sem imprimir valores.')
        if result.returncode:
            raise CheckFailure('Scanner indisponivel ou falhou; entrega bloqueada.')
    print(f'Secrets: {len(paths)} fontes versionadas verificadas; dados/historico fora do escopo.', flush=True)


def secret_self_test() -> None:
    """Prova negativa: scanner funcional aceita fonte inocua e rejeita token falso."""
    with tempfile.TemporaryDirectory(prefix='stroop-ci-negative-') as directory:
        root = Path(directory)
        run(['git', 'init', '--quiet'], cwd=root, quiet=True)
        source = root / 'example.py'
        source.write_text('value = 42\n')
        run(['git', 'add', 'example.py'], cwd=root, quiet=True)
        scan_sources(root)
        fake_token = 'gh' + 'p_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(36))
        source.write_text('api_token = "' + fake_token + '"\n')
        try:
            scan_sources(root)
        except SecretFinding:
            print('Falha controlada: token falso bloqueado sem expor seu valor.', flush=True)
        else:
            raise CheckFailure('Scanner nao bloqueou o token falso; entrega bloqueada.')


def python_suite() -> int:
    database_guard(os.environ.get('TEST_DATABASE_URL', ''))
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if result.skipped:
        print('Suite incompleta: skips bloqueiam a entrega.', file=sys.stderr)
    return 0 if result.wasSuccessful() and not result.skipped else 1


def audit_dependencies() -> None:
    run(['npm', 'audit', '--audit-level=low'], cwd=ROOT / 'web')
    with tempfile.TemporaryDirectory(prefix='stroop-ci-audit-') as directory:
        audit_venv = Path(directory) / 'venv'
        venv.EnvBuilder(with_pip=True).create(audit_venv)
        python = audit_venv / 'bin/python'
        run([str(python), '-m', 'pip', 'install', '--quiet', '--disable-pip-version-check',
             f'pip-audit=={PIP_AUDIT_VERSION}'])
        run([str(python), '-m', 'pip_audit', '--strict', '--disable-pip', '--no-deps',
             '--progress-spinner', 'off', '-r', 'dashboard/requirements.lock', '-r', 'api/requirements.lock'])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['sources', 'python', 'frontend', 'browser', 'integration', 'audit', 'secret-self-test', 'all'])
    args = parser.parse_args(argv)
    stages = ['sources', 'secret-self-test', 'python', 'frontend', 'browser', 'integration', 'audit'] if args.stage == 'all' else [args.stage]
    try:
        for stage in stages:
            print(f'CI WEB: {stage}', flush=True)
            if stage == 'sources':
                scan_sources()
            elif stage == 'secret-self-test':
                secret_self_test()
            elif stage == 'python':
                if python_suite():
                    raise CheckFailure('Suite Python incompleta ou com falha; entrega bloqueada.')
            elif stage == 'frontend':
                # build ja executa typecheck antes do bundle; nao duplicar tsc.
                for command in (['npm', 'ci'], ['npm', 'test'], ['npm', 'run', 'build']):
                    run(command, cwd=ROOT / 'web')
            elif stage == 'browser':
                # Porta exclusiva do runner; nao reutilizar uma previa aberta pelo usuario.
                environment = {**os.environ, 'WEB_TEST_PORT': '4273'}
                run(['npm', 'run', 'test:browser'], cwd=ROOT / 'web', env=environment)
            elif stage == 'integration':
                database_guard(os.environ.get('TEST_DATABASE_URL', ''))
                run(['npm', 'run', 'test:integration'], cwd=ROOT / 'web')
            elif stage == 'audit':
                audit_dependencies()
        return 0
    except (CheckFailure, SecretFinding, OSError) as error:
        print(str(error) if isinstance(error, (CheckFailure, SecretFinding)) else 'Ferramenta obrigatoria indisponivel; entrega bloqueada.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
