# backend/services/transfer_service.py
from backend.services.account_service import get_account, update_account_balance
from backend.services.transaction_service import record_transaction
from backend.services.bank_integration_service import get_bank_account, update_bank_balance
from datetime import datetime
import uuid

# In-memory store for transfers
_transfers = {}  # transfer_id → transfer details

def transfer_to_external_bank(user_id: str, from_account_id: str, to_linked_bank_id: str, 
                               amount: float, description: str = "Transfer to external bank") -> dict | None:
    """
    Transfer money from a CyBank account to a linked external bank account.
    Logic similar to PayPal to GCash: deduct from CyBank, credit external bank.
    
    Args:
        user_id: User's unique identifier
        from_account_id: Source CyBank account ID
        to_linked_bank_id: Destination linked bank account ID
        amount: Amount to transfer
        description: Optional description for the transfer
    
    Returns:
        Transfer record dict on success, None on failure
    """
    # Validate source account
    source_account = get_account(from_account_id)
    if not source_account or source_account.user_id != user_id:
        return None
    
    # Check sufficient balance
    if source_account.balance < amount:
        return None
    
    # Validate destination linked bank
    dest_bank = get_bank_account(to_linked_bank_id)
    if not dest_bank or dest_bank.user_id != user_id:
        return None
    
    # Perform transfer
    transfer_id = str(uuid.uuid4())
    
    # Deduct from CyBank account
    new_source_balance = source_account.balance - amount
    if not update_account_balance(from_account_id, new_source_balance):
        return None
    
    # Record debit transaction in source account
    debit_txn = record_transaction(from_account_id, amount, "DEBIT", 
                                   f"Transfer to {dest_bank.bank_name} ({dest_bank.account_number})")
    if not debit_txn:
        # Rollback
        update_account_balance(from_account_id, source_account.balance)
        return None
    
    # Credit linked bank account
    new_dest_balance = dest_bank.balance + amount
    if not update_bank_balance(to_linked_bank_id, new_dest_balance):
        # Rollback both
        update_account_balance(from_account_id, source_account.balance)
        return None
    
    # Record transfer metadata
    transfer_record = {
        "transfer_id": transfer_id,
        "user_id": user_id,
        "from_account_id": from_account_id,
        "from_account_name": source_account.account_name,
        "to_linked_bank_id": to_linked_bank_id,
        "to_bank_name": dest_bank.bank_name,
        "to_account_number": dest_bank.account_number,
        "amount": amount,
        "description": description,
        "timestamp": datetime.utcnow(),
        "status": "completed"
    }
    _transfers[transfer_id] = transfer_record
    
    return transfer_record


def transfer_between_cybank_accounts(user_id: str, from_account_id: str, to_account_id: str, 
                                      amount: float, description: str = "Transfer between accounts") -> dict | None:
    """
    Transfer money between two CyBank accounts (same user).
    
    Args:
        user_id: User's unique identifier
        from_account_id: Source CyBank account ID
        to_account_id: Destination CyBank account ID
        amount: Amount to transfer
        description: Optional description for the transfer
    
    Returns:
        Transfer record dict on success, None on failure
    """
    # Validate source account
    source_account = get_account(from_account_id)
    if not source_account or source_account.user_id != user_id:
        return None
    
    # Check sufficient balance
    if source_account.balance < amount:
        return None
    
    # Validate destination account
    dest_account = get_account(to_account_id)
    if not dest_account or dest_account.user_id != user_id:
        return None
    
    # Prevent self-transfer
    if from_account_id == to_account_id:
        return None
    
    # Perform transfer
    transfer_id = str(uuid.uuid4())
    
    # Deduct from source
    new_source_balance = source_account.balance - amount
    if not update_account_balance(from_account_id, new_source_balance):
        return None
    
    # Record debit in source
    debit_txn = record_transaction(from_account_id, amount, "DEBIT", 
                                   f"Transfer to {dest_account.account_name}")
    if not debit_txn:
        # Rollback
        update_account_balance(from_account_id, source_account.balance)
        return None
    
    # Add to destination
    new_dest_balance = dest_account.balance + amount
    if not update_account_balance(to_account_id, new_dest_balance):
        # Rollback both
        update_account_balance(from_account_id, source_account.balance)
        return None
    
    # Record credit in destination
    credit_txn = record_transaction(to_account_id, amount, "CREDIT", 
                                    f"Transfer from {source_account.account_name}")
    if not credit_txn:
        # Rollback all
        update_account_balance(from_account_id, source_account.balance)
        update_account_balance(to_account_id, dest_account.balance)
        return None
    
    # Record transfer metadata
    transfer_record = {
        "transfer_id": transfer_id,
        "user_id": user_id,
        "from_account_id": from_account_id,
        "from_account_name": source_account.account_name,
        "to_account_id": to_account_id,
        "to_account_name": dest_account.account_name,
        "amount": amount,
        "description": description,
        "timestamp": datetime.utcnow(),
        "status": "completed"
    }
    _transfers[transfer_id] = transfer_record
    
    return transfer_record


def get_transfer_history(user_id: str) -> list[dict]:
    """
    Get all transfers for a user.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        List of transfer records
    """
    return [t for t in _transfers.values() if t["user_id"] == user_id]


def get_transfer(transfer_id: str) -> dict | None:
    """
    Retrieve a specific transfer by ID.
    
    Args:
        transfer_id: Transfer unique identifier
    
    Returns:
        Transfer record or None if not found
    """
    return _transfers.get(transfer_id)
