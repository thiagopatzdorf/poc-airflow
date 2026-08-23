"""Politicas operacionais centralizadas para evitar DAGs inconsistentes."""
from datetime import timedelta


def retry_policy(*, critical: bool = False) -> dict:
    """Backoff limitado para falhas transientes; erros permanentes falham rapido."""
    return {
        "retries": 3 if critical else 2,
        "retry_delay": timedelta(seconds=30),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(minutes=5),
    }
