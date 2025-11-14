from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import get_db, init_db, User, Order
from app.bot import application, start_bot, stop_bot
from app.services.security import verify_pluggy_signature
from app.services.pluggy_service import PluggyService
from app.utils.logger import logger, log_to_db

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação...")
    init_db()
    await start_bot()
    yield
    await stop_bot()
    logger.info("Aplicação encerrada")

app = FastAPI(title="Telegram SMS Bot", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Bot Telegram SMS & Seguidores - API v1.0", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    try:
        update_data = await request.json()
        from telegram import Update
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erro no webhook Telegram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/pluggy")
async def pluggy_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        signature = request.headers.get("X-Pluggy-Signature", "")
        if not verify_pluggy_signature(body.decode(), signature):
            log_to_db(db, "pluggy_webhook", "warning", "Assinatura HMAC inválida")
            raise HTTPException(status_code=403, detail="Invalid signature")

        data = await request.json()
        event_type = data.get("event")
        payment_data = data.get("data", {})

        if event_type == "payment.status.updated":
            charge_id = payment_data.get("id")
            status = payment_data.get("status")

            order = db.query(Order).filter(Order.pluggy_charge_id == charge_id).first()
            if not order:
                log_to_db(db, "pluggy_webhook", "warning", f"Ordem não encontrada: {charge_id}")
                return {"status": "order_not_found"}

            if order.status == "paid":
                log_to_db(db, "pluggy_webhook", "info", f"Pagamento já processado: {charge_id}")
                return {"status": "already_processed"}

            if status == "COMPLETED":
                order.status = "paid"
                order.paid_at = datetime.utcnow()
                order.pluggy_payment_id = payment_data.get("paymentId")

                user = db.query(User).filter(User.id == order.user_id).first()
                user.balance += order.credits

                db.commit()

                log_to_db(db, "pluggy_webhook", "info", f"Pagamento confirmado: {charge_id}, Créditos: {order.credits}")

                from telegram import Bot
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                message = f"✅ *Pagamento Confirmado!*\n\n💰 *Valor:* R$ {order.amount:.2f}\n💎 *Créditos:* {order.credits:.2f}\n📦 *Pacote:* {order.package_type.title()}\n\n🎉 Seu saldo foi atualizado!\n*Saldo atual:* R$ {user.balance:.2f}\n\nUse /comprar_sms para adquirir números SMS!"
                await bot.send_message(chat_id=user.tg_id, text=message, parse_mode="Markdown")

                return {"status": "processed", "credits_added": order.credits}

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erro no webhook Pluggy: {str(e)}")
        log_to_db(db, "pluggy_webhook", "error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/apex")
async def apex_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        log_to_db(db, "apex_webhook", "info", "Webhook Apex recebido", str(data))
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erro no webhook Apex: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
