#!/usr/bin/env python3
"""Mede HTTPS/API/DB em pilha local sintetica exclusiva, sem aceitar alvo remoto.

Um GET/segundo por sessao, quatro consultas autenticadas, limites padrao ativos.
Nao mede motor experimental, Google real, coorte grande ou capacidade da VPS.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import secrets
import sys
import tempfile
import time

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.monitor_web import check
from scripts.smoke_web_compose import HOST, WebComposeSmoke, _run

API_IMAGE = 'stroop-web-api:w21'
PROXY_IMAGE = 'stroop-web-proxy:w21'


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    return sorted(values)[max(0, math.ceil(fraction * len(values)) - 1)]


def summarize(records: list[dict], elapsed: float, clients: int, seconds: int) -> dict:
    successes = [row['elapsed_ms'] for row in records if row['status'] == 200 and row['valid']]
    return {
        'clients': clients, 'offered_rps': clients, 'scheduled_requests': clients * seconds,
        'recorded_requests': len(records), 'successful_requests': len(successes),
        'statuses': dict(Counter(str(row['status']) for row in records)),
        'invalid_200_responses': sum(row['status'] == 200 and not row['valid'] for row in records),
        'elapsed_seconds': elapsed,
        'successful_rps': len(successes) / elapsed,
        'success_latency_ms': {'p50': percentile(successes, .5),
                               'p95': percentile(successes, .95),
                               'p99': percentile(successes, .99)},
        'all_scheduled_succeeded': len(successes) == clients * seconds,
    }


def seed_sessions(stack: WebComposeSmoke, count: int) -> list[str]:
    tokens = [secrets.token_urlsafe(32) for _ in range(count)]
    helper = f'''import hashlib, os
import psycopg
from api.config import secret_value
with psycopg.connect(secret_value(os.environ,'API_MIGRATION_DATABASE_URL')) as db:
    for token in {tokens!r}:
        db.execute("INSERT INTO web_professional_sessions(token_sha256,issuer,subject,oidc_expires_at,expires_at) VALUES (%s,'https://accounts.google.com','synthetic-w19-admin',CURRENT_TIMESTAMP+INTERVAL '1 hour',CURRENT_TIMESTAMP+INTERVAL '1 hour')", (hashlib.sha256(token.encode('ascii')).hexdigest(),))
print('seeded')
'''
    stack._assert(stack.compose('run', '--rm', '--no-deps', '--interactive', '--entrypoint',
                                'python', 'web-provision', '-', input_text=helper) == 'seeded')
    return tokens


def measure(stack: WebComposeSmoke, clients: int, seconds: int,
            project: str, assessment: str) -> tuple[dict, list[dict]]:
    tokens = seed_sessions(stack, clients)
    paths = [
        ('projects', '/api/v1/projects'),
        ('list', f'/api/v1/projects/{project}/assessments'),
        ('detail', f'/api/v1/projects/{project}/assessments/{assessment}'),
        ('csv', f'/api/v1/projects/{project}/assessments/{assessment}/export'),
    ]
    # Repor burst consumido pelo provisionamento, sem alterar nenhum limitador.
    time.sleep(3)
    started = time.monotonic()

    def worker(index: int) -> list[dict]:
        records = []
        headers = {'Cookie': f'__Host-stroop_professional={tokens[index]}',
                   'Origin': f'https://{HOST}:{stack.https_port}'}
        for tick in range(seconds):
            scheduled = started + tick + index / clients
            time.sleep(max(0, scheduled - time.monotonic()))
            if time.monotonic() >= started + seconds:
                break
            label, path = paths[(tick + index) % len(paths)]
            before = time.monotonic()
            status, valid = 'transport_error', False
            try:
                status, _, body = stack._request(tls=True, method='GET', path=path, headers=headers)
                if status == 200:
                    if label == 'csv':
                        import csv, io
                        rows = list(csv.reader(io.StringIO(body.decode('utf-8'))))
                        valid = len(rows) == 17 and len(rows[0]) == 21
                    else:
                        data = json.loads(body)
                        valid = (len(data.get('trials', [])) == 16 if label == 'detail'
                                 else len(data.get('items', [])) == 1)
            except Exception:
                # Nunca persistir corpo, headers, cookies, URLs ou excecao livre.
                pass
            records.append({'client': index + 1, 'operation': label, 'status': status,
                            'valid': valid, 'started_at_seconds': before - started,
                            'elapsed_ms': (time.monotonic() - before) * 1000})
        return records

    with ThreadPoolExecutor(max_workers=clients) as executor:
        records = [row for result in executor.map(worker, range(clients)) for row in result]
    time.sleep(max(0, started + seconds - time.monotonic()))
    elapsed = time.monotonic() - started
    summary = summarize(records, elapsed, clients, seconds)
    # Apenas logs dos containers sinteticos; nunca imprimir seu conteudo.
    for service in ('web-api', 'web-proxy'):
        logs = stack.compose('logs', '--no-color', '--no-log-prefix', service)
        stack._assert(not any(token in logs for token in tokens))
    summary['session_canaries_absent_from_logs'] = True
    return summary, records


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-images', action='store_true')
    parser.add_argument('--duration-seconds', type=int, default=30, choices=range(5, 121))
    parser.add_argument('--levels', default='1,4,8,16')
    parser.add_argument('--output', type=Path, required=True)
    options = parser.parse_args(argv)
    try:
        levels = [int(value) for value in options.levels.split(',')]
        if not levels or levels != sorted(set(levels)) or not all(1 <= n <= 32 for n in levels):
            raise ValueError
    except ValueError:
        parser.error('--levels exige niveis crescentes unicos entre 1 e 32')
    # Criacao exclusiva impede sobrescrever evidencia anterior ou arquivo alheio.
    options.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(options.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    report = {'schema': 'stroop-w21-local-capacity-v1',
              'created_at': datetime.now(timezone.utc).isoformat(), 'status': 'failed',
              'scope': 'isolated-local-compose', 'dataset_assessments': 1,
              'synthetic_oidc_session_fixture': True, 'physical_timing_measured': False,
              'defaults_changed': False, 'stages': [], 'samples': []}
    stage, stack = 'stack', None
    try:
        with tempfile.TemporaryDirectory(prefix='stroop-w21-') as directory:
            stack = WebComposeSmoke(Path(directory), options.build_images,
                                    api_image=API_IMAGE, proxy_image=PROXY_IMAGE)
            try:
                stack.start_stack()
                stage = 'transport'
                stack._transport_smoke()
                stage = 'reader'
                stack._read_only_role_smoke()
                stage = 'collection'
                project, assessment, _, _ = stack._collect_and_query()
                report['images'] = {label: _run(['docker', 'image', 'inspect', '--format', '{{.Id}}', image])
                                    for label, image in [('api', API_IMAGE), ('proxy', PROXY_IMAGE)]}
                report['host'] = {'logical_cpus': os.cpu_count()}
                report['resource_limits'] = {}
                for service in ('web-postgres', 'web-api', 'web-proxy'):
                    limits = json.loads(_run(['docker', 'inspect', '--format', '{{json .HostConfig}}',
                                              stack._health(service)]))
                    report['resource_limits'][service] = {
                        'memory_bytes': limits['Memory'], 'nano_cpus': limits['NanoCpus']}
                before = check(stack.environment_file, stack.project)
                stack._assert(before['status'] == 'ready')
                stage = 'load'
                for clients in levels:
                    print(f'[w21] medindo {clients} sessoes a 1 GET/s por {options.duration_seconds}s', file=sys.stderr)
                    summary, records = measure(stack, clients, options.duration_seconds, project, assessment)
                    report['stages'].append(summary)
                    report['samples'].append({'clients': clients, 'records': records})
                stage = 'restart'
                stack.compose('restart', 'web-postgres', 'web-api', 'web-proxy')
                for service in ('web-postgres', 'web-api', 'web-proxy'):
                    stack.wait_healthy(service)
                after = check(stack.environment_file, stack.project)
                stack._assert(after['status'] == 'ready' and after['counts'] == before['counts'])
                report.update(status='measured', all_containers_restart=True,
                              counts_preserved=after['counts'], host_reboot_tested=False)
                # Nao extrapolar alem da maior combinacao efetivamente ensaiada.
                report['highest_tested_clients_all_successful'] = max(
                    (row['clients'] for row in report['stages'] if row['all_scheduled_succeeded']), default=0)
            finally:
                stage = 'cleanup' if report['status'] == 'measured' else stage
                stack.cleanup()
                stack = None
    except Exception:
        report['status'] = 'failed'
        report['failed_stage'] = stage
    finally:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(report, output, ensure_ascii=False, indent=2)
            output.write('\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'samples'}))
    return int(report['status'] != 'measured')


if __name__ == '__main__':
    raise SystemExit(main())
