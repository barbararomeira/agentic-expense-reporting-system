"""Extractor selection. Mock is the default and the only backend in Phase A."""
from __future__ import annotations

from expense_pipeline.extractors.base import ReceiptExtractor
from expense_pipeline.extractors.mock import MockExtractor


def get_extractor(name: str = "mock") -> ReceiptExtractor:
    if name == "mock":
        return MockExtractor()
    raise ValueError(f"unknown extractor: {name!r}")
