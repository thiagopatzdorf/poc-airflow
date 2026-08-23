from datetime import datetime, timedelta, timezone
from airflow.sdk import dag, task
from airflow.providers.standard.operators.hitl import ApprovalOperator
from poc.agents import simulated_agent, validate_agent_contract
from poc.audit import append_event
from poc.policies import retry_policy


@dag(
    dag_id="coop_agentic_reconciliation_hitl",
    description="Agentes independentes + aprovacao humana segregada, somente dry-run",
    schedule=None,
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args=retry_policy(critical=True),
    tags=["poc", "agents-in-loop", "human-in-loop", "four-eyes", "dry-run"],
)
def agentic_reconciliation_hitl():
    @task
    def prepare_case():
        return {"case_id": "CASE-DEMO-HIGH-001", "delta": "12500.00", "currency": "BRL",
                "source": "SYNTHETIC", "action": "RELEASE_SIMULATION"}

    @task
    def proposer(case):
        result = simulated_agent("PROPOSER", case)
        validate_agent_contract(result, case)
        append_event("agent_recommendation", case["case_id"], result["recommendation"],
                     {"agent_role": "PROPOSER", "output_digest": result["output_digest"]})
        return result

    @task
    def critic(case):
        result = simulated_agent("CRITIC", case)
        validate_agent_contract(result, case)
        append_event("agent_recommendation", case["case_id"], result["recommendation"],
                     {"agent_role": "CRITIC", "output_digest": result["output_digest"]})
        return result

    @task
    def policy_gate(case, proposal, criticism):
        validate_agent_contract(proposal, case)
        validate_agent_contract(criticism, case)
        append_event("policy_gate", case["case_id"], "HUMAN_REVIEW_REQUIRED",
                     {"policy_version": "poc-v1", "four_eyes": True})
        return {"case": case, "proposal": proposal["recommendation"], "critic": criticism["recommendation"]}

    case = prepare_case()
    review_packet = policy_gate(case, proposer(case), critic(case))

    approval_l1 = ApprovalOperator(
        task_id="approval_level_1",
        subject="Aprovacao L1 — caso sintetico de alto risco",
        body="Revise o pacote: {{ ti.xcom_pull(task_ids='policy_gate') }}",
        defaults="Reject",
        response_timeout=timedelta(minutes=30),
        assigned_users=[{"id": "admin", "name": "admin"}],
    )
    approval_l2 = ApprovalOperator(
        task_id="approval_level_2_four_eyes",
        subject="Aprovacao L2 independente — quatro olhos",
        body="Segundo aprovador: confirme ou rejeite o mesmo pacote sintetico.",
        defaults="Reject",
        response_timeout=timedelta(minutes=30),
        assigned_users=[{"id": "security", "name": "security"}],
    )

    @task
    def execute_dry_run(packet):
        append_event("simulated_action", packet["case"]["case_id"], "DRY_RUN_ONLY",
                     {"action": packet["case"]["action"], "external_effect": False})
        return {"status": "SIMULATED", "external_effect": False}

    review_packet >> approval_l1 >> approval_l2
    execute_dry_run(review_packet).set_upstream(approval_l2)


agentic_reconciliation_hitl()
