from __future__ import annotations

from .alert import check_budget_alerts
from .io import (
    load_category_config,
    load_budget_rules,
    load_transactions,
    save_budget_rules,
    save_transactions,
)
from .models import CategoryManager, normalize_category
from .stats import (
    filter_by_category,
    filter_by_date_range,
    get_category_summary_by_period,
    get_monthly_trend,
    get_recent_spending_trend,
    get_spending_summary,
    get_top_categories,
    get_total_spending,
)
from .validator import validate_budget_rule, validate_date, validate_transaction


class BudgetAssistant:
    def __init__(self) -> None:
        self._load_custom_categories()
        self.transactions = load_transactions()
        self.budget_rules = load_budget_rules()

    def run(self) -> None:
        while True:
            print("\n=== Budget and Spending Assistant ===")
            print("1. View/filter transactions")
            print("2. Add transaction")
            print("3. View budget rules")
            print("4. Add budget rule")
            print("5. View overall summary")
            print("6. View period summary")
            print("7. View spending trends (monthly/7-day/30-day)")
            print("8. View category totals by period")
            print("9. Check budget alerts")
            print("10. Save")
            print("11. Reload data from files")
            print("12. Save and exit")
            print("13. Exit without saving")

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
                self.view_category_period_summary()
            elif choice == "9":
                self.view_alerts()
            elif choice == "10":
                self.save()
            elif choice == "11":
                self.reload()
            elif choice == "12":
                if self.save():
                    print("Data saved. Goodbye.")
                    return
            elif choice == "13":
                print("Goodbye.")
                return
            else:
                print("Invalid option. Try again.")

    def view_transactions(self) -> None:
        if not self.transactions:
            print("No transactions found.")
            return

        print("\nFilter mode")
        print("1. View all")
        print("2. Filter by category")
        print("3. Filter by date range")
        mode = input("Choose filter mode: ").strip()

        rows = self.transactions
        if mode == "1":
            rows = self.transactions
        elif mode == "2":
            category = self._read_category()
            rows = filter_by_category(self.transactions, category)
        elif mode == "3":
            start_date = self._read_valid_date("Start date (YYYY-MM-DD): ")
            end_date = self._read_valid_date("End date (YYYY-MM-DD): ")
            if start_date > end_date:
                print("Start date must be earlier than or equal to end date.")
                return
            rows = filter_by_date_range(self.transactions, start_date, end_date)
        else:
            print("Invalid filter mode.")
            return

        if not rows:
            print("No transactions found for this filter.")
            return

        self._print_transactions(rows)

    @staticmethod
    def _print_transactions(rows: list[dict]) -> None:
        print("\nDate        Amount   Category       Description")
        print("-" * 56)
        for row in rows:
            print(
                f"{row['date']:<10}  {row['amount']:>7.2f}  "
                f"{row['category']:<12}  {row['description']}"
            )

    def add_transaction(self) -> None:
        transaction = {
            "date": self._read_valid_date("Date (YYYY-MM-DD): "),
            "amount": self._read_positive_float("Amount: "),
            "category": self._read_category(),
            "description": self._read_non_empty("Description: "),
            "notes": input("Notes (optional): ").strip(),
        }

        valid, message = validate_transaction(transaction)
        if not valid:
            print(f"Could not add transaction: {message}")
            return

        self.transactions.append(transaction)
        print("Transaction added.")

        auto_alerts = check_budget_alerts(
            self.transactions,
            self.budget_rules,
            start_date=transaction["date"],
            include_consecutive=True,
        )
        focused_alerts = [
            message
            for message in auto_alerts
            if normalize_category(transaction["category"]) in message
        ]
        if focused_alerts:
            print("\nImmediate budget alerts for this transaction:")
            print("-" * 40)
            for message in focused_alerts:
                print(message)

    def view_budget_rules(self) -> None:
        if not self.budget_rules:
            print("No budget rules found.")
            return

        print("\nCategory      Period   Threshold   Alert Type      Settings")
        print("-" * 80)
        for row in self.budget_rules:
            settings: list[str] = []
            if row.get("ratio_threshold") not in (None, ""):
                settings.append(f"ratio>{float(row['ratio_threshold']):.0%}")
            if row.get("consecutive_days_threshold") not in (None, ""):
                settings.append(f"consecutive_days={int(row['consecutive_days_threshold'])}")

            print(
                f"{row['category']:<12}  {row['period']:<6}  "
                f"{row['threshold']:>9.2f}  {row['alert_type']:<13}  {'; '.join(settings)}"
            )

    def add_budget_rule(self) -> None:
        rule = {
            "category": self._read_category(),
            "period": self._read_choice("Period (day/week/month): ", {"day", "week", "month"}),
            "threshold": self._read_positive_float("Threshold: "),
            "alert_type": self._read_choice(
                "Alert type (over_threshold/over_ratio): ",
                {"over_threshold", "over_ratio"},
            ),
        }

        if rule["period"] == "day" and rule["alert_type"] == "over_threshold":
            consecutive_days = self._read_optional_positive_int(
                "Consecutive overspend days threshold (press Enter for default=2): "
            )
            if consecutive_days is not None:
                rule["consecutive_days_threshold"] = consecutive_days

        valid, message = validate_budget_rule(rule)
        if not valid:
            print(f"Could not add budget rule: {message}")
            return

        self.budget_rules.append(rule)
        print("Budget rule added.")

    def view_summary(self) -> None:
        if not self.transactions:
            print("No spending data available.")
            return

        total_spending = get_total_spending(self.transactions)
        summary = get_spending_summary(self.transactions)
        daily_totals = get_spending_summary(self.transactions, "day")
        weekly_totals = get_spending_summary(self.transactions, "week")
        monthly_totals = get_spending_summary(self.transactions, "month")
        top_categories = get_top_categories(self.transactions, top_n=3)

        print("\nOverall Summary")
        print("-" * 40)
        print(f"Total spending: {total_spending:.2f}")

        print("\nPer-category totals")
        print("-" * 40)
        for category, total in sorted(summary.items()):
            print(f"{category:<15} {total:>10.2f}")

        print("\nTime-based totals (daily)")
        print("-" * 40)
        for period_key, total in sorted(daily_totals.items()):
            print(f"{period_key:<15} {total:>10.2f}")

        print("\nTime-based totals (weekly)")
        print("-" * 40)
        for period_key, total in sorted(weekly_totals.items()):
            print(f"{period_key:<15} {total:>10.2f}")

        print("\nTime-based totals (monthly)")
        print("-" * 40)
        for period_key, total in sorted(monthly_totals.items()):
            print(f"{period_key:<15} {total:>10.2f}")

        print("\nTop 3 categories")
        print("-" * 40)
        for rank, (category, total) in enumerate(top_categories, start=1):
            print(f"{rank}. {category:<12} {total:>10.2f}")

        self._show_auto_alerts("overall summary")

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

        self._show_auto_alerts(f"{period} summary")

    def view_monthly_trend(self) -> None:
        monthly_trend = get_monthly_trend(self.transactions)
        trend_7_days = get_recent_spending_trend(self.transactions, 7)
        trend_30_days = get_recent_spending_trend(self.transactions, 30)

        if not monthly_trend and not trend_7_days and not trend_30_days:
            print("No trend data available.")
            return

        if monthly_trend:
            print("\nMonthly Trend")
            print("-" * 40)
            for month, total in sorted(monthly_trend.items()):
                print(f"{month:<15} {total:>10.2f}")

        if trend_7_days:
            print("\nLast 7 Days Trend")
            print("-" * 40)
            for day, total in trend_7_days.items():
                print(f"{day:<15} {total:>10.2f}")

        if trend_30_days:
            print("\nLast 30 Days Trend")
            print("-" * 40)
            for day, total in trend_30_days.items():
                print(f"{day:<15} {total:>10.2f}")

        self._show_auto_alerts("trend report")

    def view_category_period_summary(self) -> None:
        period = self._read_choice("Period (day/week/month): ", {"day", "week", "month"})
        summary = get_category_summary_by_period(self.transactions, period)
        if not summary:
            print("No spending data available.")
            return

        print(f"\nCategory totals by {period}")
        print("-" * 40)
        for period_key in sorted(summary.keys()):
            print(f"\n[{period_key}]")
            for category, total in sorted(summary[period_key].items()):
                print(f"{category:<15} {total:>10.2f}")

        self._show_auto_alerts(f"category {period} summary")

    def view_alerts(self) -> None:
        anchor_date = input("Anchor date YYYY-MM-DD (press Enter to auto-infer): ").strip() or None
        alerts = check_budget_alerts(
            self.transactions,
            self.budget_rules,
            start_date=anchor_date,
            include_consecutive=True,
        )
        if not alerts:
            print("No alerts triggered.")
            return

        print("\nAlerts")
        print("-" * 32)
        for message in alerts:
            print(message)

    def save(self) -> bool:
        try:
            save_transactions(self.transactions)
            save_budget_rules(self.budget_rules)
        except (OSError, ValueError) as error:
            print(f"Could not save data: {error}")
            return False

        print("Data saved.")
        return True

    def reload(self) -> None:
        confirm = input("Reload from files and discard unsaved changes? (y/n): ").strip().lower()
        if confirm != "y":
            print("Reload canceled.")
            return

        self._load_custom_categories()
        self.transactions = load_transactions()
        self.budget_rules = load_budget_rules()
        print("Data reloaded from files.")

    def _load_custom_categories(self) -> None:
        categories = load_category_config()
        if categories:
            print("Loaded custom categories from config: " + ", ".join(categories))

    def _show_auto_alerts(self, context: str) -> None:
        alerts = check_budget_alerts(
            self.transactions,
            self.budget_rules,
            include_consecutive=True,
        )
        if not alerts:
            return

        print(f"\nAuto Alerts ({context})")
        print("-" * 40)
        for message in alerts:
            print(message)

    @staticmethod
    def _read_float(prompt: str) -> float:
        while True:
            raw = input(prompt).strip()
            try:
                return float(raw)
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def _read_positive_float(prompt: str) -> float:
        while True:
            value = BudgetAssistant._read_float(prompt)
            if value > 0:
                return value
            print("Please enter a positive number greater than 0.")

    @staticmethod
    def _read_valid_date(prompt: str) -> str:
        while True:
            raw = input(prompt).strip()
            valid, message = validate_date(raw)
            if valid:
                return raw
            print(message)

    @staticmethod
    def _read_non_empty(prompt: str) -> str:
        while True:
            raw = input(prompt).strip()
            if raw:
                return raw
            print("This field cannot be empty.")

    @staticmethod
    def _read_optional_positive_int(prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()
            if not raw:
                return None

            try:
                value = int(raw)
            except ValueError:
                print("Please enter a valid integer or leave it empty.")
                continue

            if value <= 0:
                print("Please enter a positive integer greater than 0.")
                continue

            return value

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
