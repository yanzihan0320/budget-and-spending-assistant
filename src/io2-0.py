import csv
import json
from pathlib import Path
import shutil


# ==================== Compatibility Mapping ====================
CATEGORY_MAP = {
    "meals": "Catering",
    "transport": "Transport",
    "shopping": "Shopping"
}
PERIOD_MAP = {
    "daily": "day",
    "weekly": "week",
    "monthly": "month"
}
ALERT_TYPE_MAP = {
    "exceed": "over_threshold",
    "percentage": "over_ratio"
}


def load_transactions(filepath: str = "transactions.csv") -> tuple[list[dict], str]:
    """Return (transactions_list, message)"""
    transactions = []
    try:
        with open(filepath, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return [], f"Warning: {filepath} is an empty file"
            for row in reader:
                row = dict(row)
                cat = row.get('category', '')
                if cat in CATEGORY_MAP:
                    row['category'] = CATEGORY_MAP[cat]
                try:
                    row['amount'] = float(row.get('amount', 0))
                    transactions.append(row)
                except:
                    continue
        return transactions, f"Successfully loaded {len(transactions)} transaction records"
    except FileNotFoundError:
        return [], f"File not found: {filepath}"
    except Exception as e:
        return [], f"Failed to load transactions: {e}"


def save_transactions(filepath: str = "transactions.csv", transactions: list[dict] = None) -> tuple[bool, str]:
    """Return (success, message)"""
    if not transactions:
        return False, "No data to save"
    try:
        if Path(filepath).exists():
            shutil.copy2(filepath, f"{filepath}.bak")
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['date', 'amount', 'category', 'description', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(transactions)
        return True, f"Successfully saved {len(transactions)} records"
    except Exception as e:
        return False, f"Failed to save: {e}"


def load_budget_rules(filepath: str = "budget_rules.json") -> tuple[list[dict], str]:
    """Return (rules_list, message)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        mapped_rules = []
        for r in rules:
            r = dict(r)
            p = r.get("period") or r.get("time_period")
            if p in PERIOD_MAP:
                r["period"] = PERIOD_MAP[p]
            a = r.get("alert_type")
            if a in ALERT_TYPE_MAP:
                r["alert_type"] = ALERT_TYPE_MAP[a]
            mapped_rules.append(r)
        return mapped_rules, f"Successfully loaded {len(mapped_rules)} budget rules"
    except FileNotFoundError:
        return [], f"File not found: {filepath}"
    except Exception as e:
        return [], f"Failed to load budget rules: {e}"


def save_budget_rules(filepath: str = "budget_rules.json", rules: list[dict] = None) -> tuple[bool, str]:
    """Return (success, message)"""
    if not rules:
        return False, "No rules to save"
    try:
        if Path(filepath).exists():
            shutil.copy2(filepath, f"{filepath}.bak")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4, ensure_ascii=False)
        return True, f"Successfully saved {len(rules)} rules"
    except Exception as e:
        return False, f"Failed to save: {e}"