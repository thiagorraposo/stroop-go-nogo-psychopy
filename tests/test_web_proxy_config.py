"""Proxy WEB: geracao real de politica e limites, sem Docker/banco/coleta."""
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / 'web/deploy'


class WebProxyConfigTests(unittest.TestCase):
    def test_authority_canonica_e_limites_rejeitam_injecao(self):
        valid = {'research.example.test': 'research.example.test', 'Research.Example.test:443': 'research.example.test',
                 '127.0.0.1:00443': '127.0.0.1', 'localhost:8443': 'localhost:8443'}
        for value, expected in valid.items():
            result = subprocess.run(['awk', '-f', str(DEPLOY / 'origin.awk')], input=value + '\n', text=True, capture_output=True)
            with self.subTest(value=value):
                self.assertEqual(result.returncode, 0); self.assertEqual(result.stdout, expected)
        invalid = ('', 'user@example.test', 'example.test/path', 'example.test?query=1', 'example.test#hash',
                   'example.test:0', 'example.test:65536', 'example.test:', '-invalid.test', 'invalid-.test',
                   '.example.test', 'example..test', 'example.test.', 'a' * 64 + '.test', '[::1]:8443',
                   'example.test;return 200', 'example.test\nother.test', 'example.test\\x')
        for value in invalid:
            result = subprocess.run(['awk', '-f', str(DEPLOY / 'origin.awk')], input=value + '\n', text=True, capture_output=True)
            with self.subTest(value=value): self.assertNotEqual(result.returncode, 0)

    def test_headers_gerados_seguem_json_e_api_nao_recebe_csp_web(self):
        baseline = json.loads((ROOT / 'web/security-headers.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(['node', str(DEPLOY / 'generate-headers.mjs'), directory], check=True, capture_output=True)
            web = (Path(directory) / 'web-headers.conf').read_text()
            error = (Path(directory) / 'error-headers.conf').read_text()
            proxy = (Path(directory) / 'proxy-headers.conf').read_text()
            for name, value in baseline.items(): self.assertIn(f'add_header {name} "{value}" always;', web)
            self.assertIn('default-src \'none\'; frame-ancestors \'none\'; base-uri \'none\'; form-action \'none\'', error)
            self.assertNotIn('Content-Security-Policy', proxy)
            self.assertNotIn('Cache-Control', proxy)
            self.assertIn('Strict-Transport-Security "$web_hsts"', web)
            self.assertIn('Cache-Control "no-store"', error)

    def test_headers_malformados_nao_geram_configuracao_executavel(self):
        baseline = json.loads((ROOT / 'web/security-headers.json').read_text())
        for invalid in ('bad"; injected on;', '$request_uri', 'synthetic\nheader'):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); (root / 'deploy').mkdir()
                script = root / 'deploy/generate-headers.mjs'; script.write_text((DEPLOY / script.name).read_text())
                baseline['Referrer-Policy'] = invalid
                (root / 'security-headers.json').write_text(json.dumps(baseline))
                result = subprocess.run(['node', str(script), str(root / 'output')], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((root / 'output/web-headers.conf').exists())

    def test_logs_sao_minimos_e_proxy_sobrescreve_headers_de_cliente(self):
        config = (DEPLOY / 'nginx.conf.template').read_text()
        log = re.search(r'log_format safe.*?;', config).group()
        self.assertEqual(set(re.findall(r'\$[a-z_]+', log)), {'$request_id', '$safe_method', '$status', '$request_time'})
        self.assertIn('default OTHER;', config)
        self.assertIn('error_log /dev/null emerg;', config)
        proxy = (DEPLOY / 'proxy.conf').read_text()
        for line in ('proxy_set_header Host $http_host;', 'proxy_set_header X-Forwarded-For $remote_addr;',
                     'proxy_set_header X-Forwarded-Proto https;', 'proxy_set_header Forwarded "";',
                     'proxy_request_buffering off;', 'proxy_intercept_errors off;'):
            self.assertIn(line, proxy)
        self.assertNotIn('$proxy_add_x_forwarded_for', proxy)
        self.assertIn('client_max_body_size 64k;', config)
        self.assertIn('if ($http_host != "${WEB_AUTHORITY}")', config)
        self.assertIn('location /api/', config)
        self.assertIn('location ~ ^/api/v1/projects/[0-9a-fA-F-]{36}/imports/[0-9a-fA-F-]{36}$', config)
        self.assertIn('client_max_body_size 5m;', config)

    def test_http_acme_webroot_exclusivo_preserva_redirect_e_tls_fechado(self):
        config = (DEPLOY / 'nginx.conf.template').read_text()
        http = config.split('listen 8080 default_server;', 1)[1].split('listen 8443 ssl default_server;', 1)[0]
        challenge = re.search(r'location \^~ /\.well-known/acme-challenge/ \{([^}]+)\}', http).group(1)
        self.assertIn('root /var/www/acme;', challenge)
        self.assertIn('default_type text/plain;', challenge)
        self.assertIn('try_files $uri =404;', challenge)
        self.assertNotIn('proxy_pass', challenge)
        self.assertEqual(http.count('location '), 2)
        self.assertIn('location / { return 308 ${WEB_PUBLIC_ORIGIN}$request_uri; }', http)
        tls = config.split('listen 8443 ssl default_server;', 1)[1]
        self.assertNotIn('/var/www/acme', tls)
        self.assertIn('location ~ (^|/)\\. { return 404; }', tls)

    def test_build_context_e_runtime_excluem_fontes_secrets_e_dependencias_node(self):
        ignore = (ROOT / 'Dockerfile.web.dockerignore').read_text().splitlines()
        self.assertEqual(ignore[0], '**')
        self.assertFalse(any(line.startswith(('!data', '!database', '!.env', '!production-secrets')) for line in ignore))
        dockerfile = (ROOT / 'Dockerfile.web').read_text()
        runtime = dockerfile.split('FROM nginx:', 1)[1]
        self.assertIn('USER 101:101', runtime)
        self.assertIn('COPY --from=build /app/web/dist', runtime)
        self.assertNotIn('node_modules', runtime)
        self.assertNotIn('COPY . ', dockerfile)
        self.assertIn('nginx -t -c /tmp/stroop-nginx.conf >/dev/null 2>&1', (DEPLOY / 'start.sh').read_text())
