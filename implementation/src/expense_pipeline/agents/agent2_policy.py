"""Agent 2 — computation + policy.

Sums the receipts and checks them against policy. This is DETERMINISTIC code,
not an LLM call: a financial check must be reproducible and auditable. Phase A
only checks that categories are allowed; per-category caps come in a later phase.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from expense_pipeline.models import Receipt
from expense_pipeline.policy import Policy


@dataclass
class PolicyAnalysis:
    total: Decimal
    violations: list[str] = field(default_factory=list)
    recommend_approve: bool = True
    summary: str = ""


def run_agent2(receipts: list[Receipt], policy: Policy, transcript: list[str]) -> PolicyAnalysis:
    total = sum((r.stated_total for r in receipts), Decimal("0"))
    violations: list[str] = []

    for r in receipts:
        if policy.allowed_categories and r.category not in policy.allowed_categories:
            violations.append(f"category '{r.category}' is not an allowed expense type")

    recommend = not violations
    summary = (
        f"total {policy.currency} {total}; "
        + ("within policy" if recommend else "; ".join(violations))
    )
    transcript.append(f"agent2: {summary}")
    return PolicyAnalysis(total=total, violations=violations, recommend_approve=recommend, summary=summary)
