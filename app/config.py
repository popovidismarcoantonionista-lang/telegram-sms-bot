from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str
    PLUGGY_CLIENT_ID: str
    PLUGGY_CLIENT_SECRET: str
    PLUGGY_WEBHOOK_SECRET: str
    PLUGGY_API_URL: str = "https://api.pluggy.ai"
    SMS_ACTIVATE_API_KEY: str
    SMS_ACTIVATE_API_URL: str = "https://api.sms-activate.org/stubs/handler_api.php"
    APEX_API_KEY: str
    APEX_API_URL: str
    APEX_CREATE_ORDER_PATH: str = "/v1/orders"
    JWT_SECRET_KEY: str
    ENCRYPTION_KEY: str
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    ENVIRONMENT: str = "production"
    MIN_PURCHASE_BRL: float = 5.00
    REDIS_URL: str = "redis://localhost:6379/0"
    ECONOMIC_MULTIPLIER: float = 1.7
    STANDARD_MULTIPLIER: float = 2.2
    PREMIUM_MULTIPLIER: float = 3.5
    DISCOUNT_5_20: float = 0.05
    DISCOUNT_21_100: float = 0.12
    DISCOUNT_100_PLUS: float = 0.20

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
