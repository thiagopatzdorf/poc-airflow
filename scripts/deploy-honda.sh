#!/usr/bin/env bash
set -Eeuo pipefail

target="${1:-${DEPLOY_COMMIT:-}}"
source_dir="${GITHUB_WORKSPACE:-$(pwd)}"
control="${DEPLOY_CONTROL_REPO:-/home/patz/poc-airflow}"
releases="${DEPLOY_RELEASES_DIR:-/home/patz/poc-airflow-releases}"
state="${DEPLOY_STATE_DIR:-/home/patz/.local/state/poc-airflow-deploy}"
health="${DEPLOY_HEALTH_URL:-http://127.0.0.1:8080/api/v2/monitor/health}"

fail() { printf 'deploy error: %s\n' "$*" >&2; exit 1; }
for command_name in git docker rsync curl flock; do
  command -v "$command_name" >/dev/null || fail "$command_name required"
done
docker compose version >/dev/null || fail "Compose v2 required"
[[ "$target" =~ ^[0-9a-fA-F]{40}$ ]] || fail "full commit SHA required"
[[ -d "$source_dir/.git" ]] || fail "runner checkout unavailable"
[[ "$(git -C "$source_dir" rev-parse HEAD)" == "$target" ]] || fail "checkout identity mismatch"
[[ -f "$control/.env" ]] || fail "control .env unavailable"
docker info >/dev/null || fail "Docker daemon unavailable"

mkdir -p "$releases" "$state" "$control"
exec 9>"$state/deploy.lock"
flock -n 9 || fail "deploy already running"

release="$releases/$target"
mkdir -p "$release"
rsync -a --delete --exclude .git/ "$source_dir/" "$release/"
previous=""
[[ ! -s "$state/last-successful-sha" ]] || previous="$(<"$state/last-successful-sha")"

promote() {
  local candidate="$1"
  rsync -a --delete     --exclude .git/ --exclude .env --exclude logs/ --exclude data/     --exclude config/simple_auth_manager_passwords.json.generated     "$releases/$candidate/" "$control/"
}

rollback() {
  local rc=$?
  trap - ERR
  printf 'deploy failed; rollback=%s\n' "${previous:-unavailable}" >&2
  if [[ "$previous" =~ ^[0-9a-fA-F]{40}$ && -d "$releases/$previous" ]]; then
    promote "$previous"
    (cd "$control" && docker compose up -d --remove-orphans) || true
    curl -fsS --retry 12 --retry-delay 5 --retry-all-errors "$health" >/dev/null || true
  fi
  exit "$rc"
}
trap rollback ERR

promote "$target"
cd "$control"
docker compose config --quiet
docker compose build --pull
docker compose run --rm airflow-init
docker compose up -d --remove-orphans
curl -fsS --retry 18 --retry-delay 5 --retry-all-errors "$health" >/dev/null
for attempt in {1..12}; do
  dags="$(docker compose exec -T api-server airflow dags list 2>/dev/null || true)"
  if grep -q "synthetic_daily_workload" <<<"$dags" &&
     grep -q "document_membership_agreement" <<<"$dags"; then
    break
  fi
  [[ "$attempt" -lt 12 ]] || fail "required DAGs were not discovered"
  sleep 5
done
[[ "$(docker compose exec -T api-server airflow dags list-import-errors -o json)" == "[]" ]] ||
  fail "DAG import errors"

printf '%s\n' "$target" >"$state/last-successful-sha.tmp"
mv "$state/last-successful-sha.tmp" "$state/last-successful-sha"
trap - ERR
printf 'deployed %s; runtime data and named volumes preserved\n' "$target"
