#!/bin/sh
# Reverte a aplicacao WEB para a release anterior na VPS HostGator.
# Preserva integralmente o PostgreSQL, volumes persistentes, secrets e certificados.
set -eu

runtime="${STROOP_RUNTIME_DIR:-/home/raposo/stroop-web}"
target="${1:-}"

if [ -z "$target" ]; then
    if [ -f "$runtime/previous_release" ]; then
        target_path=$(cat "$runtime/previous_release" 2>/dev/null || true)
        target=$(basename "$target_path")
    fi
fi

if [ -z "$target" ]; then
    printf '%s\n' 'ERRO: Nenhuma release anterior identificada para rollback.' >&2
    exit 1
fi

target_dir="$runtime/releases/$target"
if [ ! -d "$target_dir" ]; then
    printf '%s\n' "ERRO: Diretorio de release inexistente: $target_dir" >&2
    exit 1
fi

printf '%s\n' "Revertendo aplicacao WEB para a release $target..."

# 1. Restaura arquivo de ambiente previo se existir
if [ -f "$runtime/web.env.pre-deploy" ]; then
    cp "$runtime/web.env.pre-deploy" "$runtime/web.env"
fi

# 2. Chaveamento atomico do symlink current
ln -sfn "$target_dir" "$runtime/current"

# 3. Recria os servicos web-api e web-proxy preservando postgres e volumes
docker compose --project-name stroop-web --env-file "$runtime/web.env" \
  -f "$runtime/current/compose.web.yaml" -f "$runtime/compose.vps.yaml" \
  --profile web up -d --no-deps --no-build --wait web-api web-proxy >/dev/null

# 4. Verificacao de saude pos-reversao
attempt=0
while [ "$attempt" -lt 10 ]; do
    if curl --fail --silent --max-time 3 \
      --connect-to strooptest.thiagorraposo.dev:443:127.0.0.1:443 \
      https://strooptest.thiagorraposo.dev/health/ready >/dev/null 2>&1; then
        printf '%s\n' "Rollback WEB concluido com sucesso; versao $target ativa e saudavel."
        exit 0
    fi
    attempt=$((attempt + 1))
    sleep 2
done

printf '%s\n' "ATENCAO: Contêineres reiniciados, mas healthcheck nao respondeu em tempo habil." >&2
exit 1
