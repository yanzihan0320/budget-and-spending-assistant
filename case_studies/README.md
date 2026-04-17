# Case Studies Evidence Chain

This folder contains four reproducible case studies. Each case includes:

1. Scenario and goals.
2. Input files (transactions and budget rules).
3. Expected summaries and alerts.
4. What works well, failure modes, and comparison with an existing budgeting tool style.

## Case Index

1. [Case 1 - Daily Food Cap](case_1_daily_food_cap.md)
2. [Case 2 - Monthly Transport Tracking](case_2_monthly_transport_tracking.md)
3. [Case 3 - Subscription Creep](case_3_subscription_creep.md)
4. [Case 4 - One-off Purchase Spike](case_4_one_off_purchase_spike.md)

## Reproduction Commands

From project root, each case can be validated by unit/integration tests:

- `python -m unittest discover -s test -p "test_*.py"`

The tests in `test/test_case_studies.py` assert the expected summaries and alerts for all four cases.
