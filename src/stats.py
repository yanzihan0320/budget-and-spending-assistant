from __future__ import annotations

from datetime import datetime

from .models import normalize_category, normalize_period


def get_spending_summary(transactions: list[dict], period: str | None = None) -> dict[str, float]:
    """
    Return a summary map.

    - If period is None, data is grouped by category.
    - If period is day/week/month, data is grouped by that period key.
    """
    if not period:
        return _group_by_category(transactions)
    return _group_by_period(transactions, period)


def get_period_summary(transactions: list[dict], period: str, start_date: str) -> dict:
    """Return total and category breakdown for one period window anchored at start_date."""
    try:
        anchor = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return {"total_spending": 0.0, "category_breakdown": {}}

    normalized_period = normalize_period(period)
    selected_rows = []
    for row in transactions:
        try:
            row_date = datetime.strptime(str(row.get("date", "")), "%Y-%m-%d").date()
        except ValueError:
            continue

        if normalized_period == "day" and row_date == anchor:
            selected_rows.append(row)
        elif normalized_period == "week":
            anchor_year, anchor_week, _ = anchor.isocalendar()
            row_year, row_week, _ = row_date.isocalendar()
            if anchor_year == row_year and anchor_week == row_week:
                selected_rows.append(row)
        elif normalized_period == "month" and row_date.year == anchor.year and row_date.month == anchor.month:
            selected_rows.append(row)

    category_breakdown = _group_by_category(selected_rows)
    return {
        "total_spending": round(sum(category_breakdown.values()), 2),
        "category_breakdown": category_breakdown,
    }


def filter_by_category(transactions: list[dict], category: str) -> list[dict]:
    target = normalize_category(category)
    return [row.copy() for row in transactions if normalize_category(str(row.get("category", ""))) == target]


def filter_by_date_range(transactions: list[dict], start_date: str, end_date: str) -> list[dict]:
    selected_rows: list[dict] = []
    for row in transactions:
        date_text = str(row.get("date", ""))
        if start_date <= date_text <= end_date:
            selected_rows.append(row.copy())
    return selected_rows


def get_top_categories(transactions: list[dict], top_n: int = 3) -> list[tuple[str, float]]:
    summary = _group_by_category(transactions)
    return sorted(summary.items(), key=lambda item: item[1], reverse=True)[:top_n]


def get_monthly_trend(transactions: list[dict]) -> dict[str, float]:
    trend: dict[str, float] = {}
    for row in transactions:
        date_text = str(row.get("date", ""))
        amount = row.get("amount", 0.0)
        if not isinstance(amount, (int, float)) or amount <= 0 or len(date_text) < 7:
            continue
        month_key = date_text[:7]
        trend[month_key] = round(trend.get(month_key, 0.0) + float(amount), 2)
    return trend


def _group_by_category(transactions: list[dict]) -> dict[str, float]:
    summary: dict[str, float] = {}
    for row in transactions:
        amount = row.get("amount", 0.0)
        if not isinstance(amount, (int, float)) or amount <= 0:
            continue
        category = normalize_category(str(row.get("category", "")).strip())
        summary[category] = round(summary.get(category, 0.0) + float(amount), 2)
    return summary


def _group_by_period(transactions: list[dict], period: str) -> dict[str, float]:
    summary: dict[str, float] = {}
    normalized_period = normalize_period(period)
    for row in transactions:
        amount = row.get("amount", 0.0)
        date_text = str(row.get("date", ""))

        if not isinstance(amount, (int, float)) or amount <= 0:
            continue

        try:
            row_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            continue

        if normalized_period == "day":
            key = row_date.isoformat()
        elif normalized_period == "week":
            year, week, _ = row_date.isocalendar()
            key = f"{year}-W{week:02d}"
        elif normalized_period == "month":
            key = f"{row_date.year}-{row_date.month:02d}"
        else:
            continue

        summary[key] = round(summary.get(key, 0.0) + float(amount), 2)
    return summary