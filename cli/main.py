import sys
import os
import platform
from getpass import getpass

# Windows-specific imports
if platform.system() == "Windows":
    try:
        import msvcrt
    except ImportError:
        print("Warning: msvcrt not available. Password input will hide characters.")
        msvcrt = None

# Add project root to sys.path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.services.user_service import register_user, authenticate_user
from backend.services.account_service import create_account, list_accounts
from backend.services.transaction_service import deposit, withdraw, get_transactions

current_user = None

class Colors:
    BROWN = "\033[38;2;139;69;19m"
    LIGHT_BROWN = "\033[38;2;222;184;135m"
    RESET = "\033[0m"
    
    @staticmethod
    def brown(text):
        return f"{Colors.BROWN}{text}{Colors.RESET}"
    
    @staticmethod
    def light_brown(text):
        return f"{Colors.LIGHT_BROWN}{text}{Colors.RESET}"
    
    @staticmethod
    def input_brown(prompt):
        """Get input with colored prompt and reset color afterwards"""
        user_input = input(f"{Colors.BROWN}{prompt}{Colors.LIGHT_BROWN}")
        print(Colors.RESET, end="")
        return user_input
    
    @staticmethod
    def getpass_brown(prompt):
        """Get password input with colored prompt"""
        print(f"{Colors.BROWN}{prompt}{Colors.RESET}", end="", flush=True)
        password = getpass("")
        return password
    
    @staticmethod
    def getpass_with_asterisks(prompt):
        """Windows-only: Get password input showing asterisks while typing"""
        if platform.system() != "Windows" or msvcrt is None:
            # Fallback to regular getpass for non-Windows
            return Colors.getpass_brown(prompt)
        
        print(f"{Colors.BROWN}{prompt}{Colors.LIGHT_BROWN}", end="", flush=True)
        
        password_chars = []
        
        while True:
            # Get a single character
            char = msvcrt.getch()
            
            # Enter key (submit)
            if char == b'\r' or char == b'\n':
                print(Colors.RESET)
                break
            
            # Backspace key
            elif char == b'\b':
                if password_chars:
                    password_chars.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            
            # Ctrl+C (exit)
            elif char == b'\x03':
                print(Colors.RESET)
                sys.exit(0)
            
            # Escape key
            elif char == b'\x1b':
                print(Colors.RESET)
                return ""
            
            # Normal character
            else:
                try:
                    # Try to decode as UTF-8
                    char_decoded = char.decode('utf-8')
                    if char_decoded.isprintable():
                        password_chars.append(char_decoded)
                        sys.stdout.write('*')
                        sys.stdout.flush()
                except UnicodeDecodeError:
                    # Skip non-UTF-8 characters
                    pass
        
        return ''.join(password_chars)

def prompt_main_menu():
    print(Colors.brown("\n---------------- CyBank CLI ----------------"))
    print(Colors.light_brown("\n1. Register"))
    print(Colors.light_brown("2. Login"))
    print(Colors.light_brown("3. Exit"))
    return Colors.input_brown("Select an option: ").strip()

def prompt_user_menu():
    print(Colors.brown(f"\n---------------- Welcome, {current_user.username} ----------------"))
    print(Colors.light_brown("1. Create Account"))
    print(Colors.light_brown("2. List Accounts"))
    print(Colors.light_brown("3. Deposit"))
    print(Colors.light_brown("4. Withdraw"))
    print(Colors.light_brown("5. Show Transactions"))
    print(Colors.light_brown("6. Logout"))
    return Colors.input_brown("Select an option: ").strip()

def handle_register():
    print(Colors.brown("\n---------------- Register New User ----------------"))
    username = Colors.input_brown("Enter username: ").strip()
    
    # Use the new asterisk password input for Windows
    if platform.system() == "Windows":
        password = Colors.getpass_with_asterisks("Enter password: ").strip()
    else:
        password = Colors.getpass_brown("Enter password: ").strip()
    
    full_name = Colors.input_brown("Enter full name: ").strip()
    email = Colors.input_brown("Enter email (optional): ").strip() or None

    user = register_user(username, password, full_name, email)
    if user:
        print(Colors.light_brown("✅ Registration successful. You can now login."))
    else:
        print(Colors.light_brown("❌ Username already exists."))

def handle_login():
    global current_user
    print(Colors.brown("\n---------------- Login ----------------"))
    username = Colors.input_brown("Username: ").strip()
    
    # Use the new asterisk password input for Windows
    if platform.system() == "Windows":
        password = Colors.getpass_with_asterisks("Password: ").strip()
    else:
        password = Colors.getpass_brown("Password: ").strip()
    
    user = authenticate_user(username, password)
    if user:
        current_user = user
        print(Colors.light_brown(f"✅ Login successful. Welcome, {user.full_name}"))
        return True
    else:
        print(Colors.light_brown("❌ Login failed. Invalid username or password."))
        return False

# [The rest of your functions remain EXACTLY THE SAME...]
# handle_create_account, handle_list_accounts, select_account, 
# handle_deposit, handle_withdraw, handle_show_transactions, and main()

def handle_create_account():
    print(Colors.brown("\n---------------- Create New Account ----------------"))
    acct_name = Colors.input_brown("Account Name: ").strip() or "Default Account"
    acct = create_account(current_user.user_id, acct_name)
    print(Colors.light_brown(f"✅ Account created. Account ID: {acct.account_id} (Balance: {acct.balance})"))

def handle_list_accounts():
    accts = list_accounts(current_user.user_id)
    if not accts:
        print(Colors.light_brown("⚠️  No accounts found."))
        return
    print(Colors.brown("\nYour Accounts:"))
    for i, a in enumerate(accts, start=1):
        print(Colors.light_brown(f" {i}. ID: {a.account_id} | Name: {a.account_name} | Balance: {a.balance}"))

def select_account():
    accts = list_accounts(current_user.user_id)
    if not accts:
        print(Colors.light_brown("⚠️  No accounts found."))
        return None
    print(Colors.brown("\nSelect an account:"))
    for i, a in enumerate(accts, start=1):
        print(Colors.light_brown(f" {i}. {a.account_name} (ID: {a.account_id}, Balance: {a.balance})"))
    try:
        idx = int(Colors.input_brown("Enter number: ").strip())
        if 1 <= idx <= len(accts):
            return accts[idx - 1]
    except ValueError:
        pass
    print(Colors.light_brown("❌ Invalid selection."))
    return None

def handle_deposit():
    acct = select_account()
    if not acct:
        return
    try:
        amt = float(Colors.input_brown("Deposit amount: ").strip())
        if amt <= 0:
            print(Colors.light_brown("⚠️  Amount must be positive."))
            return
    except ValueError:
        print(Colors.light_brown("⚠️  Invalid amount entered."))
        return

    txn = deposit(acct.account_id, amt, description="Deposit via CLI")
    if txn:
        print(Colors.light_brown(f"✅ Deposit successful. New balance: {acct.balance}"))
    else:
        print(Colors.light_brown("❌ Deposit failed."))

def handle_withdraw():
    acct = select_account()
    if not acct:
        return
    try:
        amt = float(Colors.input_brown("Withdrawal amount: ").strip())
        if amt <= 0:
            print(Colors.light_brown("⚠️  Amount must be positive."))
            return
    except ValueError:
        print(Colors.light_brown("⚠️  Invalid amount entered."))
        return

    txn = withdraw(acct.account_id, amt, description="Withdraw via CLI")
    if txn:
        print(Colors.light_brown(f"✅ Withdrawal successful. New balance: {acct.balance}"))
    else:
        print(Colors.light_brown("❌ Withdrawal failed — insufficient funds or invalid account."))

def handle_show_transactions():
    acct = select_account()
    if not acct:
        return
    txns = get_transactions(acct.account_id)
    if not txns:
        print(Colors.light_brown("⚠️  No transactions found."))
        return
    print(Colors.brown(f"\nTransactions for account {acct.account_name} (ID: {acct.account_id}):"))
    print(Colors.light_brown("-" * 60))
    for txn in txns:
        typ = txn.transaction_type
        amt = txn.amount
        time = txn.timestamp
        desc = txn.description or ""
        print(Colors.light_brown(f"{time} | {typ} | {amt:+.2f} | {desc}"))
    print(Colors.light_brown("-" * 60))

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
                        print(Colors.brown("Logging out..."))
                        break
                    else:
                        print(Colors.light_brown("⚠️  Invalid option."))
        elif choice == "3":
            print(Colors.brown("Goodbye."))
            sys.exit(0)
        else:
            print(Colors.light_brown("⚠️  Invalid option."))

if __name__ == "__main__":
    main()