"""Phase B: the validation gate catches the hallucination bug.

The `unreadable` receipt has a true total of 60.00; the mock hallucinates an
inflated 114.00 (60.00 x 1.9). With the gate on, that extraction is blocked and
nothing is paid. With the gate off (`--no-validation`), the inflated total
flows through and the company overpays — the original Step 2 bug.
"""
from decimal import Decimal

from expense_pipeline.models import DecisionStatus


def test_unreadable_is_blocked_by_the_gate(pipeline, report):
    result = pipeline.run_report(report("unreadable_receipt"))
    assert result.decision.status == DecisionStatus.NEEDS_MORE_INFO
    assert result.decision.paid is False
    assert pipeline.payment.payments == []          # nothing was paid


def test_unreadable_overpays_without_validation(pipeline, report):
    result = pipeline.run_report(report("unreadable_receipt"), validate=False)
    assert result.decision.status == DecisionStatus.APPROVED
    assert result.decision.paid is True
    assert result.decision.amount == Decimal("114.00")   # the bug: 60.00 -> 114.00


def test_blurry_is_blocked_for_low_confidence(pipeline, report):
    # Fields are accurate but confidence is low, so the gate conservatively holds it.
    result = pipeline.run_report(report("blurry_receipt"))
    assert result.decision.status == DecisionStatus.NEEDS_MORE_INFO
    assert result.decision.paid is False


def test_clear_receipts_still_pass(pipeline, report):
    result = pipeline.run_report(report("small_trip"))
    assert result.decision.status == DecisionStatus.APPROVED
    assert result.decision.paid is True
