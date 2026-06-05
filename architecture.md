# Full Architecture — After All Steps

This is the consolidated view of the expense-reporting system **after every change from Steps 2–5 is applied**. Step 1 captured the original system (`01-system-overview.md`); this diagram shows what it becomes once the bug fix, human review, privacy controls, and the new capability are all in place. (Step 6 adds no components — it analyses the cost behaviour of the ones shown here.)

```mermaid
graph TD
    Camera["Camera + Mobile UI"]
    Camera -->|"encrypted upload · Step 4"| A1["Agent 1<br/>Extraction"]
    RefDB[("Reference Image DB<br/>now consulted · Step 2")] --> A1
    A1 --> Conf{"Confidence<br/>high enough? · Step 2"}
    Conf -->|"no — re-capture"| Camera
    Conf -->|"yes · minimal fields,<br/>no full card number · Step 4"| SS[("Spreadsheet<br/>encrypted · EU · retention · Step 4")]
    SS --> A2["Agent 2<br/>Compute · Policy · VAT"]
    HR[("HR Database<br/>minimal read: role + status · Step 4")] --> A2
    A2 --> A3["Agent 3<br/>Decision"]
    A3 -->|"reject"| Rej["Rejection path<br/>notify + resubmit"]
    A3 -->|"approve"| Gate{"Approval tier? · Steps 3 + 5"}
    Gate -->|"&le; $500 (autonomous)"| Pay["Payment Service<br/>minimal encrypted payload · DPA · EU · Step 4"]
    Gate -->|"&gt; $500"| One["One Approver · Step 3"]
    Gate -->|"high-risk: &gt; $5 000,<br/>reporting-line conflict,<br/>or category · Step 5"| Two{{"Two Approvers<br/>two departments"}}
    HR -.->|"select 2 approvers in 2 depts · Step 5"| Two
    One -->|"approve"| Pay
    One -->|"reject"| Rej
    Two -->|"both approve"| Pay
    Two -->|"any reject (unanimous-blocks)"| Rej
    Pay --> Notify["Notify employee<br/>via Mobile UI"]
    Rej --> Camera
    LLM["Third-party LLM<br/>no-training clause in DPA · Step 4"]
    LLM -.-> A1
    LLM -.-> A2
    LLM -.-> A3

    classDef s2 fill:#d4edda,stroke:#155724,color:#155724;
    classDef s3 fill:#e7f0fd,stroke:#1d4ed8,color:#1d4ed8;
    classDef s5 fill:#ede9fe,stroke:#6d28d9,color:#6d28d9;
    classDef s4 fill:#fef3c7,stroke:#92400e,color:#92400e;
    class RefDB,Conf s2;
    class One,Gate s3;
    class Two s5;
    class LLM s4;
```

## What each colour means

- 🟩 **Green — Step 2 (bug fix).** The **Reference Image DB** is now consulted, and a **confidence gate** blocks low-confidence extractions before they reach the spreadsheet (routing them back to re-capture instead).
- 🟦 **Blue — Step 3 (human review).** The **approval gate** and the **one-approver** path: any approved expense over $500 is held for a human before payment.
- 🟪 **Purple — Step 5 (new capability).** The **two-approver / two-department** path for high-risk expenses, with the HR database consulted to pick the approvers.
- 🟨 **Yellow — Step 4 (privacy).** Cross-cutting controls, shown as annotations on the components and edges they apply to: encrypted upload, minimal extraction (no full card number), the encrypted/EU/retention-bound spreadsheet, the minimal HR read, the minimal encrypted payment payload under a DPA, and the **third-party LLM** node (with its no-training clause).

## End-to-end flow

The employee photographs a receipt and submits it over an encrypted connection. Agent 1 extracts the data, grounded against the Reference Image DB; low-confidence reads are sent back for re-capture, and only minimal, high-confidence fields are written to the spreadsheet. Agent 2 reads the spreadsheet plus a minimal slice of the HR database, computes the total and VAT, and checks policy. Agent 3 decides. A rejection returns to the employee; an approval enters the **tiered approval gate** — paid automatically if low-value, held for one approver above $500, or routed to two approvers in two different departments if it is high-risk (large amount, a reporting-line conflict of interest, or a high-fraud-risk category). Payment goes out only on full approval (any rejection blocks it), with a minimal encrypted payload to a DPA-bound, EU-based payment service. Throughout, the agents call a third-party LLM that is contractually barred from training on the data.
