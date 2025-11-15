from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Telegram (REQUIRED)
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str

    # Database (with SQLite fallback)
    DATABASE_URL: str = "sqlite:///./bot.db"
    SUPABASE_PROJECT_REF: Optional[str] = None

    # PixIntegra (OPTIONAL - only needed if using PIX payments)
    PIXINTEGRA_API_TOKEN: Optional[str] = None
    PIXINTEGRA_WEBHOOK_SECRET: Optional[str] = None
    PIXINTEGRA_BASE_URL: str = "https://api.pixintegra.com.br/v1"

    # SMS-Activate (OPTIONAL - only needed if selling SMS)
    SMSACTIVATE_API_KEY: Optional[str] = None
    SMSACTIVATE_BASE_URL: str = "https://api.sms-activate.org/stubs/handler_api.php"

    # Apex Seguidores (OPTIONAL - only needed if selling followers)
    APEX_API_KEY: Optional[str] = None
    APEX_BASE_URL: str = "https://apexseguidores.com/api/v2"

    # Security (with defaults for development)
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    WEBHOOK_HMAC_SECRET: str = "dev-hmac-secret-change-in-production"

    # Redis (OPTIONAL)
    REDIS_URL: Optional[str] = None

    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Pricing
    PLAN_ECONOMIC_MULTIPLIER: float = 1.7
    PLAN_STANDARD_MULTIPLIER: float = 2.2
    PLAN_PREMIUM_MULTIPLIER: float = 3.5
    MIN_PURCHASE_AMOUNT: float = 5.0

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
