# Author: Role5 Li Aitong
# Statistics module for COMP1110 Budget Assistant
# Fully compliant with team technical standard

import datetime
from typing import List, Dict

# Use SAME mapping as validator.py (NO private constants)
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


def get_spending_summary(transactions: List[Dict]) -> Dict[str, float]:
    """Calculate total spending grouped by category"""
    summary = {}
    for t in transactions:
        cat = t.get("category", "").strip()
        cat = CATEGORY_MAP.get(cat, cat)
        amt = t.get("amount", 0.0)
        if isinstance(amt, (int, float)) and amt > 0:
            summary[cat] = summary.get(cat, 0.0) + round(amt, 2)
    return summary


def get_period_summary(transactions: List[Dict], period: str, start_date: str) -> Dict:
    """
    Get summary for day/week/month.
    Week calculation uses datetime.isocalendar() (mandatory)
    """
    # Safe parse start date
    try:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return {"total_spending": 0.0, "category_breakdown": {}}

    period = PERIOD_MAP.get(period.strip().lower(), period.strip().lower())
    filtered = []

    for t in transactions:
        d_str = t.get("date", "")
        amt = t.get("amount", 0.0)
        if not d_str or not isinstance(amt, (int, float)) or amt <= 0:
            continue

        try:
            d = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Match period (strictly follow team standard)
        if period == "day":
            if d == start:
                filtered.append(t)
        elif period == "week":
            s_year, s_week, _ = start.isocalendar()
            t_year, t_week, _ = d.isocalendar()
            if s_year == t_year and s_week == t_week:
                filtered.append(t)
        elif period == "month":
            if d.year == start.year and d.month == start.month:
                filtered.append(t)

    breakdown = get_spending_summary(filtered)
    total = round(sum(breakdown.values()), 2)
    return {
        "total_spending": total,
        "category_breakdown": breakdown
    }


def filter_by_category(transactions: List[Dict], category: str) -> List[Dict]:
    """Filter transactions by category (legacy compatible)"""
    target = CATEGORY_MAP.get(category.strip(), category.strip())
    result = []
    for t in transactions:
        cat = t.get("category", "").strip()
        cat = CATEGORY_MAP.get(cat, cat)
        if cat == target:
            result.append(t.copy())  # Safe copy
    return result