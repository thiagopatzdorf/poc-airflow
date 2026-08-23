from pathlib import Path
import poc.audit as audit


def test_hash_chain_detects_tampering(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("POC_AUDIT_HMAC_KEY", "test-key-not-for-production")
    audit.AUDIT_PATH = tmp_path / "events.jsonl"
    audit.append_event("one", "subject", "ok", {})
    audit.append_event("two", "subject", "ok", {})
    assert audit.verify_chain() == (True, 2)
    text = audit.AUDIT_PATH.read_text().replace('"outcome": "ok"', '"outcome": "bad"', 1)
    audit.AUDIT_PATH.write_text(text)
    assert audit.verify_chain()[0] is False
