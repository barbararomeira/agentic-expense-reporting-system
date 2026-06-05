"""Shared pytest fixtures. Everything here is mock-only and offline."""
from pathlib import Path

import pytest

from expense_pipeline.orchestrator import Pipeline, load_report

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


@pytest.fixture
def pipeline():
    return Pipeline.default(EXAMPLES / "policy.json")


@pytest.fixture
def report():
    def _load(name: str):
        return load_report(EXAMPLES / "reports" / f"{name}.json")

    return _load
