#!/usr/bin/env python3
"""Bootstrap/recuperacao local somente em terminal de operador protegido."""
from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import sys
import warnings

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.config import postgres_database_url, secret_value
from stroop.application.local_auth import provision


def main(argv=None):
    parser = argparse.ArgumentParser(description='Provisiona a conta local sem vinculos implicitos.')
    parser.add_argument('operation', choices=('bootstrap', 'recover'))
    parser.add_argument('username')
    args = parser.parse_args(argv)
    try:
        # getpass pode cair em entrada com eco sem TTY; recusar antes disso.
        if not sys.stdin.isatty() or not sys.stderr.isatty():
            raise ValueError
        database_url = postgres_database_url(secret_value(os.environ, 'API_OPERATOR_DATABASE_URL'))
        if args.operation == 'recover':
            if input('Recuperacao revoga todas as sessoes. Digite RECUPERAR para confirmar: ') != 'RECUPERAR':
                raise ValueError
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            password = getpass.getpass('Nova senha: ')
            confirmation = getpass.getpass('Confirme a nova senha: ')
        if password != confirmation:
            raise ValueError
        success = provision(database_url, args.username, password, recover=args.operation == 'recover')
        password = confirmation = ''
        if not success:
            raise ValueError
    except Exception:
        print('Operacao recusada. Verifique acesso de operador, politica e estado da conta.', file=sys.stderr)
        return 1
    print('Operacao concluida; nenhum vinculo de projeto foi concedido.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
