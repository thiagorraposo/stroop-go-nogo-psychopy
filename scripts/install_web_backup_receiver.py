#!/usr/bin/env python3
"""Prepara receptor local privado e timer; nao conecta nem altera a VPS."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def run(arguments):
    return subprocess.run(arguments, check=True, capture_output=True, text=True).stdout.strip()


def install():
    home = Path.home()
    config = home / '.config/stroop-web-replica'
    state = home / '.local/share/stroop-web-replica'
    destination = state / 'backups'
    status = state / 'status'
    releases = home / '.local/lib/stroop-web-replica/releases'
    units = home / '.config/systemd/user'
    for directory in (config, state, destination, status, releases):
        if directory.is_symlink():
            raise RuntimeError('Diretorio local deve ser real e privado.')
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if directory.stat().st_uid != os.getuid() or directory.stat().st_mode & 0o077:
            raise RuntimeError('Diretorio local preexistente sem protecao; revisar manualmente.')
    sources = [ROOT / 'scripts/replicate_web_backup.py', ROOT / 'scripts/backup_postgres.py']
    revision = sha256(b''.join(path.read_bytes() for path in sources)).hexdigest()
    release = releases / revision
    if not release.exists():
        release.mkdir(mode=0o700)
        (release / 'scripts').mkdir(mode=0o700)
        for source in sources:
            target = release / 'scripts' / source.name
            target.write_bytes(source.read_bytes())
            target.chmod(0o400)
        (release / 'scripts').chmod(0o500)
        release.chmod(0o500)
    else:
        for source in sources:
            if (release / 'scripts' / source.name).read_bytes() != source.read_bytes():
                raise RuntimeError('Release local diverge do hash; nenhuma substituicao.')
    key = config / 'id_ed25519'
    if not key.exists():
        run(['/usr/bin/ssh-keygen', '-q', '-t', 'ed25519', '-N', '',
             '-C', 'stroop-web031-mint-receiver', '-f', str(key)])
    known = config / 'known_hosts'
    if not known.exists():
        known.touch(mode=0o600, exist_ok=False)
    example = config / 'pull.json.pending'
    if not example.exists():
        with example.open('x') as output:
            json.dump({'host': 'PENDENTE', 'port': 22, 'user': 'pendente',
                       'key_file': str(key), 'known_hosts_file': str(known),
                       'destination': str(destination)}, output, indent=2)
            output.write('\n')
        example.chmod(0o600)
    service = (ROOT / 'deploy/stroop-web-backup-pull.service.example').read_text()
    # systemd escapa espacos e % em argumentos, nao usa expansao de shell.
    def argument(path):
        return str(path).replace('%', '%%').replace(' ', r'\x20')
    service = service.replace('/CLIENTE-IMUTAVEL', argument(release))
    service = service.replace('/CONFIGURACAO-PRIVADA', argument(config))
    service = service.replace('/ESTADO-PRIVADO', argument(status))
    timer = (ROOT / 'deploy/stroop-web-backup-pull.timer').read_text()
    units.mkdir(mode=0o700, parents=True, exist_ok=True)
    for name, contents in (('stroop-web-backup-pull.service', service),
                           ('stroop-web-backup-pull.timer', timer)):
        target = units / name
        if target.is_symlink() or (target.exists() and target.read_text() != contents):
            raise RuntimeError('Unit preexistente diferente; nenhuma substituicao.')
        target.write_text(contents)
        target.chmod(0o600)
    # Linger inicia o gerenciador no boot mesmo antes de login grafico.
    run(['loginctl', 'enable-linger', str(os.getuid())])
    run(['systemctl', '--user', 'daemon-reload'])
    run(['systemctl', '--user', 'enable', '--now', 'stroop-web-backup-pull.timer'])
    print(json.dumps({'status': 'prepared', 'release_sha256': revision,
                      'origin_configured': (config / 'pull.json').exists(),
                      'timer_enabled': True, 'private_destination': str(destination),
                      'public_key': str(key) + '.pub'}))


if __name__ == '__main__':
    install()
