#!/usr/bin/env python3
"""Aplica migrations SQL versionadas ao PostgreSQL configurado."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import psycopg


MIGRATIONS_DIR = Path(__file__).with_name("migrations")
MIGRATION_NAME = re.compile(r"^[0-9]{4}_[a-z0-9_]+\.sql$")
LOCK_ID = 849_403_004


class MigrationError(Exception):
    """Erro seguro de configuracao ou execucao de migration."""


def discover_migrations(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]:
    if not migrations_dir.is_dir():
        raise MigrationError(f"Diretorio de migrations ausente: {migrations_dir}")
    migrations = sorted(path for path in migrations_dir.glob("*.sql") if path.is_file())
    invalid = [path.name for path in migrations if not MIGRATION_NAME.fullmatch(path.name)]
    if invalid:
        raise MigrationError("Nome de migration invalido: " + ", ".join(invalid))
    if len({path.name[:4] for path in migrations}) != len(migrations):
        raise MigrationError("Versoes de migration duplicadas.")
    return migrations


def apply_migrations(database_url: str, migrations_dir: Path = MIGRATIONS_DIR) -> list[str]:
    if not database_url:
        raise MigrationError("DATABASE_URL nao configurada.")
    migrations = discover_migrations(migrations_dir)
    applied_now: list[str] = []

    try:
        with psycopg.connect(database_url) as connection:
            with connection.transaction():
                connection.execute("SELECT pg_advisory_xact_lock(%s)", (LOCK_ID,))
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version TEXT PRIMARY KEY,
                        applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                applied = {
                    row[0]
                    for row in connection.execute(
                        "SELECT version FROM schema_migrations"
                    ).fetchall()
                }
                known = {path.name for path in migrations}
                unknown = sorted(applied - known)
                if unknown:
                    raise MigrationError(
                        "Banco contem migrations desconhecidas: " + ", ".join(unknown)
                    )

                for path in migrations:
                    if path.name in applied:
                        continue
                    sql = path.read_text(encoding="utf-8")
                    connection.execute(sql)
                    connection.execute(
                        "INSERT INTO schema_migrations (version) VALUES (%s)",
                        (path.name,),
                    )
                    applied_now.append(path.name)
    except psycopg.Error as exc:
        raise MigrationError("Falha ao aplicar migrations PostgreSQL.") from exc

    return applied_now


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aplica migrations PostgreSQL.")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL", ""))
    parser.add_argument("--migrations-dir", type=Path, default=MIGRATIONS_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        applied = apply_migrations(args.database_url, args.migrations_dir)
    except MigrationError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print(f"Migrations aplicadas: {len(applied)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
