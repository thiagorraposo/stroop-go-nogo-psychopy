#!/usr/bin/env python3
"""Bootstrap e recuperacao local de administradores OIDC pre-cadastrados."""

from __future__ import annotations

import argparse
import os
import sys

from dashboard.auth import AuthError, bootstrap_admin, recover_admin


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Gerencia acesso administrativo de emergencia sem senhas locais."
    )
    subparsers = result.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap", help="Cria o primeiro administrador.")
    bootstrap.add_argument("--issuer", required=True)
    bootstrap.add_argument("--subject", required=True)
    bootstrap.add_argument("--email")

    recovery = subparsers.add_parser(
        "recover-admin", help="Reativa uma conta existente como administradora."
    )
    recovery.add_argument("--issuer", required=True)
    recovery.add_argument("--subject", required=True)
    recovery.add_argument("--confirm-break-glass", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv if argv is not None else sys.argv[1:])
    database_url = os.environ.get("AUTH_DATABASE_URL", "")
    if not database_url:
        print("Erro: AUTH_DATABASE_URL nao configurada.", file=sys.stderr)
        return 1
    try:
        if args.command == "bootstrap":
            bootstrap_admin(database_url, args.issuer, args.subject, args.email)
        elif not args.confirm_break_glass:
            print("Erro: recuperacao exige --confirm-break-glass.", file=sys.stderr)
            return 2
        else:
            recover_admin(database_url, args.issuer, args.subject)
    except AuthError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print("Operacao administrativa concluida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
