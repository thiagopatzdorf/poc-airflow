"""Contratos seguros para agentes: recomendacao estruturada, sem ferramentas."""
from __future__ import annotations

import hashlib
import json

ALLOWED_RECOMMENDATIONS = {"APPROVE", "REJECT", "REVIEW"}
ALLOWED_ROLES = {"PROPOSER", "CRITIC"}


def input_digest(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def simulated_agent(role: str, case: dict) -> dict:
    """Substituto deterministico do LLM para uma demo reproduzivel e sem egress."""
    if role not in ALLOWED_ROLES:
        raise ValueError("invalid agent role")
    delta = abs(float(case["delta"]))
    recommendation = "REVIEW" if delta else "APPROVE"
    if role == "CRITIC" and delta >= 10000:
        recommendation = "REJECT"
    output = {
        "schema_version": "1.0",
        "case_id": case["case_id"],
        "input_digest": input_digest(case),
        "agent_role": role,
        "recommendation": recommendation,
        "confidence": 0.95,
        "reason_codes": ["NON_ZERO_RECONCILIATION_DELTA"] if delta else ["EXACT_MATCH"],
        "evidence_refs": ["synthetic://reconciliation/delta"],
        "requested_action": "HUMAN_REVIEW" if delta else "NONE",
        "model_id": "deterministic-demo-agent-v1",
        "prompt_template_version": "poc-v1",
        "policy_version": "poc-v1",
    }
    output["output_digest"] = input_digest(output)
    return output


def validate_agent_contract(output: dict, case: dict) -> None:
    required = {"schema_version", "case_id", "input_digest", "agent_role", "recommendation",
                "confidence", "reason_codes", "evidence_refs", "requested_action", "model_id",
                "prompt_template_version", "policy_version", "output_digest"}
    if set(output) != required:
        raise ValueError("agent contract has missing or extra fields")
    digest = output["output_digest"]
    unsigned = {key: value for key, value in output.items() if key != "output_digest"}
    if digest != input_digest(unsigned) or output["input_digest"] != input_digest(case):
        raise ValueError("agent contract digest mismatch")
    if output["agent_role"] not in ALLOWED_ROLES or output["recommendation"] not in ALLOWED_RECOMMENDATIONS:
        raise ValueError("agent contract enum violation")
    if not 0 <= output["confidence"] <= 1:
        raise ValueError("agent confidence out of range")

