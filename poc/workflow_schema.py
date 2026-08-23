"""Schema fechado para transformar YAML declarativo em DAG sem executar codigo arbitrario."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

TOP_KEYS = {"schema_version", "workflows"}
WORKFLOW_KEYS = {
    "id", "name", "document_type", "schedule", "retention_days", "signature", "reminders",
    "on_expiry", "business_owner", "exception_owner", "purpose", "sla_minutes", "inputs", "outputs",
    "automation_owner", "platform_owner", "security_owner",
}
SIGNATURE_KEYS = {"required_signatures", "expires_in_minutes", "signers"}
SIGNER_KEYS = {"id", "display_name", "airflow_user"}
REMINDER_KEYS = {"intervals_minutes", "max_attempts"}
EXPIRY_ACTIONS = {"quarantine", "manual_review"}


@dataclass(frozen=True)
class Signer:
    id: str
    display_name: str
    airflow_user: str


@dataclass(frozen=True)
class DocumentWorkflow:
    id: str
    name: str
    document_type: str
    business_owner: str
    automation_owner: str
    platform_owner: str
    security_owner: str
    exception_owner: str
    purpose: str
    sla_minutes: int
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    schedule: str | None
    retention_days: int
    required_signatures: int
    expires_in_minutes: int
    signers: tuple[Signer, ...]
    reminder_intervals: tuple[int, ...]
    max_reminders: int
    on_expiry: str


def _closed_keys(value: dict[str, Any], allowed: set[str], location: str) -> None:
    extra = set(value) - allowed
    if extra:
        raise ValueError(f"{location}: unknown fields: {sorted(extra)}")


def _identifier(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.replace("_", "").isalnum() or not value[0].isalpha():
        raise ValueError(f"{location}: invalid identifier")
    return value


def parse_workflows(path: Path) -> list[DocumentWorkflow]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("root must be a mapping")
    _closed_keys(raw, TOP_KEYS, "root")
    if raw.get("schema_version") != "1.0" or not isinstance(raw.get("workflows"), list):
        raise ValueError("unsupported schema or workflows is not a list")
    result = []
    seen = set()
    for index, item in enumerate(raw["workflows"]):
        location = f"workflows[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{location}: must be a mapping")
        _closed_keys(item, WORKFLOW_KEYS, location)
        workflow_id = _identifier(item.get("id"), f"{location}.id")
        if workflow_id in seen:
            raise ValueError(f"{location}: duplicate id")
        seen.add(workflow_id)
        signature = item.get("signature")
        reminders = item.get("reminders")
        if not isinstance(signature, dict) or not isinstance(reminders, dict):
            raise ValueError(f"{location}: signature/reminders must be mappings")
        _closed_keys(signature, SIGNATURE_KEYS, f"{location}.signature")
        _closed_keys(reminders, REMINDER_KEYS, f"{location}.reminders")
        signers_raw = signature.get("signers")
        if not isinstance(signers_raw, list) or not 1 <= len(signers_raw) <= 10:
            raise ValueError(f"{location}: signers must contain 1..10 entries")
        signers = []
        signer_ids = set()
        airflow_users = set()
        for signer_raw in signers_raw:
            if not isinstance(signer_raw, dict):
                raise ValueError(f"{location}: signer must be a mapping")
            _closed_keys(signer_raw, SIGNER_KEYS, f"{location}.signer")
            signer_id = _identifier(signer_raw.get("id"), f"{location}.signer.id")
            user = _identifier(signer_raw.get("airflow_user"), f"{location}.signer.airflow_user")
            if signer_id in signer_ids or user in airflow_users:
                raise ValueError(f"{location}: signers and users must be distinct")
            signer_ids.add(signer_id)
            airflow_users.add(user)
            signers.append(Signer(signer_id, str(signer_raw.get("display_name", "")), user))
        required = signature.get("required_signatures")
        if required != len(signers):
            raise ValueError(f"{location}: POC v1 requires every declared signer")
        expiry = signature.get("expires_in_minutes")
        if not isinstance(expiry, int) or not 1 <= expiry <= 10080:
            raise ValueError(f"{location}: invalid signature expiry")
        intervals = reminders.get("intervals_minutes")
        if not isinstance(intervals, list) or any(not isinstance(v, int) or v <= 0 for v in intervals):
            raise ValueError(f"{location}: invalid reminder intervals")
        if intervals != sorted(set(intervals)):
            raise ValueError(f"{location}: reminder intervals must be sorted and unique")
        max_reminders = reminders.get("max_attempts")
        if not isinstance(max_reminders, int) or max_reminders != len(intervals):
            raise ValueError(f"{location}: max_attempts must match configured intervals")
        retention = item.get("retention_days")
        if not isinstance(retention, int) or not 1 <= retention <= 3650:
            raise ValueError(f"{location}: invalid retention")
        on_expiry = item.get("on_expiry")
        if on_expiry not in EXPIRY_ACTIONS:
            raise ValueError(f"{location}: invalid expiry action")
        sla = item.get("sla_minutes")
        if not isinstance(sla, int) or not 1 <= sla <= 43200:
            raise ValueError(f"{location}: invalid business SLA")
        inputs = item.get("inputs")
        outputs = item.get("outputs")
        if not isinstance(inputs, list) or not inputs or not isinstance(outputs, list) or not outputs:
            raise ValueError(f"{location}: inputs/outputs must be non-empty lists")
        normalized_inputs = tuple(_identifier(value, f"{location}.inputs") for value in inputs)
        normalized_outputs = tuple(_identifier(value, f"{location}.outputs") for value in outputs)
        business_owner = str(item.get("business_owner", "")).strip()
        exception_owner = str(item.get("exception_owner", "")).strip()
        purpose = str(item.get("purpose", "")).strip()
        if not all((business_owner, exception_owner, purpose)):
            raise ValueError(f"{location}: business metadata is required")
        automation_owner = _identifier(item.get("automation_owner"), f"{location}.automation_owner")
        platform_owner = _identifier(item.get("platform_owner"), f"{location}.platform_owner")
        security_owner = _identifier(item.get("security_owner"), f"{location}.security_owner")
        result.append(DocumentWorkflow(
            id=workflow_id, name=str(item.get("name", "")),
            document_type=_identifier(item.get("document_type"), f"{location}.document_type"),
            business_owner=business_owner, exception_owner=exception_owner, purpose=purpose,
            automation_owner=automation_owner, platform_owner=platform_owner,
            security_owner=security_owner,
            sla_minutes=sla, inputs=normalized_inputs, outputs=normalized_outputs,
            schedule=item.get("schedule"), retention_days=retention,
            required_signatures=required, expires_in_minutes=expiry, signers=tuple(signers),
            reminder_intervals=tuple(intervals), max_reminders=max_reminders, on_expiry=on_expiry,
        ))
    return result


def business_markdown(flow: DocumentWorkflow) -> str:
    signers = "\n".join(f"- {signer.display_name}" for signer in flow.signers)
    return f"""## {flow.name}

**Objetivo:** {flow.purpose}

| Campo | Definicao |
|---|---|
| Area responsavel | {flow.business_owner} |
| Engenheiro dono da automacao | {flow.automation_owner} |
| Engenheiro de plataforma | {flow.platform_owner} |
| Engenheiro de seguranca | {flow.security_owner} |
| Dona da excecao | {flow.exception_owner} |
| SLA | {flow.sla_minutes} minutos |
| Entrada | {", ".join(flow.inputs)} |
| Saida | {", ".join(flow.outputs)} |
| Assinaturas obrigatorias | {flow.required_signatures} |
| Expiracao | {flow.expires_in_minutes} minutos |
| Destino ao expirar | {flow.on_expiry} |

### Signatarios

{signers}

### Etapas

`Receber → Ler e validar → Enviar → Aguardar assinaturas → Baixa documental`
"""
