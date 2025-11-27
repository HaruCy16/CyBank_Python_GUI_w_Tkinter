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
