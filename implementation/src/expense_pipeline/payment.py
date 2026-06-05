"""A mock payment service. Records reimbursements and hands back a reference;
no real money moves. Stands in for the third-party payment provider."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class PaymentService:
    _counter: int = 0
    payments: list[dict] = field(default_factory=list)

    def reimburse(self, payee: str, amount: Decimal) -> str:
        self._counter += 1
        ref = f"pay-{self._counter:04d}"
        self.payments.append({"ref": ref, "payee": payee, "amount": amount})
        return ref
