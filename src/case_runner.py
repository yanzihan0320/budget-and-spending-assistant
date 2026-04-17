from __future__ import annotations

import argparse

from .alert import check_budget_alerts
from .io import load_budget_rules, load_transactions
from .stats import get_monthly_trend, get_spending_summary


def run_case(case_id: int) -> None:
    case_prefix = f"case_{case_id}"
    transactions_file = f"data/case_studies/{case_prefix}_transactions.csv"
    rules_file = f"data/case_studies/{case_prefix}_budget_rules.json"

    transactions = load_transactions(transactions_file)
    rules = load_budget_rules(rules_file)

    print(f"\n=== {case_prefix.upper()} ===")
    print(f"Transactions loaded: {len(transactions)}")
    print(f"Rules loaded: {len(rules)}")

    category_summary = get_spending_summary(transactions)
    period_summary = get_spending_summary(transactions, "month")
    monthly_trend = get_monthly_trend(transactions)
    alerts = check_budget_alerts(transactions, rules)

    print("\nCategory summary:")
    for key, value in sorted(category_summary.items()):
        print(f"  {key}: {value:.2f}")

    print("\nMonthly totals:")
    for key, value in sorted(period_summary.items()):
        print(f"  {key}: {value:.2f}")

    print("\nMonthly trend:")
    for key, value in sorted(monthly_trend.items()):
        print(f"  {key}: {value:.2f}")

    print("\nAlerts:")
    if not alerts:
        print("  No alerts triggered.")
    else:
        for message in alerts:
            print(f"  {message}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one case study and print summaries/alerts.")
    parser.add_argument("case_id", type=int, choices=[1, 2, 3, 4], help="Case ID to run")
    args = parser.parse_args()
    run_case(args.case_id)


if __name__ == "__main__":
    main()
