import csv
import json
from pathlib import Path
import shutil


# ==================== 兼容映射 ====================
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


def load_transactions(filepath: str = "transactions.csv") -> tuple[list[dict], str]:
    """返回 (transactions_list, message)"""
    transactions = []
    try:
        with open(filepath, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return [], f"⚠️ 警告：{filepath} 是空文件"
            for row in reader:
                row = dict(row)
                cat = row.get('category', '')
                if cat in CATEGORY_MAP:
                    row['category'] = CATEGORY_MAP[cat]
                try:
                    row['amount'] = float(row.get('amount', 0))
                    transactions.append(row)
                except:
                    continue
        return transactions, f"✅ 成功加载 {len(transactions)} 条交易记录"
    except FileNotFoundError:
        return [], f"❌ 文件不存在：{filepath}"
    except Exception as e:
        return [], f"❌ 加载交易失败：{e}"


def save_transactions(filepath: str = "transactions.csv", transactions: list[dict] = None) -> tuple[bool, str]:
    """返回 (success, message)"""
    if not transactions:
        return False, "⚠️ 没有数据可保存"
    try:
        # 备份
        if Path(filepath).exists():
            shutil.copy2(filepath, f"{filepath}.bak")
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['date', 'amount', 'category', 'description', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(transactions)
        return True, f"✅ 已保存 {len(transactions)} 条记录"
    except Exception as e:
        return False, f"❌ 保存失败：{e}"


def load_budget_rules(filepath: str = "budget_rules.json") -> tuple[list[dict], str]:
    """返回 (rules_list, message)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        mapped_rules = []
        for r in rules:
            r = dict(r)
            p = r.get("period") or r.get("time_period")
            if p in PERIOD_MAP:
                r["period"] = PERIOD_MAP[p]
            a = r.get("alert_type")
            if a in ALERT_TYPE_MAP:
                r["alert_type"] = ALERT_TYPE_MAP[a]
            mapped_rules.append(r)
        return mapped_rules, f"✅ 成功加载 {len(mapped_rules)} 条预算规则"
    except FileNotFoundError:
        return [], f"❌ 文件不存在：{filepath}"
    except Exception as e:
        return [], f"❌ 加载失败：{e}"


def save_budget_rules(filepath: str = "budget_rules.json", rules: list[dict] = None) -> tuple[bool, str]:
    """返回 (success, message)"""
    if not rules:
        return False, "⚠️ 没有规则可保存"
    try:
        if Path(filepath).exists():
            shutil.copy2(filepath, f"{filepath}.bak")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4, ensure_ascii=False)
        return True, f"✅ 已保存 {len(rules)} 条规则"
    except Exception as e:
        return False, f"❌ 保存失败：{e}"