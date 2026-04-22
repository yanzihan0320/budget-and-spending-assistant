from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.alert import check_budget_alerts
from src.stats import (
    get_category_summary_by_period,
    get_monthly_trend,
    get_recent_spending_trend,
    get_spending_summary,
    get_top_categories,
    get_total_spending,
)


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

    def test_total_spending_and_top_categories(self) -> None:
        transactions = [
            {"date": "2026-03-01", "amount": 40.0, "category": "Catering", "description": "A", "notes": ""},
            {"date": "2026-03-02", "amount": 20.0, "category": "Transport", "description": "B", "notes": ""},
            {"date": "2026-03-03", "amount": 35.0, "category": "Shopping", "description": "C", "notes": ""},
            {"date": "2026-03-04", "amount": 10.0, "category": "Catering", "description": "D", "notes": ""},
        ]

        self.assertEqual(get_total_spending(transactions), 105.0)
        top3 = get_top_categories(transactions, top_n=3)
        self.assertEqual(top3[0], ("Catering", 50.0))
        self.assertEqual(len(top3), 3)

    def test_recent_spending_trend_7_and_30_days(self) -> None:
        transactions = [
            {"date": "2026-03-25", "amount": 10.0, "category": "Catering", "description": "A", "notes": ""},
            {"date": "2026-03-28", "amount": 15.0, "category": "Transport", "description": "B", "notes": ""},
            {"date": "2026-03-31", "amount": 20.0, "category": "Shopping", "description": "C", "notes": ""},
        ]

        trend_7 = get_recent_spending_trend(transactions, 7, end_date="2026-03-31")
        trend_30 = get_recent_spending_trend(transactions, 30, end_date="2026-03-31")

        self.assertEqual(len(trend_7), 7)
        self.assertEqual(len(trend_30), 30)
        self.assertEqual(trend_7["2026-03-31"], 20.0)
        self.assertAlmostEqual(sum(trend_7.values()), 45.0, places=2)

    def test_category_summary_by_day_week_month(self) -> None:
        transactions = [
            {"date": "2026-03-01", "amount": 12.0, "category": "Catering", "description": "A", "notes": ""},
            {"date": "2026-03-02", "amount": 8.0, "category": "Catering", "description": "B", "notes": ""},
            {"date": "2026-03-03", "amount": 20.0, "category": "Transport", "description": "C", "notes": ""},
        ]

        daily = get_category_summary_by_period(transactions, "day")
        weekly = get_category_summary_by_period(transactions, "week")
        monthly = get_category_summary_by_period(transactions, "month")

        self.assertEqual(daily["2026-03-01"]["Catering"], 12.0)
        self.assertTrue(any(key.startswith("2026-W") for key in weekly.keys()))
        self.assertEqual(monthly["2026-03"]["Transport"], 20.0)

    def test_consecutive_overspend_days_alert(self) -> None:
        transactions = [
            {"date": "2026-03-01", "amount": 60.0, "category": "meals", "description": "A", "notes": ""},
            {"date": "2026-03-02", "amount": 55.0, "category": "meals", "description": "B", "notes": ""},
            {"date": "2026-03-03", "amount": 45.0, "category": "meals", "description": "C", "notes": ""},
        ]
        rules = [
            {
                "category": "meals",
                "period": "daily",
                "threshold": 50.0,
                "alert_type": "exceed",
                "consecutive_days_threshold": 2,
            }
        ]

        alerts = check_budget_alerts(transactions, rules, include_consecutive=True)
        self.assertTrue(any("consecutive overspend days reached" in message for message in alerts))


if __name__ == "__main__":
    unittest.main()