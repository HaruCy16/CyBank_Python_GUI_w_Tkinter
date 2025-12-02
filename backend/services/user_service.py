from backend.models.user import User
from utils.auth import hash_password, verify_password

_users = {}

def register_user(username: str, password: str, full_name: str, email: str = None):
    for u in _users.values():
        if u.username == username:
            return None

    pwd_hash = hash_password(password)
    user = User(username=username, password_hash=pwd_hash, full_name=full_name, email=email)
    _users[user.user_id] = user
    return user

def authenticate_user(username: str, password: str):
    for u in _users.values():
        if u.username == username and verify_password(password, u.password_hash):
            return u
    return None