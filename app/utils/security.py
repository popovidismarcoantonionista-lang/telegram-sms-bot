"""
Utilitários de segurança: criptografia, HMAC, JWT.
"""
import hmac
import hashlib
from cryptography.fernet import Fernet
from jose import jwt
from datetime import datetime, timedelta
from ..config import settings


class SecurityUtils:
    """Utilitários de segurança"""

    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt(self, data: str) -> str:
        """Criptografa dados sensíveis"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografa dados"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Verifica assinatura HMAC SHA256.
        Usado para validar webhooks do PixIntegra.
        """
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def verify_telegram_webhook(data: dict, secret: str) -> bool:
        """Verifica webhook do Telegram"""
        # Telegram usa X-Telegram-Bot-Api-Secret-Token header
        return True  # Implementar conforme necessidade

    @staticmethod
    def create_jwt_token(data: dict, expires_delta: timedelta = None) -> str:
        """Cria token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        """Verifica e decodifica token JWT"""
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


security_utils = SecurityUtils()
