from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.io import load_budget_rules, load_transactions


transactions = load_transactions()
rules = load_budget_rules()

print(f"Loaded {len(transactions)} transactions successfully.")
print(f"Loaded {len(rules)} budget rules successfully.")
print("Project setup check completed.")