"""
Configuração centralizada da aplicação usando Pydantic Settings.
Carrega variáveis de ambiente e valida configurações.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from decimal import Decimal


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str
    TELEGRAM_WEBHOOK_SECRET: str

    # PixIntegra
    PIXINTEGRA_API_TOKEN: str
    PIXINTEGRA_BASE_URL: str = "https://api.pixintegra.com.br/v1"
    PIXINTEGRA_WEBHOOK_SECRET: str

    # SMS-Activate
    SMS_ACTIVATE_API_KEY: str
    SMS_ACTIVATE_BASE_URL: str = "https://api.sms-activate.org/stubs/handler_api.php"

    # Apex Seguidores
    APEX_API_KEY: str
    APEX_BASE_URL: str
    APEX_AUTH_METHOD: str = "Bearer"

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ENCRYPTION_KEY: str

    # Pricing
    MARGIN_ECONOMICO: Decimal = Decimal("1.7")
    MARGIN_PADRAO: Decimal = Decimal("2.2")
    MARGIN_PREMIUM: Decimal = Decimal("3.5")
    MIN_PURCHASE_BRL: Decimal = Decimal("5.00")

    # Rate Limiting
    RATE_LIMIT_PER_USER: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
