# Case 4 - One-off Purchase Spike

## Scenario

A user buys a laptop once in a month and receives a shopping budget alert.

## Input Files

- Transactions: `data/case_studies/case_4_transactions.csv`
- Budget rules: `data/case_studies/case_4_budget_rules.json`

## Expected Evidence

- Shopping total is `365.00` in March.
- Threshold alert triggers because `365.00 > 300.00`.

## What Works Well

- The alert correctly flags budget breach from a rules perspective.
- The case demonstrates transparency: totals and trigger condition are easy to audit.

## Failure Risk

- The system cannot distinguish one-off essential purchases from habitual overspending.

## Existing Tool Comparison

- Full budgeting apps typically support tags, goals, and "exclude one-off" views.
- This project leaves one-off interpretation to user analysis for simplicity.
