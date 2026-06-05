"""Company expense policy, loaded from examples/policy.json.

Phase A uses only `currency` and `allowed_categories`. The other fields are
read by later phases (thresholds in C/D); they live in the JSON now so we don't
keep editing the file.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path


@dataclass
class Policy:
    currency: str
    allowed_categories: list[str]
    human_review_threshold: Decimal = Decimal("500")     # Phase C
    dual_dept_threshold: Decimal = Decimal("5000")        # Phase D
    high_risk_categories: list[str] = field(default_factory=list)  # Phase D
    extraction_confidence_threshold: float = 0.75         # Phase B
    per_category_caps: dict[str, Decimal] = field(default_factory=dict)  # Phase B/C

    @classmethod
    def load(cls, path: str | Path) -> "Policy":
        data = json.loads(Path(path).read_text(), parse_float=Decimal)
        caps = {k: Decimal(v) for k, v in data.get("per_category_caps", {}).items()}
        return cls(
            currency=data.get("currency", "USD"),
            allowed_categories=data.get("allowed_categories", []),
            human_review_threshold=Decimal(str(data.get("human_review_threshold", 500))),
            dual_dept_threshold=Decimal(str(data.get("dual_dept_threshold", 5000))),
            high_risk_categories=data.get("high_risk_categories", []),
            extraction_confidence_threshold=float(data.get("extraction_confidence_threshold", 0.75)),
            per_category_caps=caps,
        )
