"""Agent 1 — extraction + the validation gate (Step 2) + minimal, region-aware
persistence (Step 4).

Reads each receipt, runs the validation gate, then persists a *minimized* row
through the region-aware store: only the fields we need, only the card's last 4
digits, and never an EU employee's data into a non-EU store (the store raises
DataResidencyError, which the orchestrator turns into a BLOCKED decision).

The full Receipt objects are still returned for in-memory processing by Agents
2/3 this run; it's the *persisted* copy that is minimized.
"""
from __future__ import annotations

from expense_pipeline.extractors.base import ReceiptExtractor
from expense_pipeline.models import Employee, ExpenseReport, ExtractionResult, Receipt
from expense_pipeline.policy import Policy
from expense_pipeline.privacy import RegionalDataStore, minimize_receipt


def _validate(result: ExtractionResult, policy: Policy) -> list[str]:
    """Return a list of problems; empty means the extraction is trustworthy."""
    if result.receipt is None:
        return ["no receipt could be extracted"]

    r = result.receipt
    problems: list[str] = []
    if result.confidence < policy.extraction_confidence_threshold:
        problems.append(
            f"low confidence {result.confidence:.2f} "
            f"(need >= {policy.extraction_confidence_threshold})"
        )
    if policy.allowed_categories and r.category not in policy.allowed_categories:
        problems.append(f"category '{r.category}' is not an allowed expense type")
    if r.computed_total != r.stated_total:
        problems.append(
            f"line items sum to {r.computed_total} but stated total is {r.stated_total} "
            "(does not reconcile)"
        )
    return problems


def run_agent1(
    report: ExpenseReport,
    extractor: ReceiptExtractor,
    store: RegionalDataStore,
    transcript: list[str],
    policy: Policy,
    employee: Employee | None,
    validate: bool = True,
) -> tuple[list[Receipt], list[str]]:
    receipts: list[Receipt] = []
    problems: list[str] = []

    for source in report.receipt_sources:
        result = extractor.extract(source)
        transcript.append(
            f"agent1: extracted '{source}' "
            f"({result.receipt.vendor}, stated {result.receipt.stated_total}) "
            f"confidence={result.confidence:.2f}"
        )
        issues = _validate(result, policy) if validate else []
        if issues:
            transcript.append(f"agent1: '{source}' FAILED validation -> NOT saved [{'; '.join(issues)}]")
            problems.extend(issues)
            continue

        row = minimize_receipt(result.receipt)
        store.write(row, employee)   # region-enforced; raises DataResidencyError if EU->non-EU
        transcript.append(f"agent1: saved minimized row {row}")
        receipts.append(result.receipt)

    return receipts, problems
