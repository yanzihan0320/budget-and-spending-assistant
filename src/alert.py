from __future__ import annotations

from datetime import date, datetime

from .models import budget_rule_from_dict, normalize_category
from .stats import filter_by_category, get_period_summary, get_spending_summary

DEFAULT_RATIO_THRESHOLD = 0.10
DEFAULT_CONSECUTIVE_DAYS_THRESHOLD = 2


def check_budget_alerts(
    transactions: list[dict],
    rules: list[dict],
    start_date: str | None = None,
    include_consecutive: bool = False,
) -> list[str]:
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

        period_totals = _resolve_period_totals(raw_rule, category_transactions, rule.period, start_date)
        if not period_totals:
            continue

        if rule.alert_type == "over_threshold":
            for period_key, spending in sorted(period_totals.items()):
                if spending > rule.threshold:
                    alerts.append(
                        f"[BUDGET ALERT] {normalize_category(rule.category)} {rule.period} spending exceeded threshold. "
                        f"Period={period_key}, Total={spending:.2f}, Threshold={rule.threshold:.2f}"
                    )

            if include_consecutive and rule.period == "day":
                daily_totals = get_spending_summary(category_transactions, "day")
                consecutive_min = _safe_int(
                    raw_rule.get("consecutive_days_threshold", DEFAULT_CONSECUTIVE_DAYS_THRESHOLD),
                    DEFAULT_CONSECUTIVE_DAYS_THRESHOLD,
                )
                max_streak, overspend_days = _count_consecutive_overspend_days(daily_totals, rule.threshold)
                if max_streak >= consecutive_min:
                    alerts.append(
                        f"[BUDGET ALERT] {normalize_category(rule.category)} consecutive overspend days reached. "
                        f"Max streak={max_streak}, Overspend days={overspend_days}, Threshold={rule.threshold:.2f}"
                    )

        if rule.alert_type == "over_ratio" and rule.threshold > 0:
            ratio_threshold = _safe_float(raw_rule.get("ratio_threshold", DEFAULT_RATIO_THRESHOLD), DEFAULT_RATIO_THRESHOLD)
            for period_key, spending in sorted(period_totals.items()):
                ratio = spending / rule.threshold
                if ratio > ratio_threshold:
                    alerts.append(
                        f"[BUDGET ALERT] {normalize_category(rule.category)} {rule.period} spending ratio exceeded {ratio_threshold:.0%}. "
                        f"Period={period_key}, Total={spending:.2f}, Threshold={rule.threshold:.2f}, Ratio={ratio:.2%}"
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


def _safe_float(value: object, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _resolve_period_totals(
    raw_rule: dict,
    category_transactions: list[dict],
    period: str,
    explicit_start_date: str | None,
) -> dict[str, float]:
    anchor_date = _resolve_anchor_date(raw_rule, explicit_start_date, category_transactions)
    if not anchor_date:
        return {}

    # If caller provides start_date or the rule defines start_date, evaluate exactly one anchored window.
    has_explicit_anchor = bool(str(raw_rule.get("start_date", "")).strip() or str(explicit_start_date or "").strip())
    if has_explicit_anchor:
        period_summary = get_period_summary(category_transactions, period, anchor_date)
        key = _build_period_key(anchor_date, period)
        return {key: float(period_summary.get("total_spending", 0.0))}

    return get_spending_summary(category_transactions, period)


def _build_period_key(anchor_date: str, period: str) -> str:
    parsed = _parse_date(anchor_date)
    if parsed is None:
        return anchor_date

    if period == "day":
        return parsed.isoformat()
    if period == "week":
        year, week, _ = parsed.isocalendar()
        return f"{year}-W{week:02d}"
    return f"{parsed.year}-{parsed.month:02d}"


def _count_consecutive_overspend_days(daily_totals: dict[str, float], threshold: float) -> tuple[int, int]:
    overspend_dates: list[date] = []
    for day_key, total in daily_totals.items():
        parsed_day = _parse_date(day_key)
        if parsed_day is not None and total > threshold:
            overspend_dates.append(parsed_day)

    if not overspend_dates:
        return 0, 0

    overspend_dates.sort()
    max_streak = 1
    current_streak = 1
    for index in range(1, len(overspend_dates)):
        if (overspend_dates[index] - overspend_dates[index - 1]).days == 1:
            current_streak += 1
            if current_streak > max_streak:
                max_streak = current_streak
        else:
            current_streak = 1

    return max_streak, len(overspend_dates)


