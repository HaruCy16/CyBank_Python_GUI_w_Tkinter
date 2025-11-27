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
