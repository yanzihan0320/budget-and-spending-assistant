from file_io import load_transactions, load_budget_rules

trans = load_transactions("transactions.csv")
rules = load_budget_rules("budget_rules.json")

print(f"✅ 成功加载 {len(trans)} 条交易记录")
print(f"✅ 成功加载 {len(rules)} 条预算规则")
print("项目文件夹设置完成！可以开始写代码啦～")