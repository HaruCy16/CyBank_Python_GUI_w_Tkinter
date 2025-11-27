# cli/main.py

import sys
from getpass import getpass
from backend.services.user_service import register_user, authenticate_user
from backend.services.account_service import create_account, list_accounts
from backend.services.transaction_service import deposit, withdraw, get_transactions

current_user = None

def prompt_main_menu():
    print("\n=== CyBank CLI ===")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    return input("Select an option: ").strip()

def prompt_user_menu():
    print(f"\n--- Welcome, {current_user.username} ---")
    print("1. Create Account")
    print("2. List Accounts")
    print("3. Deposit")
    print("4. Withdraw")
    print("5. Show Transactions")
    print("6. Logout")
    return input("Select an option: ").strip()

def handle_register():
    print("\n--- Register New User ---")
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ").strip()
    full_name = input("Enter full name: ").strip()
    email = input("Enter email (optional): ").strip() or None

    user = register_user(username, password, full_name, email)
    if user:
        print("✅ Registration successful. You can now login.")
    else:
        print("❌ Username already exists.")

def handle_login():
    global current_user
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()
    user = authenticate_user(username, password)
    if user:
        current_user = user
        print(f"✅ Login successful. Welcome, {user.full_name}")
        return True
    else:
        print("❌ Login failed. Invalid username or password.")
        return False

def handle_create_account():
    print("\n--- Create New Account ---")
    acct_name = input("Account Name: ").strip() or "Default Account"
    acct = create_account(current_user.user_id, acct_name)
    print(f"✅ Account created. Account ID: {acct.account_id} (Balance: {acct.balance})")

def handle_list_accounts():
    accts = list_accounts(current_user.user_id)
    if not accts:
        print("⚠️  No accounts found.")
        return
    print("\nYour Accounts:")
    for i, a in enumerate(accts, start=1):
        print(f" {i}. ID: {a.account_id} | Name: {a.account_name} | Balance: {a.balance}")

def select_account():
    accts = list_accounts(current_user.user_id)
    if not accts:
        print("⚠️  No accounts found.")
        return None
    print("\nSelect an account:")
    for i, a in enumerate(accts, start=1):
        print(f" {i}. {a.account_name} (ID: {a.account_id}, Balance: {a.balance})")
    try:
        idx = int(input("Enter number: ").strip())
        if 1 <= idx <= len(accts):
            return accts[idx - 1]
    except ValueError:
        pass
    print("❌ Invalid selection.")
    return None

def handle_deposit():
    acct = select_account()
    if not acct:
        return
    try:
        amt = float(input("Deposit amount: ").strip())
        if amt <= 0:
            print("⚠️  Amount must be positive.")
            return
    except ValueError:
        print("⚠️  Invalid amount input.")
        return

    txn = deposit(acct.account_id, amt, description="Deposit via CLI")
    if txn:
        print(f"✅ Deposit successful. New balance: {acct.balance}")
    else:
        print("❌ Deposit failed.")

def handle_withdraw():
    acct = select_account()
    if not acct:
        return
    try:
        amt = float(input("Withdrawal amount: ").strip())
        if amt <= 0:
            print("⚠️  Amount must be positive.")
            return
    except ValueError:
        print("⚠️  Invalid amount input.")
        return

    txn = withdraw(acct.account_id, amt, description="Withdraw via CLI")
    if txn:
        print(f"✅ Withdrawal successful. New balance: {acct.balance}")
    else:
        print("❌ Withdrawal failed — insufficient funds or invalid account.")

def handle_show_transactions():
    acct = select_account()
    if not acct:
        return
    txns = get_transactions(acct.account_id)
    if not txns:
        print("⚠️  No transactions found.")
        return
    print(f"\nTransactions for account {acct.account_name} (ID: {acct.account_id}):")
    print("-" * 60)
    for txn in txns:
        typ = txn.transaction_type
        amt = txn.amount
        time = txn.timestamp
        desc = txn.description or ""
        print(f"{time} | {typ} | {amt:+.2f} | {desc}")
    print("-" * 60)

def main():
    while True:
        choice = prompt_main_menu()
        if choice == "1":
            handle_register()
        elif choice == "2":
            if handle_login():
                # user session
                while True:
                    cmd = prompt_user_menu()
                    if cmd == "1":
                        handle_create_account()
                    elif cmd == "2":
                        handle_list_accounts()
                    elif cmd == "3":
                        handle_deposit()
                    elif cmd == "4":
                        handle_withdraw()
                    elif cmd == "5":
                        handle_show_transactions()
                    elif cmd == "6":
                        print("Logging out...")
                        break
                    else:
                        print("⚠️  Invalid option.")
        elif choice == "3":
            print("Goodbye.")
            sys.exit(0)
        else:
            print("⚠️  Invalid option.")

if __name__ == "__main__":
    main()
