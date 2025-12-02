import sys
import os

# Add project root to sys.path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.services.user_service import register_user, authenticate_user
from backend.services.account_service import create_account, list_accounts
from backend.services.transaction_service import deposit, withdraw, get_transactions
from backend.services.bank_integration_service import add_bank_account, list_bank_accounts, remove_bank_account, get_total_linked_balance
from backend.services.transfer_service import transfer_to_external_bank, transfer_between_cybank_accounts
from backend.services.report_service import generate_account_summary, generate_transaction_report, generate_multi_bank_portfolio, generate_complete_financial_report
from utils.validators import (validate_username, validate_password, validate_full_name, 
                              validate_email, validate_account_number, validate_account_type, validate_account_name,
                              validate_balance, validate_transaction_amount, validate_bank_name,
                              get_account_types, get_philippines_banks, format_currency)

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
        # Show prompt in brown, input in light brown
        user_input = input(f"{Colors.BROWN}{prompt}{Colors.LIGHT_BROWN}")
        # Reset color after input is received
        print(Colors.RESET, end="")
        return user_input
    
    @staticmethod
    def getpass_brown(prompt):
        """Get password input with colored prompt and asterisks displayed"""
        # Show prompt in brown
        print(f"{Colors.BROWN}{prompt}{Colors.LIGHT_BROWN}", end="", flush=True)
        
        # Custom password input with asterisks
        import sys
        if sys.platform == "win32":
            # Windows: use Windows API for hiding input
            import msvcrt
            password = ""
            while True:
                char = msvcrt.getch()
                if char == b'\r':  # Enter key
                    print()  # New line after password
                    break
                elif char == b'\x08':  # Backspace
                    if password:
                        password = password[:-1]
                        # Move cursor back, print space, move back again
                        print('\b \b', end='', flush=True)
                else:
                    password += char.decode('utf-8', errors='ignore')
                    print('*', end='', flush=True)
        print(Colors.RESET, end="")
        return password

def prompt_main_menu():
    print(Colors.brown("\n---------------- CyBank CLI ----------------"))
    print(Colors.light_brown("\n1. Register"))
    print(Colors.light_brown("2. Login"))
    print(Colors.light_brown("3. Exit"))
    # Don't wrap in Colors.brown - input_brown handles it
    return Colors.input_brown("Select an option: ").strip()

def prompt_user_menu():
    print(Colors.brown(f"\n---------------- Welcome, {current_user.username} ----------------"))
    print(Colors.light_brown("1. Create Account"))
    print(Colors.light_brown("2. List Accounts"))
    print(Colors.light_brown("3. Deposit"))
    print(Colors.light_brown("4. Withdraw"))
    print(Colors.light_brown("5. Show Transactions"))
    print(Colors.light_brown("6. Linked Bank Accounts"))
    print(Colors.light_brown("7. Financial Reports"))
    print(Colors.light_brown("8. Logout"))
    return Colors.input_brown("Select an option: ").strip()

def handle_register():
    print(Colors.brown("\n---------------- Register New User ----------------"))
    
    # Validate username
    while True:
        username = Colors.input_brown("Enter username: ").strip()
        is_valid, msg = validate_username(username)
        print(Colors.light_brown(msg))
        if is_valid:
            break
    
    # Validate full name
    while True:
        full_name = Colors.input_brown("Enter full name: ").strip()
        is_valid, msg = validate_full_name(full_name)
        print(Colors.light_brown(msg))
        if is_valid:
            break
    
    # Validate password
    while True:
        password = Colors.getpass_brown("Enter password: ").strip()
        is_valid, msg = validate_password(password)
        print(Colors.light_brown(msg))
        if is_valid:
            break
    
    # Validate email (optional but if provided must be valid)
    email = None
    while True:
        email_input = Colors.input_brown("Enter email (optional, press Enter to skip): ").strip()
        if not email_input:
            break
        is_valid, msg = validate_email(email_input)
        print(Colors.light_brown(msg))
        if is_valid:
            email = email_input if email_input else None
            break

    user = register_user(username, password, full_name, email)
    if user:
        print(Colors.light_brown("✅ Registration successful. You can now login."))
    else:
        print(Colors.light_brown("❌ Username already exists."))

def handle_login():
    global current_user
    print(Colors.brown("\n--- Login ---"))
    username = Colors.input_brown("Username: ").strip()
    password = Colors.getpass_brown("Password: ").strip()
    user = authenticate_user(username, password)
    if user:
        current_user = user
        print(Colors.light_brown(f"✅ Login successful. Welcome, {user.full_name}"))
        return True
    else:
        print(Colors.light_brown("❌ Login failed. Invalid username or password."))
        return False

# [Rest of your functions remain the same, just update to use Colors.input_brown where needed]

def handle_create_account():
    print(Colors.brown("\n--- Create New Account ---"))
    
    # Validate account name with loop
    while True:
        acct_name = Colors.input_brown("Account Name (2-50 chars): ").strip()
        is_valid, msg = validate_account_name(acct_name)
        print(Colors.light_brown(msg))
        if is_valid:
            break
    
    acct = create_account(current_user.user_id, acct_name)
    print(Colors.light_brown(f"✅ Account created. Account ID: {acct.account_id} (Balance: {format_currency(acct.balance)})"))

def handle_list_accounts():
    accts = list_accounts(current_user.user_id)
    if not accts:
        print(Colors.light_brown("⚠️  No accounts found."))
        return
    print(Colors.brown("\nYour Accounts:"))
    for i, a in enumerate(accts, start=1):
        print(Colors.light_brown(f" {i}. ID: {a.account_id} | Name: {a.account_name} | Balance: {format_currency(a.balance)}"))

def select_account(exclude_account_id: str = None):
    accts = list_accounts(current_user.user_id)
    if not accts:
        print(Colors.light_brown("⚠️  No accounts found."))
        return None
    
    # Filter out excluded account if specified
    available_accts = [a for a in accts if a.account_id != exclude_account_id] if exclude_account_id else accts
    
    if not available_accts:
        print(Colors.light_brown("⚠️  No other accounts available."))
        return None
    
    print(Colors.brown("\nSelect an account:"))
    for i, a in enumerate(available_accts, start=1):
        print(Colors.light_brown(f" {i}. {a.account_name} (ID: {a.account_id}, Balance: {format_currency(a.balance)})"))
    try:
        idx = int(Colors.input_brown("Enter number: ").strip())
        if 1 <= idx <= len(available_accts):
            return available_accts[idx - 1]
    except ValueError:
        pass
    print(Colors.light_brown("❌ Invalid selection."))
    return None

def handle_deposit():
    acct = select_account()
    if not acct:
        return
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            amt_input = Colors.input_brown("Deposit amount (PHP): ").strip()
            if not amt_input:
                retry_count += 1
                continue
            amt = float(amt_input)
            is_valid, msg = validate_transaction_amount(amt)
            if not is_valid:
                print(Colors.light_brown(f"❌ {msg}"))
                retry_count += 1
                continue
            break
        except ValueError:
            print(Colors.light_brown("❌ Invalid amount. Please enter a valid number."))
            retry_count += 1
    
    if retry_count >= max_retries:
        print(Colors.light_brown("⚠️  Max retries exceeded. Returning to menu."))
        return

    txn = deposit(acct.account_id, amt, description="Deposit via CLI")
    if txn:
        print(Colors.light_brown(f"✅ Deposit successful. New balance: {format_currency(acct.balance)}"))
    else:
        print(Colors.light_brown("❌ Deposit failed."))

def handle_withdraw():
    acct = select_account()
    if not acct:
        return
    
    if acct.balance <= 0:
        print(Colors.light_brown(f"❌ Cannot withdraw from account with zero balance."))
        return
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            amt_input = Colors.input_brown("Withdrawal amount (PHP): ").strip()
            if not amt_input:
                retry_count += 1
                continue
            amt = float(amt_input)
            is_valid, msg = validate_transaction_amount(amt)
            if not is_valid:
                print(Colors.light_brown(f"❌ {msg}"))
                retry_count += 1
                continue
            if amt > acct.balance:
                print(Colors.light_brown(f"❌ Insufficient balance. Available: {format_currency(acct.balance)}"))
                retry_count += 1
                continue
            break
        except ValueError:
            print(Colors.light_brown("❌ Invalid amount. Please enter a valid number."))
            retry_count += 1
    
    if retry_count >= max_retries:
        print(Colors.light_brown("⚠️  Max retries exceeded. Returning to menu."))
        return

    txn = withdraw(acct.account_id, amt, description="Withdraw via CLI")
    if txn:
        print(Colors.light_brown(f"✅ Withdrawal successful. New balance: {format_currency(acct.balance)}"))
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

def prompt_bank_menu():
    print(Colors.brown("\n--- Linked Bank Accounts --"))
    print(Colors.light_brown("1. Link New Bank Account"))
    print(Colors.light_brown("2. View Linked Banks"))
    print(Colors.light_brown("3. View Total Linked Balance"))
    print(Colors.light_brown("4. Transfer to Linked Bank"))
    print(Colors.light_brown("5. Transfer Between CyBank Accounts"))
    print(Colors.light_brown("6. Unlink Bank Account"))
    print(Colors.light_brown("7. Back to Main Menu"))
    return Colors.input_brown("Select an option: ").strip()

def handle_link_bank_account():
    print(Colors.brown("\n--- Link New Bank Account ---"))
    
    # Display available Philippine banks
    banks_list = get_philippines_banks()
    print(Colors.light_brown("\nAvailable Banks:"))
    for i, bank in enumerate(banks_list, start=1):
        print(Colors.light_brown(f" {i}. {bank}"))
    
    # Select bank
    while True:
        try:
            bank_choice = int(Colors.input_brown("Select bank number: ").strip())
            if 1 <= bank_choice <= len(banks_list):
                bank_name = banks_list[bank_choice - 1]
                break
            else:
                print(Colors.light_brown("❌ Invalid selection. Please try again."))
        except ValueError:
            print(Colors.light_brown("❌ Please enter a valid number."))
    
    # Validate account number
    while True:
        account_number = Colors.input_brown("Enter account number (8-16 digits): ").strip()
        is_valid, msg = validate_account_number(account_number)
        print(Colors.light_brown(msg))
        if is_valid:
            break
    
    # Display available account types
    account_types = get_account_types()
    print(Colors.light_brown("\nAvailable Account Types:"))
    for i, acc_type in enumerate(account_types, start=1):
        print(Colors.light_brown(f" {i}. {acc_type}"))
    
    # Select account type
    while True:
        try:
            type_choice = int(Colors.input_brown("Select account type number: ").strip())
            if 1 <= type_choice <= len(account_types):
                account_type = account_types[type_choice - 1]
                break
            else:
                print(Colors.light_brown("❌ Invalid selection. Please try again."))
        except ValueError:
            print(Colors.light_brown("❌ Please enter a valid number."))
    
    # Validate initial balance
    while True:
        try:
            initial_balance = float(Colors.input_brown("Enter initial balance (PHP): ").strip())
            is_valid, msg = validate_balance(initial_balance)
            print(Colors.light_brown(msg))
            if is_valid:
                break
        except ValueError:
            print(Colors.light_brown("❌ Invalid amount entered."))
    
    linked_bank = add_bank_account(current_user.user_id, bank_name, account_number, account_type, initial_balance)
    print(Colors.light_brown(f"✅ Bank account linked successfully!"))
    print(Colors.light_brown(f"   Bank: {linked_bank.bank_name}"))
    print(Colors.light_brown(f"   Account: {linked_bank.account_number}"))
    print(Colors.light_brown(f"   Type: {linked_bank.account_type}"))
    print(Colors.light_brown(f"   Balance: {format_currency(linked_bank.balance)}"))

def handle_view_linked_banks():
    banks = list_bank_accounts(current_user.user_id)
    if not banks:
        print(Colors.light_brown("⚠️  No linked bank accounts found."))
        return
    
    # Limit to 10 accounts displayed
    display_limit = min(10, len(banks))
    if len(banks) > 10:
        print(Colors.light_brown(f"⚠️  You have {len(banks)} linked accounts. Showing first 10."))
    
    print(Colors.brown("\nYour Linked Bank Accounts:"))
    for i, bank in enumerate(banks[:display_limit], start=1):
        print(Colors.light_brown(f" {i}. Bank: {bank.bank_name} | Account: {bank.account_number} | Type: {bank.account_type} | Balance: {format_currency(bank.balance)}"))

def handle_view_total_linked_balance():
    total = get_total_linked_balance(current_user.user_id)
    banks = list_bank_accounts(current_user.user_id)
    if not banks:
        print(Colors.light_brown("⚠️  No linked bank accounts found."))
        return
    print(Colors.brown("\n--- Total Linked Balance ---"))
    print(Colors.light_brown(f"You have {len(banks)} linked bank account(s)."))
    print(Colors.light_brown(f"Total Balance Across All Banks: {format_currency(total)}"))

def select_linked_bank():
    banks = list_bank_accounts(current_user.user_id)
    if not banks:
        print(Colors.light_brown("⚠️  No linked bank accounts found."))
        return None
    
    # Limit display to 10 accounts
    display_limit = min(10, len(banks))
    if len(banks) > 10:
        print(Colors.light_brown(f"⚠️  You have {len(banks)} linked accounts. Showing first 10."))
    
    print(Colors.brown("\nSelect a linked bank account:"))
    for i, bank in enumerate(banks[:display_limit], start=1):
        print(Colors.light_brown(f" {i}. {bank.bank_name} ({bank.account_number}) - Balance: {format_currency(bank.balance)}"))
    try:
        idx = int(Colors.input_brown("Enter number: ").strip())
        if 1 <= idx <= display_limit:
            return banks[idx - 1]
    except ValueError:
        pass
    print(Colors.light_brown("❌ Invalid selection."))
    return None

def handle_transfer_to_external_bank():
    print(Colors.brown("\n--- Transfer to Linked Bank (PayPal to GCash Logic) ---"))
    
    # Select source CyBank account
    source_account = select_account()
    if not source_account:
        return
    
    if source_account.balance <= 0:
        print(Colors.light_brown(f"❌ Cannot transfer from account with zero balance."))
        return
    
    # Select destination linked bank
    dest_bank = select_linked_bank()
    if not dest_bank:
        return
    
    # Validate transfer amount with retry limit
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            amt_input = Colors.input_brown("Transfer amount (PHP): ").strip()
            if not amt_input:
                retry_count += 1
                continue
            amt = float(amt_input)
            is_valid, msg = validate_transaction_amount(amt)
            if not is_valid:
                print(Colors.light_brown(f"❌ {msg}"))
                retry_count += 1
                continue
            if amt > source_account.balance:
                print(Colors.light_brown(f"❌ Insufficient balance in {source_account.account_name}. Available: {format_currency(source_account.balance)}"))
                retry_count += 1
                continue
            break
        except ValueError:
            print(Colors.light_brown("❌ Invalid amount. Please enter a valid number."))
            retry_count += 1
    
    if retry_count >= max_retries:
        print(Colors.light_brown("⚠️  Max retries exceeded. Returning to menu."))
        return
    
    # Confirm transfer
    print(Colors.light_brown(f"\n📋 Transfer Summary:"))
    print(Colors.light_brown(f"   From: {source_account.account_name} ({format_currency(source_account.balance)})"))
    print(Colors.light_brown(f"   To: {dest_bank.bank_name} ({dest_bank.account_number})"))
    print(Colors.light_brown(f"   Amount: {format_currency(amt)}"))
    confirm = Colors.input_brown("Proceed with transfer? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        transfer_record = transfer_to_external_bank(current_user.user_id, source_account.account_id, 
                                                   dest_bank.linked_bank_id, amt)
        if transfer_record:
            print(Colors.light_brown(f"✅ Transfer successful!"))
            print(Colors.light_brown(f"   New CyBank balance: {format_currency(source_account.balance - amt)}"))
            print(Colors.light_brown(f"   {dest_bank.bank_name} balance: {format_currency(dest_bank.balance + amt)}"))
        else:
            print(Colors.light_brown("❌ Transfer failed. Please try again."))
    else:
        print(Colors.light_brown("Transfer cancelled."))

def handle_transfer_between_cybank_accounts():
    print(Colors.brown("\n--- Transfer Between CyBank Accounts ---"))
    
    # Check if user has at least 2 accounts
    accts = list_accounts(current_user.user_id)
    if len(accts) < 2:
        print(Colors.light_brown("❌ You need at least 2 accounts to transfer between accounts."))
        print(Colors.light_brown(f"   You currently have {len(accts)} account(s)."))
        return
    
    # Select source account
    print(Colors.light_brown("\nSelect source account:"))
    source_account = select_account()
    if not source_account:
        return
    
    if source_account.balance <= 0:
        print(Colors.light_brown(f"❌ Cannot transfer from account with zero balance."))
        return
    
    # Select destination account (exclude source)
    print(Colors.light_brown("\nSelect destination account:"))
    dest_account = select_account(exclude_account_id=source_account.account_id)
    if not dest_account:
        return
    
    # Validate transfer amount with retry limit
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            amt_input = Colors.input_brown("Transfer amount (PHP): ").strip()
            if not amt_input:
                retry_count += 1
                continue
            amt = float(amt_input)
            is_valid, msg = validate_transaction_amount(amt)
            if not is_valid:
                print(Colors.light_brown(f"❌ {msg}"))
                retry_count += 1
                continue
            if amt > source_account.balance:
                print(Colors.light_brown(f"❌ Insufficient balance. Available: {format_currency(source_account.balance)}"))
                retry_count += 1
                continue
            break
        except ValueError:
            print(Colors.light_brown("❌ Invalid amount. Please enter a valid number."))
            retry_count += 1
    
    if retry_count >= max_retries:
        print(Colors.light_brown("⚠️  Max retries exceeded. Returning to menu."))
        return
    
    # Confirm transfer
    print(Colors.light_brown(f"\n📋 Transfer Summary:"))
    print(Colors.light_brown(f"   From: {source_account.account_name} ({format_currency(source_account.balance)})"))
    print(Colors.light_brown(f"   To: {dest_account.account_name} ({format_currency(dest_account.balance)})"))
    print(Colors.light_brown(f"   Amount: {format_currency(amt)}"))
    confirm = Colors.input_brown("Proceed with transfer? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        transfer_record = transfer_between_cybank_accounts(current_user.user_id, source_account.account_id, 
                                                          dest_account.account_id, amt)
        if transfer_record:
            print(Colors.light_brown(f"✅ Transfer successful!"))
            print(Colors.light_brown(f"   {source_account.account_name} new balance: {format_currency(source_account.balance - amt)}"))
            print(Colors.light_brown(f"   {dest_account.account_name} new balance: {format_currency(dest_account.balance + amt)}"))
        else:
            print(Colors.light_brown("❌ Transfer failed. Please try again."))
    else:
        print(Colors.light_brown("Transfer cancelled."))

def prompt_reports_menu():
    print(Colors.brown("\n--- Financial Reports ---"))
    print(Colors.light_brown("1. Account Summary"))
    print(Colors.light_brown("2. Transaction Report"))
    print(Colors.light_brown("3. Multi-Bank Portfolio"))
    print(Colors.light_brown("4. Complete Financial Report"))
    print(Colors.light_brown("5. Back to Main Menu"))
    return Colors.input_brown("Select an option: ").strip()

def handle_account_summary():
    print(Colors.brown("\n--- Account Summary Report ---"))
    report = generate_account_summary(current_user.user_id)
    
    print(Colors.light_brown(f"\n📊 CyBank Account Summary:"))
    print(Colors.light_brown(f"   Total Accounts: {report['account_count']}"))
    print(Colors.light_brown(f"   Total Balance: {format_currency(report['total_cybank_balance'])}\n"))
    
    if report['cybank_accounts']:
        print(Colors.light_brown("Account Details:"))
        for i, acct in enumerate(report['cybank_accounts'], 1):
            print(Colors.light_brown(f"   {i}. {acct['account_name']}"))
            print(Colors.light_brown(f"      Balance: {format_currency(acct['balance'])}"))
            print(Colors.light_brown(f"      Transactions: {acct['transaction_count']}"))
            print(Colors.light_brown(f"      Created: {acct['created_at'][:19]}\n"))
    else:
        print(Colors.light_brown("   ⚠️  No accounts found."))

def handle_transaction_report():
    print(Colors.brown("\n--- Transaction Report ---"))
    
    # Ask user if they want to filter by account
    filter_choice = Colors.input_brown("Filter by account? (yes/no): ").strip().lower()
    account_id = None
    
    if filter_choice == "yes":
        acct = select_account()
        if not acct:
            return
        account_id = acct.account_id
    
    report = generate_transaction_report(current_user.user_id, account_id)
    
    if "error" in report:
        print(Colors.light_brown(f"❌ {report['error']}"))
        return
    
    print(Colors.light_brown(f"\n📈 Transaction Report:"))
    print(Colors.light_brown(f"   Total Transactions: {report['transaction_count']}"))
    print(Colors.light_brown(f"   Total Credits: {format_currency(report['total_credits'])}"))
    print(Colors.light_brown(f"   Total Debits: {format_currency(report['total_debits'])}"))
    print(Colors.light_brown(f"   Net Change: {format_currency(report['net_change'])}\n"))
    
    if report['transactions']:
        print(Colors.light_brown("Recent Transactions (Latest First):"))
        display_limit = min(10, len(report['transactions']))
        if len(report['transactions']) > 10:
            print(Colors.light_brown(f"   (Showing first 10 of {len(report['transactions'])})\n"))
        
        for i, txn in enumerate(report['transactions'][:display_limit], 1):
            symbol = "+" if txn['transaction_type'] == "CREDIT" else "-"
            print(Colors.light_brown(f"   {i}. [{txn['transaction_type']}] {symbol}{format_currency(abs(txn['amount']))}"))
            print(Colors.light_brown(f"      Account: {txn['account_name']}"))
            print(Colors.light_brown(f"      Description: {txn['description'] or 'N/A'}"))
            print(Colors.light_brown(f"      Date: {txn['timestamp'][:19]}\n"))
    else:
        print(Colors.light_brown("   ⚠️  No transactions found."))

def handle_portfolio_report():
    print(Colors.brown("\n--- Multi-Bank Portfolio Report ---"))
    report = generate_multi_bank_portfolio(current_user.user_id)
    
    print(Colors.light_brown(f"\n🏦 Linked Banks Portfolio:"))
    print(Colors.light_brown(f"   Total Linked Banks: {report['bank_count']}"))
    print(Colors.light_brown(f"   Total Balance: {format_currency(report['total_linked_balance'])}"))
    
    if report['bank_count'] > 0:
        print(Colors.light_brown(f"   Average Balance: {format_currency(report['average_balance_per_bank'])}\n"))
        
        print(Colors.light_brown("Bank Details:"))
        for i, bank in enumerate(report['linked_banks'], 1):
            print(Colors.light_brown(f"   {i}. {bank['bank_name']}"))
            print(Colors.light_brown(f"      Account Number: {bank['account_number']}"))
            print(Colors.light_brown(f"      Type: {bank['account_type']}"))
            print(Colors.light_brown(f"      Balance: {format_currency(bank['balance'])}"))
            print(Colors.light_brown(f"      Last Synced: {bank['last_synced'][:19]}\n"))
        
        if report['bank_summary']:
            print(Colors.light_brown("Summary by Account Type:"))
            for acc_type, summary in report['bank_summary'].items():
                print(Colors.light_brown(f"   {acc_type.upper()}:"))
                print(Colors.light_brown(f"      Count: {summary['count']}"))
                print(Colors.light_brown(f"      Total Balance: {format_currency(summary['total_balance'])}\n"))
    else:
        print(Colors.light_brown("   ⚠️  No linked banks found."))

def handle_complete_report():
    print(Colors.brown("\n--- Complete Financial Report ---"))
    report = generate_complete_financial_report(current_user.user_id)
    combined = report['combined_analysis']
    
    print(Colors.light_brown(f"\n💰 Financial Overview:"))
    print(Colors.light_brown(f"   Total CyBank Balance: {format_currency(combined['total_cybank_balance'])}"))
    print(Colors.light_brown(f"   Total Linked Balance: {format_currency(combined['total_linked_balance'])}"))
    print(Colors.light_brown(f"   TOTAL ALL ACCOUNTS: {format_currency(combined['total_balance_all'])}\n"))
    
    if combined['total_balance_all'] > 0:
        print(Colors.light_brown(f"   CyBank Percentage: {combined['cybank_percentage']:.1f}%"))
        print(Colors.light_brown(f"   Linked Banks Percentage: {combined['linked_percentage']:.1f}%\n"))
    
    print(Colors.light_brown(f"📊 Account Statistics:"))
    print(Colors.light_brown(f"   Total CyBank Accounts: {combined['total_accounts']}"))
    print(Colors.light_brown(f"   Total Linked Banks: {combined['total_linked_banks']}"))
    print(Colors.light_brown(f"   Total Transactions: {combined['total_transactions']}\n"))
    
    print(Colors.light_brown(f"Account Details:"))
    cybank = report['cybank_summary']
    print(Colors.light_brown(f"   CyBank: {cybank['account_count']} account(s) | {format_currency(cybank['total_cybank_balance'])}"))
    
    portfolio = report['portfolio_report']
    if portfolio['bank_count'] > 0:
        print(Colors.light_brown(f"   Linked Banks: {portfolio['bank_count']} bank(s) | {format_currency(portfolio['total_linked_balance'])}"))
    else:
        print(Colors.light_brown(f"   Linked Banks: None\n"))

def handle_reports_menu():
    while True:
        cmd = prompt_reports_menu()
        if cmd == "1":
            handle_account_summary()
        elif cmd == "2":
            handle_transaction_report()
        elif cmd == "3":
            handle_portfolio_report()
        elif cmd == "4":
            handle_complete_report()
        elif cmd == "5":
            break
        else:
            print(Colors.light_brown("⚠️  Invalid option."))

def handle_unlink_bank_account():
    bank = select_linked_bank()
    if not bank:
        return
    confirm = Colors.input_brown(f"Are you sure you want to unlink {bank.bank_name} ({bank.account_number})? (yes/no): ").strip().lower()
    if confirm == "yes":
        if remove_bank_account(bank.linked_bank_id, current_user.user_id):
            print(Colors.light_brown(f"✅ Bank account unlinked successfully."))
        else:
            print(Colors.light_brown("❌ Failed to unlink bank account."))
    else:
        print(Colors.light_brown("Unlink cancelled."))

def handle_bank_accounts_menu():
    while True:
        cmd = prompt_bank_menu()
        if cmd == "1":
            handle_link_bank_account()
        elif cmd == "2":
            handle_view_linked_banks()
        elif cmd == "3":
            handle_view_total_linked_balance()
        elif cmd == "4":
            handle_transfer_to_external_bank()
        elif cmd == "5":
            handle_transfer_between_cybank_accounts()
        elif cmd == "6":
            handle_unlink_bank_account()
        elif cmd == "7":
            break
        else:
            print(Colors.light_brown("⚠️  Invalid option."))

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
                        handle_bank_accounts_menu()
                    elif cmd == "7":
                        handle_reports_menu()
                    elif cmd == "8":
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