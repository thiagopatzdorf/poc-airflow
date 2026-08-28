from decimal import Decimal

from poc.rules import kyc_decision, reconcile, transaction_risk


def test_high_risk_transaction_requires_review():
    score, decision = transaction_risk(Decimal(15000), "BR", 6, True)
    assert score >= 60
    assert decision == "manual_review"


def test_low_risk_transaction_is_approved():
    assert transaction_risk(Decimal(100), "BR", 1, False) == (0, "approved")


def test_kyc_never_auto_approves_sanctions_hit():
    assert kyc_decision(True, True, True) == "manual_review"


def test_reconciliation_tolerance():
    assert reconcile(Decimal("10.00"), Decimal("10.01")) == "matched"
    assert reconcile(Decimal("10.00"), Decimal("10.02")) == "exception"

