# 請確保已安裝: pip install click rich
import json
import click
import time
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from dataclasses import dataclass
# import io
# import validator
# import stats
# import alert
# import model

@dataclass

class UserManager:
    PATH = "user.json"
    
    def user_load(self):  
        try:
            with open(self.PATH, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def user_save(self, users: list[dict]) -> bool:
        try:
            with open(self.PATH, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except IOError:
            return False
    
    def user_find(self, users: list[dict], username: str):
        for user in users:
            if user["username"] == username:  
                return user
        return None
    
    def user_examine(self, user: dict, password: str) -> bool:
        return user["password"] == password
    
    def user_create(self, username: str, password: str) -> bool:
        if not username or not password:
            click.secho("❌ Username and password cannot be empty", fg="red")
            return False
        
        if len(username) < 6 or len(username) > 12: 
            click.secho("❌ Username must be 6-12 characters", fg="red")
            return False
        
        um = UserManager()  
        users = um.user_load()
        if um.user_find(users, username):
            click.secho("❌ Username already exists", fg="red")
            return False
        
        new_user = {"username": username, "password": password}
        users.append(new_user)
        return um.user_save(users)


class BudgetPlan:
    def __intit__(self):
        self.transcations_list = []
        self.budget_rules_list = []
        self.display = []

    def create_transactions_pretty(self,transactions):
        if not transactions:
            self.console.print("[red]❌ No Transcation Record[/red]")
            return

        table = Table(title="📊 Transcations Record", show_header=True, header_style="bold magenta")
        
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Amount", style="green", justify="right", width=10)
        table.add_column("Category", style="yellow", width=10)
        table.add_column("Description", style="white", width=25)
        table.add_column("Notes", style="white",width=25)
        
        # 填充数据
        for t in transactions:
            table.add_row(
                t.get("date", ""), 
                f"[bold green]¥{t.get('amount', 0):.2f}[/bold green]",
                t.get("category", ""),
                t.get("description", ""),
                t.get("notes","")
            )
        
        self.display = table

    def add_transcation(self):
        while(input("Add new transcation(y/n)",) == "y"):
            new_transcation = Transcation()
            new_transcation.date = click.prompt("Date(YYYY-MM-DD)")
            new_transcation.amount = click.prompt("Amount")
            new_transcation.category = Prompt.ask("Category:",
                                choices=CategoryManager.get_all_categories())
            new_transcation.description = click.prompt("Description")
            new_transcation.notes = click.prompt("Notes")


            valid = False
            valid, msg = validate_transcation(new_transcation)
            if valid:
                self.transcations_list.append(new_transcation)
                print()
                return
            else:
                print(f"❌ {msg}",fg ="red")
                time.sleep(2)
                return

    def view_transcations(self):
        if not self.transcations_list:
            print(f"⚠️ No Trancations Record",fg="red")
            time.sleep(2)
            return False
        self.create_transactions_pretty(self.transcations_list)
        return True

    def restore_transcations(self):
        transcations_dicts,msg = load_transcations()
        if not transcations_dicts:
            print(msg,fg="red")
            print("Initialization fails",fg="red")
            time.sleep(2)
            return
        self.transcations_list = [transaction_from_dict(d) for d in transcations_dicts]

    def clear_transcations(self):
        if Confirm.ask("Remove all existing transcation records?"):
            self.transcations_list = []
            return

    def create_budget_rules_pretty(self,budget_rules):
        if not budget_rules:
            self.console.print("[red]❌ 无预设规则记录[/red]")
            return

        table = Table(title="Budget Rules", show_header=True, header_style="bold magenta")
        
        table.add_column("Category", style="cyan", width=12)
        table.add_column("Time Period", style="green", justify="right", width=20)
        table.add_column("Threshold Value", style="yellow", width=10)
        table.add_column("Alert Type", style="white", width=15)
        
        # 填充数据
        for t in budget_rules:
            table.add_row(
                t.get("category", ""), 
                t.get("time_period",""),
                f"[bold green]¥{t.get('threshold_value', 0):.2f}[/bold green]",
                t.get("alert_type", "")
            )
        
        self.display = table

    def add_budget_rule(self):
        while(input("Add new transcation(y/n)",) == "y"):
            new_budget_rule = Budget()
            new_budget_rule.category = Prompt.ask("Category:",
                                choices=CategoryManager.get_all_categories())
            new_budget_rule.time_period = Prompt.ask("Time Period:",
                                choices=["day", "week", "month"])
            new_budget_rule.threshold_value = click.prompt("Threshold Value")
            new_budget_rule.alert_type = Prompt.ask("Alert Type:",
                                choices=["over_threshold", "over_ratio"])

            valid = False
            valid, msg = validate_budget_rule(new_budget_rule)
            if valid:
                self.budget_rules_list.append(new_budget_rule)
                print()
                return
            else:
                print(f"❌ {msg}",fg ="red")
                time.sleep(2)
                return

    def view_budget_rules(self):
        if not self.budget_rules_list:
            print("⚠️ No Budget Rules",fg="red")
            time.sleep(2)
            return False
        self.create_budget_rules_pretty(self.budget_rules_list)
        return True

    def restore_budget_rules(self):
        budget_rules_dicts,msg = load_budget_rules()
        if not budget_rules_dicts:
            print(msg,fg="red")
            print("Initialization fails",fg="red")
            time.sleep(2)
            return
        self.budget_rules_list = [budget_from_dict(d) for d in budget_rules_dicts]

    def clear_budget_rules(self):
        if Confirm.ask("Remove all existing transcation records?"):
            self.budget_rules_list = []
            return
    
    def load_transcation_and_budget_rules(self):
        transcations_dicts,msg = load_transcations()
        if not transcations_dicts:
            print(msg,fg="red")
            print("Initialization fails",fg="red")
            time.sleep(2)
            return
        self.transcations_list = [transaction_from_dict(d) for d in transcations_dicts]
        budget_rules_dicts,msg = load_budget_rules()
        if not budget_rules_dicts:
            print(msg,fg="red")
            print("Initialization fails",fg="red")
            time.sleep(2)
            return
        self.budget_rules_list = [budget_from_dict(d) for d in budget_rules_dicts]

    def save_transcation_and_budget_rules(self):
        if Confirm.ask("Save?(will override the transcation)"):
            transcations_dicts = [transaction_to_dict(t) for t in self.transcations_list]
            save_transcations("transcations.csv",transcations_dicts)
        if Confirm.ask("Save?(will override the budget rules)"):
            budget_rules_dicts = [budget_rule_to_dict(t) for t in self.budget_rules_list]
            save_budget_rules("budget_rules.json",budget_rules_dicts)

    def select_by_category(self):
        category = Prompt.ask("Category:",
                                choices=CategoryManager.get_all_categories())
        self.transcations_list = filter_by_category(self.transcations_list,category)

    def select_by_date_range(self):
        valid_start = False
        valid_end = False
        while(not valid_start):
            start_date = click.prompt("Start_date(YYYY-MM-DD)")
            valid_start,msg = validate_date(start_date)
            if not valid_start:
                print(msg,fg="red")
        while(not valid_end):
            end_date = click.prompt("End Date(YYYY-MM-DD)")
            valid_end,msg = validate_date(end_date)
            if not valid_end:
                print(msg,fg="red")        
        self.transcations_list = filter_by_date_range(self.transcations_list,start_date,end_date)

    def summary(self):
        period = Prompt.ask("Group by",
                           choices=["day","week","month"],default="month")
        summary_data = get_spending_summary(self.transcations_list,period)
        if not summary_data:
            print("No spending data found.",fg="red")
            return False
        table = Table(title=f"📊 Spending Summary by {period.capitalize()}",show_header=True,header_style="bold cyan")

        table.add_column("Period", style="white", justify="left")
        table.add_column("Total Amount", style="green", justify="right")

        for key, total in sorted(summary_data.items()):
            table.add_row(key, f"${total:.2f}")
        
        self.display = table
        return True


class AppState:
    current_user: Optional[dict] = None
    current_plan: Optional[BudgetPlan] = None
    layer: int = 1
    running: bool = True

class BudgetAssistant:
    def __init__(self):
        self.console = Console()
        self.state = AppState()
        self.user_manager = UserManager()
        self.state.current_plan = BudgetPlan()
    
    def start(self):
        while self.state.running:
            self.console.clear()
            
            if self.state.layer == 1:
                self.render_layer1()
            elif self.state.layer == 2:
                self.render_layer2()
            elif self.state.layer == 3:
                self.render_layer3()
    
    def render_layer1(self):

        menu_table = Table(show_header=False, box = None)
        menu_table.add_column(justify="center")

        menu_table.add_row("\n[bold cyan]╔═══════════════════════════════════╗[/bold cyan]")
        menu_table.add_row("[bold cyan]║         💰 個人預算助手           ║[/bold cyan]")
        menu_table.add_row("[bold cyan]║         Budget Assistant          ║[/bold cyan]")
        menu_table.add_row("[bold cyan]║                                   ║[/bold cyan]")
        menu_table.add_row("[bold cyan]║                                   ║[/bold cyan]")
        menu_table.add_row("[bold cyan]║[/bold cyan][white]              Login                [/white][bold cyan]║[/bold cyan]")
        menu_table.add_row("[bold cyan]║                                   ║[/bold cyan]")
        menu_table.add_row("[bold cyan]║[/bold cyan][white]              Register             [/white][bold cyan]║[/bold cyan]")
        menu_table.add_row("[bold cyan]║                                   ║[/bold cyan]")
        menu_table.add_row("[bold cyan]║[/bold cyan][white]              Quit                 [/white][bold cyan]║[/bold cyan]")
        menu_table.add_row("[bold cyan]║                                   ║[/bold cyan]")
        menu_table.add_row("[bold cyan]╚═══════════════════════════════════╝[/bold cyan]\n")  
        
        self.console.print(menu_table)
        
        choice = Prompt.ask("Please select", choices=["Login", "Register", "Quit"])
        if choice == "Login":
            self.login()
        elif choice == "Register":
            self.register()
        elif choice == "Quit":
            self.quit()
    
    def render_layer2(self):
        if not self.state.current_user:
            self.state.layer = 1
            return
        
        self.console.clear()
        menu_table = Table(show_header=False, box=None, padding=0)
        menu_table.add_column("left", style="bold cyan",justify="left", width=8)
        menu_table.add_column("center", style="white", justify= "center",width=19)
        menu_table.add_column("right", style="bold cyan",justify="right", width=8)
        
        menu_table.add_row("╔═══════", "[bold cyan]═══════════════════[/bold cyan]", "═══════╗")
        menu_table.add_row("║", "💰 新建预算方案", "║")
        menu_table.add_row("║", "New Budget Plan", "║")
        menu_table.add_row("║[green]User:[/green]", self.state.current_user['username'], "║")
        menu_table.add_row("║", "", "║")
        menu_table.add_row("║", Align.left("1 Trancation"), "║")
        menu_table.add_row("║", Align.left("2 Budget Rule"), "║")
        menu_table.add_row("║", Align.left("3 Selcet"), "║")
        menu_table.add_row("║", Align.left("4 Load Save"), "║")
        menu_table.add_row("║", Align.left("5 Save"), "║")
        menu_table.add_row("║", Align.left("6 Summary"), "║")
        menu_table.add_row("║", Align.left("7 Settings"), "║")
        menu_table.add_row("║", Align.left("8 Return"), "║")
        menu_table.add_row("║", Align.left("9 Quit"), "║")
        menu_table.add_row("╚═══════", "[bold cyan]═══════════════════[/bold cyan]", "═══════╝")
        
        self.console.print(menu_table)
        
        choice = Prompt.ask("[bold yellow]Select[/bold yellow]", 
                           choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"], default="9")
        
        if choice == "1":
            choice = Prompt.ask( 
                            choices=["View", "Add", "Clear", "Restore", "Exit"], default="Exit")
            self.console.clear()
            if choice == "View":
                flag = self.state.current_plan.view_transcations()
                if flag:
                    self.console.print(self.state.current_plan.display)
                    print("Type enter to exit")
                    input()
                return
            if choice == "Add":
                self.state.current_plan.add_transcation()
                return
            if choice == "Clear":
                self.state.current_plan.clear_transcations()
                return
            if choice == "Restore":
                self.state.current_plan.restore_transcations()
                return
            if choice == "Exit":
                return
        elif choice == "2":
            choice = Prompt.ask( 
                            choices=["View", "Add", "Clear", "Restore", "Exit"], default="Exit")
            if choice == "View":
                flag = self.state.current_plan.view_budget_rules()
                if flag:
                    self.console.print(self.state.current_plan.display)
                    print("Type enter to exit")
                    input()
                return
            if choice == "Add":
                self.state.current_plan.add_budget_rule()
                return
            if choice == "Clear":
                self.state.current_plan.clear_budget_rules()
                return
            if choice == "Restore":
                self.state.current_plan.restore_budget_rules()
                return
            if choice == "Exit":
                return
        elif choice == "3":
            choice = Prompt.ask("Select by ",
                            choices=["Date", "Category", "Exit"], default="Exit")
            if choice == "Date":
                self.state.current_plan.select_by_date_range()
                return
            if choice == "Category":
                self.state.current_plan.select_by_date_range()
                return
            if choice == "Exit":
                return
        elif choice == "4":
            self.state.current_plan.load_transcation_and_budget_rules()
            return
        elif choice == "5":
            self.state.current_plan.save_transcation_and_budget_rules()
            return
        elif choice == "6":
            flag = self.state.current_plan.summary()
            if flag:
                self.console.print(self.state.current_plan.display)
                print("Type enter to exit")
                input()
            return
        elif choice == "7":
            self.state.layer = 3
            return
        elif choice == "8":
            self.state.layer = 1
            return
        elif choice == "9":
            self.quit()
            return

    def render_layer3(self):
        if not self.state.current_user:
            self.state.layer = 1
            return
        
        self.console.clear()
        menu_table = Table(show_header=False, box=None, padding=0)
        menu_table.add_column("left", style="bold cyan",justify="left", width=8)
        menu_table.add_column("center", style="white", justify= "center",width=19)
        menu_table.add_column("right", style="bold cyan",justify="right", width=8)
        
        menu_table.add_row("╔═══════", "[bold cyan]═══════════════════[/bold cyan]", "═══════╗")
        menu_table.add_row("║", "设置", "║")
        menu_table.add_row("║", "Settings", "║")
        menu_table.add_row("║[green]User:[/green]", self.state.current_user['username'], "║")
        menu_table.add_row("║", "", "║")
        menu_table.add_row("║", Align.left("1 Category"), "║")
        menu_table.add_row("║", Align.left("2 Return"), "║")
        menu_table.add_row("║", Align.left("3 Quit"), "║")
        menu_table.add_row("╚═══════", "[bold cyan]═══════════════════[/bold cyan]", "═══════╝")
        
        self.console.print(menu_table)

        choice = Prompt.ask("[bold yellow]Select[/bold yellow]", 
                           choices=["1", "2", "3"], default="3")
        
        # 存疑部分category
        if choice == "1":
            choice = Prompt.ask("Selcet",choices=["Add","View","Exit"])
            if choice == "Add":
                self.add_category_flow()
                return
            elif choice == "View":
                self.view_categories()
                return
            elif choice == "Exit":
                return
        if choice == "2":
            self.state.layer = 2
        if choice == "3":
            self.quit()
        return

    def login(self):
        if self.state.current_user == None:
            username = click.prompt("Username")
            password = click.prompt("Password")
            users = self.user_manager.user_load()
            user = self.user_manager.user_find(users, username)
            if user == None:
                click.secho(f"❌ User '{username}' not found", fg="red")
                time.sleep(3)
                return
            if self.user_manager.user_examine(user, password):
                self.state.current_user = user
                self.show_welcome_panel()
                # main menu
                self.state.layer = 2
                return
            else:
                click.secho(f"❌ Wrong Password! Try again! ", fg="red")
                time.sleep(3)
                return
        else:
            click.secho(f"Already login", fg="green")
            time.sleep(0.5)
            self.show_welcome_panel()
            # open main menu
            self.state.layer = 2
            return
          
    def register(self):
        if len(self.user_manager.user_load()) > 0:
            click.secho("❌ Cannot register more users", fg="red")
            time.sleep(2)
            return
        
        username = click.prompt("Username")
        password = click.prompt("Password", hide_input=True)
        confirm = click.prompt("Confirm Password", hide_input=True)
        
        if password != confirm:
            click.secho("❌ Passwords don't match", fg="red")
            return
        
        if self.user_manager.user_create(username, password):
            click.secho(f"✅ Welcome {username}!", fg="green")
            self.state.current_user = {"username": username}
            time.sleep(2)
            self.state.layer = 2
        else:
            click.secho("❌ Registration failed", fg="red")
            self.show_username_rule()
    
    def quit(self):
        if Confirm.ask("Quit?"):
            self.console.print("[green]👋 Goodbye![/green]")
            self.state.running = False
            time.sleep(1)
            self.console.clear()

    def show_welcome_panel(self):
        panel = Panel.fit(
            f"[bold green]Welcome back![/bold green]\\n\\n"
            f"Current User: [cyan]{self.state.current_user["username"]}[/cyan]\\n",
            title="🎉 Budget Assistant",
            border_style="green"
        )
        self.console.print(panel)

    def show_username_rule(self):
        panel = Panel.fit(
            "[bold green]Valid Username[/bold green]\\n\\n"
            "1.[cyan]Letters, numbers, underscore only[/cyan]\\n"
            "2.[cyan]6-12 characters[/cyan]\\n"
            "3.[cyan]No duplicates[/cyan]",
            title="💡 Username Rules",
            border_style="blue"
        )
        self.console.print(panel)
        self.console.print("\\n[yellow]Press Enter to continue...[/yellow]")
        input()
    # 同样存疑部分 category
    def add_category_flow(self):
        new_name = Prompt.ask("Enter new category name")
        if CategoryManager.validate_category(new_name):
            self.console.print(f"[yellow]⚠ Category '{new_name}' already exists.[/yellow]")
            return
        ok, message = CategoryManager.add_category(new_name)
        if ok:
            self.console.print(f"[green]✅ {message}[/green]")
        else:
            self.console.print(f"[red]❌ {message}[/red]")
        time.sleep(2)

    def view_categories(self):
        all_categories = CategoryManager.get_all_categories()

        table = Table(title="📂 Category List", show_header=True, header_style="bold cyan")
        table.add_column("No.", justify="right", style="yellow", width=4)
        table.add_column("Category", style="white", width=20)
        table.add_column("Type", style="green", width=12)

        for i, cat in enumerate(all_categories, start=1):
            cat_type = "Predefined" if cat in CategoryManager.PREDEFINED else "Custom"
            table.add_row(str(i), cat, cat_type)

        self.console.print(table)
        time.sleep(2)

if __name__ == "__main__":
    app = BudgetAssistant()
    app.start()