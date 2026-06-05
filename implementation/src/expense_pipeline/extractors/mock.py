"""Deterministic mock extractor — the default, no API or network needed.

It reads a JSON "scanned receipt" fixture (the ground truth) and returns what a
vision model *would* return at the fixture's `image_quality`:

* clear      -> accurate fields, high confidence (0.97)
* blurry     -> accurate fields, low confidence (0.55)  ... honest uncertainty
* unreadable -> HALLUCINATED inflated total + a line item that doesn't
                reconcile, low confidence (0.38)        ... the Step 2 bug

The unreadable case is the whole point of Phase B: a naive Agent 1 would save
that fabricated total and overpay; the validation gate refuses to.
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
        quality = data.get("image_quality", "clear")
        line_items = [LineItem(li["description"], Decimal(li["amount"])) for li in data["line_items"]]
        stated_total = Decimal(data["stated_total"])

        if quality == "clear":
            receipt = Receipt(source, data["vendor"], data["date"], data["category"], line_items, stated_total)
            return ExtractionResult(source, receipt, confidence=0.97)

        if quality == "blurry":
            # Fields are still right, but the model is honestly unsure.
            receipt = Receipt(source, data["vendor"], data["date"], data["category"], line_items, stated_total)
            return ExtractionResult(source, receipt, confidence=0.55, notes=["image is blurry; values uncertain"])

        # unreadable: the model invents an inflated total (x1.9) and a single
        # vague line item that does NOT reconcile with it. Low confidence.
        inflated = (stated_total * Decimal("1.9")).quantize(Decimal("0.01"))
        receipt = Receipt(
            source,
            data.get("vendor", "Unknown"),
            data["date"],
            data["category"],
            [LineItem("Unitemized (image too unclear to read)", stated_total)],
            stated_total=inflated,
        )
        return ExtractionResult(source, receipt, confidence=0.38, notes=["image unreadable; values may be fabricated"])
