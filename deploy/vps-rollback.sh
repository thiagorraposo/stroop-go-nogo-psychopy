#!/bin/sh
# Retorna somente o trafego ao legado; nunca apaga/restaura bancos.
set -eu
docker stop --time 10 stroop-web-web-proxy-1 >/dev/null
if docker start stroop-production-dashboard-1 stroop-production-proxy-1 >/dev/null; then
    attempt=0
    while [ "$attempt" -lt 10 ]; do
        if curl --fail --silent --max-time 3 \
          --connect-to strooptest.thiagorraposo.dev:443:127.0.0.1:443 \
          https://strooptest.thiagorraposo.dev/_stcore/health >/dev/null; then
            printf '%s\n' 'Legado respondeu via HTTPS; banco WEB preservado.'
            exit 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
fi
docker stop stroop-production-proxy-1 >/dev/null 2>&1 || true
docker start stroop-web-web-proxy-1 >/dev/null
printf '%s\n' 'Rollback falhou; proxy WEB reiniciado. Verifique a saude.' >&2
exit 1
