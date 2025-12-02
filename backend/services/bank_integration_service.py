# backend/services/bank_integration_service.py
from backend.models.linked_bank import LinkedBankAccount
from datetime import datetime

# In-memory store
_linked_banks = {}  # linked_bank_id → LinkedBankAccount
_user_linked_banks = {}  # user_id → list of linked_bank_ids

def add_bank_account(user_id: str, bank_name: str, account_number: str, 
                     account_type: str, initial_balance: float = 0.0) -> LinkedBankAccount:
    """
    Link a new external bank account to the user.
    
    Args:
        user_id: User's unique identifier
        bank_name: Name of the bank (e.g., "Chase", "Bank of America")
        account_number: Account number at the external bank
        account_type: Type of account (e.g., "checking", "savings")
        initial_balance: Starting balance for this linked account
    
    Returns:
        LinkedBankAccount object
    """
    linked_bank = LinkedBankAccount(
        user_id=user_id,
        bank_name=bank_name,
        account_number=account_number,
        account_type=account_type,
        balance=initial_balance
    )
    _linked_banks[linked_bank.linked_bank_id] = linked_bank
    _user_linked_banks.setdefault(user_id, []).append(linked_bank.linked_bank_id)
    return linked_bank


def list_bank_accounts(user_id: str) -> list[LinkedBankAccount]:
    """
    Get all linked bank accounts for a user.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        List of LinkedBankAccount objects
    """
    bank_ids = _user_linked_banks.get(user_id, [])
    return [_linked_banks[bid] for bid in bank_ids]


def get_bank_account(linked_bank_id: str) -> LinkedBankAccount | None:
    """
    Retrieve a specific linked bank account by ID.
    
    Args:
        linked_bank_id: Linked bank account unique identifier
    
    Returns:
        LinkedBankAccount or None if not found
    """
    return _linked_banks.get(linked_bank_id)


def update_bank_balance(linked_bank_id: str, new_balance: float) -> bool:
    """
    Update the balance of a linked bank account (mock sync).
    
    Args:
        linked_bank_id: Linked bank account unique identifier
        new_balance: New balance to set
    
    Returns:
        True if successful, False if account not found
    """
    if linked_bank_id not in _linked_banks:
        return False
    bank_acct = _linked_banks[linked_bank_id]
    bank_acct.balance = new_balance
    bank_acct.last_synced = datetime.utcnow()
    return True


def remove_bank_account(linked_bank_id: str, user_id: str) -> bool:
    """
    Unlink a bank account from the user.
    
    Args:
        linked_bank_id: Linked bank account unique identifier
        user_id: User's unique identifier (for verification)
    
    Returns:
        True if successful, False if not found or user mismatch
    """
    if linked_bank_id not in _linked_banks:
        return False
    bank_acct = _linked_banks[linked_bank_id]
    if bank_acct.user_id != user_id:
        return False
    
    del _linked_banks[linked_bank_id]
    if user_id in _user_linked_banks:
        _user_linked_banks[user_id].remove(linked_bank_id)
    return True


def get_total_linked_balance(user_id: str) -> float:
    """
    Calculate total balance across all linked bank accounts for a user.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        Total balance across all linked accounts
    """
    accounts = list_bank_accounts(user_id)
    return sum(acct.balance for acct in accounts)
