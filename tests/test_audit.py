from pathlib import Path

from poc import audit


def test_hash_chain_detects_tampering(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("POC_AUDIT_HMAC_KEY", "test-key-not-for-production")
    audit.AUDIT_PATH = tmp_path / "events.jsonl"
    audit.append_event("one", "subject", "ok", {})
    audit.append_event("two", "subject", "ok", {})
    assert audit.verify_chain() == (True, 2)
    text = audit.AUDIT_PATH.read_text().replace('"outcome": "ok"', '"outcome": "bad"', 1)
    audit.AUDIT_PATH.write_text(text)
    assert audit.verify_chain()[0] is False


def test_append_event_is_idempotent(tmp_path, monkeypatch):
    path = tmp_path / "events.jsonl"
    monkeypatch.setattr(audit, "AUDIT_PATH", path)
    monkeypatch.setenv("POC_AUDIT_HMAC_KEY", "test-key")

    first = audit.append_event("sent", "DOC-1", "OK", {}, idempotency_key="run-1:sent")
    second = audit.append_event("sent", "DOC-1", "OK", {}, idempotency_key="run-1:sent")

    assert first == second
    assert len(path.read_text().splitlines()) == 1
    assert audit.verify_chain() == (True, 1)
