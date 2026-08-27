from datetime import datetime, timezone

from airflow.sdk import dag, task

from poc.audit import append_event
from poc.policies import retry_policy
from poc.rules import kyc_decision


@dag(dag_id="coop_kyc_onboarding", description="Onboarding KYC sintetico com human-in-the-loop", schedule=None,
     start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), catchup=False, max_active_runs=1,
     default_args=retry_policy(), tags=["poc", "kyc", "dados-sinteticos"])
def kyc_onboarding():
    @task
    def validate_cases():
        cases = [
            ("MEMBER-DEMO-001", True, False, True),
            ("MEMBER-DEMO-002", True, True, True),
            ("MEMBER-DEMO-003", False, False, False),
        ]
        summary = {"approved": 0, "manual_review": 0, "pending_evidence": 0}
        for subject, document_valid, sanctions_hit, address_match in cases:
            decision = kyc_decision(document_valid, sanctions_hit, address_match)
            summary[decision] += 1
            append_event(
                "kyc_decision",
                subject,
                decision,
                {"rule_version": "poc-v1", "human_required": decision != "approved"},
            )
        return summary

    validate_cases()


kyc_onboarding()
