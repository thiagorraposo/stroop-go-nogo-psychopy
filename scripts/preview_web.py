#!/usr/bin/env python3
"""Abre pilha local sintetica para teste manual; nunca usa banco operacional."""
from pathlib import Path
import json
import sys
import tempfile

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import smoke_web_compose as harness


def main():
    # IP literal permite abrir no navegador sem alterar DNS/hosts do usuario.
    harness.HOST = '127.0.0.1'
    directory = Path(tempfile.mkdtemp(prefix='stroop-web-preview-'))
    directory.chmod(0o700)
    stack = None
    try:
        stack = harness.WebComposeSmoke(directory, False)
        stack.start_stack()
        stack._transport_smoke()
        admin = stack._seed_admin_session()
        headers = stack._api_headers(admin, write=True)
        status, _, project = stack._json_request('POST', '/api/v1/projects',
            {'code': 'SYNTHETIC_PREVIEW', 'name': 'Teste local sintetico'}, headers)
        stack._assert(status == 201)
        path = f"/api/v1/projects/{project['id']}"
        status, _, _ = stack._json_request('PUT',
            f"{path}/members/{admin['user_id']}", {'active': True}, headers)
        stack._assert(status == 200)
        status, _, invitation = stack._json_request('POST', f'{path}/invitations',
            {'participant_id': 'P_SYNTHETIC_PREVIEW', 'visit': 'V1'}, headers)
        stack._assert(status == 201)
        state = {'project': stack.project, 'environment_file': str(stack.environment_file),
                 'url': f'https://127.0.0.1:{stack.https_port}/',
                 'invitation': invitation['code']}
        manifest = directory / 'preview.json'
        manifest.write_text(json.dumps(state), encoding='utf8')
        manifest.chmod(0o600)
        print(json.dumps(state, ensure_ascii=False))
        return 0
    except Exception:
        if stack is not None:
            stack.cleanup()
        print('Previa integrada indisponivel; nenhum acesso foi liberado.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
