"""The extractor interface.

The pipeline depends only on this Protocol, so the extraction engine is
pluggable: a deterministic mock by default (zero setup, runs anywhere), and —
later, optionally — a real backend that calls the `claude` CLI. Swapping one
for the other never touches the agents or the decision logic.
"""
from __future__ import annotations

from typing import Protocol

from expense_pipeline.models import ExtractionResult


class ReceiptExtractor(Protocol):
    name: str

    def extract(self, source: str) -> ExtractionResult:
        """Read one receipt reference and return structured fields + confidence."""
        ...
