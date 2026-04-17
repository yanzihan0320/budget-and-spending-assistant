from __future__ import annotations

from datetime import date, datetime

from .models import budget_rule_from_dict, normalize_category
from .stats import filter_by_category, get_period_summary

DEFAULT_RATIO_THRESHOLD = 0.10


def check_budget_alerts(transactions: list[dict], rules: list[dict], start_date: str | None = None) -> list[str]:
    alerts: list[str] = []
    if not transactions or not rules:
        return alerts

    for raw_rule in rules:
        try:
            rule = budget_rule_from_dict(raw_rule)
        except (TypeError, ValueError):
            continue

        category_transactions = filter_by_category(transactions, rule.category)
        if not category_transactions:
            continue

        anchor_date = _resolve_anchor_date(raw_rule, start_date, category_transactions)
        if not anchor_date:
            continue

        period_summary = get_period_summary(category_transactions, rule.period, anchor_date)
        total_spending = float(period_summary["total_spending"])

        if rule.alert_type == "over_threshold" and total_spending > rule.threshold:
            alerts.append(
                f"[BUDGET ALERT] {normalize_category(rule.category)} {rule.period} spending exceeded threshold. "
                f"Total={total_spending:.2f}, Threshold={rule.threshold:.2f}"
            )

        if rule.alert_type == "over_ratio" and rule.threshold > 0:
            ratio = total_spending / rule.threshold
            if ratio > DEFAULT_RATIO_THRESHOLD:
                alerts.append(
                    f"[BUDGET ALERT] {normalize_category(rule.category)} {rule.period} spending ratio exceeded {DEFAULT_RATIO_THRESHOLD:.0%}. "
                    f"Total={total_spending:.2f}, Threshold={rule.threshold:.2f}, Ratio={ratio:.2%}"
                )

    return alerts


def _parse_date(date_text: str) -> date | None:
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


def _resolve_anchor_date(raw_rule: dict, explicit_start_date: str | None, category_transactions: list[dict]) -> str | None:
    # Priority order: rule start_date -> caller-provided start_date -> earliest date in this category.
    candidates = [
        str(raw_rule.get("start_date", "")).strip(),
        str(explicit_start_date or "").strip(),
    ]

    for candidate in candidates:
        parsed = _parse_date(candidate)
        if parsed is not None:
            return parsed.isoformat()

    transaction_dates = []
    for row in category_transactions:
        parsed = _parse_date(str(row.get("date", "")).strip())
        if parsed is not None:
            transaction_dates.append(parsed)

    if not transaction_dates:
        return None

    return min(transaction_dates).isoformat()


