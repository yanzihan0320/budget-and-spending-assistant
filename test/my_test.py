# 从io.py导入文件加载函数（Role3写的）
from io import load_transactions, load_budget_rules

# 加载data文件夹里的两个文件（路径要写对！）
trans = load_transactions("../data/transactions.csv")
rules = load_budget_rules("../data/budget_rules.json")

# 打印加载结果，看是否成功
print(f"✅ 成功加载 {len(trans)} 条交易记录")
print(f"✅ 成功加载 {len(rules)} 条预算规则")

# 打印交易和规则预览，验证数据正确
print("\n📋 交易记录：")
for t in trans:
    print(t)
print("\n📋 预算规则：")
for r in rules:
    print(r)