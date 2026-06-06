"""The org directory, loaded from examples/org.json.

Tells the system who an employee is and who approves for a given department.
Phase C uses `employee()` and `approver_for_department()`; Phase D adds the
reporting-line lookup for the conflict-of-interest check.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from expense_pipeline.models import Employee


@dataclass(frozen=True)
class Approver:
    id: str
    name: str
    department: str


@dataclass
class OrgDirectory:
    employees: dict[str, Employee]
    approvers: dict[str, Approver]   # keyed by department

    @classmethod
    def load(cls, path: str | Path) -> "OrgDirectory":
        data = json.loads(Path(path).read_text())
        employees = {
            eid: Employee(
                id=eid,
                name=e["name"],
                role=e["role"],
                department=e["department"],
                region=e.get("region", "US"),
                manager_id=e.get("manager_id"),
            )
            for eid, e in data.get("employees", {}).items()
        }
        approvers = {
            dept: Approver(id=a["id"], name=a["name"], department=a["department"])
            for dept, a in data.get("approvers", {}).items()
        }
        return cls(employees=employees, approvers=approvers)

    def employee(self, employee_id: str) -> Employee | None:
        return self.employees.get(employee_id)

    def approver_for_department(self, department: str) -> Approver | None:
        return self.approvers.get(department)
