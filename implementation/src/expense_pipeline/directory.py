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

    def is_conflict(self, employee: Employee, approver: Approver) -> bool:
        """True if the employee reports directly to this approver — a
        conflict of interest (the approver manages the submitter)."""
        return employee.manager_id is not None and employee.manager_id == approver.id

    def select_dual_approvers(self, employee: Employee, primary_dept: str) -> list[Approver]:
        """Pick up to two approvers from two *different* departments, skipping
        any approver who is in a conflict of interest with the submitter.
        Prefers the submitter's own-department approver as the first seat."""
        chosen: list[Approver] = []
        used_depts: set[str] = set()

        primary = self.approvers.get(primary_dept)
        if primary and not self.is_conflict(employee, primary):
            chosen.append(primary)
            used_depts.add(primary.department)

        for approver in self.approvers.values():
            if len(chosen) >= 2:
                break
            if self.is_conflict(employee, approver) or approver.department in used_depts:
                continue
            chosen.append(approver)
            used_depts.add(approver.department)

        return chosen
