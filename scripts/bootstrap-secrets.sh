#!/usr/bin/env bash
set -euo pipefail
umask 077

cd "$(dirname "$0")/.."
fernet_key="$(python3 -c 'import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())')"
postgres_password="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
api_secret="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
jwt_secret="$(python3 -c 'import secrets; print(secrets.token_hex(64))')"
audit_hmac="$(python3 -c 'import secrets; print(secrets.token_hex(64))')"
grafana_password="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
business_db_password="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"

if [[ -e .env ]]; then
  append_missing() {
    local key="$1"
    local value="$2"
    if ! grep -q "^${key}=" .env; then
      printf '%s=%s\n' "$key" "$value" >> .env
      echo "Configuracao ausente adicionada: ${key}"
    fi
  }
  append_missing GRAFANA_ADMIN_PASSWORD "$grafana_password"
  append_missing BUSINESS_DB_PASSWORD "$business_db_password"
  chmod 600 .env
  echo "Upgrade de segredos concluido; valores existentes foram preservados."
  exit 0
fi

sed \
  -e "s|POSTGRES_PASSWORD=CHANGE_ME|POSTGRES_PASSWORD=${postgres_password}|" \
  -e "s|AIRFLOW_FERNET_KEY=CHANGE_ME|AIRFLOW_FERNET_KEY=${fernet_key}|" \
  -e "s|AIRFLOW_API_SECRET_KEY=CHANGE_ME|AIRFLOW_API_SECRET_KEY=${api_secret}|" \
  -e "s|AIRFLOW_JWT_SECRET=CHANGE_ME|AIRFLOW_JWT_SECRET=${jwt_secret}|" \
  -e "s|POC_AUDIT_HMAC_KEY=CHANGE_ME|POC_AUDIT_HMAC_KEY=${audit_hmac}|" \
  -e "s|GRAFANA_ADMIN_PASSWORD=CHANGE_ME|GRAFANA_ADMIN_PASSWORD=${grafana_password}|" \
  -e "s|BUSINESS_DB_PASSWORD=CHANGE_ME|BUSINESS_DB_PASSWORD=${business_db_password}|" \
  .env.example > .env
chmod 600 .env
echo "Segredos locais criados em .env (modo 0600). Nao versione esse arquivo."
