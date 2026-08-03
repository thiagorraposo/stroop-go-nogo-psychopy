#!/usr/bin/env python3
"""Diagnostica, sem modificar arquivos, o ambiente local do projeto."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MINIMUM_PYTHON = (3, 9)
SUPPORTED_SYSTEMS = {"Windows", "Linux", "Darwin"}


@dataclass(frozen=True)
class Check:
    status: str
    name: str
    detail: str
    windows_fix: str | None = None
    unix_fix: str | None = None


def venv_python_path(root: Path, system: str) -> Path:
    """Retorna o interpretador esperado para a plataforma atual."""
    if system == "Windows":
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def file_check(root: Path, relative_path: str) -> Check:
    path = root / relative_path
    if path.is_file():
        return Check("OK", relative_path, "arquivo encontrado")
    return Check(
        "ERRO",
        relative_path,
        "arquivo obrigatorio nao encontrado; restaure-o a partir do pacote original",
        "Extraia novamente o ZIP do projeto e execute: py scripts\\doctor.py",
        "Extraia novamente o ZIP do projeto e execute: python3 scripts/doctor.py",
    )


def installed_packages(python_path: Path) -> tuple[set[str], str | None]:
    """Consulta modulos na venv em um subprocesso que nao altera o ambiente."""
    code = (
        "import importlib.util,json; "
        "print(json.dumps({n: importlib.util.find_spec(n) is not None "
        "for n in ('streamlit','pandas')}))"
    )
    try:
        result = subprocess.run(
            [str(python_path), "-c", code],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return set(), f"nao foi possivel consultar a venv: {exc}"
    if result.returncode != 0:
        detail = result.stderr.strip() or f"processo encerrou com codigo {result.returncode}"
        return set(), f"nao foi possivel consultar a venv: {detail}"
    try:
        found = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        return set(), "a venv retornou uma resposta invalida"
    return {name for name, present in found.items() if present}, None


def run_checks(root: Path = PROJECT_ROOT, cwd: Path | None = None) -> list[Check]:
    """Executa verificacoes somente leitura e devolve resultados estruturados."""
    checks: list[Check] = []
    system = platform.system() or "desconhecido"
    if system in SUPPORTED_SYSTEMS:
        checks.append(Check("OK", "Sistema operacional", f"{system} suportado"))
    else:
        checks.append(
            Check("AVISO", "Sistema operacional", f"{system} nao foi validado pelo projeto")
        )

    version = sys.version_info[:3]
    version_text = ".".join(map(str, version))
    if version >= MINIMUM_PYTHON:
        checks.append(Check("OK", "Python", f"versao {version_text}"))
    else:
        checks.append(
            Check(
                "ERRO",
                "Python",
                f"versao {version_text}; requer Python 3.9 ou mais recente",
                "Instale Python 3.9+ e execute: py scripts\\doctor.py",
                "Instale Python 3.9+ e execute: python3 scripts/doctor.py",
            )
        )

    current_dir = (cwd or Path.cwd()).resolve()
    if current_dir == root.resolve():
        checks.append(Check("OK", "Raiz do projeto", str(current_dir)))
    else:
        checks.append(
            Check(
                "ERRO",
                "Raiz do projeto",
                f"diretorio atual: {current_dir}",
                f'cd /d "{root}" && py scripts\\doctor.py',
                f'cd "{root}" && python3 scripts/doctor.py',
            )
        )

    for relative_path in (
        "stroop_go_nogo_ptbr.psyexp",
        "setup.bat",
        "abrir_dashboard.bat",
        "setup.sh",
        "abrir_dashboard.sh",
        "dashboard/requirements.txt",
        "scripts/importar_csv_sqlite.py",
        "dashboard/app.py",
    ):
        checks.append(file_check(root, relative_path))

    venv_dir = root / ".venv"
    python_path = venv_python_path(root, system)
    if not venv_dir.is_dir():
        checks.append(
            Check(
                "ERRO",
                ".venv",
                "ambiente virtual nao encontrado",
                "setup.bat",
                "bash setup.sh",
            )
        )
    elif not python_path.is_file():
        checks.append(
            Check(
                "ERRO",
                ".venv",
                f"interpretador nao encontrado em {python_path}",
                "setup.bat",
                "bash setup.sh",
            )
        )
    else:
        checks.append(Check("OK", ".venv", f"interpretador encontrado em {python_path}"))
        packages, package_error = installed_packages(python_path)
        if package_error:
            checks.append(
                Check("ERRO", "Dependencias da .venv", package_error, "setup.bat", "bash setup.sh")
            )
        for package in ("streamlit", "pandas"):
            if not package_error:
                if package in packages:
                    checks.append(Check("OK", package, "instalado na .venv"))
                else:
                    checks.append(
                        Check(
                            "ERRO",
                            package,
                            "nao instalado na .venv",
                            "setup.bat",
                            "bash setup.sh",
                        )
                    )

    data_dir = root / "data"
    if data_dir.is_dir():
        checks.append(Check("OK", "data/", "diretorio encontrado"))
        csv_files = sorted(data_dir.glob("*_trials.csv"))
        if csv_files:
            checks.append(Check("OK", "CSV oficial", f"{len(csv_files)} arquivo(s) *_trials.csv"))
        else:
            checks.append(
                Check(
                    "AVISO",
                    "CSV oficial",
                    "nenhum data/*_trials.csv; realize uma coleta Pilot antes de importar",
                )
            )
    else:
        checks.append(
            Check(
                "ERRO",
                "data/",
                "diretorio local nao encontrado",
                "if not exist data mkdir data",
                "mkdir -p data",
            )
        )

    database = root / "database" / "stroop_results.sqlite3"
    if database.is_file():
        checks.append(Check("OK", "Banco SQLite", "database/stroop_results.sqlite3 encontrado"))
    else:
        checks.append(
            Check(
                "AVISO",
                "Banco SQLite",
                "ainda nao existe; sera criado somente pelo fluxo de importacao autorizado",
            )
        )
    return checks


def print_report(checks: list[Check]) -> None:
    print("Diagnostico do ambiente - Stroop Go/No-Go")
    print(f"Raiz esperada: {PROJECT_ROOT}")
    print()
    for check in checks:
        print(f"[{check.status}] {check.name}: {check.detail}")

    errors = [check for check in checks if check.status == "ERRO"]
    if errors:
        print("\nComandos/acoes para corrigir os erros:")
        for check in errors:
            print(f"- {check.name}")
            print(f"  Windows: {check.windows_fix}")
            print(f"  Linux/macOS: {check.unix_fix}")

    warnings = sum(check.status == "AVISO" for check in checks)
    print(f"\nResumo: {len(errors)} erro(s), {warnings} aviso(s).")
    print("Nenhum dado ou banco foi modificado.")


def main() -> int:
    checks = run_checks()
    print_report(checks)
    return 1 if any(check.status == "ERRO" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
