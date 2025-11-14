import hmac
import hashlib
import secrets
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings

def generate_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC SHA256 signature"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

def generate_idempotency_key() -> str:
    """Generate secure idempotency key"""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()
