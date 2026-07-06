import csv
from datetime import date
from pathlib import Path

try:
    from .rules import allocation_total, is_allocation_valid, is_overdue, risk_level
except ImportError:
    from rules import allocation_total, is_allocation_valid, is_overdue, risk_level


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OVERDUE_DAYS_THRESHOLD = 15


def _read_csv(name):
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _parse_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _parse_date(value):
    return date.fromisoformat(str(value).strip())


def get_application(apply_no: str) -> dict | None:
    """Read one application from synthetic CSV."""
    for row in _read_csv("applications.csv"):
        if row["ApplyNo"] == apply_no:
            return row
    return None

def check_allocation(apply_no: str) -> dict:
    """Check if allocation total equals 100%."""
    rows = [row for row in _read_csv("allocations.csv") if row["ApplyNo"] == apply_no]
    if not rows:
        return {
            "finding": "allocation_missing",
            "valid": False,
            "total": 0,
            "evidence": "No allocation rows found in data/allocations.csv.",
        }

    total = allocation_total(rows)
    valid = is_allocation_valid(rows)
    return {
        "finding": None if valid else "allocation_total_not_100",
        "valid": valid,
        "total": total,
        "evidence": f"Allocation total is {total:g}% in data/allocations.csv.",
    }

def check_budget_risk(apply_no: str) -> dict:
    """Check budget threshold and overrun risk."""
    allocations = [row for row in _read_csv("allocations.csv") if row["ApplyNo"] == apply_no]
    budgets = {row["EmsNo"]: row for row in _read_csv("budgets.csv")}
    overrun_ems = []

    for allocation in allocations:
        budget = budgets.get(allocation["EmsNo"])
        if not budget:
            overrun_ems.append(f"{allocation['EmsNo']} missing budget")
            continue
        if float(budget["UsedAmount"]) > float(budget["BudgetLimit"]):
            overrun_ems.append(allocation["EmsNo"])

    return {
        "finding": "budget_overrun" if overrun_ems else None,
        "valid": not overrun_ems,
        "evidence": "Budget limits checked in data/budgets.csv.",
        "overrun_ems": overrun_ems,
    }

def check_receipt_status(apply_no: str) -> dict:
    """Check overdue receipt and penalty status."""
    rows = [row for row in _read_csv("receipts.csv") if row["ApplyNo"] == apply_no]
    overdue_rows = []
    penalty_rows = []

    for row in rows:
        due_date = _parse_date(row["DueDate"])
        recv_date = _parse_date(row["RecvDate"])
        if is_overdue(due_date, recv_date, OVERDUE_DAYS_THRESHOLD):
            overdue_rows.append(row["IssueNo"])
        if _parse_bool(row["IsPenalty"]):
            penalty_rows.append(row["IssueNo"])

    return {
        "finding": "overdue_receipt" if overdue_rows else None,
        "valid": not overdue_rows,
        "evidence": "Receipt due dates checked in data/receipts.csv.",
        "overdue_issues": overdue_rows,
        "penalty_issues": penalty_rows,
    }

def summarize_financial_status(apply_no: str) -> dict:
    """Summarize voucher/payment risk."""
    rows = [row for row in _read_csv("vouchers.csv") if row["ApplyNo"] == apply_no]
    if not rows:
        return {
            "finding": None,
            "valid": True,
            "evidence": "No voucher rows found in data/vouchers.csv.",
            "summary": "No voucher has been created.",
        }

    summaries = [f"{row['VoucherStatus']} amount={row['PayAmount']}" for row in rows]
    return {
        "finding": None,
        "valid": True,
        "evidence": "Voucher status checked in data/vouchers.csv.",
        "summary": "; ".join(summaries),
    }


def review_application(apply_no: str) -> dict:
    application = get_application(apply_no)
    if application is None:
        findings = ["application_not_found"]
        return {
            "apply_no": apply_no,
            "risk_level": risk_level(findings),
            "blocked": True,
            "findings": findings,
            "evidence": ["No matching row found in data/applications.csv."],
            "recommended_next_action": "Check the ApplyNo or add a synthetic application row.",
            "safety_note": "Read-only review only; no ERP records are modified.",
        }

    checks = [
        check_allocation(apply_no),
        check_budget_risk(apply_no),
        check_receipt_status(apply_no),
        summarize_financial_status(apply_no),
    ]
    findings = [check["finding"] for check in checks if check["finding"]]
    evidence = [check["evidence"] for check in checks]
    level = risk_level(findings)

    return {
        "apply_no": apply_no,
        "project_name": application["ProjectName"],
        "risk_level": level,
        "blocked": level == "high",
        "findings": findings,
        "evidence": evidence,
        "recommended_next_action": _next_action(findings),
        "safety_note": "Read-only review only; no ERP records are modified.",
    }


def _next_action(findings):
    if "application_not_found" in findings:
        return "Verify the ApplyNo before review."
    if "allocation_total_not_100" in findings:
        return "Fix allocation rows so ShareRate totals 100% before submission."
    if "overdue_receipt" in findings:
        return "Follow up with the vendor or reviewer for overdue receipt status."
    if "budget_overrun" in findings:
        return "Review budget usage before continuing."
    return "Application can proceed to human review."
