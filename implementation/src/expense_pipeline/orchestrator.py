"""The orchestrator wires the three agents together into one pipeline run.

This is the 'conductor': it owns the data store and the transcript, and passes
the output of each agent to the next. Keeping the wiring here (and out of the
agents) is what lets us add gates between agents in later phases without
rewriting the agents themselves.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from expense_pipeline.agents.agent1_extract import run_agent1
from expense_pipeline.agents.agent2_policy import run_agent2
from expense_pipeline.agents.agent3_decision import run_agent3
from expense_pipeline.extractors import get_extractor
from expense_pipeline.extractors.base import ReceiptExtractor
from expense_pipeline.models import Decision, DecisionStatus, ExpenseReport, Receipt
from expense_pipeline.payment import PaymentService
from expense_pipeline.policy import Policy


@dataclass
class PipelineResult:
    report_id: str
    decision: Decision
    transcript: list[str]


@dataclass
class Pipeline:
    policy: Policy
    extractor: ReceiptExtractor
    payment: PaymentService

    @classmethod
    def default(cls, policy_path: str | Path) -> "Pipeline":
        return cls(
            policy=Policy.load(policy_path),
            extractor=get_extractor(),
            payment=PaymentService(),
        )

    def run_report(self, report: ExpenseReport, validate: bool = True) -> PipelineResult:
        transcript: list[str] = []
        store: list[Receipt] = []   # the 'spreadsheet' — receipts saved this run

        receipts, problems = run_agent1(
            report, self.extractor, store, transcript, self.policy, validate=validate
        )

        # Step 2 fix: if any extraction failed the gate, stop here. Nothing was
        # saved, so nothing downstream can act on fabricated data.
        if problems:
            transcript.append(
                "pipeline: extraction failed validation -> NEEDS_MORE_INFO (employee asked to resubmit)"
            )
            decision = Decision(
                report_id=report.report_id,
                status=DecisionStatus.NEEDS_MORE_INFO,
                amount=Decimal("0"),
                reason="; ".join(problems),
            )
            return PipelineResult(report_id=report.report_id, decision=decision, transcript=transcript)

        analysis = run_agent2(receipts, self.policy, transcript)
        decision = run_agent3(report, analysis, self.payment, transcript)

        return PipelineResult(report_id=report.report_id, decision=decision, transcript=transcript)


def load_report(path: str | Path) -> ExpenseReport:
    data = json.loads(Path(path).read_text())
    return ExpenseReport(
        report_id=data["report_id"],
        employee_id=data["employee_id"],
        purpose=data.get("purpose", ""),
        receipt_sources=data["receipts"],
    )
