# backend/services/account_service.py
from backend.models.account import Account

# In-memory store
_accounts = {}  # account_id → Account
_user_accounts = {}  # user_id → list of account_ids

def create_account(user_id: str, account_name: str) -> Account:
    acct = Account(user_id=user_id, account_name=account_name)
    _accounts[acct.account_id] = acct
    _user_accounts.setdefault(user_id, []).append(acct.account_id)
    return acct

def list_accounts(user_id: str) -> list[Account]:
    ids = _user_accounts.get(user_id, [])
    return [ _accounts[a] for a in ids ]

def get_account(account_id: str) -> Account | None:
    """
    Retrieve a specific account by ID.
    
    Args:
        account_id: Account unique identifier
    
    Returns:
        Account or None if not found
    """
    return _accounts.get(account_id)

def update_account_balance(account_id: str, new_balance: float) -> bool:
    """
    Update the balance of an account.
    
    Args:
        account_id: Account unique identifier
        new_balance: New balance to set
    
    Returns:
        True if successful, False if account not found
    """
    if account_id not in _accounts:
        return False
    _accounts[account_id].balance = new_balance
    return True