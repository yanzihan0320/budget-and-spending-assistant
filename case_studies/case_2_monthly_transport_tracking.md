# Case 2 - Monthly Transport Tracking

## Scenario

A student sets a monthly transport budget of HK$100 and wants to verify spending stays within budget.

## Input Files

- Transactions: `data/case_studies/case_2_transactions.csv`
- Budget rules: `data/case_studies/case_2_budget_rules.json`

## Expected Evidence

- Transport total is `85.00` for March.
- No threshold alert is triggered because `85.00 <= 100.00`.

## What Works Well

- The monthly aggregation highlights budget status over a realistic period.
- Rule-based alert remains quiet when budget is respected.

## Failure Risk

- The model does not provide "near-threshold" warnings (for example, 90% usage), only rule triggers.

## Existing Tool Comparison

- Many apps provide progress bars and warning stages (50%, 80%, 100%).
- This project intentionally keeps a binary alert model for simplicity.
