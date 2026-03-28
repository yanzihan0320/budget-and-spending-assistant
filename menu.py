# 請確保已安裝click，rich
# 輸入python menu.py [command] 以執行操作
# 我過段時間把這個文件拆分一下多個文件

import json
import os
import click
import time
from rich import print
from rich.panel import Panel
from rich.console import Console
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
def main_menu(username: str):
    """具體功能界面"""
    time.sleep(3)
    while True:
        console.clear()



# ==================== Click 命令組 ====================

@click.group()
def cli():
    """Personal Budget Assisstant"""
    pass

# log in 
@cli.command()
@click.option("--username", "-n", prompt = True, help = "用戶名稱")
@click.option("--password", "-p", prompt = True, hide_input = True, help = "密碼")
def login(username, password):
    """登錄"""
    users = user_load()
    user = user_find(users, username)
    if user == None:
        click.secho(f"❌ 用戶 '{username}' 不存在", fg="red")
        return

    result = user_examine(user, password)
    if result:
        show_welcome_panel(username)
        # opening interface
        # 這裏之後會加上跳轉到下一級界面的代碼
        main_menu()
    else:
        click.secho(f"❌ Wrong Password! Try again! ", fg="red")
    

# create new user
@cli.command()
@click.option("--username", prompt = True, help = "用戶名稱")
@click.option("--password", prompt = True, hide_input=True, help = "密碼")
@click.option("--confirm", prompt = "Confirm Password", hide_input = True, help = "確認密碼")
def register(username, password, confirm):
    """註冊新用戶"""

    if password != confirm:
        click.secho("Wrong Password! Try Again!", fg='red')
        return
    
    result = user_create(username,password)
    # 檢查用戶是否合法，目前尚未有此函數↓
    if result:
        click.secho(f"✅ Registration Succeed! Welcome {username}", fg='green')

    else:
        click.secho(f"❌ Registeration Fails! Invalid Username", fg="red")
        show_username_rule()
    
   
# ==================== 主程序入口 ====================

if __name__ == "__main__":
    # 開始界面
    print("\n[bold cyan]╔═══════════════════════════════════╗[/bold cyan]")
    print("[bold cyan]║         💰 個人預算助手           ║[/bold cyan]")
    print("[bold cyan]║         Budget Assistant          ║[/bold cyan]")
    print("[bold cyan]╚═══════════════════════════════════╝[/bold cyan]\n")
    
    # 運行 Click CLI
    cli()