"""Phase C: human review kicks in for approved expenses over $500.

large_trip totals 810.00 (flight 210 + hotel 600), so it must be escalated to
one approver. small_trip totals 255.00, below the threshold, so it stays
autonomous and no reviewer is consulted.
"""
from expense_pipeline.human_review import ScriptedReviewer
from expense_pipeline.models import DecisionStatus, Verdict


def test_over_500_triggers_one_approver(pipeline, report):
    result = pipeline.run_report(report("large_trip"))
    d = result.decision
    assert d.status == DecisionStatus.APPROVED
    assert d.paid is True
    assert len(d.approvals) == 1                       # exactly one approver
    assert d.approvals[0].verdict == Verdict.APPROVE


def test_reviewer_reject_blocks_payment(make_pipeline, report):
    pipe = make_pipeline(reviewer=ScriptedReviewer(default=Verdict.REJECT))
    result = pipe.run_report(report("large_trip"))
    assert result.decision.status == DecisionStatus.REJECTED
    assert result.decision.paid is False
    assert pipe.payment.payments == []


def test_reviewer_request_info(make_pipeline, report):
    pipe = make_pipeline(reviewer=ScriptedReviewer(default=Verdict.REQUEST_INFO))
    result = pipe.run_report(report("large_trip"))
    assert result.decision.status == DecisionStatus.NEEDS_MORE_INFO
    assert result.decision.paid is False


def test_under_500_stays_autonomous(make_pipeline, report):
    # A reviewer that WOULD reject — but small_trip is under threshold, so the
    # reviewer is never consulted and it still auto-approves with no approvals.
    pipe = make_pipeline(reviewer=ScriptedReviewer(default=Verdict.REJECT))
    result = pipe.run_report(report("small_trip"))
    assert result.decision.status == DecisionStatus.APPROVED
    assert result.decision.approvals == []
