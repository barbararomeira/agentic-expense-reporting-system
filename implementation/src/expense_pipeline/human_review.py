"""Human review (Step 3).

The pipeline talks to a `HumanReviewer` interface, so a real UI could be swapped
in later. For a runnable, testable build we use a `ScriptedReviewer` — a
deterministic stand-in for a person: it approves by default, and you can script
a specific verdict per approver (used by tests and demos).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol

from expense_pipeline.directory import Approver
from expense_pipeline.models import Approval, Verdict


@dataclass
class ReviewContext:
    """Everything a reviewer needs to make a high-quality decision — all of it
    already produced upstream (that's why the human sits after Agent 3)."""
    report_id: str
    employee_name: str
    department: str
    purpose: str
    total: Decimal
    summary: str


class HumanReviewer(Protocol):
    def decide(self, approver: Approver, ctx: ReviewContext) -> Approval:
        ...


@dataclass
class ScriptedReviewer:
    default: Verdict = Verdict.APPROVE
    scripted: dict[str, Verdict] = field(default_factory=dict)  # approver_id -> verdict

    def decide(self, approver: Approver, ctx: ReviewContext) -> Approval:
        verdict = self.scripted.get(approver.id, self.default)
        return Approval(
            approver_id=approver.id,
            approver_name=approver.name,
            department=approver.department,
            verdict=verdict,
        )
