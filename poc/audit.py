"""Trilha append-only encadeada por hash, sem armazenar payload sensivel."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(os.getenv("POC_AUDIT_PATH", "/opt/airflow/data/audit/events.jsonl"))


def pseudonymize(value: str) -> str:
    return hashlib.sha256(f"poc-only::{value}".encode()).hexdigest()[:16]


def append_event(event_type: str, subject_id: str, outcome: str, details: dict[str, Any]) -> dict[str, Any]:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = "GENESIS"
    if AUDIT_PATH.exists():
        lines = [line for line in AUDIT_PATH.read_text(encoding="utf-8").splitlines() if line]
        if lines:
            previous_hash = json.loads(lines[-1])["event_hash"]
    event = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "subject_ref": pseudonymize(subject_id),
        "outcome": outcome,
        "details": details,
        "previous_hash": previous_hash,
    }
    canonical = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    event["event_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    with AUDIT_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return event


def verify_chain(path: Path | None = None) -> tuple[bool, int]:
    path = path or AUDIT_PATH
    previous = "GENESIS"
    count = 0
    if not path.exists():
        return True, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        claimed = event.pop("event_hash")
        if event["previous_hash"] != previous:
            return False, count
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        if hashlib.sha256(canonical.encode()).hexdigest() != claimed:
            return False, count
        previous = claimed
        count += 1
    return True, count
