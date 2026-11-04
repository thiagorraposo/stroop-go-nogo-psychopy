"""Operacoes explicitas da imagem API, sem migracoes automaticas nem secrets CLI."""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import sys
from typing import Mapping
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

from api.config import APIConfig, ConfigurationError, postgres_database_url, secret_value


def trusted_proxies(value: str) -> str:
    """Confianca opt-in em IPs/CIDRs, nunca hostname resolvido implicitamente."""
    if value == '*':
        return value
    parts = value.split(',')
    if not parts or any(not part or part != part.strip() for part in parts):
        raise argparse.ArgumentTypeError('Lista de proxies invalida.')
    try:
        for part in parts:
            ipaddress.ip_network(part, strict=False)
    except ValueError:
        raise argparse.ArgumentTypeError('Lista de proxies invalida.') from None
    return ','.join(parts)


def healthcheck(environment: Mapping[str, str] | None = None) -> int:
    # Evita ler todos os secrets ou abrir a conexao PostgreSQL deste processo.
    values = os.environ if environment is None else environment
    origin = values.get('API_PUBLIC_ORIGIN', '')
    try:
        parsed = urlsplit(origin)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username is not None
                or parsed.password is not None or parsed.path not in {'', '/'}
                or parsed.query or parsed.fragment or any(c.isspace() for c in origin)):
            return 1
        hostname = f'[{parsed.hostname}]' if ':' in parsed.hostname else parsed.hostname.lower()
        host = hostname + (f':{parsed.port}' if parsed.port not in {None, 443} else '')
        request = Request('http://127.0.0.1:8000/health/ready',
                          headers={'Host': host, 'Accept': 'application/json'})
        # HTTP_PROXY/HTTPS_PROXY/ALL_PROXY nunca encaminham esta sondagem interna.
        with build_opener(ProxyHandler({})).open(request, timeout=4) as response:
            return 0 if response.status == 200 and json.loads(response.read(1025)) == {'status': 'ready'} else 1
    except Exception:
        return 1


def migrate(environment: Mapping[str, str] | None = None) -> int:
    values = os.environ if environment is None else environment
    try:
        database_url = postgres_database_url(secret_value(values, 'API_MIGRATION_DATABASE_URL'))
        from scripts.migrations import apply_migrations
        applied = apply_migrations(database_url)
    except Exception:
        print('Nao foi possivel aplicar as migrations da API.', file=sys.stderr)
        return 1
    print(f'Migrations aplicadas: {len(applied)}')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Runtime WEB: servir, verificar ou migrar explicitamente.')
    actions = parser.add_subparsers(dest='action', required=True)
    serve = actions.add_parser('serve')
    serve.add_argument('--forwarded-allow-ips', type=trusted_proxies, default=None,
                       help='IPs/CIDRs confiaveis; * somente em rede exclusivamente confinada ao proxy.')
    actions.add_parser('healthcheck')
    actions.add_parser('migrate')
    options = parser.parse_args(argv)
    if options.action == 'healthcheck':
        return healthcheck()
    if options.action == 'migrate':
        return migrate()
    try:
        # Falha antes de uvicorn importar a factory, para nao imprimir traceback/configuracao.
        config = APIConfig.from_env()
        from api.main import create_app
        import uvicorn
        uvicorn.run(create_app(config), host='0.0.0.0', port=8000,
                    access_log=False, log_level='warning', server_header=False,
                    timeout_graceful_shutdown=20,
                    proxy_headers=options.forwarded_allow_ips is not None,
                    forwarded_allow_ips=options.forwarded_allow_ips or '')
    except (ConfigurationError, OSError):
        print('Nao foi possivel iniciar a API: configuracao indisponivel ou invalida.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
