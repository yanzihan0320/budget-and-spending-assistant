from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import (
    budget_rule_from_dict,
    budget_rule_to_dict,
    transaction_from_dict,
    transaction_to_dict,
)
from .validator import validate_budget_rule, validate_transaction

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DEFAULT_TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
DEFAULT_BUDGET_RULES_FILE = DATA_DIR / "budget_rules.json"


def _resolve_path(file_path: str | None, default_path: Path) -> Path:
    if not file_path:
        return default_path

    path = Path(file_path)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def load_transactions(file_path: str | None = None) -> list[dict]:
    path = _resolve_path(file_path, DEFAULT_TRANSACTIONS_FILE)
    if not path.exists():
        return []

    transactions: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            transaction = transaction_from_dict(dict(row))
            transaction_dict = transaction_to_dict(transaction)
            valid, _ = validate_transaction(transaction_dict)
            if valid:
                transactions.append(transaction_dict)
    return transactions


def save_transactions(transactions: list[dict], file_path: str | None = None) -> None:
    path = _resolve_path(file_path, DEFAULT_TRANSACTIONS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows_to_write: list[dict] = []
    for row in transactions:
        transaction = transaction_from_dict(row)
        transaction_dict = transaction_to_dict(transaction)
        valid, message = validate_transaction(transaction_dict)
        if not valid:
            raise ValueError(f"Invalid transaction: {message}")
        rows_to_write.append(transaction_dict)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["date", "amount", "category", "description", "notes"],
        )
        writer.writeheader()
        writer.writerows(rows_to_write)


def load_budget_rules(file_path: str | None = None) -> list[dict]:
    path = _resolve_path(file_path, DEFAULT_BUDGET_RULES_FILE)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        raw_rules = json.load(file)

    rules: list[dict] = []
    for row in raw_rules:
        rule = budget_rule_from_dict(row)
        rule_dict = budget_rule_to_dict(rule)
        valid, _ = validate_budget_rule(rule_dict)
        if valid:
            rules.append(rule_dict)
    return rules


def save_budget_rules(rules: list[dict], file_path: str | None = None) -> None:
    path = _resolve_path(file_path, DEFAULT_BUDGET_RULES_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows_to_write: list[dict] = []
    for row in rules:
        rule = budget_rule_from_dict(row)
        rule_dict = budget_rule_to_dict(rule)
        valid, message = validate_budget_rule(rule_dict)
        if not valid:
            raise ValueError(f"Invalid budget rule: {message}")
        rows_to_write.append(rule_dict)

    with path.open("w", encoding="utf-8") as file:
        json.dump(rows_to_write, file, indent=2, ensure_ascii=False)
