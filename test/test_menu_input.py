from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.menu import BudgetAssistant


class TestMenuInputFlow(unittest.TestCase):
    def test_add_transaction_reprompts_invalid_date_and_amount(self) -> None:
        assistant = BudgetAssistant()
        assistant.transactions = []
        assistant.budget_rules = []

        with patch(
            "builtins.input",
            side_effect=[
                "2026/03/01",  # invalid date
                "2026-03-01",  # valid date
                "-5",          # invalid amount
                "15",          # valid amount
                "Catering",    # category
                "",            # empty description
                "Lunch",       # valid description
                "",            # notes
            ],
        ):
            with patch("src.menu.check_budget_alerts", return_value=[]) as mock_alerts:
                assistant.add_transaction()

        self.assertEqual(len(assistant.transactions), 1)
        added = assistant.transactions[0]
        self.assertEqual(added["date"], "2026-03-01")
        self.assertEqual(added["amount"], 15.0)
        self.assertEqual(added["category"], "Catering")
        self.assertEqual(added["description"], "Lunch")

        mock_alerts.assert_called_once()
        self.assertEqual(mock_alerts.call_args.kwargs["start_date"], "2026-03-01")
        self.assertTrue(mock_alerts.call_args.kwargs["include_consecutive"])

    def test_view_transactions_filter_by_date_range(self) -> None:
        assistant = BudgetAssistant()
        assistant.transactions = [
            {"date": "2026-03-01", "amount": 10.0, "category": "Catering", "description": "A", "notes": ""},
            {"date": "2026-03-02", "amount": 20.0, "category": "Transport", "description": "B", "notes": ""},
            {"date": "2026-03-10", "amount": 30.0, "category": "Shopping", "description": "C", "notes": ""},
        ]

        with patch("builtins.input", side_effect=["3", "2026-03-01", "2026-03-05"]):
            with patch.object(BudgetAssistant, "_print_transactions") as mock_printer:
                assistant.view_transactions()

        mock_printer.assert_called_once()
        filtered_rows = mock_printer.call_args.args[0]
        self.assertEqual(len(filtered_rows), 2)
        self.assertEqual(filtered_rows[0]["date"], "2026-03-01")
        self.assertEqual(filtered_rows[1]["date"], "2026-03-02")

    def test_reload_replaces_in_memory_data(self) -> None:
        assistant = BudgetAssistant()
        assistant.transactions = [
            {"date": "2026-03-01", "amount": 10.0, "category": "Catering", "description": "Old", "notes": ""},
        ]
        assistant.budget_rules = [
            {"category": "Catering", "period": "day", "threshold": 30.0, "alert_type": "over_threshold"},
        ]

        new_transactions = [
            {"date": "2026-04-01", "amount": 25.0, "category": "Transport", "description": "New", "notes": ""},
        ]
        new_rules = [
            {"category": "Transport", "period": "week", "threshold": 100.0, "alert_type": "over_threshold"},
        ]

        with patch("builtins.input", side_effect=["y"]):
            with patch("src.menu.load_transactions", return_value=new_transactions) as mock_load_tx:
                with patch("src.menu.load_budget_rules", return_value=new_rules) as mock_load_rules:
                    assistant.reload()

        mock_load_tx.assert_called_once()
        mock_load_rules.assert_called_once()
        self.assertEqual(assistant.transactions, new_transactions)
        self.assertEqual(assistant.budget_rules, new_rules)

    def test_add_budget_rule_with_custom_consecutive_days(self) -> None:
        assistant = BudgetAssistant()
        assistant.budget_rules = []

        with patch(
            "builtins.input",
            side_effect=[
                "Catering",
                "day",
                "50",
                "over_threshold",
                "4",
            ],
        ):
            assistant.add_budget_rule()

        self.assertEqual(len(assistant.budget_rules), 1)
        self.assertEqual(assistant.budget_rules[0]["consecutive_days_threshold"], 4)

    def test_view_summary_auto_shows_alerts(self) -> None:
        assistant = BudgetAssistant()
        assistant.transactions = [
            {"date": "2026-03-01", "amount": 60.0, "category": "Catering", "description": "A", "notes": ""},
        ]
        assistant.budget_rules = [
            {
                "category": "Catering",
                "period": "day",
                "threshold": 50.0,
                "alert_type": "over_threshold",
                "consecutive_days_threshold": 2,
            },
        ]

        with patch("src.menu.check_budget_alerts", return_value=["[BUDGET ALERT] test message"]) as mock_alerts:
            with patch("builtins.print") as mock_print:
                assistant.view_summary()

        mock_alerts.assert_called_once()
        self.assertTrue(mock_alerts.call_args.kwargs["include_consecutive"])
        printed_lines = [" ".join(str(arg) for arg in call.args) for call in mock_print.call_args_list]
        self.assertTrue(any("Auto Alerts (overall summary)" in line for line in printed_lines))


if __name__ == "__main__":
    unittest.main()
