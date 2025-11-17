"""
Aplicação FastAPI principal - ponto de entrada da API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .config import settings
from .database import init_db
from .routes import webhook
from .utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    logger.info("starting_application", environment=settings.ENVIRONMENT)
    await init_db()
    logger.info("database_initialized")

    # Iniciar bot Telegram (se necessário)
    # await telegram_bot.start()

    yield

    # Shutdown
    logger.info("shutting_down_application")


app = FastAPI(
    title="Telegram SMS Bot API",
    description="API para bot Telegram de venda de créditos SMS e seguidores",
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
app.include_router(webhook.router)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Telegram SMS Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
