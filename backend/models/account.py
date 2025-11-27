# backend/models/account.py

from dataclasses import dataclass, field
import uuid
from datetime import datetime

@dataclass
class Account:
    user_id: str
    account_name: str
    balance: float = 0.0
    status: str = "ACTIVE"

    account_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
