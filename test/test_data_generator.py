from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.test_data_generator import generate_test_transaction_sets, generate_transactions


class TestDataGenerator(unittest.TestCase):
    def test_generate_transactions_with_edge_cases(self) -> None:
        rows = generate_transactions(
            count=20,
            start_date="2026-01-01",
            seed=7,
            include_edge_cases=True,
        )

        self.assertGreaterEqual(len(rows), 23)
        self.assertTrue(any(row["amount"] == 0.0 for row in rows))
        self.assertGreater(len({row["date"] for row in rows}), 1)

        positive_categories = {row["category"] for row in rows if row["amount"] > 0}
        self.assertGreater(len(positive_categories), 1)

    def test_generate_test_transaction_sets_contains_required_profiles(self) -> None:
        datasets = generate_test_transaction_sets(
            base_count=10,
            start_date="2026-01-01",
            seed=3,
        )

        self.assertEqual(set(datasets.keys()), {"realistic", "zero_spending", "all_uncategorized"})
        self.assertTrue(all(row["amount"] == 0.0 for row in datasets["zero_spending"]))
        self.assertTrue(all(row["category"] == "Others" for row in datasets["all_uncategorized"]))
        self.assertEqual(len(datasets["all_uncategorized"]), 10)


if __name__ == "__main__":
    unittest.main()
