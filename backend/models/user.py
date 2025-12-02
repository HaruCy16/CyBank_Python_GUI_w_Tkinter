# backend/models/user.py

from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Optional

@dataclass
class User:
    username: str
    password_hash: str
    full_name: str
    email: Optional[str] = None

    # Fields with default values come after required fields
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)