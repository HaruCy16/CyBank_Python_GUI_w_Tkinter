# utils/validators.py
import re

# Philippine Peso Currency
PHP_SYMBOL = "₱"

# Philippines-based bank account types
ACCOUNT_TYPES = [
    "checking",
    "savings",
    "money_market",
    "salary",
    "time_deposit",
    "passbook",
    "digital"
]

# Philippines-based banks
PHILIPPINES_BANKS = [
    "BDO",
    "BPI",
    "Metrobank",
    "PNB",
    "Security Bank",
    "Eastwest Bank",
    "UCPB",
    "China Bank",
    "ING Bank",
    "Maybank",
    "Standard Chartered",
    "HSBC",
    "UBP",
    "Equitable PCBank",
    "Landbank",
    "DBP",
    "Asia United Bank",
    "Bank of Commerce",
    "Citi",
    "Other"
]

#USERNAME VALIDATION, ERROR MESSAGES
def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username.
    - Required
    - Length: 3-20 characters
    - Letters only (no numbers, special characters, or spaces)
    """
    if not username:
        return False, "Username is required."
    if ' ' in username:
        return False, "❌ Username cannot contain spaces."
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(username) > 20:
        return False, "Username must not exceed 20 characters."
    if not re.match(r"^[a-zA-Z]+$", username):
        return False, "Username can only contain letters."
    return True, "✅ Username valid."

#VALIDATION FOR PASSWORD, ERORR MESSAGES
def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password.
    - Required
    - Minimum 6 characters
    - No spaces allowed
    - At least one letter and one number recommended
    """
    if not password:
        return False, "Password is required."
    if ' ' in password:
        return False, "❌ Password cannot contain spaces."
    if len(password) < 6:
        return False, "❌ Password must be at least 6 characters (minimum 6 characters)."
    return True, "✅ Password valid."


#FULL NAME VALIDATION, ERROR MESSAGES
def validate_full_name(full_name: str) -> tuple[bool, str]:
    """
    Validate full name.
    - Required
    - Length: 2-50 characters
    - Letters, spaces, hyphens only
    """
    full_name = full_name.strip()
    if not full_name:
        return False, "Full name is required."
    if len(full_name) < 2:
        return False, "Full name must be at least 2 characters long."
    if len(full_name) > 50:
        return False, "Full name must not exceed 50 characters."
    if not re.match(r"^[a-zA-Z\s'-]+$", full_name):
        return False, "Full name can only contain letters, spaces, hyphens, and apostrophes."
    return True, "✅ Full name valid."

#EMAIL VALIDATION, ERROR MESSAGES
def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format.
    - Optional (but if provided, must be valid)
    """
    if not email:
        return True, "✅ Email optional."
    
    email = email.strip()
    # Simple email validation, CHECK IF VALID FORMAT
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format."
    return True, "✅ Email valid."

#ACCOUNT NUMBER VALIDATION, ERROR MESSAGES
def validate_account_number(account_number: str) -> tuple[bool, str]:
    """
    Validate account number (Philippines standard).
    - Required
    - Length: 8-16 digits
    - Numbers only
    """
    account_number = account_number.strip()
    if not account_number:
        return False, "Account number is required."
    if not account_number.isdigit():
        return False, "Account number must contain only digits."
    if len(account_number) < 8:
        return False, "Account number must be at least 8 digits long."
    if len(account_number) > 16:
        return False, "Account number must not exceed 16 digits."
    return True, "✅ Account number valid."

#ACCOUNT TYPE VALIDATION, ERROR MESSAGES
def validate_account_type(account_type: str) -> tuple[bool, str]:
    """
    Validate account type against predefined Philippines bank types.
    """
    account_type = account_type.strip()
    if not account_type:
        return False, "Account type is required."
    
    # Check if the provided type matches any of the valid types (case-insensitive)
    valid_types = [t.lower() for t in ACCOUNT_TYPES]
    if account_type.lower() not in valid_types:
        return False, f"Invalid account type. Valid types: {', '.join(ACCOUNT_TYPES)}"
    return True, "✅ Account type valid."

#ACCOUNT NAME VALIDATION, ERROR MESSAGES
def validate_account_name(account_name: str) -> tuple[bool, str]:
    """
    Validate CyBank account name.
    - Required
    - Length: 2-50 characters
    """
    account_name = account_name.strip()
    if not account_name:
        return False, "Account name is required."
    if len(account_name) < 2:
        return False, "Account name must be at least 2 characters long."
    if len(account_name) > 50:
        return False, "Account name must not exceed 50 characters."
    return True, "✅ Account name valid."

#BALANCE VALIDATION, ERROR MESSAGES
def validate_balance(balance: float) -> tuple[bool, str]:
    """
    Validate balance.
    - Must be non-negative
    """
    try:
        balance = float(balance)
        if balance < 0:
            return False, "Balance cannot be negative."
        return True, "✅ Balance valid."
    except (ValueError, TypeError):
        return False, "Invalid balance amount."
    
#TRANSFER AMOUNT VALIDATION, ERROR MESSAGES
def validate_transfer_amount(amount: float, available_balance: float) -> tuple[bool, str]:
    """
    Validate transfer amount.
    - Must be positive
    - Must not exceed available balance
    """
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be positive."
        if amount > available_balance:
            return False, f"Insufficient balance. Available: ${available_balance:.2f}"
        return True, "✅ Amount valid."
    except (ValueError, TypeError):
        return False, "Invalid amount."
    
# FUNCTIONS TO GET PREDEFINED LISTS
def get_account_types() -> list[str]:
    """Get list of valid account types for Philippines."""
    return ACCOUNT_TYPES

def get_philippines_banks() -> list[str]:
    """Get list of Philippines banks."""
    return PHILIPPINES_BANKS

def validate_bank_name(bank_name: str) -> tuple[bool, str]:
    """
    Validate bank name (Philippines based).
    """
    bank_name = bank_name.strip()
    if not bank_name:
        return False, "Bank name is required."
    if bank_name not in PHILIPPINES_BANKS:
        return False, f"Bank must be a Philippine bank. Valid banks: {', '.join(PHILIPPINES_BANKS[:5])}..."
    return True, "✅ Bank name valid."

#TRANSACTION AMOUNT VALIDATION, ERROR MESSAGES
def validate_transaction_amount(amount: float) -> tuple[bool, str]:
    """
    Validate transaction amount (deposit/withdraw).
    - Must be between 0.01 and 999,999.99
    """
    try:
        amt = float(amount)
        if amt < 0.01:
            return False, f"Amount must be at least {PHP_SYMBOL}0.01"
        if amt > 999999.99:
            return False, f"Amount cannot exceed {PHP_SYMBOL}999,999.99"
        return True, ""
    except (ValueError, TypeError):
        return False, "Amount must be a valid number."
  
#CURRENCY FORMATTING
def format_currency(amount: float) -> str:
    """Format amount as Philippine Peso."""
    return f"{PHP_SYMBOL}{amount:,.2f}"
