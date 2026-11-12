"""Testes unitários do mecanismo de deploy e rollback para a VPS HostGator."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from scripts import deploy_vps
from scripts.deploy_vps import (
    DeployError,
    SSHClient,
    probe_healthcheck,
    resolve_commit_sha,
    verify_commit_in_main,
    verify_github_ci_status,
)

ROOT = Path(__file__).resolve().parents[1]
WEB_ROLLBACK_SCRIPT = ROOT / "deploy/vps-web-rollback.sh"


class DeployVPSTests(unittest.TestCase):
    def test_resolve_commit_sha_valido_e_invalido(self) -> None:
        valid_sha = "0123456789abcdef0123456789abcdef01234567"
        self.assertEqual(resolve_commit_sha(valid_sha), valid_sha.lower())
        self.assertEqual(resolve_commit_sha(valid_sha.upper()), valid_sha.lower())

        # Vazio ou HEAD resolve para o commit atual do repositório
        self.assertEqual(len(resolve_commit_sha("")), 40)
        self.assertEqual(len(resolve_commit_sha("HEAD")), 40)
        self.assertEqual(len(resolve_commit_sha(None)), 40)

        for invalid in ("short", "1234", "g" * 40, "0123456789abcdef0123456789abcdef0123456!", "z" * 40):
            with self.assertRaises(DeployError):
                resolve_commit_sha(invalid)

    def test_ssh_client_build_ssh_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "id_ed25519"
            key_path.write_text("SINTETICO")
            hosts_path = Path(tmpdir) / "known_hosts"
            hosts_path.write_text("SINTETICO")

            client = SSHClient(
                host="108.174.145.177",
                port=22022,
                user="raposo",
                key_file=key_path,
                known_hosts_file=hosts_path,
            )
            args = client.build_ssh_args()
            self.assertIn("ssh", args)
            self.assertIn("-p", args)
            self.assertIn("22022", args)
            self.assertIn("StrictHostKeyChecking=yes", " ".join(args))
            self.assertIn(f"UserKnownHostsFile={hosts_path}", " ".join(args))
            self.assertIn(f"-i {key_path}", " ".join(args))
            self.assertEqual(args[-1], "raposo@108.174.145.177")

    def test_ssh_client_dry_run_nao_dispara_processos(self) -> None:
        client = SSHClient(host="108.174.145.177", port=22022, user="raposo", dry_run=True)
        with patch("subprocess.run") as mock_run:
            res = client.run("docker compose ps", quiet=True)
            mock_run.assert_not_called()
            self.assertEqual(res.returncode, 0)
            self.assertIn("[dry-run output]", res.stdout)

    def test_verify_github_ci_status_aprovado(self) -> None:
        sha = "a" * 40
        fake_payload = json.dumps({
            "check_runs": [
                {"name": "verify", "status": "completed", "conclusion": "success"}
            ]
        }).encode("utf-8")

        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_payload
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        with patch("scripts.deploy_vps.urlopen", return_value=mock_resp):
            ok = verify_github_ci_status(sha, token="fake_token")
            self.assertTrue(ok)

    def test_verify_github_ci_status_reprovado_lanca_erro(self) -> None:
        sha = "b" * 40
        fake_payload = json.dumps({
            "check_runs": [
                {"name": "verify", "status": "completed", "conclusion": "failure"}
            ]
        }).encode("utf-8")

        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_payload
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp

        with patch("scripts.deploy_vps.urlopen", return_value=mock_resp):
            with self.assertRaises(DeployError) as ctx:
                verify_github_ci_status(sha, token="fake_token")
            self.assertIn("falhou na CI", str(ctx.exception))

    def test_probe_healthcheck_sucesso_e_falha(self) -> None:
        # Sucesso
        mock_ok = MagicMock()
        mock_ok.status = 200
        mock_ok.read.return_value = b'{"status":"ready"}'
        mock_ok.__enter__.return_value = mock_ok
        with patch("scripts.deploy_vps.urlopen", return_value=mock_ok):
            self.assertTrue(probe_healthcheck("https://strooptest.thiagorraposo.dev", retries=1))

        # Falha
        mock_fail = MagicMock()
        mock_fail.status = 500
        mock_fail.read.return_value = b'{"status":"down"}'
        mock_fail.__enter__.return_value = mock_fail
        with patch("scripts.deploy_vps.urlopen", return_value=mock_fail):
            self.assertFalse(probe_healthcheck("https://strooptest.thiagorraposo.dev", retries=1))

    def test_cmd_validate_com_flags(self) -> None:
        # Validação de HEAD com --skip-ci-check
        code = deploy_vps.main(["validate", "--commit", "HEAD", "--skip-ci-check"])
        self.assertEqual(code, 0)

    def test_cmd_deploy_dry_run_completo(self) -> None:
        code = deploy_vps.main([
            "deploy",
            "--commit",
            "HEAD",
            "--dry-run",
            "--skip-ci-check",
            "--skip-healthcheck",
        ])
        self.assertEqual(code, 0)

    def test_cmd_rollback_dry_run(self) -> None:
        code = deploy_vps.main([
            "rollback",
            "--dry-run",
            "--target-release",
            "26fa9bf",
        ])
        self.assertEqual(code, 0)


class VPSWebRollbackScriptTests(unittest.TestCase):
    def execute_script(self, healthy: bool, target: str | None = None) -> tuple[subprocess.CompletedProcess[str], str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "stroop-web"
            releases = runtime / "releases"
            releases.mkdir(parents=True)
            prev_dir = releases / "26fa9bf"
            prev_dir.mkdir()
            (runtime / "previous_release").write_text(str(prev_dir))
            (runtime / "web.env.pre-deploy").write_text("WEB_APP_ENV=production\n")

            bin_dir = root / "bin"
            bin_dir.mkdir()
            log = root / "commands.log"

            (bin_dir / "docker").write_text(
                '#!/bin/sh\nprintf "docker %s\\n" "$*" >> "$SYNTHETIC_COMMAND_LOG"\n'
            )
            (bin_dir / "docker").chmod(0o700)

            (bin_dir / "curl").write_text(
                '#!/bin/sh\nprintf "curl %s\\n" "$*" >> "$SYNTHETIC_COMMAND_LOG"\nexit "$SYNTHETIC_HEALTH_STATUS"\n'
            )
            (bin_dir / "curl").chmod(0o700)

            (bin_dir / "sleep").write_text("#!/bin/sh\nexit 0\n")
            (bin_dir / "sleep").chmod(0o700)

            args = ["/bin/sh", str(WEB_ROLLBACK_SCRIPT)]
            if target:
                args.append(target)

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
                    "STROOP_RUNTIME_DIR": str(runtime),
                    "SYNTHETIC_COMMAND_LOG": str(log),
                    "SYNTHETIC_HEALTH_STATUS": "0" if healthy else "1",
                },
                check=False,
            )
            commands = log.read_text() if log.is_file() else ""
            return result, commands

    def test_rollback_web_sucesso_com_recriacao_e_symlink(self) -> None:
        result, commands = self.execute_script(healthy=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Rollback WEB concluido com sucesso", result.stdout)
        self.assertIn("docker compose --project-name stroop-web", commands)
        self.assertIn("up -d --no-deps --no-build --wait web-api web-proxy", commands)

    def test_rollback_web_sem_saude_retorna_codigo_erro(self) -> None:
        result, _ = self.execute_script(healthy=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("healthcheck nao respondeu", result.stderr)


if __name__ == "__main__":
    unittest.main()
