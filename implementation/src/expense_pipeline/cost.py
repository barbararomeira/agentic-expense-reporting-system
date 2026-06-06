"""Operational cost-driver report (Step 6).

Classifies each component by how its cost behaves with volume. This mirrors the
06-cost-drivers.md table: the three agents and the payment service scale with
volume (per-token LLM calls and per-transaction fees); the data stores and the
mobile layer are flat and cheap; private infrastructure is flat and expensive.
"""
from __future__ import annotations

from dataclasses import dataclass

FLAT_LOW = "flat-low"
FLAT_HIGH = "flat-high"
VARIABLE = "variable"

_LABELS = {
    FLAT_LOW: "Flat & low",
    FLAT_HIGH: "Flat & high",
    VARIABLE: "Variable w/ volume",
}


@dataclass(frozen=True)
class CostDriver:
    component: str
    category: str
    why: str


COST_DRIVERS: list[CostDriver] = [
    CostDriver("Database", FLAT_LOW, "provisioned instance; you pay for the instance, not per query"),
    CostDriver("Spreadsheet", FLAT_LOW, "cheap cloud storage; no per-transaction fee"),
    CostDriver("Mobile Web and Camera", FLAT_LOW, "camera runs on the user's phone; web frontend is a small fixed host"),
    CostDriver("Agent 1", VARIABLE, "an LLM call per receipt; cost rises with volume"),
    CostDriver("Agent 2", VARIABLE, "an LLM call per report; Remember-heavy, the largest token footprint"),
    CostDriver("Agent 3", VARIABLE, "an LLM call per decision; cost rises with volume"),
    CostDriver("Private infrastructure", FLAT_HIGH, "capacity provisioned up front regardless of volume; large fixed cost"),
    CostDriver("Payment service", VARIABLE, "a fee per transaction; scales with reimbursements"),
]


def render_table() -> str:
    width = max(len(d.component) for d in COST_DRIVERS)
    label_width = max(len(label) for label in _LABELS.values())
    header = f"{'Component'.ljust(width)}  {'Cost behaviour'.ljust(label_width)}  Why"
    lines = [header, "-" * len(header)]
    for d in COST_DRIVERS:
        lines.append(f"{d.component.ljust(width)}  {_LABELS[d.category].ljust(label_width)}  {d.why}")
    return "\n".join(lines)
