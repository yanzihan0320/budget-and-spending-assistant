'''
models.py - Data models for Personal Budget and Spending Assistent

This module defines the core data structures used throughout the application:
- Transaction: spending records
- Budget: budget alert rules
- CategoryManagers: category validation and management
'''

from dataclasses import dataclass
from typing import Optional, List, Tuple
from datetime import datetime

class CategoryManagers:
    '''
    Manage transaction categories.

    Phase 1: Fixed category list only.
    Phase 2 (future): May support custom categories via config file.
    '''
    PREDEFINED = ['Catering', 'Transport', 'Shopping', 'Entertainment', 'Housing', 'Medical', 'Education', 'Others']

    @classmethod
    def get_predefined_categories(cls) -> List[str]:
        return cls.PREDEFINED.copy()
    
    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        return category in cls.PREDEFINED
    
    @classmethod
    def validate_category(cls, category: str) -> Tuple[bool, str]:
        if cls.is_valid_category(category):
            return True, ""
        return False, f"{category} is not a valid category. Allowed categories are: {', '.join(cls.PREDEFINED)}"
    
@dataclass
class Transaction:
    date: str
    amount: float
    category: str
    description: str
    notes: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.amount, int):
            self.amount = float(self.amount)

@dataclass
class Budget:
    category: str
    time_period: str
    threshold_value: float
    alert_type: str

    def __post_init__(self):
        if isinstance(self.threshold_value, int):
            self.threshold_value = float(self.threshold_value)

def validate_date(date_str: str) -> Tuple[bool, str]:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "Invalid date format '{date_str}'. Please use YYYY-MM-DD"
        
def validate_transaction(transaction: Transaction) -> Tuple[bool, List[str]]:
    errors = []

    # Date verification
    valid, msg = validate_date(transaction.date)
    if not valid:
        errors.append(msg)

    # Amount verification
    if transaction.amount <= 0:
        errors.append("Amount must be greater than zero, current value: {transaction.amount}")

    # Category verification
    valid, msg = CategoryManagers.validate_category(transaction.category)
    if not valid:
        errors.append(msg)

    # Description verification
    if transaction.description is None or transaction.description.strip() == "":
        errors.append("Description cannot be empty")
    elif len(transaction.description) > 100:
        errors.append("Description cannot be longer than 100 characters")

    # Notes verification
    if transaction.notes and len(transaction.notes) > 200:
        errors.append("Notes cannot be longer than 200 characters")

    return len(errors) == 0, errors

def validate_budget_rule(rule: Budget) -> Tuple[bool, List[str]]:
    errors = []

    # Valid time_period values
    valid_periods = ['day', 'week', 'month']
    if rule.time_period not in valid_periods:
        errors.append(f"Invalid time_period '{rule.time_period}'. Allowed values are: {', '.join(valid_periods)}")

    # Validate threshold
    if rule.threshold <= 0:
        errors.append("Threshold must be greater than zero, current value: {rule.threshold}")

    # Valid alert_type values
    valid_alert_types = ['over_threshold', 'over_ratio']
    if rule.alert_type not in valid_alert_types:
        errors.append(f"invalid alert_type '{rule.alert_type}'. Allowed values are: {', '.join(valid_alert_types)}")

    # Valid category exists
    valid, msg = CategoryManagers.validate_category(rule.category)
    if not valid:
        errors.append(msg)
    
    return len(errors) == 0, errors
    
def filter_by_category(transactions: List[Transaction], category: str) -> List[Transaction]:
    return [t for t in transactions if t.category == category]

def filter_by_date_range(transactions: List[Transaction],
                         start_date: str,
                         end_date: str) -> List[Transaction]:
    return [t for t in transactions if start_date <= t.date <= end_date]

def get_spending_summary(transactions: List[Transaction],period: str) -> dict:
    summary = {}
    for t in transactions:
        if period == 'day':
            key = t.date
        elif period == 'week':
            date_obj = datetime.strptime(t.date, '%Y-%m-%d')
            year, week, _ = date_obj
            key = f'{year}-W{week:02d}'
        elif period == 'month':
            key = t.date[:7]
        else:
            continue
        summary[key] = summary.get(key, 0) + t.amount
    return summary

# ========================================================================
# Dict = Dataclass Conversion Functions (for I/O layer)
# ========================================================================

def transaction_from_dict(data: dict) -> Transaction:
    '''
    Convert a dictionary to a Transaction object.
    
    Args:
        data: dict with keys: date, amount, category, description, notes (optional)
         
    Returns:
        Transaction object
    '''
    return Transaction(
        date=data["date"],
        amount=float(data["amount"]),
        category=data["category"],
        description=data["description"],
        notes=data.get("notes")
    )

def transaction_to_dict(t: Transaction) -> dict:
    '''
    Convert a Transaction object to a dictionary.

    Args:
        t: Transaction object

    Returns:
        dict with keys as CSV header
    '''
    return {
        "date": t.date,
        "amount": t.amount,
        "category": t.category,
        "description": t.description,
        "notes": t.notes
    }


def budget_from_dict(data: dict) -> Budget:
    '''
    Convert a dictionary to a Budget object.
    Handles legacy field names (time_period, threshold_value) and old enum values.
    
    Args:
        data: dict with keys: category, time_period, threshold_value, alert_type
         
    Returns:
        Budget object
    '''
    # Extract period (support legacy "time_period")
    period = data.get("period") or data.get("time_period", "month")
    # Apply mapping (daily->day, weekly->week, monthly->month)
    period_mapping = {
        "daily": "day", "weekly": "week", "monthly": "month",
        "day": "day", "week": "week", "month": "month"
    }
    period = period_mapping.get(period, "month")

    # Extract threshold (support legacy "threshold_value")
    threshold = data.get("threshold") or data.get("threshold_value", 0.0)

    # Extract alert_type (support legacy "exceed"/"percentage")
    alert_type = data.get("alert_type", "over_threshold")
    alert_mapping = {
        "exceed": "over_threshold",
        "percentage": "over_ratio",
        "over_threshold": "over_threshold",
        "over_ratio": "over_ratio",
    }
    alert_type = alert_mapping.get(alert_type, "over_threshold")

    return Budget(
        category=data["category"],
        time_period=period,
        threshold_value=float(threshold),
        alert_type=alert_type
    )


def budget_rule_to_dict(rule: Budget) -> dict:
    '''
    Convert a Budget object to a dictionary
    
    Args:
        rule: Budget object
        
    Returns:
        dict with standard field names
    '''
    return {
        "category": rule.category,
        "period": rule.period,
        "threshold": rule.threshold,
        "alert_type": rule.alert_type
    }


# ===============================================================
# Extend CategoryManager to match document interface
# ===============================================================

class CategoryManager:
    '''
    Managers transaction categories.
    Implements the interface required by the project document.
    '''

    PREDEFINED = ['Caterting', 'Transport', 'Shopping', 'Entertainment',
                  'Housing', 'Medical', 'Education', 'Others']
    
    # Internal storage for categories (Phase 2)
    _custom_categories = []

    @classmethod
    def get_all_categories(cls) -> list:
        '''Return all categories (predefined and custom).'''
        return cls.PREDEFINED.copy() + cls._custom_categories.copy()
    
    @classmethod
    def add_category(cls, name: str) -> None:
        '''
        Add a custom category.
        Phase 1: Only prints a warning; does not persist.
        Phase 2: Will save to config file.
        '''
        if name in cls.PREDEFINED:
            return # already exists
        if name not in cls._custom_categories:
            cls._custom_categories.append(name)
            # In phase 1, we don't save to disk, just keep in memory.
            print(f"[Info] Custom category '{name}' added (memory only).")

    @classmethod
    def is_valid(cls, category: str) -> bool:
        '''Check if category exists (predefinded or custom).'''
        return category in cls.get_all_categories()
    
    # Legacy alias for backward compatibility
    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        return cls.is_valid(category)
    
    @classmethod
    def validate_category(cls, category: str) -> tuple:
        '''Return (is_valid, error_message).'''
        if cls.is_valid(category):
            return True, ''
        return False, f"Invalid category '{category}'. Allowed: {','.join}"