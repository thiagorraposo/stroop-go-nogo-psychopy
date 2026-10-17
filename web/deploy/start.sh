#!/bin/sh
set -eu
fail() { printf '%s\n' 'Configuracao WEB invalida ou indisponivel.' >&2; exit 1; }
[ "$#" -le 1 ] || fail
case "${1:-serve}" in
  healthcheck) exec curl --fail --silent --max-time 2 http://127.0.0.1:8081/health/live >/dev/null 2>&1 ;;
  serve) ;;
  *) fail ;;
esac
: "${WEB_PUBLIC_ORIGIN:=}"
case "$WEB_PUBLIC_ORIGIN" in
  https://*) ;;
  *) fail ;;
esac
case "$WEB_PUBLIC_ORIGIN" in *[!A-Za-z0-9.:/-]*) fail ;; esac
WEB_AUTHORITY=$(printf '%s\n' "${WEB_PUBLIC_ORIGIN#https://}" | LC_ALL=C awk -f /etc/nginx/web/origin.awk) || fail
[ -n "$WEB_AUTHORITY" ] || fail
WEB_PUBLIC_ORIGIN="https://$WEB_AUTHORITY"
export WEB_AUTHORITY WEB_PUBLIC_ORIGIN
[ -s /run/secrets/tls_certificate ] && [ -r /run/secrets/tls_certificate ] || fail
[ -s /run/secrets/tls_private_key ] && [ -r /run/secrets/tls_private_key ] || fail
command -v envsubst >/dev/null 2>&1 || fail
command -v openssl >/dev/null 2>&1 || fail
: "${APP_ENV:=production}"
: "${ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS:=0}"
case "$APP_ENV:$ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS" in production:0|test:0|test:1) ;; *) fail ;; esac
WEB_HOST=${WEB_AUTHORITY%:*}
openssl x509 -in /run/secrets/tls_certificate -noout -checkend 0 >/dev/null 2>&1 || fail
openssl pkey -passin pass: -in /run/secrets/tls_private_key -check -noout >/dev/null 2>&1 || fail
subject=$(openssl x509 -in /run/secrets/tls_certificate -noout -subject 2>/dev/null | tr '[:upper:]' '[:lower:]') || fail
synthetic=0
case "$subject" in *synthetic.invalid*|*stroop\ synthetic\ test*) synthetic=1 ;; esac
if [ "$synthetic" = 1 ]; then
    [ "$APP_ENV:$ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS" = test:1 ] || fail
fi
if [ "$ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS" = 1 ]; then [ "$synthetic" = 1 ] || fail; fi
start=$(openssl x509 -in /run/secrets/tls_certificate -noout -startdate 2>/dev/null) || fail
[ "$(date -d "${start#notBefore=}" +%s)" -le "$(date +%s)" ] || fail
case "$WEB_HOST" in
    *[!0-9.]*) openssl x509 -in /run/secrets/tls_certificate -noout -checkhost "$WEB_HOST" >/dev/null 2>&1 || fail ;;
    *) openssl x509 -in /run/secrets/tls_certificate -noout -checkip "$WEB_HOST" >/dev/null 2>&1 || fail ;;
esac
if [ "$ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS" = 0 ]; then
    openssl verify -purpose sslserver -CApath /etc/ssl/certs -untrusted /run/secrets/tls_certificate \
      /run/secrets/tls_certificate >/dev/null 2>&1 || fail
fi
openssl x509 -in /run/secrets/tls_certificate -pubkey -noout > /tmp/stroop-cert-public.pem 2>/dev/null || fail
openssl pkey -passin pass: -in /run/secrets/tls_private_key -pubout > /tmp/stroop-key-public.pem 2>/dev/null || fail
cmp -s /tmp/stroop-cert-public.pem /tmp/stroop-key-public.pem || fail
rm -f /tmp/stroop-cert-public.pem /tmp/stroop-key-public.pem
# Somente estas duas variaveis sao substituidas: variaveis Nginx permanecem literais.
envsubst '${WEB_AUTHORITY} ${WEB_PUBLIC_ORIGIN}' < /etc/nginx/web/nginx.conf.template > /tmp/stroop-nginx.conf || fail
nginx -t -c /tmp/stroop-nginx.conf >/dev/null 2>&1 || fail
exec nginx -c /tmp/stroop-nginx.conf -g 'daemon off;'
