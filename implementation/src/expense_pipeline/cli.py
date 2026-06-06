"""Command-line entry point.

    python -m expense_pipeline run examples/reports/small_trip.json

Phase A exposes one subcommand, `run`. Later phases add flags (`--no-validation`,
`--region`) and the `cost` subcommand.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from expense_pipeline.orchestrator import Pipeline, load_report

# .../implementation/src/expense_pipeline/cli.py -> parents[2] = implementation/
EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def cmd_run(args: argparse.Namespace) -> None:
    policy_path = args.policy or (EXAMPLES / "policy.json")
    pipeline = Pipeline.default(policy_path, store_region=args.region)
    report = load_report(args.report)
    result = pipeline.run_report(report, validate=not args.no_validation)

    print(f"Report {result.report_id}:")
    for line in result.transcript:
        print("  " + line)
    d = result.decision
    tail = f" | ref={d.payment_ref}" if d.payment_ref else ""
    print(f"-> {d.status.value} | amount={d.amount} | paid={d.paid}{tail}")


def cmd_cost(args: argparse.Namespace) -> None:
    from expense_pipeline.cost import render_table

    print(render_table())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="expense-pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run one expense report through the pipeline")
    p_run.add_argument("report", help="path to a report JSON file")
    p_run.add_argument("--policy", help="path to policy.json (default: examples/policy.json)")
    p_run.add_argument(
        "--no-validation",
        action="store_true",
        help="skip Agent 1's validation gate (reproduces the Step 2 bug)",
    )
    p_run.add_argument(
        "--region",
        default="US",
        choices=["US", "EU"],
        help="where the data store is hosted (default: US)",
    )
    p_run.set_defaults(func=cmd_run)

    p_cost = sub.add_parser("cost", help="show the operational cost-driver table")
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
