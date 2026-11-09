#!/usr/bin/env python3
"""Mecanismo canônico de deploy controlado e validação para a VPS HostGator.

Integra o deploy ao GitHub Flow adotado pelo projeto Stroop:
Branch -> Commit -> Push -> Pull Request -> CI verify -> Merge Commit na main -> Deploy controlado.

Suporta modo real e modo simulação (--dry-run). Nunca expõe segredos em logs ou saídas.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VPS_HOST = "108.174.145.177"
DEFAULT_VPS_PORT = 22022
DEFAULT_VPS_USER = "raposo"
DEFAULT_RUNTIME_DIR = "/home/raposo/stroop-web"
DEFAULT_PUBLIC_URL = "https://strooptest.thiagorraposo.dev"
DEFAULT_REPO = "thiagorraposo/stroop-test-web"
HEX_SHA_REGEX = re.compile(r"^[0-9a-fA-F]{40}$")


class DeployError(Exception):
    """Erro controlado durante validação, deploy ou rollback."""


class SSHClient:
    """Cliente SSH mínimo e seguro com isolamento de credenciais e modo dry-run."""

    def __init__(
        self,
        host: str = DEFAULT_VPS_HOST,
        port: int = DEFAULT_VPS_PORT,
        user: str = DEFAULT_VPS_USER,
        key_file: str | Path | None = None,
        known_hosts_file: str | Path | None = None,
        dry_run: bool = False,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.key_file = str(key_file) if key_file else None
        self.known_hosts_file = str(known_hosts_file) if known_hosts_file else None
        self.dry_run = dry_run

    def build_ssh_args(self) -> list[str]:
        args = [
            "ssh",
            "-p",
            str(self.port),
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=15",
            "-o",
            "ServerAliveInterval=15",
        ]
        if self.known_hosts_file and Path(self.known_hosts_file).is_file():
            args.extend([
                "-o",
                "StrictHostKeyChecking=yes",
                "-o",
                f"UserKnownHostsFile={self.known_hosts_file}",
            ])
        else:
            args.extend(["-o", "StrictHostKeyChecking=accept-new"])

        if self.key_file and Path(self.key_file).is_file():
            args.extend(["-i", self.key_file, "-o", "IdentitiesOnly=yes"])

        args.append(f"{self.user}@{self.host}")
        return args

    def run(self, remote_command: str, quiet: bool = False) -> subprocess.CompletedProcess[str]:
        """Executa um comando remoto na VPS via SSH."""
        if self.dry_run:
            if not quiet:
                print(f"[DRY-RUN] SSH exec ({self.user}@{self.host}:{self.port}): {remote_command}")
            return subprocess.CompletedProcess(
                args=["ssh", f"{self.user}@{self.host}", remote_command],
                returncode=0,
                stdout="[dry-run output]\n",
                stderr="",
            )

        cmd = self.build_ssh_args() + [remote_command]
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=300,
            )
        except subprocess.TimeoutExpired as exc:
            raise DeployError(f"Tempo limite excedido na execução SSH remota ({self.host}).") from exc


def resolve_commit_sha(commit_input: str | None = None, cwd: Path = ROOT) -> str:
    """Resolve e valida o SHA exato de 40 caracteres hexadecimais."""
    target = (commit_input or "").strip()
    if not target or target.upper() == "HEAD":
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            raise DeployError("Falha ao resolver HEAD do repositório local.")
        target = res.stdout.strip()

    if not HEX_SHA_REGEX.match(target):
        raise DeployError(f"SHA de commit inválido (deve conter 40 caracteres hexadecimais): {target}")

    return target.lower()


def verify_commit_in_main(sha: str, cwd: Path = ROOT) -> bool:
    """Verifica se o commit informado pertence ou é ancestral da branch main."""
    # Tenta verificar se o commit é ancestral de origin/main ou main
    for ref in ("origin/main", "main"):
        res = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, ref],
            cwd=cwd,
            capture_output=True,
            check=False,
        )
        if res.returncode == 0:
            return True
    return False


def verify_github_ci_status(
    sha: str,
    token: str | None = None,
    repo: str = DEFAULT_REPO,
) -> bool:
    """Consulta a API do GitHub para validar se o check 'verify' da CI foi aprovado para o SHA."""
    if not token:
        token = os.environ.get("GITHUB_TOKEN")

    if not token:
        # Sem token, não é possível consultar a API do GitHub Actions
        return False

    url = f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "stroop-web-deployer",
        },
    )

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            check_runs = data.get("check_runs", [])
            for check in check_runs:
                if check.get("name") == "verify":
                    status = check.get("status")
                    conclusion = check.get("conclusion")
                    if status == "completed" and conclusion == "success":
                        return True
                    if conclusion in ("failure", "timed_out", "cancelled"):
                        raise DeployError(
                            f"Check 'verify' para {sha[:7]} falhou na CI (status={status}, conclusion={conclusion})."
                        )
    except HTTPError as exc:
        if exc.code == 404:
            # Fallback para consulta de runs de actions
            pass
        else:
            raise DeployError(f"Falha ao consultar API do GitHub: HTTP {exc.code}") from exc
    except URLError as exc:
        raise DeployError(f"Falha de conexão com a API do GitHub: {exc.reason}") from exc

    # Fallback: consultar actions/runs
    runs_url = f"https://api.github.com/repos/{repo}/actions/runs?head_sha={sha}"
    req_runs = Request(
        runs_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "stroop-web-deployer",
        },
    )
    try:
        with urlopen(req_runs, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for run in data.get("workflow_runs", []):
                if run.get("name") in ("WEB validada", "verify"):
                    if run.get("status") == "completed" and run.get("conclusion") == "success":
                        return True
                    if run.get("conclusion") in ("failure", "timed_out", "cancelled"):
                        raise DeployError(
                            f"Workflow '{run.get('name')}' para {sha[:7]} falhou na CI (conclusion={run.get('conclusion')})."
                        )
    except Exception as exc:
        if isinstance(exc, DeployError):
            raise
        return False

    return False


def probe_healthcheck(url: str = DEFAULT_PUBLIC_URL, timeout: int = 10, retries: int = 6) -> bool:
    """Verifica se o endpoint HTTPS de prontidão responde HTTP 200 com payload esperado."""
    endpoint = f"{url.rstrip('/')}/health/ready"
    req = Request(endpoint, headers={"User-Agent": "stroop-web-healthcheck"})

    for attempt in range(1, retries + 1):
        try:
            with urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("status") == "ready":
                        return True
        except Exception:
            pass
        if attempt < retries:
            time.sleep(3)

    return False


def cmd_validate(args: argparse.Namespace) -> int:
    """Valida o commit informado e o status de sua verificação de CI."""
    sha = resolve_commit_sha(args.commit)
    print(f"Commit para deploy: {sha}")

    if not args.skip_main_check:
        in_main = verify_commit_in_main(sha)
        if not in_main:
            print(f"AVISO: O commit {sha[:7]} não foi identificado localmente em main/origin/main.")
        else:
            print(f"Integridade Git: Commit {sha[:7]} pertence à branch main estável.")

    if args.skip_ci_check:
        print("AVISO: Verificação de CI ignorada por flag explícita (--skip-ci-check).")
    else:
        token = args.token or os.environ.get("GITHUB_TOKEN")
        if token:
            print(f"Consultando status do check 'verify' na CI para o commit {sha[:7]}...")
            ci_ok = verify_github_ci_status(sha, token=token, repo=args.repo)
            if not ci_ok:
                raise DeployError(
                    f"Entrega bloqueada: O commit {sha[:7]} não possui check 'verify' aprovado na CI."
                )
            print(f"Status CI: Check 'verify' APROVADO com sucesso para {sha[:7]}.")
        else:
            print("AVISO: GITHUB_TOKEN não fornecido. Validação remota de CI dispensada em ambiente local.")

    # Registra no arquivo de saída do GitHub Actions se disponível
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output and Path(github_output).is_file():
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"commit_sha={sha}\n")
            f.write(f"short_sha={sha[:7]}\n")

    return 0


def cmd_deploy(args: argparse.Namespace) -> int:
    """Executa o pipeline controlado de implantação na VPS HostGator."""
    sha = resolve_commit_sha(args.commit)
    short_sha = sha[:7]
    api_image_tag = f"stroop-web-api:deploy-{short_sha}"
    proxy_image_tag = f"stroop-web-proxy:deploy-{short_sha}"

    print(f"=== INICIANDO IMPLANTAÇÃO CONTROLADA (SHA: {short_sha}) ===")
    if args.dry_run:
        print("MODO SIMULAÇÃO ATIVO (--dry-run): Nenhuma alteração real será aplicada na VPS.")

    # 1. Validação do commit e da CI
    if not args.skip_ci_check and not args.dry_run:
        token = args.token or os.environ.get("GITHUB_TOKEN")
        if token and not verify_github_ci_status(sha, token=token, repo=args.repo):
            raise DeployError(f"Commit {short_sha} não possui check 'verify' aprovado na CI.")

    client = SSHClient(
        host=args.ssh_host,
        port=args.ssh_port,
        user=args.ssh_user,
        key_file=args.ssh_key_file,
        known_hosts_file=args.known_hosts_file,
        dry_run=args.dry_run,
    )

    # 2. Teste de conectividade SSH
    print(f"1/8. Testando conexão SSH com {args.ssh_user}@{args.ssh_host}:{args.ssh_port}...")
    res = client.run("echo PING_SSH_OK")
    if res.returncode != 0:
        raise DeployError(f"Falha de conexão SSH com a VPS HostGator: {res.stderr.strip()}")
    print("      Conexão SSH estabelecida com sucesso.")

    # 3. Snapshot de pré-deploy na VPS
    print("2/8. Executando snapshot de salvaguarda pré-deploy na VPS...")
    predeploy_cmd = (
        f"python3 {args.runtime_dir}/current/scripts/backup_postgres.py backup "
        f"--compose-file {args.runtime_dir}/current/compose.web.yaml "
        f"--env-file {args.env_file} "
        f"--project-name stroop-web --service web-postgres --database stroop_web "
        f"--user stroop_web_owner --key-file /home/{args.ssh_user}/.local/share/stroop-web/keys/predeploy.key "
        f"--output-dir /home/{args.ssh_user}/.local/share/stroop-web/backups "
        f"&& cp {args.env_file} {args.env_file}.pre-deploy "
        f"&& readlink {args.runtime_dir}/current > {args.runtime_dir}/previous_release"
    )
    res = client.run(predeploy_cmd)
    if res.returncode != 0 and not args.dry_run:
        raise DeployError(f"Falha ao executar backup preventivo na VPS: {res.stderr.strip()}")
    print("      Backup preventivo e snapshot do ambiente concluídos.")

    # 4. Preparação do diretório da nova release na VPS
    release_dir = f"{args.runtime_dir}/releases/{short_sha}"
    print(f"3/8. Criando diretório de release: {release_dir}...")
    client.run(f"mkdir -p {release_dir}")

    # 5. Manifesto da release
    manifest = {
        "commit_sha": sha,
        "short_sha": short_sha,
        "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "deployed_by": os.environ.get("GITHUB_ACTOR", args.ssh_user),
        "api_image": api_image_tag,
        "proxy_image": proxy_image_tag,
        "status": "active",
    }
    manifest_json = json.dumps(manifest, indent=2)
    print("4/8. Registrando manifesto da release...")
    write_manifest_cmd = f"cat << 'EOF' > {release_dir}/release.json\n{manifest_json}\nEOF"
    client.run(write_manifest_cmd)

    # 6. Atualização controlada do arquivo de ambiente (tags de imagens)
    print("5/8. Atualizando referências de imagens em web.env...")
    update_env_cmd = (
        f"sed -i 's|^WEB_API_IMAGE=.*|WEB_API_IMAGE={api_image_tag}|' {args.env_file} && "
        f"sed -i 's|^WEB_PROXY_IMAGE=.*|WEB_PROXY_IMAGE={proxy_image_tag}|' {args.env_file}"
    )
    client.run(update_env_cmd)

    # 7. Execução transacional de migrations e permissões (se aplicável)
    print("6/8. Executando migrations aditivas e provisionamento de papéis...")
    migrate_cmd = (
        f"docker compose --project-name stroop-web --env-file {args.env_file} "
        f"-f {args.runtime_dir}/current/compose.web.yaml -f {args.runtime_dir}/compose.vps.yaml "
        f"--profile web --profile web-tools run --rm web-migrate "
        f"&& docker compose --project-name stroop-web --env-file {args.env_file} "
        f"-f {args.runtime_dir}/current/compose.web.yaml -f {args.runtime_dir}/compose.vps.yaml "
        f"--profile web --profile web-tools run --rm web-provision"
    )
    res = client.run(migrate_cmd)
    if res.returncode != 0 and not args.dry_run:
        print("ERRO nas migrations ou provisionamento! Iniciando rollback...")
        cmd_rollback(args)
        raise DeployError(f"Falha na execução de migrations: {res.stderr.strip()}")

    # 8. Troca atômica de symlink e recriação dos contêineres web-api e web-proxy
    print("7/8. Chaveando symlink 'current' e reiniciando serviços web...")
    switch_cmd = (
        f"ln -sfn {release_dir} {args.runtime_dir}/current && "
        f"docker compose --project-name stroop-web --env-file {args.env_file} "
        f"-f {args.runtime_dir}/current/compose.web.yaml -f {args.runtime_dir}/compose.vps.yaml "
        f"--profile web up -d --no-deps --no-build --wait web-api web-proxy"
    )
    res = client.run(switch_cmd)
    if res.returncode != 0 and not args.dry_run:
        print("ERRO na recriação dos contêineres! Iniciando rollback...")
        cmd_rollback(args)
        raise DeployError(f"Falha na recriação de contêineres: {res.stderr.strip()}")

    # 9. Healthcheck pós-implantação
    print("8/8. Verificando healthcheck pós-deploy...")
    if args.dry_run:
        print("      [DRY-RUN] Healthcheck simulado: OK.")
    elif not args.skip_healthcheck:
        healthy = probe_healthcheck(url=args.public_url, timeout=10, retries=8)
        if not healthy:
            print("ERRO: Healthcheck público falhou após o deploy! Iniciando rollback automático...")
            cmd_rollback(args)
            raise DeployError(f"Healthcheck pós-deploy falhou em {args.public_url}/health/ready.")
        print(f"      Healthcheck aprovado: {args.public_url}/health/ready retornou HTTP 200 OK.")

    print(f"=== IMPLANTAÇÃO CONTROLADA CONCLUÍDA COM SUCESSO (SHA: {short_sha}) ===")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    """Executa rollback rápido para a versão anterior preservada."""
    print("=== INICIANDO PROCEDIMENTO DE ROLLBACK NA VPS HOSTGATOR ===")
    client = SSHClient(
        host=args.ssh_host,
        port=args.ssh_port,
        user=args.ssh_user,
        key_file=args.ssh_key_file,
        known_hosts_file=args.known_hosts_file,
        dry_run=args.dry_run,
    )

    # Descobre o release alvo para rollback
    target_release = args.target_release
    if not target_release:
        res = client.run(f"cat {args.runtime_dir}/previous_release 2>/dev/null || true")
        target_path = res.stdout.strip()
        if target_path and "/" in target_path:
            target_release = target_path.split("/")[-1]

    if not target_release and not args.dry_run:
        raise DeployError("Não foi possível identificar a release anterior para rollback.")

    target_release = target_release or "previous"
    print(f"Revertendo symlink 'current' para a release: {target_release}...")

    rollback_cmd = (
        f"if [ -d '{args.runtime_dir}/releases/{target_release}' ]; then "
        f"  ln -sfn '{args.runtime_dir}/releases/{target_release}' '{args.runtime_dir}/current'; "
        f"elif [ -d '{target_release}' ]; then "
        f"  ln -sfn '{target_release}' '{args.runtime_dir}/current'; "
        f"fi && "
        f"if [ -f '{args.env_file}.pre-deploy' ]; then "
        f"  cp '{args.env_file}.pre-deploy' '{args.env_file}'; "
        f"fi && "
        f"docker compose --project-name stroop-web --env-file '{args.env_file}' "
        f"-f '{args.runtime_dir}/current/compose.web.yaml' -f '{args.runtime_dir}/compose.vps.yaml' "
        f"--profile web up -d --no-deps --no-build --wait web-api web-proxy"
    )

    res = client.run(rollback_cmd)
    if res.returncode != 0 and not args.dry_run:
        raise DeployError(f"Falha ao executar comandos de rollback na VPS: {res.stderr.strip()}")

    if not args.dry_run:
        healthy = probe_healthcheck(url=args.public_url, timeout=10, retries=5)
        if healthy:
            print(f"Rollback concluído: Sistema restaurado e saudável em {args.public_url}.")
        else:
            print(f"ATENÇÃO: Rollback executado, mas healthcheck não respondeu prontidão em {args.public_url}.")

    return 0


def cmd_healthcheck(args: argparse.Namespace) -> int:
    """Verifica saúde do endpoint público da aplicação."""
    print(f"Sondando prontidão em {args.public_url}/health/ready...")
    ok = probe_healthcheck(url=args.public_url, timeout=args.timeout, retries=args.retries)
    if ok:
        print("Saúde da aplicação: PRONTA (HTTP 200 OK, status='ready').")
        return 0
    print("Saúde da aplicação: FALHA (não respondeu prontidão no tempo limite).", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mecanismo de deploy e validação para VPS HostGator (Stroop Web)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando validate
    p_val = subparsers.add_parser("validate", help="Valida SHA e status da CI")
    p_val.add_argument("--commit", default="HEAD", help="SHA de commit ou HEAD")
    p_val.add_argument("--token", default=None, help="GitHub Token para consulta de API")
    p_val.add_argument("--repo", default=DEFAULT_REPO, help="Repositório GitHub")
    p_val.add_argument("--skip-main-check", action="store_true", help="Ignora verificação de ancestral de main")
    p_val.add_argument("--skip-ci-check", action="store_true", help="Ignora verificação de CI")

    # Subcomando deploy
    p_dep = subparsers.add_parser("deploy", help="Executa deploy controlado na VPS")
    p_dep.add_argument("--commit", default="HEAD", help="SHA de commit ou HEAD")
    p_dep.add_argument("--ssh-host", default=DEFAULT_VPS_HOST, help="Endereço IP ou hostname da VPS")
    p_dep.add_argument("--ssh-port", type=int, default=DEFAULT_VPS_PORT, help="Porta SSH")
    p_dep.add_argument("--ssh-user", default=DEFAULT_VPS_USER, help="Usuário SSH na VPS")
    p_dep.add_argument("--ssh-key-file", default=None, help="Caminho da chave privada SSH")
    p_dep.add_argument("--known-hosts-file", default=None, help="Caminho do arquivo known_hosts")
    p_dep.add_argument("--runtime-dir", default=DEFAULT_RUNTIME_DIR, help="Diretório da aplicação na VPS")
    p_dep.add_argument("--env-file", default=f"{DEFAULT_RUNTIME_DIR}/web.env", help="Arquivo web.env na VPS")
    p_dep.add_argument("--public-url", default=DEFAULT_PUBLIC_URL, help="URL pública para healthcheck")
    p_dep.add_argument("--dry-run", action="store_true", help="Executa em modo simulação sem aplicar alterações")
    p_dep.add_argument("--skip-ci-check", action="store_true", help="Ignora verificação de CI")
    p_dep.add_argument("--skip-healthcheck", action="store_true", help="Pula verificação pós-deploy")
    p_dep.add_argument("--token", default=None, help="GitHub Token")
    p_dep.add_argument("--repo", default=DEFAULT_REPO, help="Repositório GitHub")

    # Subcomando rollback
    p_rb = subparsers.add_parser("rollback", help="Executa rollback para a release anterior")
    p_rb.add_argument("--target-release", default=None, help="SHA ou pasta da release alvo")
    p_rb.add_argument("--ssh-host", default=DEFAULT_VPS_HOST, help="Endereço IP ou hostname da VPS")
    p_rb.add_argument("--ssh-port", type=int, default=DEFAULT_VPS_PORT, help="Porta SSH")
    p_rb.add_argument("--ssh-user", default=DEFAULT_VPS_USER, help="Usuário SSH na VPS")
    p_rb.add_argument("--ssh-key-file", default=None, help="Caminho da chave privada SSH")
    p_rb.add_argument("--known-hosts-file", default=None, help="Caminho do arquivo known_hosts")
    p_rb.add_argument("--runtime-dir", default=DEFAULT_RUNTIME_DIR, help="Diretório da aplicação na VPS")
    p_rb.add_argument("--env-file", default=f"{DEFAULT_RUNTIME_DIR}/web.env", help="Arquivo web.env na VPS")
    p_rb.add_argument("--public-url", default=DEFAULT_PUBLIC_URL, help="URL pública para healthcheck")
    p_rb.add_argument("--dry-run", action="store_true", help="Executa em modo simulação")

    # Subcomando healthcheck
    p_hc = subparsers.add_parser("healthcheck", help="Sonda o endpoint público de prontidão")
    p_hc.add_argument("--public-url", default=DEFAULT_PUBLIC_URL, help="URL pública")
    p_hc.add_argument("--timeout", type=int, default=10, help="Timeout por tentativa em segundos")
    p_hc.add_argument("--retries", type=int, default=6, help="Número de tentativas")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            return cmd_validate(args)
        if args.command == "deploy":
            return cmd_deploy(args)
        if args.command == "rollback":
            return cmd_rollback(args)
        if args.command == "healthcheck":
            return cmd_healthcheck(args)
        parser.print_help()
        return 1
    except DeployError as exc:
        print(f"ERRO DE DEPLOY: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
