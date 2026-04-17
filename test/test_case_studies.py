from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.alert import check_budget_alerts
from src.io import load_budget_rules, load_transactions
from src.stats import get_spending_summary


class TestCaseStudies(unittest.TestCase):
    def _load_case(self, case_id: int) -> tuple[list[dict], list[dict]]:
        transactions = load_transactions(f"data/case_studies/case_{case_id}_transactions.csv")
        rules = load_budget_rules(f"data/case_studies/case_{case_id}_budget_rules.json")
        return transactions, rules

    def test_case_1_daily_food_cap(self) -> None:
        transactions, rules = self._load_case(1)
        summary = get_spending_summary(transactions)
        alerts = check_budget_alerts(transactions, rules)

        self.assertAlmostEqual(summary["Catering"], 73.0, places=2)
        self.assertAlmostEqual(summary["Transport"], 8.0, places=2)
        self.assertEqual(len(alerts), 1)
        self.assertIn("Catering day spending exceeded threshold", alerts[0])

    def test_case_2_monthly_transport_tracking(self) -> None:
        transactions, rules = self._load_case(2)
        summary = get_spending_summary(transactions)
        alerts = check_budget_alerts(transactions, rules)

        self.assertAlmostEqual(summary["Transport"], 85.0, places=2)
        self.assertEqual(len(alerts), 0)

    def test_case_3_subscription_creep(self) -> None:
        transactions, rules = self._load_case(3)
        summary = get_spending_summary(transactions)
        alerts = check_budget_alerts(transactions, rules)

        self.assertAlmostEqual(summary["Entertainment"], 66.0, places=2)
        self.assertEqual(len(alerts), 1)
        self.assertIn("spending ratio exceeded", alerts[0])

    def test_case_4_one_off_purchase_spike(self) -> None:
        transactions, rules = self._load_case(4)
        summary = get_spending_summary(transactions)
        alerts = check_budget_alerts(transactions, rules)

        self.assertAlmostEqual(summary["Shopping"], 365.0, places=2)
        self.assertEqual(len(alerts), 1)
        self.assertIn("Shopping month spending exceeded threshold", alerts[0])


if __name__ == "__main__":
    unittest.main()
