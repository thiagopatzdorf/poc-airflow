#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

failed=0
if git ls-files | grep -Eq '(^|/)(\.env|.*\.pem|.*\.key)$'; then
  echo "FALHA: arquivo potencialmente secreto esta versionado"; failed=1
fi
if rg -n --glob '!scripts/security-check.sh' '(password|secret|token|key)\s*=\s*["'"'][^$<{][^"'"']{7,}' .; then
  echo "FALHA: possivel segredo hardcoded"; failed=1
fi
if rg -n '(CPF|CNPJ|nome|conta).*(real|producao)' data dags poc; then
  echo "FALHA: possivel referencia a dado real"; failed=1
fi
docker compose config --quiet
python3 -m compileall -q dags poc
[[ "$failed" -eq 0 ]] || exit 1
echo "Security baseline OK (nao substitui SAST/DAST ou pentest independente)."

