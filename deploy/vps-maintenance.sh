#!/bin/sh
# Rotinas do usuario raposo. Nunca imprime credenciais nem dumps.
set -eu
umask 077
runtime=/home/raposo/stroop-web
state=/home/raposo/.local/share/stroop-web
mkdir -p "$state/logs"
log="$state/logs/maintenance-$(date -u +%Y-%m-%d).log"
case "${1:-}" in
  monitor)
    temporary=$(mktemp "$state/logs/health.XXXXXX")
    status=0
    python3 "$runtime/current/scripts/monitor_web.py" --env-file "$runtime/web.env" \
      --project-name stroop-web > "$temporary" 2>/dev/null || status=$?
    mv "$temporary" "$state/logs/health-last.json"
    exit "$status"
    ;;
  backup)
    exec python3 "$runtime/current/scripts/backup_postgres.py" backup \
      --compose-file "$runtime/current/compose.web.yaml" --env-file "$runtime/web.env" \
      --project-name stroop-web --service web-postgres --database stroop_web \
      --user stroop_web_owner --key-file "$state/keys/web-backup.key" \
      --output-dir "$state/backups/web" >> "$log" 2>&1
    ;;
  restore-check)
    latest=$(python3 -c 'from pathlib import Path; import sys; p=sorted(Path(sys.argv[1]).glob("stroop-*.dump.enc")); print(p[-1] if p else "")' "$state/backups/web")
    [ -n "$latest" ] || exit 1
    exec python3 "$runtime/current/scripts/backup_postgres.py" restore-test --verify-web \
      --key-file "$state/keys/web-backup.key" --backup "$latest" >> "$log" 2>&1
    ;;
  *) printf '%s\n' 'Use monitor, backup ou restore-check.' >&2; exit 2 ;;
esac
