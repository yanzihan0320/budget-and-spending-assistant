from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from .models import PREDEFINED_CATEGORIES

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"


def generate_transactions(count: int = 50, start_date: str = "2026-01-01") -> list[dict]:
    start = date.fromisoformat(start_date)
    rows: list[dict] = []

    for index in range(count):
        day_offset = random.randint(0, 120)
        row_date = start + timedelta(days=day_offset)
        amount = round(random.uniform(5, 200), 2)
        category = random.choice(PREDEFINED_CATEGORIES)
        rows.append(
            {
                "date": row_date.isoformat(),
                "amount": amount,
                "category": category,
                "description": f"Generated transaction #{index + 1}",
                "notes": "",
            }
        )

    return rows


def save_generated_transactions(count: int = 50, output_file: str = "data/generated_transactions.csv") -> Path:
    output_path = ROOT_DIR / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = generate_transactions(count=count)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["date", "amount", "category", "description", "notes"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return output_path


if __name__ == "__main__":
    path = save_generated_transactions(50)
    print(f"Generated test data: {path}")
