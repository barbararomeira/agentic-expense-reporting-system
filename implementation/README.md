# Implementation — runnable expense pipeline

A working version of the system designed in the step docs above. Built
incrementally; each phase is runnable on its own. Receipt extraction runs on a
**deterministic mock** by default — no API key, no network — so the whole
pipeline and every test are reproducible.

## Run it

```bash
python3 -m venv .venv
./.venv/bin/pip install -e ".[dev]"

# auto-approved (under $500)
./.venv/bin/python -m expense_pipeline run examples/reports/small_trip.json

# the Step 2 bug: blocked by the validation gate, then reproduced
./.venv/bin/python -m expense_pipeline run examples/reports/unreadable_receipt.json
./.venv/bin/python -m expense_pipeline run examples/reports/unreadable_receipt.json --no-validation

# human review (> $500) and two-person approval (amount / category / conflict)
./.venv/bin/python -m expense_pipeline run examples/reports/large_trip.json
./.venv/bin/python -m expense_pipeline run examples/reports/huge_trip.json
./.venv/bin/python -m expense_pipeline run examples/reports/gift_highrisk.json
./.venv/bin/python -m expense_pipeline run examples/reports/conflict_report.json

# EU data residency
./.venv/bin/python -m expense_pipeline run examples/reports/eu_resident.json --region US   # BLOCKED
./.venv/bin/python -m expense_pipeline run examples/reports/eu_resident.json --region EU   # proceeds

# operational cost drivers
./.venv/bin/python -m expense_pipeline cost

# tests
./.venv/bin/python -m pytest
```

## How it's organised

| Path | Role |
|---|---|
| `src/expense_pipeline/models.py` | The data shapes (Receipt, Decision, …). Money is always `Decimal`. |
| `src/expense_pipeline/extractors/` | Receipt reader behind an interface; `MockExtractor` is the default. |
| `src/expense_pipeline/agents/` | Agent 1 (extract), Agent 2 (policy/totals), Agent 3 (decide). |
| `src/expense_pipeline/orchestrator.py` | Wires the agents together; owns the data store + transcript. |
| `examples/` | Policy, org directory, sample reports and receipt fixtures. |
| `tests/` | One test file per capability, all mock-only. |

**Design rule:** only Agent 1's extraction is model-shaped. Agent 2's policy
checks and all approval gates are deterministic Python — a financial decision
must be reproducible, never an LLM guess.

## Build phases

- ✅ **A** — end-to-end slice: one report → 3 agents → decision + mock payment.
- ✅ **B** — validation gate (Step 2 bug fix): refuse low-confidence / non-reconciling extractions.
- ✅ **C** — human review (Step 3): one approver for approved expenses over $500.
- ✅ **D** — two-person approval (Step 5): two departments when amount > $5000, a reporting-line conflict, or a high-risk category; unanimous-blocks.
- ✅ **E** — privacy (Step 4): EU data residency, minimisation, card last-4 only, pseudonymised payee.
- ✅ **F** — cost-driver report (Step 6).
- ⬜ **G** (optional) — real receipt extraction via the `claude` CLI (Max subscription, no API key). Mock stays the default; tests remain offline.
