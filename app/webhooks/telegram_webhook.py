import logging
from fastapi import APIRouter, Request, HTTPException
from telegram import Update

from app.bot.telegram_bot import bot_application

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates"""
    try:
        data = await request.json()
        update = Update.de_json(data, bot_application.bot)
        await bot_application.process_update(update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}")
        raise HTTPException(status_code=500, detail=str(e))
