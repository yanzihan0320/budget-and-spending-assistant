# Author: role 5 Li Aitong
# Function: Data validation for transaction and budget rule

# Allowed consumption categories 
CATEGORY_LIST = ["Catering", "Transportation", "Shopping", "Entertainment", 
                 "Housing", "Medical", "Education", "Others"]

def validate_transaction(transaction):

    # 1. Validate date format: YYYY-MM-DD
    date = transaction.get("date", "")
    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        return False, "Invalid date format, must be YYYY-MM-DD"

    # 2. Validate amount is a positive number
    amount = transaction.get("amount", 0)
    if not isinstance(amount, (int, float)) or amount <= 0:
        return False, "Amount must be a number greater than 0"

    # 3. Validate category is in the allowed list
    category = transaction.get("category", "")
    if category not in CATEGORY_LIST:
        return False, f"Category [{category}] is not in the allowed list"

    # All validations passed
    return True, "Validation passed"

def validate_budget_rule(rule):
 
    # 1. Validate threshold is a positive number
    threshold = rule.get("threshold", 0)
    if not isinstance(threshold, (int, float)) or threshold <= 0:
        return False, "Budget threshold must be greater than 0"

    # 2. Validate time period is limited to day/week/month
    period = rule.get("time_period", "")
    if period not in ["day", "week", "month"]:
        return False, "Time period can only be day / week / month"

    # 3. Validate alert type is limited to over_threshold/over_ratio
    alert_type = rule.get("alert_type", "")
    if alert_type not in ["over_threshold", "over_ratio"]:
        return False, "Alert type can only be over_threshold / over_ratio"

    # All validations passed
    return True, "Validation passed"