from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

PREDEFINED_CATEGORIES = [
    "Catering",
    "Transport",
    "Shopping",
    "Entertainment",
    "Housing",
    "Medical",
    "Education",
    "Others",
]

LEGACY_CATEGORY_MAP = {
    "meals": "Catering",
    "transport": "Transport",
    "shopping": "Shopping",
}

LEGACY_PERIOD_MAP = {
    "daily": "day",
    "weekly": "week",
    "monthly": "month",
}

LEGACY_ALERT_TYPE_MAP = {
    "exceed": "over_threshold",
    "percentage": "over_ratio",
}

VALID_PERIODS = {"day", "week", "month"}
VALID_ALERT_TYPES = {"over_threshold", "over_ratio"}


def normalize_category(category: str) -> str:
    return LEGACY_CATEGORY_MAP.get(category.strip(), category.strip())


def normalize_period(period: str) -> str:
    return LEGACY_PERIOD_MAP.get(period.strip(), period.strip())


def normalize_alert_type(alert_type: str) -> str:
    return LEGACY_ALERT_TYPE_MAP.get(alert_type.strip(), alert_type.strip())


@dataclass
class Transaction:
    date: str
    amount: float
    category: str
    description: str
    notes: Optional[str] = ""


@dataclass
class BudgetRule:
    category: str
    period: str
    threshold: float
    alert_type: str
    ratio_threshold: Optional[float] = None
    consecutive_days_threshold: Optional[int] = None


# Compatibility alias for older code paths.
Budget = BudgetRule


class CategoryManager:
    PREDEFINED = PREDEFINED_CATEGORIES.copy()
    _custom_categories: list[str] = []

    @classmethod
    def get_all_categories(cls) -> list[str]:
        return cls.PREDEFINED + cls._custom_categories

    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        return normalize_category(category) in cls.get_all_categories()

    @classmethod
    def add_category(cls, category: str) -> None:
        normalized = normalize_category(category)
        if normalized not in cls.PREDEFINED and normalized not in cls._custom_categories:
            cls._custom_categories.append(normalized)

    @classmethod
    def set_custom_categories(cls, categories: list[str]) -> None:
        cls._custom_categories = []
        for category in categories:
            cls.add_category(category)

    @classmethod
    def clear_custom_categories(cls) -> None:
        cls._custom_categories = []


def transaction_from_dict(data: dict) -> Transaction:
    return Transaction(
        date=str(data.get("date", "")).strip(),
        amount=float(data.get("amount", 0.0)),
        category=normalize_category(str(data.get("category", "")).strip()),
        description=str(data.get("description", "")).strip(),
        notes=str(data.get("notes", "")).strip(),
    )


def transaction_to_dict(transaction: Transaction) -> dict:
    return {
        "date": transaction.date,
        "amount": float(transaction.amount),
        "category": normalize_category(transaction.category),
        "description": transaction.description,
        "notes": transaction.notes or "",
    }


def budget_rule_from_dict(data: dict) -> BudgetRule:
    raw_period = str(data.get("period", data.get("time_period", ""))).strip()
    raw_threshold = data.get("threshold", data.get("threshold_value", 0.0))
    raw_alert_type = str(data.get("alert_type", "")).strip()
    raw_ratio_threshold = data.get("ratio_threshold")
    raw_consecutive_threshold = data.get("consecutive_days_threshold")

    ratio_threshold = None
    if raw_ratio_threshold not in (None, ""):
        ratio_threshold = float(raw_ratio_threshold)

    consecutive_days_threshold = None
    if raw_consecutive_threshold not in (None, ""):
        consecutive_days_threshold = int(raw_consecutive_threshold)

    return BudgetRule(
        category=normalize_category(str(data.get("category", "")).strip()),
        period=normalize_period(raw_period),
        threshold=float(raw_threshold),
        alert_type=normalize_alert_type(raw_alert_type),
        ratio_threshold=ratio_threshold,
        consecutive_days_threshold=consecutive_days_threshold,
    )


def budget_rule_to_dict(rule: BudgetRule) -> dict:
    rule_dict = {
        "category": normalize_category(rule.category),
        "period": normalize_period(rule.period),
        "threshold": float(rule.threshold),
        "alert_type": normalize_alert_type(rule.alert_type),
    }

    if rule.ratio_threshold is not None:
        rule_dict["ratio_threshold"] = float(rule.ratio_threshold)
    if rule.consecutive_days_threshold is not None:
        rule_dict["consecutive_days_threshold"] = int(rule.consecutive_days_threshold)

    return rule_dict


# Compatibility alias for older function names.
budget_from_dict = budget_rule_from_dict
