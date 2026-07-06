from google.adk.agents import Agent
from google.adk.tools import FunctionTool

try:
    from .tools import (
        check_allocation,
        check_budget_risk,
        check_receipt_status,
        get_application,
        summarize_financial_status,
    )
except ImportError:
    from tools import (
        check_allocation,
        check_budget_risk,
        check_receipt_status,
        get_application,
        summarize_financial_status,
    )


def _adk_safe(value):
    if value is None:
        return "none"
    if isinstance(value, dict):
        return {key: _adk_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_adk_safe(item) for item in value]
    return value


def adk_get_application(apply_no: str) -> dict:
    """Read one synthetic application by ApplyNo for ADK tool use."""
    application = get_application(apply_no)
    if application is None:
        return {
            "found": False,
            "apply_no": apply_no,
            "evidence": "No matching row found in data/applications.csv.",
        }
    return _adk_safe({"found": True, "application": application})


def adk_check_allocation(apply_no: str) -> dict:
    """Check whether allocation ShareRate total equals 100% for an ApplyNo."""
    return _adk_safe(check_allocation(apply_no))


def adk_check_budget_risk(apply_no: str) -> dict:
    """Check budget limit and overrun risk for an ApplyNo."""
    return _adk_safe(check_budget_risk(apply_no))


def adk_check_receipt_status(apply_no: str) -> dict:
    """Check overdue receipt and penalty status for an ApplyNo."""
    return _adk_safe(check_receipt_status(apply_no))


def adk_summarize_financial_status(apply_no: str) -> dict:
    """Summarize voucher and payment status for an ApplyNo."""
    return _adk_safe(summarize_financial_status(apply_no))


root_agent = Agent(
    name="engineering_risk_review_agent",
    model="gemini-3.1-flash-lite",
    description="Read-only agent for reviewing synthetic engineering application risk.",
    instruction="""
You are a read-only engineering application risk review agent.

You must:
- Review only synthetic CSV data.
- Never approve applications.
- Never update ERP data.
- Never create vouchers.
- Never connect to production databases.
- Always return risk level, findings, evidence, recommended next action, and safety note.
- If data is missing, say so clearly and ask a human reviewer to verify the ApplyNo.

Use the available tools to inspect applications, allocations, budgets, receipts, and vouchers.
Do not invent data that is not returned by the tools.
""",
    tools=[
        FunctionTool(adk_get_application),
        FunctionTool(adk_check_allocation),
        FunctionTool(adk_check_budget_risk),
        FunctionTool(adk_check_receipt_status),
        FunctionTool(adk_summarize_financial_status),
    ],
)
