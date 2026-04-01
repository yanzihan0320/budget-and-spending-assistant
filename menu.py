
# 請確保已安裝click，rich

import json
import os
import click
import time
from typing import Optional
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
# from role3dewenjian import load,save...
''' 
用戶數據儲存結構

{
    "username": "",
    "password": "",
    "key": "",
    "PATH":"" //指向該用戶數據的地址
    //如有其他補充麻煩告訴我（而且我覺得肯定有補充吧）
    //另外我默認這些都是Alphanumeric"\\w"
}
'''

# 這裏是我想要的user部分的io函數大致樣子（文件數據的界面目前還沒）
# PATH refers to the file where store user data

PATH = "user.json"
def user_load():
    try:
        with open(PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def user_save(user : list[dict]):
    try:
        with open(PATH, 'w') as f:
            json.dump(user, f, indent = 2)
            return True
    except IOError:
        return False
def user_find(users : list[dict], username : str):
    for user in users:
        if user["username"] == username:
            return user
    return None
def user_examine(user,password):
    if user["password"] == password:
        return True
    return False
def user_create(username: str, password: str):
    
    # 輸入驗證
    if not username or not password:
        click.secho(f"❌ Username and password cannot be empty", fg="red")
        return False
    
    users = user_load()
    
    # 檢查用戶名是否已存在
    if user_find(users, username):
        click.secho(f"❌ The username already exists", fg="red")
        return False

    # 還要給用戶指定一個地址和文件來儲存方案内容
    
    new_user = {
        "username": username,
        "password": password
    }

    users.append(new_user)
    if user_save(users):
        return True
    else:
        click.secho("❌ Failed to save user data", fg="red")
        return False

# 下面是用戶界面核心相關部分
console = Console()

def show_welcome_panel(username: str):
    """顯示歡迎面板"""
    panel = Panel.fit(
        f"[bold green]Welcome back![/bold green]\n\n"
        f"Current User: [cyan]{username}[/cyan]\n",
        title="🎉 Budget Assisstant",
        border_style="green"
    )
    console.print(panel)
def show_username_rule():
    panel = Panel.fit(
        f"[bold green]Valid Username[/bold green]\n\n"
        f"1.[cyan]Only contain numbers, letters and underscore[/cyan]\n"
        f"2.[cyan]Do not duplicate existing usernames[/cyan]\n"
        f"3.[cyan]                                   [/cyan]\n",
        title="💡Tips",
        border_style="blue"
    )
    console.print(panel)


def add_budget_plan_menu():
    
    time.sleep(1)
    while True:
        console.clear()

        menu_table = Table(show_header=False, box=None)
        menu_table.add_column("Option", style="bold yellow", width=8)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1", "View Budget Overview")
        menu_table.add_row("2", "Add Expense")
        menu_table.add_row("3", "View Expenses")
        menu_table.add_row("4", "Set Budget Goal")
        menu_table.add_row("5", "Statistics & Reports")
        menu_table.add_row("6", "Help")
        menu_table.add_row("7", "Back to main menu")
        menu_table.add_row("8", "Quit")

        print(menu_table)



 
class AppState:
    current_user: Optional[dict] = None      # {"username": "", "user_id": ""}
    current_plan: Optional[dict] = None      # {"plan_id": "", "name": "", "files": {...}}
    layer: int = 1                           # 1=登录页 2=主菜单 3=方案详情
    running: bool = True


class BudgetAssistant:
    # region 構造方法（含字段無屬性）
    def __init__(self):
        self.console = Console()
        self.state = AppState()
    # endregion
    
    # region 各級界面
    def start(self):
        """開始界面"""
        # 開始界面
        while self.state.running:
            self.console.clear()

            if self.state.layer == 1:
                self.render_layer1()
            elif self.state.layer == 2:
                self.render_layer2()

    def render_layer1(self):
        """第一层：登录注册界面"""
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

        print(menu_table)

        choice = Prompt.ask(
            "Please select",
                choices=["Login", "Register", "Quit"]
            )

        if choice == "Login":
            self.login()
        elif choice == "Register":
            self.register()
        elif choice == "Quit":
            self.quit()
  
    def render_layer2(self):
        """核心功能界面，方案选择"""
        if not self.state.current_user:
            return
        time.sleep(3)
        while self.state.running:
            self.console.clear()

            title_panel = Panel.fit(
                f"[bold cyan]Personal Budget Assistant[/bold cyan]\n"
                f"[green]Current User: {self.state.current_user['username']}[/green]",
                title="💰 Main Menu",
                border_style="cyan"
            )
            self.console.print(title_panel)
            self.console.print()

            menu_table = Table(show_header=False, box=None)
            menu_table.add_column("Option", style="bold yellow", width=8)
            menu_table.add_column("Description", style="white")
            
            menu_table.add_row("1", "And New Budget Plan")
            menu_table.add_row("2", "View Past Budget Plan")
            menu_table.add_row("3", "Back to login interface")
            menu_table.add_row("4", "Quit")

            self.console.print(menu_table)

            time.sleep(1)

            choice = Prompt.ask(
                "[bold yellow]Please select an option[/bold yellow]",
                choices=["1", "2", "3", "4"],
                default="4"
            )

            if choice == "1":
                break
            elif choice == "2":
                break
            elif choice == "3":
                if Confirm.ask("[yellow]Return to login screen?[/yellow]"):
                    self.console.clear()
                    return
            elif choice == "4":
                self.quit()
                break
    # endregion

    # region 方法

    # region 用戶識別方法
    def login(self):
        if self.state.current_user == None:
            username = click.prompt("Username")
            password = click.prompt("Password")
            users = user_load()
            self.state.current_user = user_find(users, username)
            if self.state.current_user == None:
                click.secho(f"❌ 用戶 '{username}' 不存在", fg="red")
                time.sleep(3)
                return
            if user_examine(self.state.current_user, password):
                show_welcome_panel(username)
                # opening interface
                self.state.layer = 2
                return
            else:
                self.state.current_user = None;
                click.secho(f"❌ Wrong Password! Try again! ", fg="red")
                time.sleep(3)
                return
        else:
            click.secho(f"Already login", fg="green")
            time.sleep(0.5)
            show_welcome_panel(self.state.current_user["username"])
            # opening interface
            self.state.layer = 2
            return
    
    def register(self):
        """註冊新用戶"""

        username = click.prompt("Username")
        password = click.prompt("Password")
        confirm = click.prompt("Confirm")
        if password != confirm:
            click.secho("Wrong Password! Try Again!", fg='red')
            time.sleep(3)
            return
        
        result = user_create(username,password)
        # 檢查用戶是否合法↓
        if result:
            click.secho(f"✅ Registration Succeed! Welcome {username}", fg='green')
            time.sleep(3)
        else:
            click.secho(f"❌ Registeration Fails! Invalid Username", fg="red")
            time.sleep(3)
            show_username_rule()
    # endregion

    # region 頁面跳轉方法
    def quit(self):
        if Confirm.ask("[yellow]Are you sure you want to quit?[/yellow]"):
            self.console.print("[green]👋 Goodbye! See you next time![/green]\n")
            time.sleep(1)
            self.console.clear()
            self.state.running = False
    # endregion

    # endregion
   
# ==================== 主程序入口 ====================

if __name__ == "__main__":
   
    app = BudgetAssistant()
    app.start()
