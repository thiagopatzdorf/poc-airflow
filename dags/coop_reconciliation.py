from datetime import datetime, timezone
from decimal import Decimal

from airflow.sdk import dag, task

from poc.audit import append_event, verify_chain
from poc.policies import retry_policy
from poc.rules import reconcile


@dag(dag_id="coop_reconciliation", description="Conciliacao sintetica e verificacao da trilha de auditoria",
     schedule="0 6 * * 1-5", start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), catchup=False, max_active_runs=1,
     default_args=retry_policy(critical=True), tags=["poc", "conciliacao", "auditoria"])
def reconciliation():
    @task
    def compare_totals():
        samples = [("BATCH-001", Decimal("985021.17"), Decimal("985021.17")),
                   ("BATCH-002", Decimal("71108.30"), Decimal("71105.10"))]
        output = []
        for batch, ledger, settlement in samples:
            outcome = reconcile(ledger, settlement)
            delta = str(ledger - settlement)
            append_event("reconciliation_completed", batch, outcome, {"delta": delta, "currency": "BRL"})
            output.append({"batch": batch, "outcome": outcome, "delta": delta})
        return output

    @task
    def audit_gate(_results):
        valid, count = verify_chain()
        if not valid:
            raise ValueError("audit chain integrity failure")
        return {"audit_chain_valid": True, "events_verified": count}

    audit_gate(compare_totals())


reconciliation()
