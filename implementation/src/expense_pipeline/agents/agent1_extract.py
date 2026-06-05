"""Agent 1 — extraction + the validation gate (Step 2 bug fix).

Reads each receipt via the pluggable extractor, then runs it through a
validation gate BEFORE saving. The gate is the fix for the hallucination bug:
an extraction that is low-confidence, in a disallowed category, or whose line
items don't reconcile with the stated total is refused and never saved — so
fabricated data can't cascade to Agents 2 and 3.

`validate=False` skips the gate, which reproduces the original bug on purpose
(used by the CLI's `--no-validation` flag for the demo).
"""
from __future__ import annotations

from expense_pipeline.extractors.base import ReceiptExtractor
from expense_pipeline.models import ExpenseReport, ExtractionResult, Receipt
from expense_pipeline.policy import Policy


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
    store: list[Receipt],
    transcript: list[str],
    policy: Policy,
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
        store.append(result.receipt)
        receipts.append(result.receipt)

    return receipts, problems
