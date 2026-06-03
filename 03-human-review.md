# Step 3: Add Human Review

> **STATUS: just started.** Step 2 is fully closed (committed, pushed, mirrored into the Google Doc). The first question for Step 3 has been posed but not yet answered — see *Work in progress* at the bottom of this file before continuing.

## Submission

### Location

_Where in the system should the human be consulted?_

### Decision

_List the possible decisions the human could make._

### Data

_What data will the human need to make the decision, and where will they get it?_

## Reasoning

_What was considered, what was ruled out, and why this answer was chosen._

## Diagram

_Diagram showing the human-review insertion point goes here._

---

## Work in progress — pick up here

### Context anchored from Step 1

We already documented in `01-system-overview.md` that the system sits at the *fully autonomous* end of the spectrum, and that the playbook flagged this as unusual. We explicitly said:

> *This is the gap Step 3 is going to close (human review for any expense over $500).*

So the *why* of Step 3 is settled. What's open is the *where*, *what*, and *with what data*.

### The first question to answer

Current flow: **receipt → Agent 1 → spreadsheet → Agent 2 → Agent 3 → payment service**.

If a human needs to weigh in on expenses over $500, *where in that chain do they need to sit, and why there and not somewhere else?*

The answer will pin down the **Location** field of the Submission. Once that lands, the next two questions are:

- **Decision** — what set of choices does the human have at that point? (approve / reject is the obvious starting pair — but is that the full set?)
- **Data** — what information does the human need to make the choice, and which existing component(s) already hold that information?

### Playbook lenses likely to apply

- **Phase 3 — Guardrails:** specifically the *behavioural* / *escalation* guardrails (rules about when an action is allowed to proceed autonomously vs. when it must be escalated).
- **Progressive authorization ladder** (read → draft → supervised → autonomous): Step 3 is essentially pulling Agent 3's decision back from *autonomous* to *supervised* — but only above a threshold. Worth noting in the Reasoning section.

### When picking back up

Resume by re-asking the *Location* question above. Once Barbara names the insertion point and why, move to Decision, then Data, then write up the Submission and the diagram. Then mirror the answer into the Google Doc and capture Step 3 findings in `playbook-evaluation.md` (Phase 3 fit, autonomy-spectrum follow-through from Step 1).
