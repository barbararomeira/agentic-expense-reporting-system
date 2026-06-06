"""Agent 3 — decision, with single- and two-person review (Steps 3 + 5).

Escalation tiers (only reached if Agent 2 recommends approval):
* total <= human_review_threshold and no risk flags -> autonomous.
* high-risk (amount > dual_dept_threshold, OR a reporting-line conflict of
  interest, OR a high-fraud-risk category) -> TWO approvers in two different
  departments; unanimous-blocks (any non-approve blocks payment).
* otherwise over human_review_threshold -> ONE approver (Step 3).

Agent 3 only routes; "who approves" is the directory's job and "what they
decide" is the reviewer's.
"""
from __future__ import annotations

from expense_pipeline.agents.agent2_policy import PolicyAnalysis
from expense_pipeline.directory import Approver, OrgDirectory
from expense_pipeline.human_review import HumanReviewer, ReviewContext
from expense_pipeline.models import Approval, Decision, DecisionStatus, ExpenseReport, Verdict
from expense_pipeline.payment import PaymentService
from expense_pipeline.policy import Policy


def _pay_and_approve(report, analysis, payment, transcript, approvals) -> Decision:
    ref = payment.reimburse(report.employee_id, analysis.total)
    transcript.append(f"agent3: APPROVED; reimbursed {analysis.total} (ref {ref})")
    return Decision(
        report_id=report.report_id, status=DecisionStatus.APPROVED, amount=analysis.total,
        reason="approved", paid=True, payment_ref=ref, approvals=approvals,
    )


def _review(approver: Approver, reviewer: HumanReviewer, ctx: ReviewContext, transcript) -> Approval:
    approval = reviewer.decide(approver, ctx)
    transcript.append(f"  reviewer {approval.approver_name} ({approval.department}): {approval.verdict.value}")
    return approval


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

    employee = directory.employee(report.employee_id)
    dept = employee.department if employee else "Unknown"
    primary = directory.approver_for_department(dept)

    # The three Step 5 risk triggers.
    conflict = bool(employee and primary and directory.is_conflict(employee, primary))
    high_risk = any(c in policy.high_risk_categories for c in analysis.categories)
    over_dual = analysis.total > policy.dual_dept_threshold
    needs_dual = over_dual or conflict or high_risk
    needs_review = needs_dual or analysis.total > policy.human_review_threshold

    if not needs_review:
        return _pay_and_approve(report, analysis, payment, transcript, [])

    ctx = ReviewContext(
        report_id=report.report_id,
        employee_name=employee.name if employee else report.employee_id,
        department=dept,
        purpose=report.purpose,
        total=analysis.total,
        summary=analysis.summary,
    )

    if needs_dual:
        reasons = []
        if over_dual:
            reasons.append(f"amount {analysis.total} over {policy.dual_dept_threshold}")
        if conflict:
            reasons.append("reporting-line conflict of interest")
        if high_risk:
            reasons.append("high-fraud-risk category")
        transcript.append(f"agent3: two-person approval required ({'; '.join(reasons)})")

        approvers = directory.select_dual_approvers(employee, dept) if employee else []
        if len(approvers) < 2:
            transcript.append("agent3: cannot form a two-department panel -> NEEDS_HUMAN_REVIEW")
            return Decision(
                report.report_id, DecisionStatus.NEEDS_HUMAN_REVIEW, analysis.total,
                "insufficient independent approvers for a two-department panel",
            )
        transcript.append(
            f"agent3: routing to {approvers[0].name} ({approvers[0].department}) "
            f"and {approvers[1].name} ({approvers[1].department})"
        )
        approvals = [_review(a, reviewer, ctx, transcript) for a in approvers]
        if all(ap.verdict == Verdict.APPROVE for ap in approvals):
            return _pay_and_approve(report, analysis, payment, transcript, approvals)
        transcript.append("agent3: not unanimous -> BLOCKED (REJECTED)")
        return Decision(
            report.report_id, DecisionStatus.REJECTED, analysis.total,
            "two-person approval was not unanimous", approvals=approvals,
        )

    # Single-approver tier (over $500, no risk flags) — Step 3.
    transcript.append(f"agent3: {analysis.total} over {policy.human_review_threshold} -> human review required")
    if primary is None:
        transcript.append(f"agent3: no approver configured for '{dept}' -> NEEDS_HUMAN_REVIEW")
        return Decision(report.report_id, DecisionStatus.NEEDS_HUMAN_REVIEW, analysis.total, f"no approver for '{dept}'")

    approval = _review(primary, reviewer, ctx, transcript)
    if approval.verdict == Verdict.APPROVE:
        return _pay_and_approve(report, analysis, payment, transcript, [approval])
    if approval.verdict == Verdict.REJECT:
        transcript.append("agent3: REJECTED by reviewer")
        return Decision(report.report_id, DecisionStatus.REJECTED, analysis.total, "rejected by reviewer", approvals=[approval])
    transcript.append("agent3: reviewer requested more info -> NEEDS_MORE_INFO")
    return Decision(report.report_id, DecisionStatus.NEEDS_MORE_INFO, analysis.total, "reviewer requested more information", approvals=[approval])
