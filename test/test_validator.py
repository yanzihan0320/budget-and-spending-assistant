from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models import CategoryManager
from src.validator import validate_budget_rule, validate_transaction


class TestValidatorModule(unittest.TestCase):
    def setUp(self) -> None:
        CategoryManager.clear_custom_categories()

    def test_validate_transaction_negative_amount(self) -> None:
        transaction = {
            "date": "2026-04-01",
            "amount": -1.0,
            "category": "Catering",
            "description": "Invalid",
            "notes": "",
        }

        valid, message = validate_transaction(transaction)
        self.assertFalse(valid)
        self.assertIn("greater than 0", message)

    def test_validate_transaction_invalid_date(self) -> None:
        transaction = {
            "date": "2026/04/01",
            "amount": 10.0,
            "category": "Catering",
            "description": "Invalid date",
            "notes": "",
        }

        valid, message = validate_transaction(transaction)
        self.assertFalse(valid)
        self.assertIn("Invalid date format", message)

    def test_validate_budget_rule_accepts_custom_consecutive_threshold(self) -> None:
        rule = {
            "category": "Catering",
            "period": "day",
            "threshold": 50.0,
            "alert_type": "over_threshold",
            "consecutive_days_threshold": 3,
        }

        valid, message = validate_budget_rule(rule)
        self.assertTrue(valid)
        self.assertIn("Validation passed", message)

    def test_validate_budget_rule_rejects_invalid_consecutive_threshold(self) -> None:
        rule = {
            "category": "Catering",
            "period": "day",
            "threshold": 50.0,
            "alert_type": "over_threshold",
            "consecutive_days_threshold": 0,
        }

        valid, message = validate_budget_rule(rule)
        self.assertFalse(valid)
        self.assertIn("positive integer", message)


if __name__ == "__main__":
    unittest.main()
