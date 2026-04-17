from __future__ import annotations

from .alert import check_budget_alerts
from .io import (
    load_budget_rules,
    load_transactions,
    save_budget_rules,
    save_transactions,
)
from .models import CategoryManager
from .stats import get_monthly_trend, get_spending_summary
from .validator import validate_budget_rule, validate_transaction


class BudgetAssistant:
    def __init__(self) -> None:
        self.transactions = load_transactions()
        self.budget_rules = load_budget_rules()

    def run(self) -> None:
        while True:
            print("\n=== Budget and Spending Assistant ===")
            print("1. View transactions")
            print("2. Add transaction")
            print("3. View budget rules")
            print("4. Add budget rule")
            print("5. View category summary")
            print("6. View period summary")
            print("7. View monthly trend")
            print("8. Check budget alerts")
            print("9. Save")
            print("10. Save and exit")
            print("11. Exit without saving")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.view_transactions()
            elif choice == "2":
                self.add_transaction()
            elif choice == "3":
                self.view_budget_rules()
            elif choice == "4":
                self.add_budget_rule()
            elif choice == "5":
                self.view_summary()
            elif choice == "6":
                self.view_period_summary()
            elif choice == "7":
                self.view_monthly_trend()
            elif choice == "8":
                self.view_alerts()
            elif choice == "9":
                self.save()
            elif choice == "10":
                self.save()
                print("Data saved. Goodbye.")
                return
            elif choice == "11":
                print("Goodbye.")
                return
            else:
                print("Invalid option. Try again.")

    def view_transactions(self) -> None:
        if not self.transactions:
            print("No transactions found.")
            return

        print("\nDate        Amount   Category       Description")
        print("-" * 56)
        for row in self.transactions:
            print(
                f"{row['date']:<10}  {row['amount']:>7.2f}  "
                f"{row['category']:<12}  {row['description']}"
            )

    def add_transaction(self) -> None:
        transaction = {
            "date": input("Date (YYYY-MM-DD): ").strip(),
            "amount": self._read_float("Amount: "),
            "category": self._read_category(),
            "description": input("Description: ").strip(),
            "notes": input("Notes (optional): ").strip(),
        }

        valid, message = validate_transaction(transaction)
        if not valid:
            print(f"Could not add transaction: {message}")
            return

        self.transactions.append(transaction)
        print("Transaction added.")

    def view_budget_rules(self) -> None:
        if not self.budget_rules:
            print("No budget rules found.")
            return

        print("\nCategory      Period   Threshold   Alert Type")
        print("-" * 56)
        for row in self.budget_rules:
            print(
                f"{row['category']:<12}  {row['period']:<6}  "
                f"{row['threshold']:>9.2f}  {row['alert_type']}"
            )

    def add_budget_rule(self) -> None:
        rule = {
            "category": self._read_category(),
            "period": self._read_choice("Period (day/week/month): ", {"day", "week", "month"}),
            "threshold": self._read_float("Threshold: "),
            "alert_type": self._read_choice(
                "Alert type (over_threshold/over_ratio): ",
                {"over_threshold", "over_ratio"},
            ),
        }

        valid, message = validate_budget_rule(rule)
        if not valid:
            print(f"Could not add budget rule: {message}")
            return

        self.budget_rules.append(rule)
        print("Budget rule added.")

    def view_summary(self) -> None:
        summary = get_spending_summary(self.transactions)
        if not summary:
            print("No spending data available.")
            return

        print("\nCategory Summary")
        print("-" * 32)
        for category, total in sorted(summary.items()):
            print(f"{category:<15} {total:>10.2f}")

    def view_period_summary(self) -> None:
        period = self._read_choice("Period (day/week/month): ", {"day", "week", "month"})
        summary = get_spending_summary(self.transactions, period)
        if not summary:
            print("No spending data available.")
            return

        print(f"\nPeriod Summary ({period})")
        print("-" * 32)
        for period_key, total in sorted(summary.items()):
            print(f"{period_key:<15} {total:>10.2f}")

    def view_monthly_trend(self) -> None:
        trend = get_monthly_trend(self.transactions)
        if not trend:
            print("No monthly trend data available.")
            return

        print("\nMonthly Trend")
        print("-" * 32)
        for month, total in sorted(trend.items()):
            print(f"{month:<15} {total:>10.2f}")

    def view_alerts(self) -> None:
        anchor_date = input("Anchor date YYYY-MM-DD (press Enter to auto-infer): ").strip() or None
        alerts = check_budget_alerts(self.transactions, self.budget_rules, start_date=anchor_date)
        if not alerts:
            print("No alerts triggered.")
            return

        print("\nAlerts")
        print("-" * 32)
        for message in alerts:
            print(message)

    def save(self) -> None:
        save_transactions(self.transactions)
        save_budget_rules(self.budget_rules)
        print("Data saved.")

    @staticmethod
    def _read_float(prompt: str) -> float:
        while True:
            raw = input(prompt).strip()
            try:
                return float(raw)
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def _read_choice(prompt: str, options: set[str]) -> str:
        while True:
            raw = input(prompt).strip()
            if raw in options:
                return raw
            print(f"Please choose one of: {', '.join(sorted(options))}")

    @staticmethod
    def _read_category() -> str:
        options = CategoryManager.get_all_categories()
        print("Available categories: " + ", ".join(options))
        while True:
            raw = input("Category: ").strip()
            if CategoryManager.is_valid_category(raw):
                return raw
            print("Invalid category.")


if __name__ == "__main__":
    BudgetAssistant().run()
