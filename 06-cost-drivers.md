# Step 6: Estimate Operational Cost Drivers

## Submission

Mark each component with an "x" in the appropriate cost category.

| Component | Flat and low, regardless of volume | Flat and high, regardless of volume | Highly variable, depending on volume |
|---|:---:|:---:|:---:|
| Database | x | | |
| Spreadsheet | x | | |
| Mobile Web and Camera | x | | |
| Agent 1 | | | x |
| Agent 2 | | | x |
| Agent 3 | | | x |
| Private infrastructure | | x | |
| Payment service | | | x |

## Reasoning

The sorting question for every row: *if the company goes from 100 expense reports a month to 100 000, does this component's cost rise roughly in proportion, or stay about the same?* If it rises with volume it is **highly variable**; if it stays flat, the only remaining question is whether that fixed amount is **low** or **high**.

### Highly variable — the per-expense costs

- **Agent 1, Agent 2, Agent 3.** Each agent makes **LLM calls per expense**, billed per token. Processing 1 000× the receipts means ~1 000× the calls, so cost rises directly with volume. Of the three, **Agent 2 is the cost hot-spot**: it is the agent with the *Remember* capability (see Step 1), holding many receipts in context to compute totals and run policy checks, so it carries the largest token footprint per run.
- **Payment service.** Charged a fee **per transaction**, so the cost scales one-for-one with the number of reimbursements paid.

### Flat and low — fixed and cheap

- **Spreadsheet.** Cheap cloud storage with no per-transaction fee; it costs about the same whether it holds 100 rows or 100 000.
- **Database.** You pay for the provisioned instance, not per query, and the read-only HR store is modest. It is placed *low* (rather than *high*) deliberately, to distinguish it from private infrastructure, which is the system's large fixed cost.
- **Mobile Web and Camera.** The camera runs on the **user's own phone**, so it costs the company nothing at the margin; the web frontend is a small, fixed hosting cost.

### Flat and high — fixed and expensive

- **Private infrastructure.** Capacity (servers/hosting) is provisioned **up front regardless of volume**, so the cost is flat rather than variable — but dedicated/private infrastructure is a large ongoing expense, so it is high. Its magnitude is exactly what separates it from the Database row, which is also flat but small.

### Takeaway

As the business scales, the cost that actually grows is concentrated in two places: the **agents' token usage** and the **payment fees**. Everything else is fixed. So cost control at scale means optimising the agents — model choice, smaller context windows, caching — rather than the infrastructure. That is the core economic lesson of an agentic system: the intelligence is the variable cost.
