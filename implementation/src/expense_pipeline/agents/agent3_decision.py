"""Agent 3 — decision.

Turns Agent 2's analysis into a final Decision and triggers payment on approval.
Phase A is the simplest version: approve (and pay) if Agent 2 found no
violations, otherwise reject. The human-review and four-eyes escalations are
layered on here in Phases C and D.
"""
from __future__ import annotations

from expense_pipeline.agents.agent2_policy import PolicyAnalysis
from expense_pipeline.models import Decision, DecisionStatus, ExpenseReport
from expense_pipeline.payment import PaymentService


def run_agent3(
    report: ExpenseReport,
    analysis: PolicyAnalysis,
    payment: PaymentService,
    transcript: list[str],
) -> Decision:
    if not analysis.recommend_approve:
        transcript.append("agent3: REJECTED (policy violations)")
        return Decision(
            report_id=report.report_id,
            status=DecisionStatus.REJECTED,
            amount=analysis.total,
            reason=analysis.summary,
        )

    ref = payment.reimburse(report.employee_id, analysis.total)
    transcript.append(f"agent3: APPROVED; reimbursed {analysis.total} (ref {ref})")
    return Decision(
        report_id=report.report_id,
        status=DecisionStatus.APPROVED,
        amount=analysis.total,
        reason="auto-approved (within policy)",
        paid=True,
        payment_ref=ref,
    )
