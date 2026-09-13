#!/bin/sh
set -eu

certificate=/run/secrets/tls_certificate
private_key=/run/secrets/tls_private_key

if [ ! -r "$certificate" ] || [ ! -r "$private_key" ]; then
    echo "TLS obrigatorio ausente ou inacessivel." >&2
    exit 1
fi

if ! openssl x509 -in "$certificate" -noout >/dev/null 2>&1; then
    echo "Certificado TLS invalido." >&2
    exit 1
fi

if ! openssl pkey -in "$private_key" -noout >/dev/null 2>&1; then
    echo "Chave TLS invalida." >&2
    exit 1
fi

subject="$(openssl x509 -in "$certificate" -noout -subject 2>/dev/null)"
if printf '%s' "$subject" | grep -Eqi 'synthetic[.]invalid|STROOP SYNTHETIC TEST'; then
    if [ "${APP_ENV:-}" != "test" ] || [ "${ALLOW_SYNTHETIC_CERTIFICATE_FOR_TESTS:-}" != "1" ]; then
        echo "Certificado sintetico recusado fora do teste isolado." >&2
        exit 1
    fi
fi

exec "$@"
