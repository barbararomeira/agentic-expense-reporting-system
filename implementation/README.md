# Implementation — runnable expense pipeline

A working version of the system designed in the step docs above. Built
incrementally; each phase is runnable on its own. Receipt extraction runs on a
**deterministic mock** by default — no API key, no network — so the whole
pipeline and every test are reproducible.

## Run it

```bash
python3 -m venv .venv
./.venv/bin/pip install -e ".[dev]"

# run one expense report through the three agents
./.venv/bin/python -m expense_pipeline run examples/reports/small_trip.json

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

- **A — end-to-end slice** (done): one report → 3 agents → decision + mock payment.
- B — validation gate (the bug fix) · C — human review (>$500) · D — two-person
  approval · E — privacy / EU residency · F — cost report · G (optional) — real
  `claude`-CLI extraction.
