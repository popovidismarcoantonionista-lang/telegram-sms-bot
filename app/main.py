import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.webhooks.telegram_webhook import router as telegram_router
from app.webhooks.pixintegra_webhook import router as pixintegra_router
from app.bot.telegram_bot import setup_bot, shutdown_bot

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Telegram SMS Bot...")
    Base.metadata.create_all(bind=engine)
    await setup_bot()
    logger.info("Bot started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down bot...")
    await shutdown_bot()

app = FastAPI(
    title="Telegram SMS Bot",
    description="Bot de venda de créditos SMS e seguidores com pagamento PIX automático",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(telegram_router, prefix="/webhook", tags=["telegram"])
app.include_router(pixintegra_router, prefix="/webhook", tags=["pixintegra"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Telegram SMS Bot",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
