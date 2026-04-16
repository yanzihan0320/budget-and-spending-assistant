from __future__ import annotations

from datetime import date

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

        anchor_date = str(raw_rule.get("start_date", "")).strip() or start_date or date.today().isoformat()
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


