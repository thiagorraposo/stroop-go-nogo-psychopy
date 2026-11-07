"""Regenera lista publica SecLists fixada; nenhuma senha de usuario e recebida."""
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen

REVISION = 'c205c36a445bff37f8e58a9ec829105cd4975c58'
SOURCE_PATH = 'Passwords/Common-Credentials/xato-net-10-million-passwords-1000000.txt'
SOURCE_SHA256 = '424a3e03a17df0a2bc2b3ca749d81b04e79d59cb7aeec8876a5a3f308d0caf51'
URL = f'https://raw.githubusercontent.com/danielmiessler/SecLists/{REVISION}/{SOURCE_PATH}'
ROOT = Path(__file__).resolve().parents[1]


def main():
    with urlopen(URL, timeout=30) as response:
        content = response.read(16 * 1024 * 1024)
    if sha256(content).hexdigest() != SOURCE_SHA256:
        raise RuntimeError('Fonte publica divergente; lista nao alterada.')
    values = {line.casefold() for line in content.decode('utf-8').splitlines() if 15 <= len(line) <= 128}
    hashes = sorted(sha256(value.encode('utf-8')).hexdigest() for value in values)
    if len(content.splitlines()) != 1000000 or len(hashes) != 10898:
        raise RuntimeError('Contagem publica divergente; lista nao alterada.')
    target = ROOT / 'stroop/domain/password_blocklist.py'
    target.write_text('''"""Lista publica derivada de SecLists (MIT); nao sao hashes de contas.

Gerado por scripts/build_password_blocklist.py. Proveniencia/licenca:
docs/seguranca/SECLISTS_LICENSE.md. Somente entradas de 15–128 caracteres;
casefold exclusivo para consulta da lista, nunca para verificar credencial.
"""
COMMON_PASSWORD_SHA256 = frozenset("""\n''' + '\n'.join(hashes) + '\n""".split())\n', encoding='utf-8')
    print(f'Lista publica gerada: {len(hashes)} digests, fonte conferida por SHA-256.')


if __name__ == '__main__':
    main()
