"""Phase A: the thin end-to-end slice runs and auto-approves a clean small report."""
from decimal import Decimal

from expense_pipeline.models import DecisionStatus


def test_small_report_auto_approves(pipeline, report):
    result = pipeline.run_report(report("small_trip"))
    d = result.decision

    assert d.status == DecisionStatus.APPROVED
    assert d.paid is True
    assert d.amount == Decimal("255.00")        # flight 210.00 + taxi 45.00
    assert d.payment_ref is not None
    assert result.transcript                     # the run produced a transcript


def test_payment_was_recorded(pipeline, report):
    pipeline.run_report(report("small_trip"))
    assert len(pipeline.payment.payments) == 1
    assert pipeline.payment.payments[0]["amount"] == Decimal("255.00")
