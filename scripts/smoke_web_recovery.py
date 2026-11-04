#!/usr/bin/env python3
"""Ensaio WEB sintetico: backup, restauracao, falha de banco e rollback."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile
import time

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.backup_postgres import create_backup, generate_key, restore_isolated
from scripts.monitor_web import check
from scripts.migrations import discover_migrations
from scripts.smoke_web_compose import API_IMAGE, PROXY_IMAGE, WebComposeSmoke, _run


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-image', default=API_IMAGE)
    parser.add_argument('--proxy-image', default=PROXY_IMAGE)
    options = parser.parse_args(argv)
    stack = None
    candidate = None
    stage = 'stack'
    try:
        with tempfile.TemporaryDirectory(prefix='stroop-web-recovery-') as directory:
            root = Path(directory)
            stack = WebComposeSmoke(root, False, api_image=options.api_image,
                                    proxy_image=options.proxy_image)
            try:
                stack.run()
                stage = 'monitor'
                before = check(stack.environment_file, stack.project)
                stack._assert(before['status'] == 'ready' and before['counts']['web_assessments'] == 1)
                key = root / 'keys' / 'recovery.key'
                key.parent.mkdir(mode=0o700)
                generate_key(key)
                started = time.monotonic()
                stage = 'backup'
                backup = create_backup(compose_file=Path(__file__).resolve().parents[1] / 'compose.web.yaml',
                    key_file=key, output_directory=root / 'backups', database='stroop_w19',
                    user='stroop_owner', service='web-postgres', project_name=stack.project,
                    env_file=stack.environment_file)
                stage = 'restore'
                migrations, assessments = restore_isolated(backup, key, verify_web=True)
                stack._assert(migrations == len(discover_migrations()) and assessments == 1)
                restoration_seconds = round(time.monotonic() - started, 3)
                stage = 'outage'
                stack.compose('stop', 'web-postgres')
                outage = check(stack.environment_file, stack.project)
                stack._assert(outage['alert'] and outage['status'] == 'unavailable')
                stack.compose('start', 'web-postgres')
                stack.wait_healthy('web-postgres')
                stack.wait_healthy('web-api')
                # Candidato deliberadamente invalido, sem alterar a imagem aceita.
                stage = 'rollback'
                candidate = stack.project + ':invalid-candidate'
                context = root / 'candidate-context'
                context.mkdir(mode=0o700)
                dockerfile = context / 'Dockerfile'
                dockerfile.write_text(f'FROM {stack.api_image}\nENTRYPOINT ["python","-c","raise SystemExit(1)"]\n')
                _run(['docker','build','-f',str(dockerfile),'-t',candidate,str(context)])
                override = root / 'rollback.yaml'
                override.write_text(f'services:\n  web-api:\n    image: {candidate}\n    restart: "no"\n')
                _run([*stack._compose_prefix,'-f',str(override),'up','-d','--no-deps','--no-build','web-api'])
                time.sleep(2)
                stack._assert(check(stack.environment_file,stack.project)['alert'])
                stack.compose('up','-d','--no-deps','--no-build','--force-recreate','web-api')
                stack.wait_healthy('web-api')
                after = check(stack.environment_file, stack.project)
                stack._assert(after['status'] == 'ready' and after['counts'] == before['counts'])
                print(json.dumps({'status':'passed','restoration_seconds':restoration_seconds,
                    'restored_assessments':assessments,'restored_migrations':migrations,'database_outage_detected':True,
                    'failed_candidate_rollback':True,'counts_preserved':True}))
            finally:
                stack.cleanup()
                stack = None
        return 0
    except Exception as error:
        print(f'Ensaio WEB de recuperacao falhou em {stage} ({type(error).__name__}); detalhes suprimidos.',file=sys.stderr)
        return 1
    finally:
        if candidate:
            subprocess.run(['docker','image','rm',candidate],capture_output=True,check=False)


if __name__ == '__main__':
    raise SystemExit(main())
