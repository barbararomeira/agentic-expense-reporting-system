"""Phase E: privacy controls — residency, minimisation, redaction, pseudonymity."""
from decimal import Decimal

from expense_pipeline.models import DecisionStatus, Employee, LineItem, Receipt
from expense_pipeline.privacy import minimize_receipt, pseudonymize, redact_text


def test_eu_employee_blocked_from_us_store(make_pipeline, report):
    result = make_pipeline(store_region="US").run_report(report("eu_resident"))
    assert result.decision.status == DecisionStatus.BLOCKED
    assert result.decision.paid is False


def test_eu_employee_allowed_in_eu_store(make_pipeline, report):
    result = make_pipeline(store_region="EU").run_report(report("eu_resident"))
    assert result.decision.status == DecisionStatus.APPROVED
    assert result.decision.paid is True


def test_payment_uses_a_pseudonym_not_the_name(make_pipeline, report):
    pipe = make_pipeline(store_region="EU")
    pipe.run_report(report("eu_resident"))
    assert pipe.payment.payments[0]["payee"] == "employee:emp-200"


def test_redact_masks_card_numbers():
    assert redact_text("paid with 4111 1111 1111 1234 today") == "paid with ****1234 today"


def test_pseudonymize_never_leaks_the_name():
    e = Employee(id="emp-9", name="Jane Doe", role="Engineer", department="Eng")
    assert pseudonymize(e) == "employee:emp-9"
    assert "Jane" not in pseudonymize(e)


def test_persisted_row_drops_line_items_and_full_card():
    r = Receipt("s", "Vendor", "2026-01-01", "meals", [LineItem("x", Decimal("10"))],
                Decimal("10"), card_last4="1234")
    row = minimize_receipt(r)
    assert row["card_last4"] == "1234"
    assert "line_items" not in row
