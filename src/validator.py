from __future__ import annotations

from datetime import datetime

from .models import (
    CategoryManager,
    VALID_ALERT_TYPES,
    VALID_PERIODS,
    normalize_alert_type,
    normalize_category,
    normalize_period,
)


def validate_date(date_str: str) -> tuple[bool, str]:
    if not date_str:
        return False, "Date cannot be empty."

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, "Validation passed"
    except ValueError:
        return False, "Invalid date format. Expected YYYY-MM-DD."


def validate_transaction(transaction: dict) -> tuple[bool, str]:
    valid, message = validate_date(str(transaction.get("date", "")).strip())
    if not valid:
        return False, message

    amount = transaction.get("amount", 0)
    if not isinstance(amount, (int, float)):
        return False, "Amount must be numeric."
    if float(amount) <= 0:
        return False, "Amount must be greater than 0."

    category = normalize_category(str(transaction.get("category", "")).strip())
    if not CategoryManager.is_valid_category(category):
        return False, f"Invalid category: {category}."

    description = str(transaction.get("description", "")).strip()
    if not description:
        return False, "Description cannot be empty."

    return True, "Validation passed"


def validate_budget_rule(rule: dict) -> tuple[bool, str]:
    category = normalize_category(str(rule.get("category", "")).strip())
    if not CategoryManager.is_valid_category(category):
        return False, f"Invalid category: {category}."

    period = normalize_period(str(rule.get("period", rule.get("time_period", "")).strip()))
    if period not in VALID_PERIODS:
        return False, "Period must be one of: day, week, month."

    threshold = rule.get("threshold", rule.get("threshold_value", 0))
    if not isinstance(threshold, (int, float)):
        return False, "Threshold must be numeric."
    if float(threshold) <= 0:
        return False, "Threshold must be greater than 0."

    alert_type = normalize_alert_type(str(rule.get("alert_type", "")).strip())
    if alert_type not in VALID_ALERT_TYPES:
        return False, "Alert type must be over_threshold or over_ratio."

    return True, "Validation passed"


def validate_rule(rule: dict) -> tuple[bool, str]:
    return validate_budget_rule(rule)


