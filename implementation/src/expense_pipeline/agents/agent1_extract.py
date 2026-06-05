"""Agent 1 — extraction.

Reads each receipt via the pluggable extractor and saves it to the store.
Phase A has no validation gate: every extraction is trusted and saved. Phase B
inserts the gate here (the bug fix) so low-confidence / non-reconciling
extractions are refused before they reach the store.
"""
from __future__ import annotations

from expense_pipeline.extractors.base import ReceiptExtractor
from expense_pipeline.models import ExpenseReport, Receipt


def run_agent1(
    report: ExpenseReport,
    extractor: ReceiptExtractor,
    store: list[Receipt],
    transcript: list[str],
) -> list[Receipt]:
    receipts: list[Receipt] = []
    for source in report.receipt_sources:
        result = extractor.extract(source)
        transcript.append(
            f"agent1: extracted '{source}' "
            f"({result.receipt.vendor}, {result.receipt.stated_total}) "
            f"confidence={result.confidence:.2f}"
        )
        store.append(result.receipt)   # Phase A: saved unconditionally
        receipts.append(result.receipt)
    return receipts
