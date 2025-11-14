from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str

    # Database
    DATABASE_URL: str
    SUPABASE_PROJECT_REF: str = "lnmndaxsjhmfldzuiwqk"

    # PixIntegra
    PIXINTEGRA_API_TOKEN: str
    PIXINTEGRA_WEBHOOK_SECRET: str
    PIXINTEGRA_BASE_URL: str = "https://api.pixintegra.com.br/v1"

    # SMS-Activate
    SMSACTIVATE_API_KEY: str
    SMSACTIVATE_BASE_URL: str = "https://api.sms-activate.org/stubs/handler_api.php"

    # Apex Seguidores
    APEX_API_KEY: str
    APEX_BASE_URL: str = "https://apexseguidores.com/api/v2"

    # Security
    JWT_SECRET_KEY: str
    WEBHOOK_HMAC_SECRET: str

    # Redis
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
