# utils/auth.py
import hashlib
import os

def hash_password(raw_password: str) -> str:
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((salt + raw_password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(raw_password: str, stored_hash: str) -> bool:
    salt, pwd = stored_hash.split('$', 1)
    return hashlib.sha256((salt + raw_password).encode()).hexdigest() == pwd