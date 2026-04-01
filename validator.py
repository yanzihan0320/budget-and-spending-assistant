from datetime import datetime
from typing import tuple

# Standard category list (FROM TEAM STANDARD, NO CHANGE)
CATEGORY_LIST = [
    "Catering", "Transport", "Shopping", "Entertainment",
    "Housing", "Medical", "Education", "Others"
]

# Old format → Standard format mapping
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

def validate_transaction(transaction: dict) -> tuple[bool, str]:
    data = transaction.copy()

    # Date check
    date = data.get("date", "")
    if not date:
        return False, "Date cannot be empty"
    try:
        datetime.strptime(date, "%Y-%-%d")
    except ValueError:
        return False, "Invalid date format, must be YYYY-MM-DD"

    # Amount check
    amount = data.get("amount", 0)
    if not isinstance(amount, (int, float)):
        return False, "Amount must be a number"
    if amount <= 0:
        return False, "Amount must be greater than 0"

    # Category check
    category = data.get("category", "")
    cat_std = CATEGORY_MAP.get(category, category)
    if cat_std not in CATEGORY_LIST:
        return False, f"Category [{category}] is invalid"

    # Description check
    desc = data.get("description", "").strip()
    if not desc:
        return False, "Description cannot be empty"

    return True, "Validation passed"

def validate_budget_rule(rule: dict) -> tuple[bool, str]:
    data = rule.copy()

    period = data.get("period", data.get("time_period", ""))
    threshold = data.get("threshold", data.get("threshold_value", 0))
    alert_type = data.get("alert_type", "")
    category = data.get("category", "")

    # Threshold
    if not isinstance(threshold, (int, float)):
        return False, "Threshold must be a number"
    if threshold <= 0:
        return False, "Threshold must be greater than 0"

    # Period
    period_std = PERIOD_MAP.get(period, period)
    if period_std not in ["day", "week", "month"]:
        return False, "Period must be day/week/month"

    # Alert type
    alert_std = ALERT_TYPE_MAP.get(alert_type, alert_type)
    if alert_std not in ["over_threshold", "over_ratio"]:
        return False, "Alert type must be over_threshold/over_ratio"

    # Category
    cat_std = CATEGORY_MAP.get(category, category)
    if cat_std not in CATEGORY_LIST:
        return False, f"Category [{category}] is invalid"

    return True, "Validation passed"


