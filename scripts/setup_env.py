#!/usr/bin/env python3
"""Cria o ambiente virtual local e instala as dependencias do dashboard."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS_PATH = PROJECT_ROOT / "dashboard" / "requirements.txt"
MINIMUM_PYTHON = (3, 9)


def operating_system() -> str:
    """Retorna o nome do sistema operacional detectado pelo Python."""
    return platform.system() or "desconhecido"


def venv_python_path(venv_dir: Path, system: str | None = None) -> Path:
    """Resolve o executavel Python de uma venv sem depender do shell."""
    system = system or operating_system()
    if system == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def run_command(command: list[str]) -> None:
    print("Executando:", " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> int:
    version = sys.version_info[:3]
    print(f"Sistema detectado: {operating_system()}")
    print(f"Python detectado: {'.'.join(map(str, version))}")

    if version < MINIMUM_PYTHON:
        minimum = ".".join(map(str, MINIMUM_PYTHON))
        print(f"Erro: Python {minimum} ou mais recente e necessario.", file=sys.stderr)
        return 1
    if not REQUIREMENTS_PATH.is_file():
        print(f"Erro: dependencias nao encontradas em {REQUIREMENTS_PATH}.", file=sys.stderr)
        return 1

    python_path = venv_python_path(VENV_DIR)
    try:
        if not VENV_DIR.exists():
            print(f"Criando ambiente virtual em {VENV_DIR}...")
            run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
        else:
            print(f"Ambiente virtual existente: {VENV_DIR}")

        if not python_path.is_file():
            print(f"Erro: Python da venv nao encontrado em {python_path}.", file=sys.stderr)
            return 1

        print("Instalando dependencias do dashboard...")
        run_command(
            [
                str(python_path),
                "-m",
                "pip",
                "install",
                "-r",
                str(REQUIREMENTS_PATH),
            ]
        )
    except subprocess.CalledProcessError as exc:
        print(f"Erro: comando encerrado com codigo {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1

    print("Configuracao concluida. Use o atalho abrir_dashboard do seu sistema.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
