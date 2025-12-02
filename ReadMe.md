# CyBank - CLI Banking Application

A lightweight, in-memory Python banking application featuring user authentication, multi-account management, multi-bank integration, and secure fund transfers. Built with Philippines-first localization (₱ currency, 20 local banks, 7 account types).

**Status:** Phase 3b Complete - Full CLI with transfer to linked banks feature  
**Python Version:** 3.8+ (tested on Python 3.13)  
**Architecture:** CLI-only, in-memory services (no database backend)

---

## 📁 Project Structure & Documentation

### **`backend/` — Core Business Logic & Data Models**

#### **Models** (`backend/models/`)

**`user.py` — User Account Model**
```python
@dataclass
class User:
    username: str              # Letters only (3-20 chars)
    full_name: str            # Letters/spaces/hyphens (2-50 chars)
    password_hash: str        # SHA-256 hash with salt
    user_id: str              # Unique UUID
    email: str = None         # Optional, valid format if provided
    created_at: datetime      # Registration timestamp
```
- Represents a CyBank user account with authentication credentials
- Stores hashed password (never plain text) using `utils/auth.py`
- Email is optional; validation skipped if empty

**`account.py` — CyBank Account Model**
```python
@dataclass
class Account:
    user_id: str              # Owner's user ID
    account_name: str         # Account identifier (2-50 chars)
    account_id: str           # Unique UUID
    balance: float = 0.0      # Starting balance in Philippine Peso (₱)
    created_at: datetime      # Account creation timestamp
```
- Represents a user's bank account within CyBank
- Each user can have multiple accounts
- Balance is in Philippine Peso currency

**`transaction.py` — Transaction Record Model**
```python
@dataclass
class Transaction:
    account_id: str           # Account being transacted
    amount: float             # Signed amount (+deposit, -withdrawal)
    transaction_type: str     # "CREDIT" (deposit) or "DEBIT" (withdrawal)
    transaction_id: str       # Unique UUID
    timestamp: datetime       # When transaction occurred
    description: str = ""     # Optional note (e.g., "Salary deposit")
    category: str = None      # Optional category tag
```
- Records financial transactions (deposits, withdrawals, transfers)
- Amount is signed; positive for CREDIT, negative for DEBIT
- Used for transaction history and audit trails

**`linked_bank.py` — External Bank Account Model**
```python
@dataclass
class LinkedBankAccount:
    user_id: str              # CyBank user linking external bank
    bank_name: str            # Bank name (from 20 Philippines banks)
    account_number: str       # External bank account number (8-16 digits)
    account_type: str         # Type (checking, savings, salary, etc.)
    balance: float = 0.0      # Linked bank balance
    last_synced: datetime     # Last balance update timestamp
    linked_bank_id: str       # Unique UUID
```
- Represents an external bank account linked to a CyBank user
- Enables multi-bank integration (PayPal to GCash style transfers)
- Stores mock balance for linked external banks

#### **Services** (`backend/services/`)

**`user_service.py` — User Management**
- `register_user(username, password, full_name, email)` → User | None
  - Creates new user with validation (username letters-only, 6+ char password)
  - Hashes password using `utils/auth.py`
  - Returns User object or None if username already exists
  
- `authenticate_user(username, password)` → User | None
  - Verifies credentials by comparing password hash
  - Returns User object on success, None on auth failure

**`account_service.py` — Account Management**
- `create_account(user_id, account_name)` → Account
  - Creates new account for user with initial balance ₱0.00
  - Returns Account object with unique ID
  
- `list_accounts(user_id)` → list[Account]
  - Retrieves all accounts owned by user
  
- `get_account(account_id)` → Account | None
  - Retrieves specific account by ID (used in transfers)
  
- `update_account_balance(account_id, new_balance)` → bool
  - Updates account balance atomically (used in transfers)

**`transaction_service.py` — Transaction Recording**
- `deposit(account_id, amount, description, category)` → Transaction | None
  - Records credit transaction (adds to balance)
  - Creates Transaction with type "CREDIT"
  - Returns Transaction object or None if account not found
  
- `withdraw(account_id, amount, description, category)` → Transaction | None
  - Records debit transaction (subtracts from balance)
  - Validates sufficient balance before withdrawal
  - Creates Transaction with type "DEBIT" (amount stored as negative)
  - Returns None if insufficient funds
  
- `record_transaction(account_id, amount, transaction_type, description, category)` → Transaction | None
  - Generic transaction recorder used by transfer operations
  - Handles both CREDIT and DEBIT types
  - Signs amount based on transaction type
  
- `get_transactions(account_id)` → list[Transaction]
  - Retrieves all transactions for an account

**`bank_integration_service.py` — Multi-Bank Integration**
- `add_bank_account(user_id, bank_name, account_number, account_type, initial_balance)` → LinkedBankAccount
  - Links external bank account to CyBank user
  - Validates bank name (must be from 20 Philippines banks)
  - Validates account number (8-16 digits only)
  - Returns LinkedBankAccount object
  
- `list_bank_accounts(user_id)` → list[LinkedBankAccount]
  - Retrieves all linked external banks for user (max 10 displayed in CLI)
  
- `get_bank_account(linked_bank_id)` → LinkedBankAccount | None
  - Retrieves specific linked bank by ID
  
- `update_bank_balance(linked_bank_id, new_balance)` → bool
  - Updates linked bank balance (mock sync operation)
  
- `remove_bank_account(linked_bank_id, user_id)` → bool
  - Unlinks external bank from user
  - Requires user verification
  
- `get_total_linked_balance(user_id)` → float
  - Calculates total balance across all linked banks

**`transfer_service.py` — Fund Transfer Operations**
- `transfer_to_external_bank(user_id, from_account_id, to_linked_bank_id, amount, description)` → dict | None
  - Transfers funds from CyBank account to linked external bank (PayPal→GCash logic)
  - Deducts from CyBank account, credits external bank
  - Records transaction in source account
  - Validates sufficient balance; returns None on failure
  - Automatic rollback if any step fails
  
- `transfer_between_cybank_accounts(user_id, from_account_id, to_account_id, amount, description)` → dict | None
  - Transfers between two CyBank accounts (same user)
  - Records DEBIT in source, CREDIT in destination
  - Prevents self-transfers
  - Validates sufficient balance; returns None on failure
  
- `get_transfer_history(user_id)` → list[dict]
  - Retrieves all transfers for user
  
- `get_transfer(transfer_id)` → dict | None
  - Retrieves specific transfer by ID

---

### **`cli/` — Command-Line Interface**

**`main.py` — Interactive CLI Menu System**

**Main Menu Functions:**
- `prompt_main_menu()` → Returns user choice
  - 1. Register new user
  - 2. Login existing user
  - 3. Exit application

**User Session Menu:**
- `prompt_user_menu()` → Returns user choice
  - 1. Create Account
  - 2. List Accounts
  - 3. Deposit
  - 4. Withdraw
  - 5. Show Transactions
  - 6. Linked Bank Accounts
  - 7. Logout

**Bank Account Menu:**
- `prompt_bank_menu()` → Returns user choice
  - 1. Link New Bank Account
  - 2. View Linked Banks
  - 3. View Total Linked Balance
  - 4. Transfer to Linked Bank (new)
  - 5. Transfer Between CyBank Accounts (new)
  - 6. Unlink Bank Account
  - 7. Back to Main Menu

**Authentication Handlers:**
- `handle_register()` - User registration with validation loops (username, password, full name, email)
- `handle_login()` - User authentication with password verification

**Account Management Handlers:**
- `handle_create_account()` - Create new CyBank account with name validation (2-50 chars)
- `handle_list_accounts()` - Display all user accounts with balances
- `handle_deposit()` - Deposit funds with **3-retry max on invalid input**
- `handle_withdraw()` - Withdraw funds with **3-retry max, zero balance check**
- `handle_show_transactions()` - Display transaction history

**Bank Integration Handlers:**
- `handle_link_bank_account()` - Link external bank with dropdown selections (20 banks, 7 types)
- `handle_view_linked_banks()` - Display linked banks (max 10 shown)
- `handle_view_total_linked_balance()` - Calculate and display total linked balance
- `handle_transfer_to_external_bank()` - Transfer to linked bank with **3-retry max, zero balance check**
- `handle_transfer_between_cybank_accounts()` - Transfer between CyBank accounts with **3-retry max, 2-account minimum**
- `handle_unlink_bank_account()` - Unlink external bank with confirmation

**Helper Functions:**
- `select_account(exclude_account_id=None)` - Account selector with optional source filtering
- `select_linked_bank()` - Linked bank selector (shows max 10)
- `handle_bank_accounts_menu()` - Bank submenu loop handler

**Utility Class:**
- `Colors` - ANSI color formatting for terminal output
  - `brown()` - Header color
  - `light_brown()` - Content color
  - `input_brown()` - Colored input prompt
  - `getpass_brown()` - Colored password input (hidden)

---

### **`utils/` — Shared Utilities & Helpers**

**`auth.py` — Password Security**
- `hash_password(raw_password)` → str
  - Generates random 16-byte salt + SHA-256 hash
  - Returns format: `"salt$hash"` (e.g., `"a1b2c3d4...$e5f6g7h8..."`)
  - Each password gets unique salt (prevents rainbow table attacks)
  
- `verify_password(raw_password, stored_hash)` → bool
  - Extracts salt from stored hash
  - Rehashes entered password with same salt
  - Returns True if matches, False otherwise
  - Never stores or compares plain text

**`validators.py` — Input Validation with Philippines Localization**

**Username/Password/Name Validators:**
- `validate_username(str)` → (bool, str)
  - Letters only, 3-20 chars
  - Returns (True, "✅ Username valid.") or (False, error message)
  
- `validate_password(str)` → (bool, str)
  - Minimum 6 characters
  - Detects empty input (including stripped whitespace)
  
- `validate_full_name(str)` → (bool, str)
  - Letters, spaces, hyphens only
  - 2-50 characters
  
- `validate_email(str)` → (bool, str)
  - Optional field; validates format if provided
  - Checks for @ symbol and domain

**Account Validators:**
- `validate_account_name(str)` → (bool, str)
  - 2-50 characters (any characters allowed)
  
- `validate_account_number(str)` → (bool, str)
  - 8-16 digits only (for linked banks)
  
- `validate_account_type(str)` → (bool, str)
  - Must match predefined types: checking, savings, money_market, salary, time_deposit, passbook, digital

**Transaction Validators:**
- `validate_transaction_amount(float)` → (bool, str)
  - Range: ₱0.01 to ₱999,999.99
  - Prevents zero/negative amounts
  
- `validate_balance(float)` → (bool, str)
  - Range: ₱0 to ₱999,999,999.99
  
- `validate_bank_name(str)` → (bool, str)
  - Must be in `get_philippines_banks()` list

**Philippines Localization:**
- `get_philippines_banks()` → list[str]
  - Returns 20 major Philippine banks: BDO, BPI, Metrobank, PNB, Security Bank, etc.
  
- `get_account_types()` → list[str]
  - Returns 7 account types: checking, savings, money_market, salary, time_deposit, passbook, digital
  
- `format_currency(float)` → str
  - Formats amount as Philippine Peso: `"₱X,XXX.XX"`
  - Example: `format_currency(1234.5)` → `"₱1,234.50"`

**`config.py` — Configuration Values**
- Central configuration file (implementation specific to project needs)

**`helpers.py` — General Utilities**
- Shared helper functions across the project

---

## 🚀 Quick Start

### **Installation**
```bash
# Clone repository
git clone <repo-url>
cd CyBank

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
# OR: source .venv/bin/activate  # Linux/Mac

# No external dependencies required (uses Python stdlib)
```

### **Running the Application**
```bash
python -m cli.main
```

### **User Flow Example**
1. Register: Enter username (letters only), password (6+ chars), full name
2. Login: Enter credentials
3. Create account: Name your account (2-50 chars)
4. Deposit: Add funds (₱0.01-₱999,999.99)
5. Link bank: Select from 20 Philippines banks
6. Transfer: Send to linked bank or another account

---

## 🔐 Security Features

| Feature | Implementation |
|---------|-----------------|
| **Password Hashing** | SHA-256 with random 16-byte salt per password |
| **Input Validation** | Comprehensive validators with user feedback loops |
| **Retry Limits** | Max 3 attempts on invalid input to prevent infinite loops |
| **Zero Balance Check** | Prevents withdrawal/transfer from empty accounts |
| **Account Filtering** | Source account excluded from destination selection |
| **Transaction Rollback** | Automatic rollback if transfer fails mid-operation |
| **Balance Verification** | All transfers check sufficient funds before processing |

---

## 📊 Data Storage

**Architecture:** In-memory service layer with Python dictionaries
- No external database required
- Data persists only during runtime (in-memory)
- Ideal for MVP and testing
- Easy to add JSON/CSV export later

**Storage Maps:**
```
Users:              user_id → User object
Accounts:           account_id → Account object
Transactions:       account_id → list[Transaction]
Linked Banks:       linked_bank_id → LinkedBankAccount object
Transfers:          transfer_id → transfer record dict
```

---

## ⚙️ Error Handling & Edge Cases

**Handled Scenarios:**
- ✅ Empty/invalid user input (3 retries max, then return to menu)
- ✅ Insufficient balance (prevents overdraft)
- ✅ Zero account balance (prevents withdrawal/transfer)
- ✅ Only 1 account (prevents inter-account transfer; shows error)
- ✅ Duplicate usernames (shows error, allows retry)
- ✅ Invalid credentials (shows error, returns to main menu)
- ✅ Missing linked banks (shows warning message)
- ✅ Account not found (returns None, shows error)

---

## 🧪 Testing

### **Test Scripts Included:**
- `test_transfers.py` - Comprehensive transfer functionality test
- `test_retry_limits.py` - Retry limits and edge cases verification

### **Running Tests:**
```bash
python test_transfers.py          # Transfer feature test
python test_retry_limits.py       # Retry limits verification
```

---

## 📈 Project Progress

**Phase 1: Core Infrastructure** ✅
- User authentication with password hashing
- Account management
- Transaction recording (deposit/withdraw)

**Phase 2: CLI & Bank Linking** ✅
- Interactive menu system
- Multi-bank account linking (20 Philippines banks)
- 7 account types support
- Philippines currency (₱) formatting
- 10-item display limit on linked banks

**Phase 3a: Transfer to Linked Banks** ✅
- Transfer from CyBank to external linked banks
- PayPal→GCash style integration
- Transaction history recording
- Retry limits and balance validation

**Phase 3b: Transfer Between CyBank Accounts** ✅
- Internal account-to-account transfers
- Dual transaction recording (DEBIT + CREDIT)
- Account exclusion on destination selection
- Minimum 2-account requirement

**Phase 4: Analysis Reports** ⏳
- Account summary generation
- Transaction filtering and reporting
- Multi-bank portfolio analysis

**Phase 5: Database Integration** ⏳
- Optional persistent storage (JSON/CSV export)
- Deferred for MVP

---

## 🛠️ Development Notes

### **Adding New Features:**
1. Add model to `backend/models/` (dataclass)
2. Add service functions to `backend/services/`
3. Add CLI handlers to `cli/main.py`
4. Add validators to `utils/validators.py` if needed
5. Test with interactive CLI or test scripts

### **Code Style:**
- Type hints on all functions
- Docstrings for complex functions
- ANSI color formatting for CLI output
- Validation functions return `(bool, str)` tuples

### **Common Patterns:**
```python
# Validation with retry loop (3 max retries)
max_retries = 3
retry_count = 0
while retry_count < max_retries:
    user_input = get_input()
    is_valid, msg = validator(user_input)
    if is_valid:
        break
    retry_count += 1
else:
    print("Max retries exceeded. Returning to menu.")
    return

# Service layer call pattern
result = service_function(user_id, ...)
if result:
    print("Success!")
else:
    print("Failed.")
```

---

## 📝 Files Summary

| File | Purpose | Key Functions |
|------|---------|---------------|
| `backend/models/user.py` | User dataclass | User(username, password_hash, full_name, email, user_id) |
| `backend/models/account.py` | Account dataclass | Account(user_id, account_name, account_id, balance) |
| `backend/models/transaction.py` | Transaction dataclass | Transaction(account_id, amount, transaction_type, timestamp) |
| `backend/models/linked_bank.py` | LinkedBankAccount dataclass | LinkedBankAccount(user_id, bank_name, account_number, account_type) |
| `backend/services/user_service.py` | User auth & management | register_user(), authenticate_user() |
| `backend/services/account_service.py` | Account CRUD | create_account(), list_accounts(), get_account(), update_account_balance() |
| `backend/services/transaction_service.py` | Transaction recording | deposit(), withdraw(), record_transaction(), get_transactions() |
| `backend/services/bank_integration_service.py` | Multi-bank linking | add_bank_account(), list_bank_accounts(), remove_bank_account(), get_total_linked_balance() |
| `backend/services/transfer_service.py` | Fund transfers | transfer_to_external_bank(), transfer_between_cybank_accounts() |
| `cli/main.py` | Interactive CLI | Main menu system with all handlers and helpers |
| `utils/auth.py` | Password security | hash_password(), verify_password() |
| `utils/validators.py` | Input validation | 15+ validators with Philippines localization |
| `utils/config.py` | Configuration | Central config (if needed) |
| `utils/helpers.py` | General utilities | Shared helper functions |

---

## 📞 Support & Contributing

- **Questions?** Check function docstrings and inline comments
- **Found a bug?** Create an issue with steps to reproduce
- **Want to contribute?** Follow the code patterns above and test thoroughly

---

**Last Updated:** December 2, 2025  
**Version:** 1.0 (Phase 3b Complete)