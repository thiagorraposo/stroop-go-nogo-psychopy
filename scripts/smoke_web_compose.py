#!/usr/bin/env python3
"""Smoke descartavel da pilha WEB Compose, com coleta inteiramente sintetica.

As imagens `stroop-web-api:w19` e `stroop-web-proxy:w19` devem estar prontas.
Para construi-las nesta maquina, passe `--build-images`; a construcao e serial.
Todo segredo, certificado, cookie, codigo de convite e payload fica em memoria
ou em um diretorio temporario privado removido no encerramento.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import http.client
import csv
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from urllib.parse import quote
import uuid


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "compose.web.yaml"
API_IMAGE = "stroop-web-api:w19"
PROXY_IMAGE = "stroop-web-proxy:w19"
SYNTHETIC_DATABASE = "stroop_etapa4_test_compose"
HOST = "synthetic.invalid"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


def _free_port(excluded: set[int]) -> int:
    for _ in range(8):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        if port not in excluded and port not in {4173, 4373, 4381}:
            return port
    raise SmokeFailure


class SmokeFailure(RuntimeError):
    pass


def _run(command: list[str], *, input_text: str | None = None,
         cwd: Path = ROOT, timeout: int = 180) -> str:
    try:
        completed = subprocess.run(
            command, cwd=cwd, input=input_text, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise SmokeFailure from None
    if completed.returncode:
        for marker in ('Permission denied', 'ModuleNotFoundError', 'Configuracao da API',
                       'Falha ao aplicar migrations', 'Migracao recusada'):
            if marker in completed.stderr + completed.stdout:
                print(f'[smoke] categoria de falha: {marker}', file=sys.stderr)
        raise SmokeFailure
    return completed.stdout.strip()


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Conecta ao loopback, mantendo SNI e Host sinteticos para o proxy."""

    def __init__(self, port: int, context: ssl.SSLContext, timeout: float = 8):
        super().__init__(HOST, port, timeout=timeout, context=context)

    def connect(self):
        raw = socket.create_connection(("127.0.0.1", self.port), self.timeout)
        self.sock = self._context.wrap_socket(raw, server_hostname=HOST)


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, port: int, timeout: float = 8):
        super().__init__(HOST, port, timeout=timeout)

    def connect(self):
        self.sock = socket.create_connection(("127.0.0.1", self.port), self.timeout)


class WebComposeSmoke:
    def __init__(self, temporary: Path, build_images: bool, *,
                 api_image: str = API_IMAGE, proxy_image: str = PROXY_IMAGE):
        if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/@:-]*', image)
               for image in (api_image, proxy_image)):
            raise SmokeFailure('image')
        self.api_image = api_image
        self.proxy_image = proxy_image
        self.temporary = temporary
        self.project = "stroopw19" + secrets.token_hex(5)
        self.environment_file = temporary / "compose.env"
        self.certificate = temporary / "tls_certificate.pem"
        self.private_key = temporary / "tls_private_key.pem"
        self._containers: dict[str, str] = {}
        self.http_port = _free_port(set())
        self.https_port = _free_port({self.http_port})
        self._write_secrets()
        self._write_environment()
        self._compose_prefix = [
            "docker", "compose", "--file", str(COMPOSE), "--env-file",
            str(self.environment_file), "--project-name", self.project,
            "--profile", "web", "--profile", "web-tools",
        ]
        if build_images:
            self._build_images()
        self._require_images()

    def _write_secret(self, name: str, value: str) -> Path:
        path = self.temporary / name
        path.write_text(value + "\n", encoding="utf-8")
        path.chmod(0o444)
        return path

    def _write_secrets(self):
        self.owner_password = secrets.token_urlsafe(32)
        self.session_secret = secrets.token_urlsafe(48)
        self._write_secret("postgres_password", self.owner_password)
        self.migration_url = self._dsn("stroop_owner", self.owner_password)
        self.writer_url = self._dsn("stroop_writer", secrets.token_urlsafe(32))
        self.reader_url = self._dsn("stroop_reader", secrets.token_urlsafe(32))
        self.secret_paths = {
            "WEB_POSTGRES_PASSWORD_FILE": self._write_secret("postgres_password_copy", self.owner_password),
            "WEB_MIGRATION_DATABASE_URL_FILE": self._write_secret("migration_database_url", self.migration_url),
            "WEB_DATABASE_URL_FILE": self._write_secret("api_database_url", self.writer_url),
            "WEB_READ_DATABASE_URL_FILE": self._write_secret("api_read_database_url", self.reader_url),
            "WEB_OIDC_CLIENT_ID_FILE": self._write_secret("oidc_client_id", "synthetic-client.invalid"),
            "WEB_OIDC_CLIENT_SECRET_FILE": self._write_secret("oidc_client_secret", secrets.token_urlsafe(24)),
            "WEB_SESSION_SECRET_FILE": self._write_secret("api_session_secret", self.session_secret),
            "WEB_TLS_CERTIFICATE_FILE": self.certificate,
            "WEB_TLS_PRIVATE_KEY_FILE": self.private_key,
        }
        self._create_certificate()

    @staticmethod
    def _dsn(user: str, password: str) -> str:
        return (f"postgresql://{user}:{quote(password, safe='')}@web-postgres:5432/"
                f"{SYNTHETIC_DATABASE}?connect_timeout=5")

    def _create_certificate(self):
        _run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-sha256", "-days", "7", "-subj", "/CN=stroop synthetic test",
            "-addext", f"subjectAltName=DNS:{HOST},IP:127.0.0.1",
            "-keyout", str(self.private_key), "-out", str(self.certificate),
        ], timeout=30)
        self.private_key.chmod(0o444)
        self.certificate.chmod(0o444)

    def _write_environment(self):
        # Compose dotenv: todos os demais valores sao fixos ou gerados localmente.
        values = {
            "WEB_APP_ENV": "test",
            "WEB_PUBLIC_ORIGIN": f"https://{HOST}:{self.https_port}",
            "WEB_POSTGRES_DB": SYNTHETIC_DATABASE,
            "WEB_POSTGRES_OWNER": "stroop_owner",
            "WEB_BIND_ADDRESS": "127.0.0.1",
            "WEB_HTTP_PORT": str(self.http_port),
            "WEB_HTTPS_PORT": str(self.https_port),
            "WEB_API_IMAGE": self.api_image,
            "WEB_PROXY_IMAGE": self.proxy_image,
            "WEB_ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS": "1",
        }
        values.update({key: str(value) for key, value in self.secret_paths.items()})
        self.environment_file.write_text(
            "".join(f"{key}={value}\n" for key, value in values.items()),
            encoding="utf-8",
        )
        self.environment_file.chmod(0o600)

    def _build_images(self):
        # Sequential on purpose: API and frontend builds do not compete for CPU/RAM.
        _run(["docker", "build", "--file", "Dockerfile.api", "--tag", self.api_image, "."])
        _run(["docker", "build", "--file", "Dockerfile.web", "--tag", self.proxy_image, "."])

    def _require_images(self):
        _run(["docker", "image", "inspect", self.api_image])
        _run(["docker", "image", "inspect", self.proxy_image])

    def compose(self, *args: str, input_text: str | None = None,
                timeout: int = 180) -> str:
        return _run([*self._compose_prefix, *args], input_text=input_text, timeout=timeout)

    def _health(self, service: str) -> str:
        return self.compose("ps", "--quiet", service).strip()

    def wait_healthy(self, service: str, timeout: int = 150):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            container = self._health(service)
            if container:
                state = _run([
                    "docker", "inspect", "--format",
                    "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
                    container,
                ])
                if state == "healthy":
                    self._containers[service] = container
                    return
                if state in {"exited", "dead"}:
                    raise SmokeFailure
            time.sleep(2)
        raise SmokeFailure

    def start_stack(self):
        print("[smoke] iniciando banco", file=sys.stderr)
        self.compose("up", "--detach", "--no-build", "web-postgres")
        self.wait_healthy("web-postgres")
        print("[smoke] aplicando migracoes", file=sys.stderr)
        self.compose("run", "--rm", "--no-deps", "web-migrate")
        print("[smoke] provisionando credenciais", file=sys.stderr)
        self.compose("run", "--rm", "--no-deps", "web-provision")
        print("[smoke] iniciando API e proxy", file=sys.stderr)
        self.compose("up", "--detach", "--no-build", "web-api", "web-proxy")
        self.wait_healthy("web-api")
        self.wait_healthy("web-proxy")
        print('[smoke] verificando isolamento', file=sys.stderr)
        self._assert_isolation()
        print('[smoke] verificando portas', file=sys.stderr)
        self._assert_published_port("web-proxy", "8080", self.http_port)
        self._assert_published_port("web-proxy", "8443", self.https_port)

    def _assert_published_port(self, service: str, target: str, expected: int):
        address = self.compose("port", service, target)
        try:
            value = int(address.rsplit(":", 1)[1])
        except (IndexError, ValueError):
            raise SmokeFailure from None
        if value != expected or not 1 <= value <= 65535:
            raise SmokeFailure

    def _assert_isolation(self):
        for service, expected_user in (("web-api", "10001:10001"), ("web-proxy", "101:101")):
            container = self._health(service)
            if not container:
                raise SmokeFailure
            details = json.loads(_run(["docker", "inspect", container]))[0]
            config = details.get("Config", {})
            host = details.get("HostConfig", {})
            if config.get("User") != expected_user:
                raise SmokeFailure('uid')
            if not host.get("ReadonlyRootfs"):
                raise SmokeFailure('readonly')
            if "ALL" not in host.get("CapDrop", []):
                raise SmokeFailure('capabilities')
            if not any("no-new-privileges" in item for item in host.get("SecurityOpt", [])):
                raise SmokeFailure('privileges')
            self._containers[service] = container
        for service, target in (("web-api", "8000"), ("web-postgres", "5432")):
            details = json.loads(_run(['docker', 'inspect', self._health(service)]))[0]
            if any(details.get('HostConfig', {}).get('PortBindings', {}).values()):
                raise SmokeFailure('published-port')

    def _request(self, *, tls: bool, method: str, path: str, body: bytes | None = None,
                 headers: dict[str, str] | None = None, host_header: str | None = None):
        if tls:
            context = ssl.create_default_context(cafile=str(self.certificate))
            connection = _PinnedHTTPSConnection(self.https_port, context)
        else:
            connection = _PinnedHTTPConnection(self.http_port)
        default_host = f"{HOST}:{self.https_port if tls else self.http_port}"
        request_headers = {"Host": host_header or default_host, "Accept": "application/json"}
        if body is not None:
            request_headers["Content-Type"] = "application/json"
        request_headers.update(headers or {})
        try:
            connection.request(method, path, body=body, headers=request_headers)
            response = connection.getresponse()
            payload = response.read(MAX_RESPONSE_BYTES + 1)
            if len(payload) > MAX_RESPONSE_BYTES:
                raise SmokeFailure
            return response.status, {name.lower(): value for name, value in response.getheaders()}, payload
        except (OSError, http.client.HTTPException, ssl.SSLError):
            raise SmokeFailure from None
        finally:
            connection.close()

    @staticmethod
    def _assert(condition: bool):
        if not condition:
            raise SmokeFailure

    def _transport_smoke(self):
        status, headers, body = self._request(tls=False, method="GET", path="/research?x=synthetic")
        self._assert(status == 308)
        self._assert(headers.get("location") == f"https://{HOST}:{self.https_port}/research?x=synthetic")
        status, headers, body = self._request(tls=True, method="GET", path="/")
        self._assert(status == 200 and b"<html" in body.lower())
        self._assert("content-security-policy" in headers)
        self._assert("strict-transport-security" in headers)
        status, headers, body = self._request(
            tls=True, method="GET", path="/api/v1/auth/me"
        )
        self._assert(status == 401)
        self._assert(headers.get("cache-control") == "no-store")
        request_id = headers.get("x-request-id", "")
        try:
            self._assert(str(uuid.UUID(request_id)) == request_id)
            self._assert(json.loads(body)["request_id"] == request_id)
        except (ValueError, KeyError, json.JSONDecodeError):
            raise SmokeFailure from None
        status, _, _ = self._request(
            tls=True, method="GET", path="/",
            host_header=f"attacker.invalid:{self.https_port}",
        )
        self._assert(status == 400)
        status, _, body = self._request(tls=True, method="GET", path="/health/ready")
        self._assert(status == 200 and json.loads(body) == {"status": "ready"})
        # Regex com quantificadores precisa ser aceita pelo parser real Nginx.
        # A rota CSV deixa passar mais de 64 KiB ate a autenticacao da API,
        # enquanto as demais mantem o limite global na borda.
        oversized = b' ' * (65536 + 1)
        status, _, _ = self._request(tls=True, method='POST',
            path=f'/api/v1/projects/{uuid.uuid4()}/imports/{uuid.uuid4()}', body=oversized,
            headers={'Content-Type': 'text/csv; charset=utf-8'})
        self._assert(status == 401)
        status, _, _ = self._request(tls=True, method='POST',
                                     path='/api/v1/projects', body=oversized)
        self._assert(status == 413)
        # Exercise the real proxy: a SPA fallback must never serve source,
        # configuration or secret paths, even when no matching file exists.
        for path in (
            '/.env', '/src/main.tsx', '/docs/', '/node_modules/',
            '/production-secrets/', '/Dockerfile.web', '/package-lock.json',
            '/assets/synthetic.js.map', '/scripts/synthetic.py',
        ):
            status, _, _ = self._request(tls=True, method='GET', path=path)
            self._assert(status == 404)

    def _seed_admin_session(self) -> dict[str, str]:
        # Provision container reads credentials via *_FILE; session creation is
        # a fixture operation, not an OIDC endpoint/mocked identity-provider flow.
        token = secrets.token_urlsafe(32)
        helper = f'''import hashlib, os, time
import psycopg
from api.config import secret_value, postgres_database_url
from stroop.domain.auth import opaque_user_id
owner = postgres_database_url(secret_value(os.environ, 'API_MIGRATION_DATABASE_URL'))
subject = 'synthetic-w19-admin'
token = {token!r}
expires = int(time.time()) + 3600
with psycopg.connect(owner) as db:
    db.execute("INSERT INTO app_users(issuer,subject,email,role,active) VALUES ('https://accounts.google.com',%s,NULL,'administracao',TRUE)", (subject,))
    db.execute("INSERT INTO web_professional_sessions(token_sha256,issuer,subject,oidc_expires_at,expires_at) VALUES (%s,'https://accounts.google.com',%s,to_timestamp(%s),LEAST(to_timestamp(%s),CURRENT_TIMESTAMP+INTERVAL '8 hours'))", (hashlib.sha256(token.encode('ascii')).hexdigest(),subject,expires,expires))
print('seeded')
'''
        result = self.compose(
            "run", "--rm", "--no-deps", "--interactive", "--entrypoint", "python",
            "web-provision", "-", input_text=helper,
        )
        if result != "seeded":
            raise SmokeFailure
        csrf = hmac.new(
            self.session_secret.encode("utf-8"),
            b"stroop-professional-csrf-v1\0" + token.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return {
            "cookie": token,
            "csrf": base64.urlsafe_b64encode(csrf).rstrip(b"=").decode("ascii"),
            "user_id": base64.urlsafe_b64encode(
                b"https://accounts.google.com\0synthetic-w19-admin"
            ).rstrip(b"=").decode("ascii"),
        }

    def _api_headers(self, admin: dict[str, str], *, write: bool = False):
        headers = {
            "Cookie": f"__Host-stroop_professional={admin['cookie']}",
            "Origin": f"https://{HOST}:{self.https_port}",
        }
        if write:
            headers["X-CSRF-Token"] = admin["csrf"]
        return headers

    def _json_request(self, method: str, path: str, payload: dict | None,
                      headers: dict[str, str]):
        body = None if payload is None else json.dumps(
            payload, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        status, response_headers, response = self._request(
            tls=True, method=method, path=path, body=body, headers=headers
        )
        try:
            decoded = json.loads(response) if response else None
        except json.JSONDecodeError:
            raise SmokeFailure from None
        return status, response_headers, decoded

    def _read_only_role_smoke(self):
        helper = r'''import json, os
import psycopg
from api.config import secret_value, postgres_database_url
read_url = postgres_database_url(secret_value(os.environ, 'API_READ_DATABASE_URL'))
with psycopg.connect(read_url, connect_timeout=5) as db:
    allowed = db.execute("SELECT has_column_privilege(current_user,'public.web_assessments','assessment_id','SELECT'),has_column_privilege(current_user,'public.web_assessments','assessment_id','INSERT'),has_schema_privilege(current_user,'public','CREATE')").fetchone()
    if allowed != (True, False, False): raise SystemExit(2)
    try:
        db.execute('CREATE TABLE public.synthetic_w19_forbidden(id integer)')
    except psycopg.errors.InsufficientPrivilege:
        db.rollback()
    else:
        raise SystemExit(3)
print(json.dumps({'select':True,'insert':False,'schema_create':False}))
'''
        output = self.compose(
            "run", "--rm", "--no-deps", "--interactive", "--entrypoint", "python",
            "web-provision", "-", input_text=helper,
        )
        try:
            self._assert(json.loads(output) == {
                "select": True, "insert": False, "schema_create": False,
            })
        except json.JSONDecodeError:
            raise SmokeFailure from None

    def _administration_smoke(self, admin: dict[str, str]):
        """Exige gestao real pelo writer restrito, sem promover o runtime a owner."""
        headers = self._api_headers(admin, write=True)
        status, _, user = self._json_request(
            'POST', '/api/v1/admin/users',
            {'issuer': 'https://accounts.google.com',
             'subject': 'synthetic-w21-managed', 'role': 'consulta'}, headers,
        )
        self._assert(status == 201 and user['role'] == 'consulta' and user['active'])
        status, _, result = self._json_request(
            'PUT', f"/api/v1/admin/users/{user['user_id']}",
            {'role': 'importacao', 'active': False, 'email': None}, headers,
        )
        self._assert(status == 200 and result['role'] == 'importacao'
                     and result['active'] is False)
        status, _, result = self._json_request(
            'PUT', f"/api/v1/admin/users/{admin['user_id']}",
            {'role': 'consulta', 'active': True, 'email': None}, headers,
        )
        self._assert(status == 409 and result['error']['code'] == 'state_conflict')

    def _collect_and_query(self):
        admin = self._seed_admin_session()
        self._administration_smoke(admin)
        admin_headers = self._api_headers(admin)
        write_headers = self._api_headers(admin, write=True)
        status, _, project = self._json_request(
            "POST", "/api/v1/projects",
            {"code": "SYNTHETIC_W19", "name": "Projeto sintetico W19"},
            write_headers,
        )
        self._assert(status == 201)
        project_id = project["id"]
        status, _, member = self._json_request(
            "PUT", f"/api/v1/projects/{project_id}/members/{admin['user_id']}",
            {"active": True}, write_headers,
        )
        self._assert(status == 200 and member["active"] is True)
        status, _, invitation = self._json_request(
            "POST", f"/api/v1/projects/{project_id}/invitations",
            {"participant_id": "P_SYNTHETIC_W19", "visit": "V1"}, write_headers,
        )
        self._assert(status == 201 and len(invitation["code"]) >= 40)

        body = json.dumps(
            {"code": invitation["code"]}, separators=(",", ":")
        ).encode()
        status, response_headers, response_body = self._request(
            tls=True, method="POST", path="/api/v1/participant/redeem", body=body,
            headers={"Content-Type": "application/json",
                     "Origin": f"https://{HOST}:{self.https_port}"},
        )
        self._assert(status == 201)
        try:
            redeemed = json.loads(response_body)
            set_cookie = response_headers["set-cookie"]
            cookie_pair = set_cookie.split(";", 1)[0]
            cookie_name, separator, participant_cookie = cookie_pair.partition("=")
        except (KeyError, ValueError, json.JSONDecodeError):
            raise SmokeFailure from None
        self._assert(redeemed["state"] == "preparing")
        self._assert(cookie_name == "__Host-stroop_participant" and separator == "=")
        participant_headers = {
            "Origin": f"https://{HOST}:{self.https_port}",
            "Cookie": f"__Host-stroop_participant={participant_cookie}",
        }
        status, _, bootstrap = self._json_request(
            "GET", "/api/v1/participant/session", None, participant_headers,
        )
        self._assert(status == 200 and bootstrap["state"] == "preparing")
        participant_headers["X-CSRF-Token"] = bootstrap["csrf_token"]
        app_version = "synthetic-w19-0.1"
        status, _, started = self._json_request(
            "POST", "/api/v1/participant/start", {"app_version": app_version},
            participant_headers,
        )
        self._assert(status == 200 and started["state"] == "running")
        trials = []
        for index, condition in enumerate(bootstrap["main_conditions"]):
            start = index * 3750
            trials.append({
                "trial_number": index + 1,
                "condition_id": condition["condition_id"],
                "key_pressed": None,
                "reaction_time_ms": None,
                "trial_start_ms": start,
                "stimulus_onset_ms": start + 300,
                "stimulus_offset_ms": start + 2800,
                "trial_end_ms": start + 3750,
                "key_at_ms": None,
            })
        result = {
            "protocol_id": bootstrap["protocol_id"],
            "test_version": bootstrap["test_version"],
            "platform": "web",
            "app_version": app_version,
            "frame_period_ms": 16.666667,
            "trials": trials,
        }
        status, _, receipt = self._json_request(
            "POST", "/api/v1/participant/complete", result, participant_headers,
        )
        self._assert(status == 201 and receipt["state"] == "completed")
        status, _, retry = self._json_request(
            "POST", "/api/v1/participant/complete", result, participant_headers,
        )
        self._assert(status == 200 and retry["assessment_id"] == receipt["assessment_id"])

        list_path = f"/api/v1/projects/{project_id}/assessments"
        status, _, listing = self._json_request("GET", list_path, None, admin_headers)
        self._assert(status == 200 and len(listing["items"]) == 1)
        listed = listing["items"][0]
        self._assert(listed["assessment_id"] == receipt["assessment_id"])
        self._assert(listed["platform"] == "web")
        self._assert(listed["test_code"] == "stroop_go_nogo_ptbr")
        self._assert("participant_name" not in listed and "initials" not in listed)
        detail_path = f"{list_path}/{receipt['assessment_id']}"
        status, _, detail = self._json_request("GET", detail_path, None, admin_headers)
        self._assert(status == 200 and len(detail["trials"]) == 16)
        self._assert(detail["platform"] == "web" and detail["project_id"] == project_id)
        self._assert("participant_name" not in detail and "initials" not in detail)
        status, response_headers, csv_body = self._request(
            tls=True, method="GET", path=f"{detail_path}/export",
            headers=admin_headers,
        )
        self._assert(status == 200)
        self._assert(response_headers.get("content-type", "").startswith("text/csv; charset=utf-8"))
        self._assert(response_headers.get("cache-control") == "no-store")
        parsed_csv = list(csv.reader(io.StringIO(csv_body.decode("utf-8"))))
        self._assert(len(parsed_csv) == 17)
        self._assert(len(parsed_csv[0]) == 21 and len(parsed_csv[1]) == 21)
        self._assert(parsed_csv[1][parsed_csv[0].index("participant_id")] == "P_SYNTHETIC_W19")
        self._assert(parsed_csv[1][parsed_csv[0].index("participant_name")] == "NAO_COLETADO")
        self._assert(parsed_csv[1][parsed_csv[0].index("initials")] == "")
        return project_id, receipt["assessment_id"], admin, admin_headers

    def run(self):
        self.start_stack()
        print("[smoke] validando transporte e isolamento", file=sys.stderr)
        self._transport_smoke()
        self._read_only_role_smoke()
        print("[smoke] executando fluxo sintetico de coleta", file=sys.stderr)
        project_id, assessment_id, admin, admin_headers = self._collect_and_query()
        self.compose("restart", "web-postgres")
        self.wait_healthy("web-postgres")
        self.wait_healthy("web-api")
        status, _, projects = self._json_request(
            "GET", "/api/v1/projects", None, admin_headers,
        )
        self._assert(status == 200 and any(item["id"] == project_id for item in projects["items"]))
        status, _, listing = self._json_request(
            "GET", f"/api/v1/projects/{project_id}/assessments", None, admin_headers,
        )
        self._assert(status == 200 and any(
            item["assessment_id"] == assessment_id for item in listing["items"]
        ))
        print("[smoke] verificacao concluida", file=sys.stderr)

    def cleanup(self):
        self.compose("down", "--volumes", "--remove-orphans", timeout=90)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--build-images", action="store_true",
        help="build API e proxy em sequencia antes do smoke",
    )
    options = parser.parse_args(argv)
    temporary_path = Path(tempfile.mkdtemp(prefix="stroop-w19-"))
    temporary_path.chmod(0o700)
    smoke = None
    failed = False
    try:
        if not COMPOSE.is_file():
            raise SmokeFailure
        smoke = WebComposeSmoke(temporary_path, options.build_images)
        smoke.run()
    except Exception as error:
        if isinstance(error, SmokeFailure) and str(error) in {
            'uid', 'readonly', 'capabilities', 'privileges', 'published-port'
        }:
            print(f'[smoke] isolamento: {error}', file=sys.stderr)
        failed = True
    finally:
        if smoke is not None:
            try:
                smoke.cleanup()
            except Exception:
                failed = True
        shutil.rmtree(temporary_path, ignore_errors=True)
    if failed:
        print("Smoke WEB Compose falhou; detalhes e secrets foram suprimidos.", file=sys.stderr)
        return 1
    print("Smoke WEB Compose passou com infraestrutura e dados sinteticos descartaveis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
