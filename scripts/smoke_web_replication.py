#!/usr/bin/env python3
"""Replica SSH e agenda locais com ciphertext/chaves exclusivamente sinteticos.

Instala openssh-server somente em uma imagem Docker descartavel derivada da
imagem API informada. Nao acessa VPS, configuracao SSH do usuario ou backups.
Requer Docker, ssh/ssh-keygen e um gerenciador systemd de usuario ativo.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.backup_postgres import create_backup, generate_key, restore_isolated
from scripts.migrations import discover_migrations
from scripts.smoke_web_compose import API_IMAGE, PROXY_IMAGE, SYNTHETIC_DATABASE, WebComposeSmoke

ROOT = Path(__file__).resolve().parents[1]


def run(arguments, *, expected=0, timeout=180):
    result = subprocess.run(arguments, capture_output=True, text=True, timeout=timeout)
    if result.returncode != expected:
        raise RuntimeError('Comando sintetico recusado')
    return result.stdout.strip()


def scheduled(config: Path, temporary: Path, *, expected: int) -> dict:
    unit = 'stroop-synthetic-replica-' + secrets.token_hex(5)
    report = temporary / (unit + '.json')
    try:
        run(['systemd-run', '--user', '--quiet', '--unit=' + unit, '--on-active=1s',
             '--timer-property=AccuracySec=100ms',
             '--property=StandardOutput=file:' + str(report), '--property=StandardError=null',
             sys.executable, str(ROOT / 'scripts/replicate_web_backup.py'), '--config', str(config)])
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            state = run(['systemctl', '--user', 'show', '--property=ActiveState', '--value', unit + '.service'])
            if state in {'inactive', 'failed'} and report.exists():
                value = json.loads(report.read_text())
                status = run(['systemctl', '--user', 'show', '--property=ExecMainStatus', '--value', unit + '.service'])
                if status != str(expected):
                    raise RuntimeError('Status da agenda divergente')
                return value
            time.sleep(.1)
        raise RuntimeError('Agenda nao concluiu')
    finally:
        subprocess.run(['systemctl', '--user', 'stop', unit + '.timer', unit + '.service'], capture_output=True)
        subprocess.run(['systemctl', '--user', 'reset-failed', unit + '.service'], capture_output=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-image', default=API_IMAGE)
    parser.add_argument('--proxy-image', default=PROXY_IMAGE)
    options = parser.parse_args(argv)
    # Dockerfile FROM receives only a Docker image reference, never shell text.
    import re
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/@:-]*', image)
           for image in (options.api_image, options.proxy_image)):
        parser.error('Imagem invalida')
    identity = secrets.token_hex(5)
    image = 'stroop-synthetic-ssh:' + identity
    container = 'stroop-synthetic-ssh-' + identity
    started_container = False
    stage = 'prepare'
    try:
        with tempfile.TemporaryDirectory(prefix='stroop-synthetic-ssh-') as directory:
            temporary = Path(directory)
            context = temporary / 'context'
            context.mkdir()
            (context / 'backup_postgres.py').write_bytes((ROOT / 'scripts/backup_postgres.py').read_bytes())
            (context / 'exporter.py').write_bytes((ROOT / 'deploy/vps-export-encrypted-backup.py').read_bytes())
            (context / 'export.py').write_text('''import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('synthetic_exporter', '/app/deploy/exporter.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
try:
    module.export(os.environ.get('SSH_ORIGINAL_COMMAND', ''), base=Path('/synthetic-backups'))
except Exception:
    print('Exportacao de backup recusada.', file=sys.stderr)
    raise SystemExit(1)
''')
            (context / 'Dockerfile').write_text(f'''FROM {options.api_image}
USER root
RUN apt-get update && apt-get install --yes --no-install-recommends openssh-server && rm -rf /var/lib/apt/lists/* && mkdir -p /run/sshd /app/deploy && useradd --create-home --shell /bin/sh --password x synthetic
COPY backup_postgres.py /app/scripts/backup_postgres.py
COPY exporter.py export.py /app/deploy/
COPY authorized_keys /etc/ssh/synthetic_authorized_keys
RUN chmod 0444 /etc/ssh/synthetic_authorized_keys
ENTRYPOINT ["/usr/sbin/sshd"]
''')
            config_root = temporary / 'ssh-config'
            config_root.mkdir(mode=0o755)
            client_key = temporary / 'client-key'
            host_key = config_root / 'host-key'
            for key in (client_key, host_key):
                run(['/usr/bin/ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(key)])
            authorized = context / 'authorized_keys'
            authorized.write_text('restrict,command="/usr/local/bin/python /app/deploy/export.py" ' + client_key.with_suffix('.pub').read_text())
            authorized.chmod(0o444)
            (config_root / 'sshd_config').write_text('''Port 2222
HostKey /synthetic-config/host-key
PidFile /run/sshd/synthetic.pid
AuthorizedKeysFile /etc/ssh/synthetic_authorized_keys
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM no
PermitRootLogin no
AllowUsers synthetic
AllowTcpForwarding no
X11Forwarding no
PermitTunnel no
LogLevel VERBOSE
''')
            (config_root / 'sshd_config').chmod(0o444)
            remote = temporary / 'remote'
            remote.mkdir(mode=0o755)
            stage = 'synthetic-postgres-backup'
            backup_key = temporary / 'backup.key'
            generate_key(backup_key)
            with tempfile.TemporaryDirectory(prefix='stroop-synthetic-replica-source-') as stack_directory:
                stack = WebComposeSmoke(Path(stack_directory), False,
                    api_image=options.api_image, proxy_image=options.proxy_image)
                try:
                    stack.run()
                    source = create_backup(compose_file=ROOT / 'compose.web.yaml',
                        key_file=backup_key, output_directory=remote,
                        database=SYNTHETIC_DATABASE, user='stroop_owner', service='web-postgres',
                        project_name=stack.project, env_file=stack.environment_file)
                finally:
                    stack.cleanup()
            name = source.name
            ciphertext = source.read_bytes()
            digest = sha256(ciphertext).hexdigest()
            # Make only this newly generated synthetic ciphertext readable by
            # the unprivileged SSH exporter; its AES key is never mounted.
            remote.chmod(0o755)
            source.chmod(0o644)
            source.with_suffix(source.suffix + '.sha256').chmod(0o644)
            stage = 'build-local-ssh'
            print('[replication] construindo servidor SSH descartavel', file=sys.stderr)
            run(['docker', 'build', '--tag', image, str(context)], timeout=300)
            stage = 'start-local-ssh'
            run(['docker', 'run', '--detach', '--name', container, '--publish', '127.0.0.1::2222',
                 '--mount', f'type=bind,src={config_root},dst=/synthetic-config,readonly',
                 '--mount', f'type=bind,src={remote},dst=/synthetic-backups,readonly',
                 image, '-D', '-e', '-f', '/synthetic-config/sshd_config'])
            started_container = True
            address = run(['docker', 'port', container, '2222/tcp'])
            if not address.startswith('127.0.0.1:'):
                raise RuntimeError('SSH nao isolado em loopback')
            port = int(address.rsplit(':', 1)[1])
            deadline = time.monotonic() + 15
            while True:
                try:
                    with socket.create_connection(('127.0.0.1', port), timeout=1):
                        break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(.1)
            known = temporary / 'known_hosts'
            known.write_text(f'[127.0.0.1]:{port} ' + host_key.with_suffix('.pub').read_text())
            destination = temporary / 'copies'
            values = {'host': '127.0.0.1', 'port': port, 'user': 'synthetic',
                      'key_file': str(client_key), 'known_hosts_file': str(known),
                      'destination': str(destination)}
            config = temporary / 'replica.json'
            config.write_text(json.dumps(values))
            config.chmod(0o600)
            cli = [sys.executable, str(ROOT / 'scripts/replicate_web_backup.py'), '--config', str(config)]
            stage = 'copy-and-idempotency'
            started = time.monotonic()
            first = json.loads(run(cli))
            copy_seconds = round(time.monotonic() - started, 3)
            target = destination / name
            if first['status'] != 'copied' or first['alert'] or target.read_bytes() != ciphertext:
                raise RuntimeError('Copia SSH divergente')
            if sha256(target.read_bytes()).hexdigest() != digest:
                raise RuntimeError('Checksum divergente')
            stage = 'restore-replicated-copy'
            migrations, assessments = restore_isolated(target, backup_key, verify_web=True)
            if migrations != len(discover_migrations()) or assessments != 1:
                raise RuntimeError('Copia restaurada divergente')
            stage = 'idempotency'
            inode = target.stat().st_ino
            second = json.loads(run(cli))
            if second['status'] != 'already_current' or second['copied'] or target.stat().st_ino != inode:
                raise RuntimeError('Idempotencia divergente')
            # Same real forced command must refuse arbitrary shell requests.
            from scripts.replicate_web_backup import ReplicationError, _fetch, configuration
            try:
                _fetch(configuration(values), 'cat /etc/passwd', io.BytesIO(), 65536)
            except ReplicationError:
                pass
            else:
                raise RuntimeError('Comando livre aceito')
            stage = 'scheduled-copy'
            values['destination'] = str(temporary / 'scheduled-copies')
            config.write_text(json.dumps(values))
            scheduled_report = scheduled(config, temporary, expected=0)
            if scheduled_report['status'] != 'copied' or scheduled_report['alert']:
                raise RuntimeError('Copia agendada divergente')
            if (Path(values['destination']) / name).read_bytes() != ciphertext:
                raise RuntimeError('Bytes agendados divergentes')
            stage = 'scheduled-outage-alert'
            run(['docker', 'stop', container])
            outage = scheduled(config, temporary, expected=1)
            if outage != {'status': 'unavailable', 'alert': True, 'error': 'replication_failed'}:
                raise RuntimeError('Alerta divergente')
            print(json.dumps({'status':'passed', 'real_ssh_copy':True, 'bytes':len(ciphertext),
                'checksum_verified':True, 'idempotency_verified':True, 'forced_command_rejected_shell':True,
                'scheduled_copy_verified':True, 'scheduled_outage_alert':True,
                'backup_age_seconds':first['backup_age_seconds'], 'copy_seconds':copy_seconds,
                'restored_migrations':migrations, 'restored_assessments':assessments,
                'restored_receipt_verified':True, 'external_rpo_not_measured':True}))
        return 0
    except Exception as error:
        print(f'Ensaio de replica falhou em {stage} ({type(error).__name__}); detalhes suprimidos.', file=sys.stderr)
        if started_container:
            diagnostic = subprocess.run(['docker', 'logs', container], capture_output=True, text=True)
            for marker in ('bad ownership', 'not allowed because', 'Permission denied',
                           'No such file', 'ModuleNotFoundError', 'Authentication refused'):
                if marker in diagnostic.stdout + diagnostic.stderr:
                    print('[replication] categoria: ' + marker, file=sys.stderr)
        return 1
    finally:
        if started_container:
            subprocess.run(['docker', 'rm', '--force', container], capture_output=True)
        subprocess.run(['docker', 'image', 'rm', image], capture_output=True)


if __name__ == '__main__':
    raise SystemExit(main())
