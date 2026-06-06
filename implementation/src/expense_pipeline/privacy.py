"""Privacy controls (Step 4) — data minimisation, redaction, pseudonymisation,
and EU data residency.

These are deterministic utilities, not model calls. They make the four GDPR
principles from the write-up concrete: keep less, mask what's sensitive, never
log a real name, and don't let EU data leave the EU.
"""
from __future__ import annotations

import re

from expense_pipeline.models import Employee, Receipt


class DataResidencyError(Exception):
    """Raised when EU personal data would be written to a non-EU store."""


class RegionalDataStore:
    """The 'spreadsheet', but region-aware. Writing an EU employee's data to a
    store hosted outside the EU is refused (Step 4 residency requirement)."""

    def __init__(self, region: str = "US") -> None:
        self.region = region
        self.rows: list[dict] = []

    def write(self, row: dict, employee: Employee | None) -> None:
        if employee and employee.region == "EU" and self.region != "EU":
            raise DataResidencyError(
                f"refusing to write EU employee {employee.id}'s data to a {self.region} store"
            )
        self.rows.append(row)


_CARD_LIKE = re.compile(r"\b\d[\d \-]{10,}\d\b")


def redact_text(text: str) -> str:
    """Mask card-like digit sequences in free text, keeping only the last 4."""
    def _mask(match: re.Match) -> str:
        digits = re.sub(r"\D", "", match.group())
        return "****" + digits[-4:]

    return _CARD_LIKE.sub(_mask, text)


def pseudonymize(employee: Employee | None, fallback: str = "unknown") -> str:
    """A stable, non-identifying handle for logs and payment — never the name."""
    return f"employee:{employee.id}" if employee else f"employee:{fallback}"


def minimize_receipt(receipt: Receipt) -> dict:
    """The row we actually persist: only what's needed, no line-item detail,
    and only the last 4 card digits (never the full number)."""
    return {
        "source": receipt.source,
        "vendor": receipt.vendor,
        "date": receipt.date,
        "category": receipt.category,
        "stated_total": str(receipt.stated_total),
        "card_last4": receipt.card_last4,
    }
