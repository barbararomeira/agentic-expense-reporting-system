"""Phase F: the cost-driver report matches the Step 6 design."""
from expense_pipeline.cost import COST_DRIVERS, FLAT_HIGH, FLAT_LOW, VARIABLE, render_table


def test_all_eight_components_present():
    assert len(COST_DRIVERS) == 8
    names = {d.component for d in COST_DRIVERS}
    for expected in [
        "Database", "Spreadsheet", "Mobile Web and Camera",
        "Agent 1", "Agent 2", "Agent 3", "Private infrastructure", "Payment service",
    ]:
        assert expected in names


def test_categories_match_the_design():
    cat = {d.component: d.category for d in COST_DRIVERS}
    assert cat["Agent 1"] == VARIABLE
    assert cat["Agent 2"] == VARIABLE
    assert cat["Agent 3"] == VARIABLE
    assert cat["Payment service"] == VARIABLE
    assert cat["Private infrastructure"] == FLAT_HIGH
    assert cat["Database"] == FLAT_LOW
    assert cat["Spreadsheet"] == FLAT_LOW
    assert cat["Mobile Web and Camera"] == FLAT_LOW


def test_render_table_lists_every_component():
    table = render_table()
    assert table.strip()
    for d in COST_DRIVERS:
        assert d.component in table
