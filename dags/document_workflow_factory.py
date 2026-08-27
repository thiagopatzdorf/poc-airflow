"""Gera DAGs documentais exclusivamente a partir do YAML validado."""
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow.providers.standard.operators.hitl import ApprovalOperator
from airflow.sdk import dag, get_current_context, task

from poc.audit import append_event
from poc.policies import retry_policy
from poc.process_store import start_process, transition
from poc.workflow_schema import business_markdown, parse_workflows

CONFIG_PATH = Path("/opt/airflow/config/workflows/document_lifecycle.yaml")


def build_document_dag(flow):
    @dag(
        dag_id=f"document_{flow.id}",
        description=flow.name,
        schedule=flow.schedule,
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        catchup=False,
        max_active_runs=1,
        default_args=retry_policy(critical=True),
        tags=["poc", "documentos", "yaml", flow.document_type],
        doc_md=business_markdown(flow),
    )
    def generated():
        @task
        def receive_document():
            context = get_current_context()
            run_suffix = hashlib.sha256(context["run_id"].encode()).hexdigest()[:12]
            document = {"document_id": f"DOC-DEMO-{flow.id}-{run_suffix}", "type": flow.document_type,
                        "source": "SYNTHETIC", "content_digest": "sha256:demo"}
            start_process(process_id=document["document_id"], flow=flow, run_ref=context["run_id"])
            append_event("document_received", document["document_id"], "RECEIVED",
                         {"document_type": flow.document_type, "source": "SYNTHETIC"},
                         idempotency_key=f'{context["run_id"]}:document_received')
            return document

        @task
        def read_and_validate(document):
            context = get_current_context()
            transition(document["document_id"], "VALIDATED", context["run_id"])
            append_event("document_read", document["document_id"], "VALIDATED",
                         {"reader": "deterministic-demo-v1", "content_stored_in_log": False},
                         idempotency_key=f'{context["run_id"]}:document_read')
            return document

        @task
        def send_to_associated(document):
            context = get_current_context()
            transition(document["document_id"], "AWAITING_SIGNATURES", context["run_id"])
            append_event("document_sent", document["document_id"], "AWAITING_SIGNATURES",
                         {"channel": "SIMULATED", "required_signatures": flow.required_signatures},
                         idempotency_key=f'{context["run_id"]}:document_sent')
            return document

        @task
        def complete(document):
            context = get_current_context()
            transition(document["document_id"], "COMPLETED", context["run_id"],
                       signature_delta=flow.required_signatures)
            append_event("document_discharged", document["document_id"], "COMPLETED",
                         {"signatures": flow.required_signatures, "retention_days": flow.retention_days},
                         idempotency_key=f'{context["run_id"]}:document_discharged')
            return {"document_ref": document["document_id"], "status": "COMPLETED"}

        document = send_to_associated(read_and_validate(receive_document()))
        previous = document
        for position, signer in enumerate(flow.signers, start=1):
            approval = ApprovalOperator(
                task_id=f"await_signature_{position}_{signer.id}",
                subject=f"Assinatura {position}/{flow.required_signatures}: {flow.name}",
                body=f"Documento sintetico. Papel esperado: {signer.display_name}.",
                defaults="Reject",
                response_timeout=timedelta(minutes=flow.expires_in_minutes),
                assigned_users=[{"id": signer.airflow_user, "name": signer.airflow_user}],
            )
            previous >> approval
            previous = approval
        final = complete(document)
        previous >> final

    return generated()


for workflow in parse_workflows(CONFIG_PATH):
    globals()[f"document_{workflow.id}"] = build_document_dag(workflow)
