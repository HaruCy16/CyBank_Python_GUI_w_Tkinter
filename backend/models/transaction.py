# backend/models/transaction.py

from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    account_id: str #string ang input ng user or ung data type na tintanggap
    amount: float #float na para sa amount ng transaction
    transaction_type: str  # "CREDIT" or "DEBIT"
    description: Optional[str] = None #string na para sa description ng transaction optional lang
    category: Optional[str] = None #string na para sa category ng transaction optional lang 

    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4())) #string na unique identifier para sa transaction
    timestamp: datetime = field(default_factory=datetime.utcnow)

    """
    Represents a financial transaction linked to a user's account.

    Model para sa financial transaction na naka-link sa user account.
    Para siyang query sa database pero using dataclass
    Dataclass - ginagamit to add special methods

    Records financial transactions (deposits, withdrawals, transfers)
    Amount is signed; positive for CREDIT, negative for DEBIT
    Used for transaction history and audit trails

    KEY LOGIC:
    - transaction_type determines if amount is positive (CREDIT) or negative (DEBIT)
    - description and category are optional metadata fields
    - transaction_id is a unique identifier for each transaction
    """
