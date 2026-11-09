#!/usr/bin/env python3
"""Inicializador da aplicação Web local com autenticação e projeto pré-configurados."""
from __future__ import annotations

import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from urllib.parse import urlsplit
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg
from scripts.migrations import apply_migrations
from scripts.provision_web_database import provision
from stroop.application import local_auth
from stroop.domain.local_auth import LOCAL_ISSUER

PORT_HTTPS = 4473
PORT_API = 4481
ORIGIN = f"https://127.0.0.1:{PORT_HTTPS}"
USERNAME = "admin"
PASSWORD = "Pesquisador@2026!"
SESSION_SECRET = "stroop-local-preview-session-secret-key-32chars!!"
DEFAULT_DB_URL = "postgresql://synthetic:synthetic-ci-only@127.0.0.1:32769/stroop_etapa4_test_ci"

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_occupants(ports: list[int]):
    for port in ports:
        try:
            out = subprocess.check_output(["fuser", f"{port}/tcp"], stderr=subprocess.DEVNULL).decode()
            pids = out.strip().split()
            for pid in pids:
                if pid:
                    os.kill(int(pid), signal.SIGTERM)
        except Exception:
            pass
    time.sleep(0.5)

def main():
    database = os.environ.get("TEST_DATABASE_URL", DEFAULT_DB_URL)
    os.environ["TEST_DATABASE_URL"] = database

    # Kill any stale server on our ports
    kill_occupants([PORT_HTTPS, PORT_API])

    print("[1/5] Inicializando banco de dados e aplicando migrations...")
    apply_migrations(database)
    
    # Provision reader/writer credentials
    import importlib.util
    spec = importlib.util.spec_from_file_location("common", str(ROOT / "web/e2e/local-auth/common.py"))
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    provision({'API_MIGRATION_DATABASE_URL': database,
               'API_DATABASE_URL': common.write_url(),
               'API_READ_DATABASE_URL': common.read_url()})

    print(f"[2/5] Provisionando usuário administrativo '{USERNAME}'...")
    with psycopg.connect(database, autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM web_local_credentials WHERE username=%s", (USERNAME,)).fetchone()
    
    local_auth.provision(database, USERNAME, PASSWORD, recover=bool(exists))

    # Obter subject do admin e criar projeto inicial
    with psycopg.connect(database, autocommit=True) as conn:
        row = conn.execute("SELECT principal_id FROM web_local_credentials WHERE username=%s", (USERNAME,)).fetchone()
        admin_subject = str(row[0])

        # Criar projeto padrão se não existir
        proj_row = conn.execute("SELECT project_id FROM web_projects WHERE code='PROJ_STROOP'").fetchone()
        if not proj_row:
            proj_id = uuid4()
            conn.execute("""
                INSERT INTO web_projects (project_id, code, name, active, created_by_issuer, created_by_subject)
                VALUES (%s, %s, %s, TRUE, %s, %s)
            """, (proj_id, 'PROJ_STROOP', 'Pesquisa Stroop Go/No-Go', LOCAL_ISSUER, admin_subject))
        else:
            proj_id = proj_row[0]

        # Vincular admin ao projeto
        conn.execute("""
            INSERT INTO web_project_members (project_id, issuer, subject, active)
            VALUES (%s, %s, %s, TRUE)
            ON CONFLICT (project_id, issuer, subject) DO UPDATE SET active=TRUE
        """, (proj_id, LOCAL_ISSUER, admin_subject))

    print("[3/5] Populando dados demonstrativos e avaliações...")
    from scripts.seed_demo_data import seed
    seed()

    print("[4/5] Gerando certificados TLS locais...")
    cert_dir = Path("/tmp/stroop-preview-certs")
    cert_dir.mkdir(parents=True, exist_ok=True)
    private_key = cert_dir / "key.pem"
    certificate = cert_dir / "cert.pem"
    
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '30',
        '-subj', '/CN=127.0.0.1', '-addext', 'subjectAltName=IP:127.0.0.1',
        '-keyout', str(private_key), '-out', str(certificate)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    env = {
        **os.environ,
        'APP_ENV': 'development',
        'API_DATABASE_URL': common.write_url(),
        'API_READ_DATABASE_URL': common.read_url(),
        'API_PUBLIC_ORIGIN': ORIGIN,
        'API_AUTH_MODE': 'local',
        'API_SESSION_SECRET': SESSION_SECRET,
        'API_REDEEM_RATE_LIMIT': '100',
        'STROOP_TEST_TLS_KEY': str(private_key),
        'STROOP_TEST_TLS_CERT': str(certificate),
    }

    print("[4/5] Iniciando API FastAPI (uvicorn) e Proxy HTTPS...")
    api_proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'api.main:create_app', '--factory',
         '--host', '127.0.0.1', '--port', str(PORT_API), '--no-access-log'],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    # Wait for API
    for _ in range(60):
        if api_proc.poll() is not None:
            raise RuntimeError("API FastAPI encerrou inesperadamente.")
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PORT_API}/health/live",
                                         headers={'Host': urlsplit(ORIGIN).netloc})
            with urllib.request.urlopen(req, timeout=0.3):
                break
        except Exception:
            time.sleep(0.1)

    proxy_proc = subprocess.Popen(
        ['node', str(ROOT / 'web/e2e/local-auth/proxy.mjs')],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    time.sleep(1)
    print("\n" + "=" * 60)
    print("🚀 APLICAÇÃO STROOP WEB EM EXECUÇÃO!")
    print("=" * 60)
    print(f"🔗 Link de Acesso: {ORIGIN}")
    print(f"👤 Usuário:        {USERNAME}")
    print(f"🔑 Senha:          {PASSWORD}")
    print("📁 Projeto Ativo:  Pesquisa Stroop Go/No-Go (PROJ_STROOP)")
    print("=" * 60 + "\n")
    print("(Pressione Ctrl+C para encerrar quando terminar)")

    try:
        while api_proc.poll() is None and proxy_proc.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for p in [api_proc, proxy_proc]:
            try:
                p.terminate()
                p.wait(timeout=3)
            except Exception:
                p.kill()

if __name__ == "__main__":
    main()
