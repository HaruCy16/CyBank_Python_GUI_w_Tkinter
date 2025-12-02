# backend/models/transaction.py

from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    account_id: str
    amount: float
    transaction_type: str  # "CREDIT" or "DEBIT"
    description: Optional[str] = None
    category: Optional[str] = None

    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    """
    Represents a financial transaction linked to a user's account.

    Model para sa financial transaction na naka-link sa user account.
    Para siyang query sa database pero using dataclass
    Dataclass - ginagamit to add special methods

    Records financial transactions (deposits, withdrawals, transfers)
    Amount is signed; positive for CREDIT, negative for DEBIT
    Used for transaction history and audit trails
    """
