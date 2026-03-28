import csv
import json
from typing import List,Dict

def load_transactions(filepath:str = "transactions.csv")->List[Dict]:
    '''
    csv文件格式:
    date,amount,category,description,notes
    2026-03-01,50.0,meals,中午吃饭,在学校食堂
    '''
    transactions=[]
    try:
        with open(filepath,'r',encoding='utf-8',newline='')as f:
            reader=csv.DictReader(f)
            if not reader.filenames:
                print(f"警告：{filepath}是空文件")
                return []
            for row in reader:
                # 基础类型转换（后面角色2可以进一步校验）
                try:
                   row['amount']=float(row['amount'])
                   transactions.append(row)
                except (ValueError, TypeError):
                   print(f" 跳过格式错误行：{row}")
                   continue
        print(f" ✅成功加载 {len(transactions)} 条交易记录 from {filepath}")
        return transactions
    except FileNotFoundError:
        print(f" ❌文件不存在：{filepath} → 返回空列表）")
        return []
    except Exception as e:
        print(f" ❌加载交易失败：{e} → 返回空列表")
        return []
    
def save_transaction (filepath: str = "transactions.csv", transactions:List[Dict]=None):
        
        '''
        把记录存为csv文档
        '''
        
    if not transactions:
        print("⚠️没有记录可存")   
        return
        
    try:
        with open(filepath,'w',encoding='utf-8',newline='') as f:
            fieldname = ['date', 'amount', 'category', 'description', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldname)
            writer.writeheader()
            writer.writerows(transactions)
        print(f" ✅已保存 {len(transactions)} 条交易记录 到 {filepath}")
    except Exception as e:
        print(f" ❌保存交易失败：{e}")    

def load_budget_rules(filepath: str = "budget_rules.json") -> List[Dict]:
    """
     JSON 文件示例格式：
    [
        {"category": "meals", "period": "daily", "threshold": 50.0, "alert_type": "exceed"},
        {"category": "transport", "period": "weekly", "threshold": 200.0, "alert_type": "percentage"}
    ]
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        print(f"✅ 成功加载 {len(rules)} 条预算规则 from {filepath}")
        return rules
    except FileNotFoundError:
        print(f"❌ 预算规则文件不存在：{filepath} → 返回空列表")
        return []
    except json.JSONDecodeError:
        print(f"❌ {filepath} JSON 格式错误 → 返回空列表")
        return []
    except Exception as e:
        print(f"❌ 加载预算规则失败：{e} → 返回空列表")
        return []


def save_budget_rules(filepath: str = "budget_rules.json", rules: List[Dict] = None):
    """
    将预算规则保存为 JSON 文件
    """
    if not rules:
        print("⚠️ 没有预算规则可保存")
        return

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4, ensure_ascii=False)
        print(f"✅ 已保存 {len(rules)} 条预算规则 到 {filepath}")
    except Exception as e:
        print(f"❌ 保存预算规则失败：{e}")  






    


