# Engineering Application Risk Review Agent

**Track:** Agents for Business  
**Tagline:** A read-only Google ADK agent that helps reviewers identify engineering application risks before human approval.

![Project Cover](assets/cover.png)

## Problem

Engineering application review is often spread across several business records: application headers, allocation rows, budget usage, receipt status, and voucher/payment state. A reviewer may need to inspect multiple reports before deciding whether an application can proceed. That manual process is slow, inconsistent, and easy to get wrong.

The key risks are practical business risks: allocation share rates may not total 100%, receipts may be overdue, budgets may show pressure, or the requested application may not exist in the source data. These are exactly the kinds of issues that should be detected before a human reviewer spends time on approval decisions.

This project uses only synthetic data. It does not include real ERP records, real employee data, credentials, API keys, or production systems.

## Solution

The Engineering Application Risk Review Agent is a read-only assistant for pre-review screening. Given an `ApplyNo`, it checks synthetic CSV data across applications, allocations, budgets, receipts, and vouchers. It returns a structured review containing:

- risk level
- blocking status
- findings
- evidence
- recommended next action
- safety note

The agent is not designed to approve applications or update records. It is designed to help a human reviewer quickly understand what evidence requires attention.

## Why Agents

This workflow is more than a single lookup. A useful answer requires gathering evidence from several sources, combining the results, and explaining the risk in natural language. A Google ADK agent fits this pattern because it can orchestrate multiple read-only tools, call only the data checks it needs, and produce a concise risk review for the reviewer.

The agentic value is the evidence workflow: from a single review request, the system inspects allocation, budget, receipt, and voucher signals, then turns those signals into an actionable risk summary.

## Architecture

![Architecture Diagram](assets/architecture.png)

The project uses a small, auditable architecture:

- `app/adk_agent.py` defines a Google ADK `root_agent` named `engineering_risk_review_agent`.
- ADK `FunctionTool` wrappers expose read-only review tools to the agent.
- `data/*.csv` contains synthetic application, allocation, budget, receipt, and voucher records.
- `app/rules.py` contains deterministic risk rules.
- `policies.yaml` documents read-only permissions and forbidden actions.
- `specs/*.yaml` defines schema, risk rules, and golden cases.
- `tests/` verifies expected outcomes and ADK tool wiring.

There is also a local CLI demo in `app/agent.py` so the deterministic review logic can be tested without consuming Gemini API quota.

## Key Concepts Demonstrated

### 1. Agent / Google ADK

`app/adk_agent.py` defines a Google ADK `root_agent` using the Gemini model. The agent exposes existing Python review functions through ADK `FunctionTool` wrappers:

- `adk_get_application`
- `adk_check_allocation`
- `adk_check_budget_risk`
- `adk_check_receipt_status`
- `adk_summarize_financial_status`

These tools let the agent gather evidence across multiple synthetic business records before producing a risk review.

### 2. Security Features

The project is intentionally read-only. `policies.yaml` defines the permission tier and forbids approving applications, updating ERP data, creating vouchers, deleting records, or connecting to production databases. The ADK instruction repeats those restrictions so the agent remains a reviewer, not an actor that changes business state.

### 3. Agent Skill

The project uses an `engineering-risk-review` skill to define the review workflow, output format, permission tier, and forbidden actions. This keeps the agent focused on evidence-based risk review.

### 4. Evaluation and Spec-Driven Development

The `specs/` directory documents the problem, schema, risk rules, and golden cases. `tests/test_agent.py` verifies low-risk, high-risk, and unknown-application behavior. `tests/test_adk_agent.py` verifies that the ADK wrapper exposes the expected tools and avoids unsafe `None` values in tool responses.

## Demo Plan

**YouTube Demo:** https://youtu.be/rEs4bYiMa_0

The demo shows both the local deterministic review and the ADK runtime.

1. Show the architecture diagram and explain the read-only boundary.
2. Run the local CLI for a low-risk case:

   ```powershell
   py app/agent.py EG-2026-0001
   ```

3. Run the local CLI for a high-risk case:

   ```powershell
   py app/agent.py EG-2026-0002
   ```

   Expected findings include `allocation_total_not_100` and `overdue_receipt`.

4. Run the ADK agent with a Gemini API key:

   ```powershell
   $env:GOOGLE_GENAI_USE_VERTEXAI="FALSE"
   $env:GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
   adk run app "Review EG-2026-0001" --in_memory
   ```

5. Show `policies.yaml` and explain that the agent cannot approve, update ERP data, or create vouchers.

## Results

Current verification:

- CLI low-risk case runs successfully.
- CLI high-risk case flags the expected findings.
- ADK `root_agent` loads with five read-only `FunctionTool` wrappers.
- Unit test suite passes with six tests.
- No real credentials or API keys are stored in the repository.

## Safety and Limitations

All data is synthetic. The project does not include real ERP data, production database connections, real employee data, passwords, or API keys.

Current limitations:

- MCP server integration is not implemented yet.
- Cloud deployment is not included yet.
- Runtime policy enforcement can be strengthened beyond the current declarative policy and ADK instruction.
- The demo is focused on a clear capstone prototype, not production ERP integration.

## Links

- GitHub Repo: https://github.com/mikenick456/engineering-risk-review-agent
- YouTube Demo: https://youtu.be/rEs4bYiMa_0
- Kaggle Writeup: TODO
