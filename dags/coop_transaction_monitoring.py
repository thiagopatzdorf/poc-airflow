from datetime import datetime, timezone
from decimal import Decimal

from airflow.sdk import dag, task

from poc.audit import append_event
from poc.policies import retry_policy
from poc.rules import transaction_risk


@dag(
    dag_id="coop_transaction_monitoring",
    description="Monitoramento explicavel de transacoes sinteticas",
    schedule="*/15 * * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args=retry_policy(critical=True),
    tags=["poc", "cooperativa", "risco", "dados-sinteticos"],
)
def transaction_monitoring():
    @task
    def ingest_synthetic():
        return [
            {"id": "TX-DEMO-001", "amount": "125.40", "country": "BR", "attempts": 1, "new_device": False},
            {"id": "TX-DEMO-002", "amount": "18500.00", "country": "BR", "attempts": 6, "new_device": True},
            {"id": "TX-DEMO-003", "amount": "4200.00", "country": "UY", "attempts": 2, "new_device": True},
        ]

    @task
    def evaluate(rows):
        results = []
        for row in rows:
            score, decision = transaction_risk(
                Decimal(row["amount"]), row["country"], row["attempts"], row["new_device"]
            )
            append_event(
                "transaction_risk_evaluated",
                row["id"],
                decision,
                {"risk_score": score, "rule_version": "poc-v1"},
            )
            results.append({"transaction_ref": row["id"], "risk_score": score, "decision": decision})
        return results

    @task
    def route_exceptions(results):
        exceptions = [item for item in results if item["decision"] == "manual_review"]
        append_event("exception_queue_updated", "batch", "success", {"exception_count": len(exceptions)})
        return {"processed": len(results), "manual_review": len(exceptions)}

    route_exceptions(evaluate(ingest_synthetic()))


transaction_monitoring()
