"""Trilha append-only encadeada por hash, sem armazenar payload sensivel."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(os.getenv("POC_AUDIT_PATH", "/opt/airflow/data/audit/events.jsonl"))


def pseudonymize(value: str) -> str:
    return hashlib.sha256(f"poc-only::{value}".encode()).hexdigest()[:16]


def append_event(event_type: str, subject_id: str, outcome: str, details: dict[str, Any]) -> dict[str, Any]:
    audit_key = os.environ.get("POC_AUDIT_HMAC_KEY")
    if not audit_key:
        raise RuntimeError("POC_AUDIT_HMAC_KEY is required")
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.seek(0)
        lines = [line for line in stream.read().splitlines() if line]
        previous_hash = json.loads(lines[-1])["event_hash"] if lines else "GENESIS"
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
        event["event_hash"] = hmac.new(audit_key.encode(), canonical.encode(), hashlib.sha256).hexdigest()
        stream.seek(0, os.SEEK_END)
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    return event


def verify_chain(path: Path | None = None) -> tuple[bool, int]:
    path = path or AUDIT_PATH
    audit_key = os.environ.get("POC_AUDIT_HMAC_KEY")
    if not audit_key:
        raise RuntimeError("POC_AUDIT_HMAC_KEY is required")
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
        expected = hmac.new(audit_key.encode(), canonical.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, claimed):
            return False, count
        previous = claimed
        count += 1
    return True, count
