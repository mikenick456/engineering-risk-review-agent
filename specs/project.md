# Engineering Application Risk Review Agent

## Problem
Engineering application data is spread across application records, allocation rows, budget limits, receipt status, and voucher records. Managers need a quick read-only assistant to identify risk before sending applications forward.

## Solution
This project builds a read-only AI agent that reviews synthetic engineering application data and explains risks with evidence.

## Scope
- In scope: allocation check, budget risk, project classification, overdue receipt, voucher inconsistency.
- Out of scope: real ERP integration, approval, database writes, real vouchers, BPM workflow.

## Data Safety
All data is synthetic. No proprietary ERP source code, real company data, credentials, or production identifiers are included.