# backend/services/user_service.py
from backend.models.user import User
from utils.auth import hash_password, verify_password

# In-memory store (for now)
_users = {}  # user_id → User

def register_user(username: str, password: str, full_name: str, email: str = None) -> User | None:
    # ensure unique username
    for u in _users.values():
        if u.username == username:
            return None
    pwd_hash = hash_password(password)
    user = User(username=username, password_hash=pwd_hash, full_name=full_name, email=email)
    _users[user.user_id] = user
    return user

def authenticate_user(username: str, password: str) -> User | None:
    for u in _users.values():
        if u.username == username and verify_password(password, u.password_hash):
            return u
    return None
