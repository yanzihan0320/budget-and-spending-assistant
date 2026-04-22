from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from .models import PREDEFINED_CATEGORIES

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
FIELDNAMES = ["date", "amount", "category", "description", "notes"]

CATEGORY_AMOUNT_RANGES = {
    "Catering": (15.0, 120.0),
    "Transport": (5.0, 60.0),
    "Shopping": (30.0, 400.0),
    "Entertainment": (20.0, 180.0),
    "Housing": (80.0, 900.0),
    "Medical": (20.0, 300.0),
    "Education": (30.0, 250.0),
    "Others": (10.0, 150.0),
}

CATEGORY_DESCRIPTIONS = {
    "Catering": ["Lunch", "Dinner", "Coffee", "Snacks"],
    "Transport": ["Bus fare", "MTR", "Taxi", "Parking"],
    "Shopping": ["Groceries", "Electronics", "Household items", "Clothes"],
    "Entertainment": ["Movie", "Streaming subscription", "Gaming", "Concert"],
    "Housing": ["Rent", "Utility bill", "Home supplies", "Maintenance"],
    "Medical": ["Clinic", "Medicine", "Check-up", "Dental"],
    "Education": ["Books", "Course fee", "Printing", "Learning platform"],
    "Others": ["Misc expense", "Gift", "Service fee", "Other"],
}


def generate_transactions(
    count: int = 50,
    start_date: str = "2026-01-01",
    seed: int | None = None,
    include_edge_cases: bool = False,
    force_uncategorized: bool = False,
) -> list[dict]:
    rng = random.Random(seed)
    start = date.fromisoformat(start_date)
    rows: list[dict] = []
    categories = ["Others"] if force_uncategorized else PREDEFINED_CATEGORIES

    for index in range(count):
        day_offset = rng.randint(0, 120)
        row_date = start + timedelta(days=day_offset)
        category = rng.choice(categories)
        amount_min, amount_max = CATEGORY_AMOUNT_RANGES.get(category, (5.0, 200.0))
        amount = round(rng.uniform(amount_min, amount_max), 2)
        description = rng.choice(CATEGORY_DESCRIPTIONS.get(category, ["Generated expense"]))

        rows.append(
            {
                "date": row_date.isoformat(),
                "amount": amount,
                "category": category,
                "description": description,
                "notes": "Generated sample",
            }
        )

    if include_edge_cases:
        rows.extend(_generate_edge_case_rows(start_date))

    rows.sort(key=lambda row: row["date"])
    return rows


def generate_test_transaction_sets(
    base_count: int = 50,
    start_date: str = "2026-01-01",
    seed: int | None = None,
) -> dict[str, list[dict]]:
    base_seed = seed if seed is not None else 2026
    return {
        "realistic": generate_transactions(
            count=base_count,
            start_date=start_date,
            seed=base_seed,
            include_edge_cases=False,
        ),
        "zero_spending": _generate_zero_spending_rows(start_date=start_date, days=7),
        "all_uncategorized": generate_transactions(
            count=base_count,
            start_date=start_date,
            seed=base_seed + 1,
            force_uncategorized=True,
        ),
    }


def save_generated_transactions(
    count: int = 50,
    output_file: str = "data/generated_transactions.csv",
    seed: int | None = None,
    include_edge_cases: bool = False,
) -> Path:
    output_path = ROOT_DIR / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = generate_transactions(
        count=count,
        seed=seed,
        include_edge_cases=include_edge_cases,
    )
    _write_transactions_csv(output_path, rows)

    return output_path


def save_generated_transaction_sets(
    output_dir: str = "data/generated_transaction_sets",
    base_count: int = 50,
    start_date: str = "2026-01-01",
    seed: int | None = None,
) -> dict[str, Path]:
    rows_by_set = generate_test_transaction_sets(
        base_count=base_count,
        start_date=start_date,
        seed=seed,
    )
    output_dir_path = ROOT_DIR / output_dir
    output_dir_path.mkdir(parents=True, exist_ok=True)

    saved_paths: dict[str, Path] = {}
    for dataset_name, rows in rows_by_set.items():
        file_path = output_dir_path / f"{dataset_name}.csv"
        _write_transactions_csv(file_path, rows)
        saved_paths[dataset_name] = file_path

    return saved_paths


def _write_transactions_csv(output_path: Path, rows: list[dict]) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _generate_edge_case_rows(start_date: str) -> list[dict]:
    start = date.fromisoformat(start_date)
    rows: list[dict] = []
    for index in range(3):
        rows.append(
            {
                "date": (start + timedelta(days=index)).isoformat(),
                "amount": 0.0,
                "category": "Others",
                "description": f"Edge zero spending #{index + 1}",
                "notes": "edge_case=zero_spending",
            }
        )
    return rows


def _generate_zero_spending_rows(start_date: str, days: int = 7) -> list[dict]:
    start = date.fromisoformat(start_date)
    rows: list[dict] = []
    for day_index in range(days):
        rows.append(
            {
                "date": (start + timedelta(days=day_index)).isoformat(),
                "amount": 0.0,
                "category": "Others",
                "description": f"Zero spending day #{day_index + 1}",
                "notes": "edge_case=zero_spending",
            }
        )
    return rows


if __name__ == "__main__":
    path = save_generated_transactions(50, include_edge_cases=True)
    print(f"Generated test data: {path}")

    saved_sets = save_generated_transaction_sets(base_count=30)
    for name, saved_path in saved_sets.items():
        print(f"Generated {name} dataset: {saved_path}")
