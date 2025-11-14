import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from app.config import settings
from app.bot import handlers

logger = logging.getLogger(__name__)

# Global bot instance
bot_application: Application = None

async def setup_bot():
    """Initialize the Telegram bot"""
    global bot_application

    bot_application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Command handlers
    bot_application.add_handler(CommandHandler("start", handlers.start_command))
    bot_application.add_handler(CommandHandler("saldo", handlers.balance_command))
    bot_application.add_handler(CommandHandler("comprar_creditos", handlers.buy_credits_command))
    bot_application.add_handler(CommandHandler("comprar_sms", handlers.buy_sms_command))
    bot_application.add_handler(CommandHandler("comprar_seguidores", handlers.buy_followers_command))
    bot_application.add_handler(CommandHandler("ajuda", handlers.help_command))

    # Callback query handler
    bot_application.add_handler(CallbackQueryHandler(handlers.button_callback))

    # Message handlers
    bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.message_handler))

    # Set webhook
    await bot_application.bot.set_webhook(
        url=settings.TELEGRAM_WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )

    logger.info(f"Webhook set to: {settings.TELEGRAM_WEBHOOK_URL}")

async def shutdown_bot():
    """Shutdown the bot gracefully"""
    global bot_application
    if bot_application:
        await bot_application.bot.delete_webhook()
        await bot_application.shutdown()

def get_bot() -> Bot:
    """Get bot instance"""
    return bot_application.bot if bot_application else None
