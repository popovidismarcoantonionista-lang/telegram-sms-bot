import hmac
import hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

def verify_pluggy_signature(payload: str, signature: str) -> bool:
    expected = hmac.new(settings.PLUGGY_WEBHOOK_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)

def create_jwt_token(data: dict, expires_delta: timedelta = timedelta(hours=24)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return None
