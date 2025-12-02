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

    """
    Represents a user's bank account within the CyBank system.

    Represents a CyBank user account with authentication credentials
    Stores hashed password (never plain text) using utils/auth.py
    Email is optional; validation skipped if empty
    """