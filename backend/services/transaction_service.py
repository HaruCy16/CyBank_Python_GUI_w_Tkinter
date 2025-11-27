# backend/services/transaction_service.py
from backend.models.transaction import Transaction
from backend.services.account_service import _accounts

# In-memory store
_account_transactions = {}  # account_id → list of Transaction

def deposit(account_id: str, amount: float, description: str = "", category: str = None) -> Transaction | None:
    acct = _accounts.get(account_id)
    if not acct:
        return None
    txn = Transaction(account_id=account_id, amount=amount, transaction_type="CREDIT",
                      description=description, category=category)
    _account_transactions.setdefault(account_id, []).append(txn)
    acct.balance += amount
    return txn

def withdraw(account_id: str, amount: float, description: str = "", category: str = None) -> Transaction | None:
    acct = _accounts.get(account_id)
    if not acct or acct.balance < amount:
        return None
    txn = Transaction(account_id=account_id, amount=-amount, transaction_type="DEBIT",
                      description=description, category=category)
    _account_transactions.setdefault(account_id, []).append(txn)
    acct.balance -= amount
    return txn

def get_transactions(account_id: str) -> list[Transaction]:
    return _account_transactions.get(account_id, [])
