# Case 3 - Subscription Creep

## Scenario

A student has multiple small entertainment subscriptions and wants an early warning before spending drifts too far.

## Input Files

- Transactions: `data/case_studies/case_3_transactions.csv`
- Budget rules: `data/case_studies/case_3_budget_rules.json`

## Expected Evidence

- Entertainment monthly total is `66.00`.
- Ratio alert triggers because `66.00 / 150.00 = 44%`, which is above the project ratio threshold (10%).

## What Works Well

- Ratio alerts can detect spending drift before absolute threshold is exceeded.
- Monthly trend values reveal recurring subscription impact.

## Failure Risk

- A fixed 10% ratio threshold may trigger very early and create noisy alerts.

## Existing Tool Comparison

- Commercial tools often allow custom ratio thresholds per category.
- This project uses a unified threshold to keep logic transparent and testable.
