"""Deterministic mock extractor — the default, no API or network needed.

It reads a JSON "scanned receipt" fixture and returns structured fields. In
Phase A it handles clear receipts only (high confidence). Phase B adds the
`blurry` and `unreadable` behaviours that drive the bug-fix demo.
"""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from expense_pipeline.models import ExtractionResult, LineItem, Receipt

# .../implementation/src/expense_pipeline/extractors/mock.py -> parents[3] = implementation/
DEFAULT_FIXTURE_DIR = Path(__file__).resolve().parents[3] / "examples" / "fixtures"


class MockExtractor:
    name = "mock"

    def __init__(self, fixture_dir: Path | None = None) -> None:
        self.fixture_dir = Path(fixture_dir) if fixture_dir else DEFAULT_FIXTURE_DIR

    def extract(self, source: str) -> ExtractionResult:
        # parse_float=Decimal keeps money as Decimal end-to-end: JSON 210.00
        # becomes Decimal("210.00"), never the lossy float 210.0.
        data = json.loads((self.fixture_dir / f"{source}.json").read_text(), parse_float=Decimal)
        line_items = [
            LineItem(li["description"], Decimal(li["amount"])) for li in data["line_items"]
        ]
        receipt = Receipt(
            source=source,
            vendor=data["vendor"],
            date=data["date"],
            category=data["category"],
            line_items=line_items,
            stated_total=Decimal(data["stated_total"]),
        )
        # Phase A: clear receipts only -> high confidence.
        return ExtractionResult(source=source, receipt=receipt, confidence=0.97)
