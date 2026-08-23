#!/usr/bin/env bash
set -euo pipefail

psql --set=ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=business_password="$BUSINESS_DB_PASSWORD" <<'SQL'
CREATE USER poc_business WITH PASSWORD :'business_password';
CREATE DATABASE poc_business OWNER poc_business;
SQL

psql --set=ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname poc_business <<'SQL'
SET ROLE poc_business;
CREATE TABLE process_instances (
    process_id text PRIMARY KEY,
    workflow_id text NOT NULL,
    workflow_name text NOT NULL,
    business_area text NOT NULL,
    automation_owner text NOT NULL,
    exception_owner text NOT NULL,
    document_type text NOT NULL,
    status text NOT NULL,
    required_signatures integer NOT NULL CHECK (required_signatures >= 0),
    collected_signatures integer NOT NULL DEFAULT 0 CHECK (collected_signatures >= 0),
    started_at timestamptz NOT NULL DEFAULT now(),
    due_at timestamptz NOT NULL,
    completed_at timestamptz,
    updated_at timestamptz NOT NULL DEFAULT now(),
    is_synthetic boolean NOT NULL DEFAULT true,
    version integer NOT NULL DEFAULT 1
);
CREATE INDEX process_instances_area_status_idx ON process_instances (business_area, status);
CREATE INDEX process_instances_due_idx ON process_instances (due_at) WHERE completed_at IS NULL;

CREATE TABLE process_events (
    event_id bigserial PRIMARY KEY,
    process_id text NOT NULL REFERENCES process_instances(process_id),
    event_type text NOT NULL,
    previous_status text,
    new_status text NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    run_ref text NOT NULL,
    details jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX process_events_process_time_idx ON process_events (process_id, occurred_at);

CREATE VIEW business_process_overview AS
SELECT business_area, workflow_name, status,
       count(*) AS process_count,
       count(*) FILTER (WHERE completed_at IS NULL AND due_at < now()) AS overdue_count,
       sum(required_signatures - collected_signatures) AS pending_signatures
FROM process_instances
GROUP BY business_area, workflow_name, status;
RESET ROLE;
SQL
