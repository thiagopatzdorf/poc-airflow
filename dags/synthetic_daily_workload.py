"""Mantém a TV viva com 200-400 tickets sintéticos por dia."""
from datetime import datetime, timezone

from airflow.sdk import dag, task

from poc.policies import retry_policy
from poc.synthetic_load import generate_due_tickets


@dag(
    dag_id="synthetic_daily_workload",
    description="Carga sintética diária para painel operacional",
    schedule="*/2 * * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args=retry_policy(critical=False),
    tags=["poc", "synthetic", "observability"],
    doc_md="""## Carga sintética da TV

Converge ao longo do dia para 200-400 tickets, todos marcados como sintéticos.
Não representa produção nem dispara comunicação real.
""",
)
def synthetic_daily_workload():
    @task
    def generate():
        return generate_due_tickets()

    generate()


synthetic_daily_workload()
