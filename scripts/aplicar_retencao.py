#!/usr/bin/env python3
"""Aplica somente retencao de auditorias; nunca remove dados da pesquisa."""

from __future__ import annotations

import argparse
import os
import sys

import psycopg


DEFAULT_OPERATIONAL_DAYS = 30
DEFAULT_AUTH_DAYS = 180
MAX_DAYS = 36_500


class RetentionError(Exception):
    """Erro operacional sanitizado."""


def _days(value: str | int, label: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise RetentionError(f"{label} deve ser um numero inteiro.") from None
    if not 1 <= parsed <= MAX_DAYS:
        raise RetentionError(f"{label} fora do intervalo permitido.")
    return parsed


def apply_retention(
    database_url: str,
    *,
    operational_days: int = DEFAULT_OPERATIONAL_DAYS,
    auth_days: int = DEFAULT_AUTH_DAYS,
    apply: bool = False,
) -> dict[str, int]:
    """Conta ou elimina auditorias vencidas, sem consultar seu conteudo."""
    if not database_url:
        raise RetentionError("AUTH_DATABASE_URL nao configurada.")
    operational_days = _days(operational_days, "Retencao operacional")
    auth_days = _days(auth_days, "Retencao de autenticacao")
    try:
        with psycopg.connect(database_url) as connection:
            if apply:
                import_count = connection.execute(
                    """
                    DELETE FROM import_audit_events
                    WHERE occurred_at < CURRENT_TIMESTAMP - make_interval(days => %s)
                    """,
                    (operational_days,),
                ).rowcount
                auth_count = connection.execute(
                    """
                    DELETE FROM auth_audit_events
                    WHERE occurred_at < CURRENT_TIMESTAMP - make_interval(days => %s)
                    """,
                    (auth_days,),
                ).rowcount
            else:
                import_count = connection.execute(
                    """
                    SELECT COUNT(*) FROM import_audit_events
                    WHERE occurred_at < CURRENT_TIMESTAMP - make_interval(days => %s)
                    """,
                    (operational_days,),
                ).fetchone()[0]
                auth_count = connection.execute(
                    """
                    SELECT COUNT(*) FROM auth_audit_events
                    WHERE occurred_at < CURRENT_TIMESTAMP - make_interval(days => %s)
                    """,
                    (auth_days,),
                ).fetchone()[0]
        return {"operational": int(import_count), "authentication": int(auth_count)}
    except psycopg.Error as exc:
        raise RetentionError("Falha ao aplicar retencao de auditorias.") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Conta auditorias vencidas; use --apply para elimina-las."
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--operational-days",
        default=os.environ.get(
            "OPERATIONAL_LOG_RETENTION_DAYS", str(DEFAULT_OPERATIONAL_DAYS)
        ),
    )
    parser.add_argument(
        "--auth-days",
        default=os.environ.get("AUTH_AUDIT_RETENTION_DAYS", str(DEFAULT_AUTH_DAYS)),
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    try:
        counts = apply_retention(
            os.environ.get("AUTH_DATABASE_URL", ""),
            operational_days=args.operational_days,
            auth_days=args.auth_days,
            apply=args.apply,
        )
    except RetentionError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    mode = "eliminadas" if args.apply else "vencidas"
    print(
        f"Auditorias {mode}: operacionais={counts['operational']}; "
        f"autenticacao={counts['authentication']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
