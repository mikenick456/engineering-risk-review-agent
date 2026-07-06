---
name: engineering-risk-review
description: Use when reviewing synthetic engineering application data for allocation, budget, overdue receipt, voucher, or project-classification risks.
---

# Engineering Risk Review

## Overview

This skill defines the evidence-first workflow used by the Engineering Application Risk Review Agent. It is intentionally read-only and is designed for synthetic capstone data only.

## Source of Truth

Assume the project root is `eg-risk-agent/`.

- Project spec: `specs/project.md`
- Schema: `specs/schema.yaml`
- Risk rules: `specs/risk-rules.yaml`
- Golden cases: `specs/golden-cases.yaml`
- Policy: `policies.yaml`
- Synthetic data: `data/`
- ADK agent wrapper: `app/adk_agent.py`
- Local CLI entrypoint: `app/agent.py`

## Workflow

1. Identify the requested `ApplyNo`.
2. Read the matching application from synthetic CSV data.
3. Check allocation total equals 100%.
4. Check budget risk and project thresholds.
5. Check receipt overdue status.
6. Check voucher/payment status.
7. Return risk level, findings, evidence, recommended next action, and safety note.

## Output Format

Return:

- Summary
- Risk level: `low` | `medium` | `high`
- Blocked: `true` | `false`
- Findings
- Evidence
- Recommended next action
- Safety note

## Safety Rules

- Use synthetic data only.
- Do not approve applications.
- Do not update ERP data.
- Do not create vouchers.
- Do not delete records.
- Do not connect to production databases.
- Do not use real company, employee, vendor, or credential data.

## Relationship to Runtime

This skill documents the review workflow and safety boundary. The runtime implementation is split into two entrypoints:

- `app/agent.py` runs the deterministic local CLI demo.
- `app/adk_agent.py` exposes the same read-only review logic through Google ADK `FunctionTool` wrappers.

Both entrypoints share the same underlying review functions in `app/tools.py` and deterministic rules in `app/rules.py`.
