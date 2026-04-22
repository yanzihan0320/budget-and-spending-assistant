from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import (
    CategoryManager,
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
DEFAULT_CATEGORY_CONFIG_FILE = DATA_DIR / "category_config.json"
REQUIRED_TRANSACTION_FIELDS = {"date", "amount", "category", "description"}


def _resolve_path(file_path: str | None, default_path: Path) -> Path:
    if not file_path:
        return default_path

    path = Path(file_path)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def load_category_config(file_path: str | None = None) -> list[str]:
    path = _resolve_path(file_path, DEFAULT_CATEGORY_CONFIG_FILE)
    if not path.exists():
        CategoryManager.clear_custom_categories()
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)
    except json.JSONDecodeError as error:
        print(f"[WARN] Malformed category config JSON in {path}: {error.msg}")
        CategoryManager.clear_custom_categories()
        return []
    except UnicodeDecodeError as error:
        print(f"[WARN] Could not decode category config file at {path}: {error}")
        CategoryManager.clear_custom_categories()
        return []
    except OSError as error:
        print(f"[WARN] Could not read category config file at {path}: {error}")
        CategoryManager.clear_custom_categories()
        return []

    if isinstance(raw_data, dict):
        raw_categories = raw_data.get("custom_categories", [])
    elif isinstance(raw_data, list):
        raw_categories = raw_data
    else:
        print(f"[WARN] Category config must be a JSON list or object with custom_categories: {path}")
        CategoryManager.clear_custom_categories()
        return []

    if not isinstance(raw_categories, list):
        print(f"[WARN] custom_categories must be a list in category config: {path}")
        CategoryManager.clear_custom_categories()
        return []

    normalized_categories: list[str] = []
    for index, value in enumerate(raw_categories, start=1):
        if not isinstance(value, str):
            print(f"[WARN] Skipping custom category at index {index}: expected string")
            continue

        category = value.strip()
        if not category:
            print(f"[WARN] Skipping custom category at index {index}: empty value")
            continue
        normalized_categories.append(category)

    CategoryManager.set_custom_categories(normalized_categories)
    return CategoryManager.get_all_categories()[len(CategoryManager.PREDEFINED):]


def load_transactions(file_path: str | None = None) -> list[dict]:
    load_category_config()
    path = _resolve_path(file_path, DEFAULT_TRANSACTIONS_FILE)
    if not path.exists():
        print(f"[INFO] Transactions file not found: {path}. Starting with empty data.")
        return []

    transactions: list[dict] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            header_fields = [field.strip() for field in (reader.fieldnames or []) if field]
            if not header_fields:
                print(f"[WARN] Transactions file is empty or missing a CSV header: {path}")
                return []

            if not REQUIRED_TRANSACTION_FIELDS.issubset(set(header_fields)):
                expected = ", ".join(sorted(REQUIRED_TRANSACTION_FIELDS))
                print(
                    f"[WARN] Malformed transactions file header in {path}. "
                    f"Expected at least: {expected}."
                )
                return []

            for line_number, row in enumerate(reader, start=2):
                try:
                    transaction = transaction_from_dict(dict(row))
                    transaction_dict = transaction_to_dict(transaction)
                except (TypeError, ValueError) as error:
                    print(f"[WARN] Skipping malformed transaction row at line {line_number}: {error}")
                    continue

                valid, message = validate_transaction(transaction_dict)
                if valid:
                    transactions.append(transaction_dict)
                else:
                    print(f"[WARN] Skipping invalid transaction row at line {line_number}: {message}")
    except csv.Error as error:
        print(f"[WARN] Could not parse transactions CSV at {path}: {error}")
        return []
    except UnicodeDecodeError as error:
        print(f"[WARN] Could not decode transactions file at {path}: {error}")
        return []
    except OSError as error:
        print(f"[WARN] Could not read transactions file at {path}: {error}")
        return []

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

    try:
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["date", "amount", "category", "description", "notes"],
            )
            writer.writeheader()
            writer.writerows(rows_to_write)
    except OSError as error:
        raise OSError(f"Could not write transactions file at {path}: {error}") from error


def load_budget_rules(file_path: str | None = None) -> list[dict]:
    load_category_config()
    path = _resolve_path(file_path, DEFAULT_BUDGET_RULES_FILE)
    if not path.exists():
        print(f"[INFO] Budget rules file not found: {path}. Starting with empty rules.")
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            raw_rules = json.load(file)
    except json.JSONDecodeError as error:
        print(f"[WARN] Malformed budget rules JSON in {path}: {error.msg}")
        return []
    except UnicodeDecodeError as error:
        print(f"[WARN] Could not decode budget rules file at {path}: {error}")
        return []
    except OSError as error:
        print(f"[WARN] Could not read budget rules file at {path}: {error}")
        return []

    if not isinstance(raw_rules, list):
        print(f"[WARN] Budget rules file must contain a JSON list: {path}")
        return []

    rules: list[dict] = []
    for index, row in enumerate(raw_rules, start=1):
        if not isinstance(row, dict):
            print(f"[WARN] Skipping malformed budget rule at index {index}: expected an object")
            continue

        try:
            rule = budget_rule_from_dict(row)
            rule_dict = budget_rule_to_dict(rule)
        except (TypeError, ValueError) as error:
            print(f"[WARN] Skipping malformed budget rule at index {index}: {error}")
            continue

        valid, message = validate_budget_rule(rule_dict)
        if valid:
            rules.append(rule_dict)
        else:
            print(f"[WARN] Skipping invalid budget rule at index {index}: {message}")

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

    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(rows_to_write, file, indent=2, ensure_ascii=False)
    except OSError as error:
        raise OSError(f"Could not write budget rules file at {path}: {error}") from error
