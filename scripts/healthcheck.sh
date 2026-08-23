#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a
url="http://${AIRFLOW_BIND_ADDRESS}:${AIRFLOW_PORT}/api/v2/monitor/health"
curl --fail --silent --show-error --max-time 5 "$url"
printf '\nhealth check OK: %s\n' "$url"

