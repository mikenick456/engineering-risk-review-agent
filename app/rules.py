from datetime import date


def is_project(budget, currency, ems_kind, thresholds, project_kinds):
    currency_key = currency.strip()
    return budget > thresholds.get(currency_key, thresholds.get("NTD")) or ems_kind in project_kinds

def allocation_total(rows):
    return sum(float(row["ShareRate"]) for row in rows)

def is_allocation_valid(rows):
    return allocation_total(rows) == 100

def is_overdue(due_date, recv_date, threshold_days):
    if not isinstance(due_date, date) or not isinstance(recv_date, date):
        raise TypeError("due_date and recv_date must be date values")
    return (recv_date - due_date).days > threshold_days


def risk_level(findings):
    high_risk_findings = {
        "application_not_found",
        "allocation_total_not_100",
        "budget_overrun",
    }
    if any(finding in high_risk_findings for finding in findings):
        return "high"
    if findings:
        return "medium"
    return "low"
