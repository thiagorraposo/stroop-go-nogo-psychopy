"""Prontidao somente leitura; nao aplica migrations nem cria schema."""

from pathlib import Path
import re

import psycopg


MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "scripts" / "migrations"
MIGRATION_NAME = re.compile(r"^[0-9]{4}_[a-z0-9_]+\.sql$")


def database_ready(database_url: str) -> bool:
    try:
        if not MIGRATIONS_DIR.is_dir():
            return False
        migrations = {path.name for path in MIGRATIONS_DIR.glob("*.sql") if path.is_file()}
        if not migrations or any(not MIGRATION_NAME.fullmatch(name) for name in migrations):
            return False
        if len({name[:4] for name in migrations}) != len(migrations):
            return False
        with psycopg.connect(
            database_url, connect_timeout=3, autocommit=True,
            options="-c default_transaction_read_only=on -c statement_timeout=3000",
        ) as connection:
            applied = {row[0] for row in connection.execute(
                "SELECT version FROM public.schema_migrations"
            ).fetchall()}
        return applied == migrations
    except (psycopg.Error, OSError, ValueError):
        return False
