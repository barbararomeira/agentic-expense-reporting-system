"""Phase D: two-person approval (four-eyes), one test per trigger.

Each of the three triggers must independently force TWO approvers from TWO
different departments, and unanimous-blocks must hold.
"""
from expense_pipeline.human_review import ScriptedReviewer
from expense_pipeline.models import DecisionStatus, Verdict


def _two_departments(decision):
    return len(decision.approvals) == 2 and len({a.department for a in decision.approvals}) == 2


def test_amount_over_5000_requires_two_departments(pipeline, report):
    d = pipeline.run_report(report("huge_trip")).decision      # 6600
    assert d.status == DecisionStatus.APPROVED
    assert _two_departments(d)


def test_high_risk_category_requires_two_departments(pipeline, report):
    d = pipeline.run_report(report("gift_highrisk")).decision   # gift, 800
    assert d.status == DecisionStatus.APPROVED
    assert _two_departments(d)


def test_conflict_of_interest_requires_two_and_excludes_manager(pipeline, report):
    # emp-300 reports directly to the Engineering approver (mgr-eng).
    d = pipeline.run_report(report("conflict_report")).decision  # 600, conflict
    assert d.status == DecisionStatus.APPROVED
    assert _two_departments(d)
    assert "mgr-eng" not in {a.approver_id for a in d.approvals}  # conflicted manager excluded


def test_unanimous_blocks_on_a_single_reject(make_pipeline, report):
    # The second approver (Finance) rejects -> whole thing is blocked.
    pipe = make_pipeline(reviewer=ScriptedReviewer(scripted={"mgr-fin": Verdict.REJECT}))
    d = pipe.run_report(report("huge_trip")).decision
    assert d.status == DecisionStatus.REJECTED
    assert d.paid is False
    assert pipe.payment.payments == []


def test_normal_over_500_stays_single_approver(pipeline, report):
    # large_trip (810, no risk flags) must NOT trigger the dual gate.
    d = pipeline.run_report(report("large_trip")).decision
    assert d.status == DecisionStatus.APPROVED
    assert len(d.approvals) == 1
