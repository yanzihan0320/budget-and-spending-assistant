# Case 1 - Daily Food Cap

## Scenario

A student wants to cap food spending at HK$50/day and quickly detect daily overspending.

## Input Files

- Transactions: `data/case_studies/case_1_transactions.csv`
- Budget rules: `data/case_studies/case_1_budget_rules.json`

## Expected Evidence

- Category summary includes `Catering: 73.00` and `Transport: 8.00`.
- Daily alert triggers for `2026-03-01` because food spending is `55.00 > 50.00`.

## What Works Well

- Legacy labels (`meals`, `transport`) are normalized to standard categories.
- A direct threshold alert is easy to understand and explain to non-technical users.

## Failure Risk

- If a meal is miscategorized as `shopping`, the food cap alert may be missed.

## Existing Tool Comparison

- Typical commercial apps support receipt scanning or auto-categorization.
- This project uses manual category input, which is simpler but less accurate.
