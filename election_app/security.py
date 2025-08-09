# ----------------------------
# File: election_app/security.py
# ----------------------------
"""Security helpers for password hashing/verification."""
import hashlib

class SecurityManager:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(password: str, hash_value: str) -> bool:
        return SecurityManager.hash_password(password) == hash_value