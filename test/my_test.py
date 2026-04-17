from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.alert import check_budget_alerts
from src.stats import get_monthly_trend, get_spending_summary


class TestStatsAndAlerts(unittest.TestCase):
    def test_get_spending_summary_grouped_by_period(self) -> None:
        transactions = [
            {"date": "2026-03-01", "amount": 10.0, "category": "meals", "description": "A", "notes": ""},
            {"date": "2026-03-02", "amount": 20.0, "category": "transport", "description": "B", "notes": ""},
            {"date": "2026-04-01", "amount": 30.0, "category": "shopping", "description": "C", "notes": ""},
        ]

        daily = get_spending_summary(transactions, "day")
        monthly = get_spending_summary(transactions, "month")

        self.assertEqual(daily["2026-03-01"], 10.0)
        self.assertEqual(daily["2026-03-02"], 20.0)
        self.assertEqual(monthly["2026-03"], 30.0)
        self.assertEqual(monthly["2026-04"], 30.0)

    def test_get_monthly_trend(self) -> None:
        transactions = [
            {"date": "2026-03-01", "amount": 10.0, "category": "meals", "description": "A", "notes": ""},
            {"date": "2026-03-20", "amount": 30.0, "category": "shopping", "description": "B", "notes": ""},
            {"date": "2026-04-05", "amount": 15.0, "category": "transport", "description": "C", "notes": ""},
        ]

        trend = get_monthly_trend(transactions)
        self.assertEqual(trend["2026-03"], 40.0)
        self.assertEqual(trend["2026-04"], 15.0)

    def test_alert_anchor_defaults_to_earliest_transaction_date(self) -> None:
        transactions = [
            {"date": "2026-03-01", "amount": 60.0, "category": "meals", "description": "A", "notes": ""},
            {"date": "2026-03-02", "amount": 5.0, "category": "meals", "description": "B", "notes": ""},
        ]
        rules = [
            {"category": "meals", "period": "daily", "threshold": 50.0, "alert_type": "exceed"}
        ]

        alerts = check_budget_alerts(transactions, rules)
        self.assertEqual(len(alerts), 1)
        self.assertIn("Catering day spending exceeded threshold", alerts[0])


if __name__ == "__main__":
    unittest.main()