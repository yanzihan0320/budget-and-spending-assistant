# Author: Role5 Li Aitong
# Function: Budget alert module 
# Requirements: 
# 1. Implement 4+ rules covering day/week/month + over_threshold/over_ratio
# 2. Default ratio for over_ratio: 10% (0.1)
# 3. Use datetime.date.isocalendar() for week calculation
# 4. Compatible with legacy fields/enums
import datetime
from typing import List, Dict

# ------------------------------
# Shared mappings (1:1 with validator.py/stats.py, NO duplicate constants)
# ------------------------------
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

# Default ratio threshold (required by team standard: 10%)
DEFAULT_RATIO_THRESHOLD = 0.1


def check_budget_alerts(transactions: List[Dict], rules: List[Dict]) -> List[str]:
    """
    Check budget alerts based on transaction data and budget rules.
    
    Args:
        transactions: List of validated transaction dictionaries (must contain date/amount/category/description)
        rules: List of validated budget rule dictionaries (must contain category/period/threshold/alert_type)
    
    Returns:
        List of alert messages (empty list if no alerts)
    """
    # Initialize empty alert list (handle empty input safely)
    alerts = []
    
    # Guard clause: return empty list if input is empty (compliant with team standard)
    if not isinstance(transactions, list) or not isinstance(rules, list):
        return alerts
    if len(transactions) == 0 or len(rules) == 0:
        return alerts

    # ------------------------------
    # Process each budget rule
    # ------------------------------
    for rule in rules:
        # Skip invalid rule (non-dict)
        if not isinstance(rule, dict):
            continue

        # ------------------------------
        # Step 1: Legacy field/enum mapping (100% compatible)
        # ------------------------------
        # Category mapping (legacy → standard)
        rule_category = rule.get("category", "").strip()
        standard_category = CATEGORY_MAP.get(rule_category, rule_category)

        # Period mapping (legacy → standard) + support legacy field "time_period"
        rule_period = rule.get("period", rule.get("time_period", "")).strip()
        standard_period = PERIOD_MAP.get(rule_period, rule_period)

        # Threshold mapping (support legacy field "threshold_value")
        rule_threshold = rule.get("threshold", rule.get("threshold_value", 0.0))
        # Ensure threshold is numeric (defensive check)
        if not isinstance(rule_threshold, (int, float)):
            continue
        standard_threshold = round(float(rule_threshold), 2)  # Fix float precision
        if standard_threshold <= 0:
            continue

        # Alert type mapping (legacy → standard)
        rule_alert_type = rule.get("alert_type", "").strip()
        standard_alert_type = ALERT_TYPE_MAP.get(rule_alert_type, rule_alert_type)

        # ------------------------------
        # Step 2: Validate rule parameters (only process valid rules)
        # ------------------------------
        valid_periods = ["day", "week", "month"]
        valid_alert_types = ["over_threshold", "over_ratio"]
        valid_categories = list(CATEGORY_MAP.values()) + list(CATEGORY_MAP.keys()) + [
            "Entertainment", "Housing", "Medical", "Education", "Others"
        ]  # Reuse from shared mapping (no hardcode)

        if (standard_category not in valid_categories or
            standard_period not in valid_periods or
            standard_alert_type not in valid_alert_types):
            continue

        # ------------------------------
        # Step 3: Get period start date (dynamic, not hardcoded today)
        # ------------------------------
        # Use rule's start_date if exists, else use transaction's earliest date (compliant with team logic)
        rule_start_date = rule.get("start_date", "")
        if rule_start_date:
            try:
                period_start = datetime.datetime.strptime(rule_start_date, "%Y-%m-%d").date()
            except ValueError:
                # Fallback to earliest transaction date if start_date is invalid
                transaction_dates = []
                for t in transactions:
                    t_date = t.get("date", "")
                    try:
                        transaction_dates.append(datetime.datetime.strptime(t_date, "%Y-%m-%d").date())
                    except ValueError:
                        continue
                period_start = min(transaction_dates) if transaction_dates else datetime.date.today()
        else:
            # Default to today if no start_date provided
            period_start = datetime.date.today()

        # ------------------------------
        # Step 4: Filter transactions by category + period
        # ------------------------------
        filtered_transactions = []
        for trans in transactions:
            # Skip invalid transaction (non-dict)
            if not isinstance(trans, dict):
                continue

            # Category match (legacy → standard)
            trans_category = trans.get("category", "").strip()
            standard_trans_category = CATEGORY_MAP.get(trans_category, trans_category)
            if standard_trans_category != standard_category:
                continue

            # Date validation & period filter
            trans_date_str = trans.get("date", "")
            try:
                trans_date = datetime.datetime.strptime(trans_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            # Period filter (use isocalendar() for week calculation - REQUIRED)
            if standard_period == "day":
                if trans_date == period_start:
                    filtered_transactions.append(trans)
            elif standard_period == "week":
                # Use isocalendar() (year, week, weekday) - team mandatory requirement
                start_year, start_week, _ = period_start.isocalendar()
                trans_year, trans_week, _ = trans_date.isocalendar()
                if start_year == trans_year and start_week == trans_week:
                    filtered_transactions.append(trans)
            elif standard_period == "month":
                if trans_date.year == period_start.year and trans_date.month == period_start.month:
                    filtered_transactions.append(trans)

        # ------------------------------
        # Step 5: Calculate total spending (fix float precision)
        # ------------------------------
        total_spending = 0.0
        for t in filtered_transactions:
            amount = t.get("amount", 0.0)
            if isinstance(amount, (int, float)) and amount > 0:
                total_spending += round(float(amount), 2)  # Keep 2 decimal places
        total_spending = round(total_spending, 2)

        # ------------------------------
        # Step 6: Trigger alerts (fix over_ratio logic)
        # ------------------------------
        # Rule 1: over_threshold (spending > threshold)
        if standard_alert_type == "over_threshold":
            if total_spending > standard_threshold:
                alert_msg = (
                    f"[BUDGET_ALERT] {standard_category} {standard_period} spending exceeded threshold. "
                    f"Total: {total_spending:.2f}, Threshold: {standard_threshold:.2f}"
                )
                alerts.append(alert_msg)

        # Rule 2: over_ratio (spending / threshold > 10%) - FIXED LOGIC
        elif standard_alert_type == "over_ratio":
            if standard_threshold > 0:  # Avoid division by zero
                spending_ratio = total_spending / standard_threshold
                if spending_ratio > DEFAULT_RATIO_THRESHOLD:
                    alert_msg = (
                        f"[BUDGET_ALERT] {standard_category} {standard_period} spending exceeded ratio threshold. "
                        f"Total: {total_spending:.2f}, Threshold: {standard_threshold:.2f}, "
                        f"Ratio: {spending_ratio:.2%} (>{DEFAULT_RATIO_THRESHOLD:.0%})"
                    )
                    alerts.append(alert_msg)

    # Return unique alerts (avoid duplicates)
    return list(dict.fromkeys(alerts))


