"""Agent 3 — decision, now with human-review escalation (Step 3).

If Agent 2 recommends approval, Agent 3 checks the amount: at or below the
human-review threshold it approves autonomously; above it, the decision is
escalated to one human approver, whose verdict is final. The escalation logic
lives here; the "who is the approver" lookup is the directory's job and the
"what did they decide" is the reviewer's — Agent 3 just routes between them.
"""
from __future__ import annotations

from expense_pipeline.agents.agent2_policy import PolicyAnalysis
from expense_pipeline.directory import OrgDirectory
from expense_pipeline.human_review import HumanReviewer, ReviewContext
from expense_pipeline.models import Approval, Decision, DecisionStatus, ExpenseReport, Verdict
from expense_pipeline.payment import PaymentService
from expense_pipeline.policy import Policy


def _pay_and_approve(
    report: ExpenseReport,
    analysis: PolicyAnalysis,
    payment: PaymentService,
    transcript: list[str],
    approvals: list[Approval],
) -> Decision:
    ref = payment.reimburse(report.employee_id, analysis.total)
    transcript.append(f"agent3: APPROVED; reimbursed {analysis.total} (ref {ref})")
    return Decision(
        report_id=report.report_id,
        status=DecisionStatus.APPROVED,
        amount=analysis.total,
        reason="approved",
        paid=True,
        payment_ref=ref,
        approvals=approvals,
    )


def run_agent3(
    report: ExpenseReport,
    analysis: PolicyAnalysis,
    payment: PaymentService,
    transcript: list[str],
    policy: Policy,
    directory: OrgDirectory,
    reviewer: HumanReviewer,
) -> Decision:
    if not analysis.recommend_approve:
        transcript.append("agent3: REJECTED (policy violations)")
        return Decision(report.report_id, DecisionStatus.REJECTED, analysis.total, analysis.summary)

    # Under the threshold: stay autonomous, as before.
    if analysis.total <= policy.human_review_threshold:
        return _pay_and_approve(report, analysis, payment, transcript, [])

    # Over the threshold: escalate to one human approver.
    employee = directory.employee(report.employee_id)
    dept = employee.department if employee else "Unknown"
    approver = directory.approver_for_department(dept)
    transcript.append(
        f"agent3: {analysis.total} over {policy.human_review_threshold} -> human review required"
    )
    if approver is None:
        transcript.append(f"agent3: no approver configured for '{dept}' -> NEEDS_HUMAN_REVIEW")
        return Decision(
            report.report_id, DecisionStatus.NEEDS_HUMAN_REVIEW, analysis.total,
            f"no approver for department '{dept}'",
        )

    ctx = ReviewContext(
        report_id=report.report_id,
        employee_name=employee.name if employee else report.employee_id,
        department=dept,
        purpose=report.purpose,
        total=analysis.total,
        summary=analysis.summary,
    )
    approval = reviewer.decide(approver, ctx)
    transcript.append(f"  reviewer {approval.approver_name} ({approval.department}): {approval.verdict.value}")

    if approval.verdict == Verdict.APPROVE:
        return _pay_and_approve(report, analysis, payment, transcript, [approval])
    if approval.verdict == Verdict.REJECT:
        transcript.append("agent3: REJECTED by reviewer")
        return Decision(
            report.report_id, DecisionStatus.REJECTED, analysis.total,
            "rejected by human reviewer", approvals=[approval],
        )
    transcript.append("agent3: reviewer requested more info -> NEEDS_MORE_INFO")
    return Decision(
        report.report_id, DecisionStatus.NEEDS_MORE_INFO, analysis.total,
        "human reviewer requested more information", approvals=[approval],
    )
