#!/bin/sh
# Hook Certbot desta instalacao; executar como root, sem imprimir chaves.
set -eu
domain=strooptest.thiagorraposo.dev
lineage=/etc/letsencrypt/live/$domain
[ "${RENEWED_LINEAGE:-}" = "$lineage" ] || exit 0
runtime=/home/raposo/stroop-web
secrets=/home/raposo/.local/share/stroop-web/secrets
openssl x509 -in "$lineage/fullchain.pem" -noout -checkend 0 >/dev/null
openssl x509 -in "$lineage/fullchain.pem" -noout -checkhost "$domain" >/dev/null
temporary=$(mktemp -d)
trap 'rm -f "$temporary/cert.pub" "$temporary/key.pub"; rmdir "$temporary"' EXIT HUP INT TERM
openssl x509 -in "$lineage/fullchain.pem" -pubkey -noout > "$temporary/cert.pub"
openssl pkey -in "$lineage/privkey.pem" -pubout > "$temporary/key.pub" 2>/dev/null
cmp -s "$temporary/cert.pub" "$temporary/key.pub"
install -m 0600 -o 101 -g 101 "$lineage/fullchain.pem" "$secrets/tls_certificate.next"
install -m 0600 -o 101 -g 101 "$lineage/privkey.pem" "$secrets/tls_private_key.next"
mv "$secrets/tls_certificate.next" "$secrets/tls_certificate"
mv "$secrets/tls_private_key.next" "$secrets/tls_private_key"
# Recriar e necessario: mounts de arquivo conservam o inode antigo.
docker compose --project-name stroop-web --env-file "$runtime/web.env" \
  -f "$runtime/current/compose.web.yaml" -f "$runtime/compose.vps.yaml" \
  --profile web up -d --no-deps --no-build --force-recreate --wait web-proxy
