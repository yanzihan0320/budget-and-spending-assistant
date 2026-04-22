from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stats import get_top_categories


class TestTopCategories(unittest.TestCase):
    def test_get_top_categories_independent(self) -> None:
        transactions = [
            {"date": "2026-03-01", "amount": 10.0, "category": "Catering", "description": "A", "notes": ""},
            {"date": "2026-03-02", "amount": 90.0, "category": "Shopping", "description": "B", "notes": ""},
            {"date": "2026-03-03", "amount": 40.0, "category": "Transport", "description": "C", "notes": ""},
            {"date": "2026-03-04", "amount": 15.0, "category": "Catering", "description": "D", "notes": ""},
            {"date": "2026-03-05", "amount": -5.0, "category": "Entertainment", "description": "E", "notes": ""},
        ]

        top3 = get_top_categories(transactions, top_n=3)
        self.assertEqual(top3, [("Shopping", 90.0), ("Transport", 40.0), ("Catering", 25.0)])


if __name__ == "__main__":
    unittest.main()
