#!/usr/bin/env python3
"""Importacao transacional do CSV Stroop para PostgreSQL, sem alterar o legado."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

import psycopg

# Execucao direta por caminho continua funcionando sem instalar o pacote local.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stroop.application.errors import DuplicateAssessmentError, PostgresImportError
from stroop.application.import_postgres import import_csv


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, "Argumentos invalidos. Consulte --help.\n")


def main(argv: list[str] | None = None) -> int:
    parser = SafeArgumentParser(description="Importa CSV Stroop via DATABASE_URL.")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--force", action="store_true", help="Substitui avaliacao existente em transacao.")
    parser.add_argument("--validate-only", action="store_true", help="Valida CSV sem conectar ou persistir.")
    args = parser.parse_args(argv)
    try:
        result = import_csv(args.csv_path, os.environ.get("DATABASE_URL", ""),
                            force=args.force, validate_only=args.validate_only)
    except DuplicateAssessmentError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except PostgresImportError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Importacao: {result['status']}; tentativas={result['trials']}; metricas={result['metrics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
