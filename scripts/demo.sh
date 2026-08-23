#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "DAGs da demonstracao:"
docker compose exec api-server airflow dags list | grep '^coop_' || true
echo
echo "Acesse via Tailscale: http://honda:8080"
echo "Roteiro completo: docs/DEMO.md"

