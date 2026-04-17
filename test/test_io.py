from pathlib import Path
import sys
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.io import load_budget_rules, load_transactions, save_budget_rules, save_transactions


class TestIOModule(unittest.TestCase):
    def test_load_default_transactions_returns_records(self) -> None:
        transactions = load_transactions()
        self.assertGreater(len(transactions), 0)
        self.assertTrue({"date", "amount", "category", "description", "notes"}.issubset(transactions[0].keys()))

    def test_load_default_rules_are_normalized(self) -> None:
        rules = load_budget_rules()
        self.assertGreater(len(rules), 0)
        self.assertIn(rules[0]["period"], {"day", "week", "month"})
        self.assertIn(rules[0]["alert_type"], {"over_threshold", "over_ratio"})

    def test_save_and_reload_roundtrip(self) -> None:
        transactions = [
            {
                "date": "2026-04-01",
                "amount": 12.5,
                "category": "meals",
                "description": "Roundtrip test",
                "notes": "",
            }
        ]
        rules = [
            {
                "category": "meals",
                "period": "daily",
                "threshold": 20.0,
                "alert_type": "exceed",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            tx_path = Path(temp_dir) / "transactions.csv"
            rule_path = Path(temp_dir) / "budget_rules.json"

            save_transactions(transactions, str(tx_path))
            save_budget_rules(rules, str(rule_path))

            reloaded_transactions = load_transactions(str(tx_path))
            reloaded_rules = load_budget_rules(str(rule_path))

            self.assertEqual(len(reloaded_transactions), 1)
            self.assertEqual(reloaded_transactions[0]["category"], "Catering")
            self.assertEqual(len(reloaded_rules), 1)
            self.assertEqual(reloaded_rules[0]["period"], "day")
            self.assertEqual(reloaded_rules[0]["alert_type"], "over_threshold")


if __name__ == "__main__":
    unittest.main()