from dataclasses import dataclass, field
import uuid
from datetime import datetime

@dataclass
class LinkedBankAccount:
    """Represents a bank account linked from an external bank."""
    user_id: str #string ang input ng user or ung data type na tintanggap
    bank_name: str #string na para sa bank names
    account_number: int # assuming account numbers are numeric
    account_type: str  # e.g., "checking", "savings", "money_market"
    balance: float = 0.0
    last_synced: datetime = field(default_factory=datetime.utcnow)
    linked_bank_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    """
    Represents a bank account linked from an external bank.

    Model para sa external banked account na naka-link sa CyBank user.
    Para siyang query sa database pero using dataclass
    Dataclass - ginagamit to add special methods

    Check niyo na lang to for more infor
    https://docs.python.org/3/library/dataclasses.html

    KEY LOGIC:
    - linked_bank_id is a unique identifier for each linked bank account
    - last_synced tracks the last time the account data was synchronized
    - balance reflects the current balance of the linked bank account
    """