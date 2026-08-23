"""Estado operacional separado do metadata DB do Airflow."""
from __future__ import annotations
import json
import os
from datetime import datetime, timedelta, timezone


def _connect():
    import psycopg2
    dsn = os.environ.get("POC_BUSINESS_DB_DSN")
    if not dsn:
        raise RuntimeError("POC_BUSINESS_DB_DSN is required")
    return psycopg2.connect(dsn)


def start_process(*, process_id: str, flow, run_ref: str) -> dict:
    due_at = datetime.now(timezone.utc) + timedelta(minutes=flow.sla_minutes)
    with _connect() as conn, conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO process_instances
               (process_id, workflow_id, workflow_name, business_area, automation_owner, exception_owner,
                document_type, status, required_signatures, due_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'RECEIVED',%s,%s)
               ON CONFLICT (process_id) DO NOTHING""",
            (process_id, flow.id, flow.name, flow.business_owner, flow.automation_owner, flow.exception_owner,
             flow.document_type, flow.required_signatures, due_at),
        )
        cursor.execute(
            """INSERT INTO process_events(process_id,event_type,new_status,run_ref,details)
               VALUES (%s,'process_started','RECEIVED',%s,%s)""",
            (process_id, run_ref, json.dumps({"synthetic": True})),
        )
    return {"process_id": process_id, "status": "RECEIVED"}


def transition(process_id: str, new_status: str, run_ref: str, *, signature_delta: int = 0) -> None:
    allowed = {
        "RECEIVED", "VALIDATED", "SENT", "AWAITING_SIGNATURES", "COMPLETED",
        "QUARANTINED", "MANUAL_REVIEW",
    }
    if new_status not in allowed:
        raise ValueError("invalid process state")
    with _connect() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT status FROM process_instances WHERE process_id=%s FOR UPDATE", (process_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("unknown process")
        previous = row[0]
        cursor.execute(
            """UPDATE process_instances SET status=%s,
               collected_signatures=collected_signatures+%s, updated_at=now(),
               completed_at=CASE WHEN %s='COMPLETED' THEN now() ELSE completed_at END,
               version=version+1 WHERE process_id=%s""",
            (new_status, signature_delta, new_status, process_id),
        )
        cursor.execute(
            """INSERT INTO process_events(process_id,event_type,previous_status,new_status,run_ref)
               VALUES (%s,'state_transition',%s,%s,%s)""",
            (process_id, previous, new_status, run_ref),
        )
