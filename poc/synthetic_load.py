"""Gerador determinístico de tickets sintéticos para a demonstração operacional."""
from __future__ import annotations

import hashlib
import os
from datetime import date, datetime, timedelta, timezone

from poc.process_store import _connect


def daily_target(day: date, minimum: int = 200, maximum: int = 400) -> int:
    if minimum < 1 or maximum < minimum:
        raise ValueError("invalid daily volume range")
    seed = int(hashlib.sha256(day.isoformat().encode()).hexdigest()[:8], 16)
    return minimum + seed % (maximum - minimum + 1)


def expected_count(now: datetime, target: int) -> int:
    start = datetime.combine(now.date(), datetime.min.time(), tzinfo=timezone.utc)
    elapsed = max(0.0, min(86400.0, (now - start).total_seconds()))
    return min(target, int(target * elapsed / 86400.0))


def status_for(sequence: int) -> str:
    bucket = sequence % 20
    if bucket < 14:
        return "COMPLETED"
    if bucket < 17:
        return "AWAITING_SIGNATURES"
    if bucket == 17:
        return "VALIDATED"
    if bucket == 18:
        return "MANUAL_REVIEW"
    return "QUARANTINED"


def generate_due_tickets(*, now: datetime | None = None, max_batch: int = 12) -> dict[str, int]:
    now = now or datetime.now(timezone.utc)
    minimum = int(os.getenv("POC_SYNTHETIC_DAILY_MIN", "200"))
    maximum = int(os.getenv("POC_SYNTHETIC_DAILY_MAX", "400"))
    target = daily_target(now.date(), minimum, maximum)
    expected = expected_count(now, target)
    day_prefix = f"TKT-{now:%Y%m%d}-"

    with _connect() as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT count(*) FROM process_instances WHERE process_id LIKE %s AND is_synthetic",
            (day_prefix + "%",),
        )
        current = cursor.fetchone()[0]
        amount = min(max(0, expected - current), max_batch)
        for sequence in range(current + 1, current + amount + 1):
            process_id = f"{day_prefix}{sequence:06d}"
            status = status_for(sequence)
            age_minutes = sequence % 26
            started_at = now - timedelta(minutes=age_minutes)
            due_at = started_at + timedelta(minutes=20)
            completed_at = None
            signatures = 0
            if status == "COMPLETED":
                completion_minutes = 4 + sequence % 19
                completed_at = min(now, started_at + timedelta(minutes=completion_minutes))
                signatures = 2
            elif status == "AWAITING_SIGNATURES":
                signatures = sequence % 2

            cursor.execute(
                """INSERT INTO process_instances
                   (process_id,workflow_id,workflow_name,business_area,automation_owner,
                    exception_owner,document_type,status,required_signatures,collected_signatures,
                    started_at,due_at,completed_at,updated_at,is_synthetic)
                   VALUES (%s,'daily_document_operations','Operacao documental diaria',
                           'Operacoes Documentais','area_automation_engineer',
                           'Operacoes Documentais','synthetic_document',%s,2,%s,%s,%s,%s,%s,true)
                   ON CONFLICT (process_id) DO NOTHING""",
                (process_id, status, signatures, started_at, due_at, completed_at,
                 completed_at or now),
            )
            cursor.execute(
                """INSERT INTO process_events
                   (process_id,event_type,new_status,occurred_at,run_ref,details,event_key)
                   VALUES (%s,'synthetic_ticket_created',%s,%s,%s,
                           '{"synthetic":true,"generator":"daily-load-v1"}'::jsonb,%s)
                   ON CONFLICT (event_key) DO NOTHING""",
                (process_id, status, started_at, f"synthetic:{now.date()}",
                 f"synthetic:{process_id}:created"),
            )
            if status == "COMPLETED":
                cursor.execute(
                    """INSERT INTO process_events
                       (process_id,event_type,previous_status,new_status,occurred_at,run_ref,
                        details,event_key)
                       VALUES (%s,'state_transition','AWAITING_SIGNATURES','COMPLETED',%s,%s,
                               '{"synthetic":true}'::jsonb,%s)
                       ON CONFLICT (event_key) DO NOTHING""",
                    (process_id, completed_at, f"synthetic:{now.date()}",
                     f"synthetic:{process_id}:completed"),
                )
    return {"target": target, "expected": expected, "before": current, "created": amount}
