# Playbook Evaluation

Throughout this project, an internal agentic AI playbook was used as the working reference. This file tracks the meta-learning: which sections of the playbook were applied at each step, where the playbook gave clean guidance, and where it left gaps that suggest improvements for a future version.

The project is a brownfield exercise (extending an existing agentic system), so only a subset of the playbook's phases are exercised here. Findings are scoped to that subset.

## Sections exercised in this project

| Playbook section | Project step(s) where applied |
|---|---|
| Foundations — four capabilities, agent roles | Step 1 |
| Design — guardrails, progressive authorization | Steps 2, 3 |
| Cost — token economics, linear scaling | Step 6 |
| Govern — silent failure, control toolkit | Steps 2, 3, 4 |
| Agent Definition Worksheet | Step 5 |

## Findings

_Filled in as we work through each step._

### What the playbook covered cleanly

- **Step 1 — Foundations (four capabilities + autonomy spectrum).** The Perceive / Reason / Act / Remember frame held up under pressure for each agent. The autonomy-spectrum heuristic ("middle of the spectrum is usually the right answer") immediately flagged Agent 3's fully-autonomous reimbursement as unusual — which is exactly the gap Step 3 will close.
- **Step 2 — Phase 3 Guardrails (output filtering).** The confidence-score gate before the spreadsheet write is a textbook output-filter guardrail. The playbook's framing of "block low-confidence outputs at the boundary, not after" matched the chosen fix one-to-one.
- **Step 2 — Phase 6 Govern (silent failure / cascade).** Naming the pattern up front made it easy to see why catching the bug at Agent 3's decision (or at reimbursement) would be too late — the cascade was already corrupting Agent 2's summary by then.
- **Step 3 — Phase 3 Guardrails (behavioural / escalation) + progressive authorization ladder.** The over-$500 human-review gate is the direct follow-through on the autonomy-spectrum gap flagged in Step 1: it pulls Agent 3's reimbursement decision back from *autonomous* to *supervised*, but only above the threshold, so low-value expenses keep their autonomy. The ladder (read → draft → supervised → autonomous) gave a clean vocabulary for "supervise only the high-value, irreversible slice." The playbook's "place the gate before the irreversible action" guidance also mapped one-to-one onto the after-Agent-3 / before-payment placement.
- **Step 4 — Phase 6 Govern (control toolkit) + least privilege, applied to privacy.** The governance toolkit (minimisation, purpose limitation, retention, access control) transferred cleanly from correctness to data privacy. Least privilege carried the HR-database fix (read only role + status) and the access restrictions throughout. The single highest-leverage control was *minimisation*, which recurred at four of the five surfaces (send / store / log / read less) — the playbook's framing of "the safest data is data you never hold" matched every one.
- **Step 5 — Agent Definition Worksheet + reuse of an existing guardrail.** Scoping the chosen capability (two-person approval) leaned on the four-capabilities frame to estimate effort — *effort ≈ how much of the agent architecture must change*. The strongest move was **reuse**: rather than invent a new control, the feature extends the Step 3 human-gate (autonomous → one approver → two approvers) and reuses the existing rejection path, so the new build is just the tiered criteria and the approval routing. The "unanimous-blocks" rule then collapsed the conflict case entirely — the safest rule was also the one with the fewest new branches.
- **Step 6 — Cost (token economics / linear scaling).** The single diagnostic — *does this component's cost scale with volume?* — cleanly sorted every component, and the playbook's "agents scale linearly with usage" framing was exactly right: the three agents and the per-transaction payment fee are the only volume-driven costs, everything else is fixed. The Step 1 capability matrix paid off here — the *Remember*-heavy agent (Agent 2) was identifiable as the per-run cost hot-spot from its capability profile alone.

### Where the playbook left gaps

- **Step 2 — Self-grading confidence is treated as a guardrail without warning that it can be circular.** Phase 3 introduces "confidence scoring" as an output filter, but doesn't flag that asking the same model "how sure are you?" is the LLM grading its own homework — and a hallucination is, by definition, confident wrongness. The fix in this project only became trustworthy once Agent 1's confidence was grounded against the Reference Image Database (a separate, known-good corpus). Without that grounding, the guardrail is theatre.
- **Step 2 — Brownfield clue: "what's already in the architecture but unused?"** The Reference Image DB was sitting in the system overview the whole time. The playbook does not prompt the reader to scan an existing architecture for unused components before proposing a fix — but in a brownfield context, the unused component is often there *because* it is meant to be activated for exactly this kind of problem. This question (*"is the answer already in the architecture?"*) was load-bearing for Step 2 and isn't in the playbook.
- **Step 3 — Escalation is listed as a guardrail option without noting it needs a defined recipient.** The playbook offers "escalate to a human/team" as an escalation-guardrail move, but doesn't flag that escalation only exists if the system *defines a distinct higher authority* to escalate to. In this system there is none — so escalation collapses into reject, and the option had to be deliberately deferred. The missing prompt: *before adding an escalation path, name who it routes to and why they are the right authority; if you can't, it isn't an escalation, it's a rejection.*
- **Step 4 — No lens for *finding* the exposure surfaces, and no flag for the AI-specific erasure trap.** Two gaps surfaced. (1) The playbook lists privacy controls but doesn't give a method for *locating* where personal data is exposed; the data-lifecycle lens (captured → transmitted → processed → stored → shared) was what made the five surfaces findable rather than guessed, and it isn't in the playbook. (2) It treats third-party processors uniformly, but an **LLM processor is different**: training on the data is irreversible and silently defeats the right to erasure. A payment processor can delete on request; a model that trained on the data cannot un-learn it. The playbook should flag that LLM processors need an explicit *no-training* clause, because this is the one privacy failure with no technical undo.
- **Step 5 — The worksheet defines *new* agents but doesn't separate an architectural change from a logic/config change.** The Agent Definition Worksheet helps when you are adding a *new* agent, but the more common brownfield case is *extending* what exists — and there the load-bearing distinction is whether a feature changes the **workflow shape** (a new agent, step, gate, or loop) or just the **logic/inputs inside an existing box**. The group-expense candidate looked like a big change but is the latter (same flow, richer Agent 2 logic); two-person approval is the former. The playbook offers no test for telling these apart, yet it drives both the effort estimate and how much of the architecture a feature actually exercises.

### Suggested additions for a future version

- **Add to Phase 3 — Guardrails:** a "circular confidence" warning. When the same model both produces output and assesses its own confidence in that output, the score is not a guardrail. Real output filtering needs an *independent* signal — a separate model, a rules check, or grounding against a known-good corpus. Worked example: receipt-extraction hallucination caught only when confidence is measured as similarity to a reference-image database, not as the LLM's self-rating.
- **Add as a new short section (or to Phase 0):** *Brownfield audit — read the architecture before reaching for the playbook.* Before applying any phase to a brownfield problem, scan the existing system for components that are documented but unused, capabilities that exist but aren't wired up, or data stores nothing currently reads from. These are usually load-bearing for the next step.
