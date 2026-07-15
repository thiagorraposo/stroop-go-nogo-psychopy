#!/usr/bin/env python3
"""Importa o CSV local mais recente e inicia o dashboard Streamlit."""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = PROJECT_ROOT / ".venv"
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = PROJECT_ROOT / "database" / "stroop_results.sqlite3"
IMPORT_SCRIPT = PROJECT_ROOT / "scripts" / "importar_csv_sqlite.py"
DASHBOARD_APP = PROJECT_ROOT / "dashboard" / "app.py"
DUPLICATE_MESSAGE = "assessment_id ja importado"


def operating_system() -> str:
    return platform.system() or "desconhecido"


def venv_python_path(venv_dir: Path, system: str | None = None) -> Path:
    system = system or operating_system()
    if system == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def find_latest_csv(data_dir: Path = DATA_DIR) -> Path | None:
    candidates = [path for path in data_dir.glob("*_trials.csv") if path.is_file()]
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def build_import_command(python_path: Path, csv_path: Path, force: bool) -> list[str]:
    command = [
        str(python_path),
        str(IMPORT_SCRIPT),
        str(csv_path),
        "--db",
        str(DB_PATH),
    ]
    if force:
        command.append("--force")
    return command


def build_streamlit_command(python_path: Path) -> list[str]:
    return [str(python_path), "-m", "streamlit", "run", str(DASHBOARD_APP)]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa um CSV local e abre o dashboard Streamlit."
    )
    parser.add_argument("--force", action="store_true", help="Reimporta o assessment_id.")
    parser.add_argument("--csv", type=Path, help="CSV especifico; por padrao usa o mais recente.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    python_path = venv_python_path(VENV_DIR)
    print(f"Sistema detectado: {operating_system()}")

    if not VENV_DIR.is_dir() or not python_path.is_file():
        print("Erro: .venv ausente ou incompleta. Execute setup_env.py primeiro.", file=sys.stderr)
        return 1

    csv_path = args.csv.expanduser().resolve() if args.csv else find_latest_csv()
    if csv_path is None:
        print("Nenhum CSV *_trials.csv encontrado em data/.")
        if not DB_PATH.is_file():
            print("Erro: tambem nao existe banco local para exibir.", file=sys.stderr)
            return 1
        print("Continuando com o banco local existente, sem nova importacao.")
    elif not csv_path.is_file():
        print(f"Erro: CSV nao encontrado: {csv_path}", file=sys.stderr)
        return 1
    else:
        print(f"CSV selecionado: {csv_path}")
        result = subprocess.run(
            build_import_command(python_path, csv_path, args.force),
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
        )
        if result.stdout:
            print(result.stdout.rstrip())
        if result.returncode != 0:
            details = result.stderr.rstrip()
            if DUPLICATE_MESSAGE in details and not args.force:
                print("CSV ja importado; mantendo os dados existentes e continuando.")
            else:
                print(details or "Erro desconhecido durante a importacao.", file=sys.stderr)
                return result.returncode or 1

    print("Abrindo dashboard Streamlit...")
    try:
        return subprocess.run(
            build_streamlit_command(python_path), cwd=PROJECT_ROOT, check=False
        ).returncode
    except KeyboardInterrupt:
        print("Dashboard encerrado.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
