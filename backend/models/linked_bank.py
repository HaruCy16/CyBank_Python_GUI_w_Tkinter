from dataclasses import dataclass, field
import uuid
from datetime import datetime

@dataclass
class LinkedBankAccount:
    """Represents a bank account linked from an external bank."""
    user_id: str
    bank_name: str
    account_number: str
    account_type: str  # e.g., "checking", "savings", "money_market"
    balance: float = 0.0
    last_synced: datetime = field(default_factory=datetime.utcnow)
    linked_bank_id: str = field(default_factory=lambda: str(uuid.uuid4()))
