"""Regras didaticas sobre dados 100% sinteticos; nao representam politica real."""
from __future__ import annotations
from decimal import Decimal


def transaction_risk(amount: Decimal, country: str, attempts_10m: int, new_device: bool) -> tuple[int, str]:
    score = 0
    score += 45 if amount >= Decimal("10000") else 15 if amount >= Decimal("3000") else 0
    score += 30 if country not in {"BR"} else 0
    score += 25 if attempts_10m >= 5 else 10 if attempts_10m >= 3 else 0
    score += 15 if new_device else 0
    return score, "manual_review" if score >= 60 else "approved"


def kyc_decision(document_valid: bool, sanctions_hit: bool, address_match: bool) -> str:
    if sanctions_hit:
        return "manual_review"
    if not document_valid or not address_match:
        return "pending_evidence"
    return "approved"


def reconcile(ledger_total: Decimal, settlement_total: Decimal, tolerance: Decimal = Decimal("0.01")) -> str:
    return "matched" if abs(ledger_total - settlement_total) <= tolerance else "exception"

