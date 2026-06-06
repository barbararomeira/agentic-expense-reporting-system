"""The data shapes that flow through the pipeline.

Everything that touches money uses `Decimal`, never `float` — float rounding
(0.1 + 0.2 != 0.3) would make the receipt-reconciliation check in later phases
flaky and could move the wrong amount of money.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


@dataclass(frozen=True)
class LineItem:
    """One line on a receipt, e.g. ('Round-trip flight', 210.00)."""
    description: str
    amount: Decimal


@dataclass
class Receipt:
    """A single receipt after extraction."""
    source: str            # the fixture/image reference it came from
    vendor: str
    date: str
    category: str
    line_items: list[LineItem]
    stated_total: Decimal  # the total printed on the receipt
    card_last4: str | None = None  # only the last 4 digits are ever kept (Phase E)

    @property
    def computed_total(self) -> Decimal:
        """The sum of the line items. In a healthy receipt this equals
        `stated_total`; a mismatch is a signal of a bad extraction (Phase B)."""
        return sum((li.amount for li in self.line_items), Decimal("0"))


@dataclass
class ExtractionResult:
    """What Agent 1 returns for one receipt: the structured Receipt plus how
    confident the extractor was, and any notes (e.g. 'image is blurry')."""
    source: str
    receipt: Receipt | None
    confidence: float
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Employee:
    """A person in the org. `region` drives data-residency (Phase E);
    `manager_id` drives the conflict-of-interest check (Phase D)."""
    id: str
    name: str
    role: str
    department: str
    region: str = "US"
    manager_id: str | None = None


@dataclass
class ExpenseReport:
    """What an employee submits: a purpose and a list of receipt references."""
    report_id: str
    employee_id: str
    purpose: str
    receipt_sources: list[str]


class DecisionStatus(str, Enum):
    """The possible outcomes of a run. Phase A only produces APPROVED/REJECTED;
    the rest are wired in by later phases (declared now to avoid churn)."""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_MORE_INFO = "NEEDS_MORE_INFO"        # Phase B/C: bad extraction or info request
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"  # Phase C/D: escalated, couldn't route
    BLOCKED = "BLOCKED"                        # Phase E: data-residency violation


class Verdict(str, Enum):
    """What a human reviewer can decide (Phase C)."""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_INFO = "request_more_info"


@dataclass
class Approval:
    """One reviewer's verdict on an escalated expense."""
    approver_id: str
    approver_name: str
    department: str
    verdict: Verdict
    note: str = ""


@dataclass
class Decision:
    """The final result of running one report through the pipeline."""
    report_id: str
    status: DecisionStatus
    amount: Decimal
    reason: str
    paid: bool = False
    payment_ref: str | None = None
    approvals: list[Approval] = field(default_factory=list)  # who signed off (Phase C/D)
