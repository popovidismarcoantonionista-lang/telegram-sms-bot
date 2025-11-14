import logging
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, User, Order, OrderStatus, Log
from app.bot.telegram_bot import get_bot

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify PixIntegra webhook HMAC signature"""
    expected_sig = hmac.new(
        settings.WEBHOOK_HMAC_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature)

@router.post("/pixintegra")
async def pixintegra_webhook(
    request: Request,
    x_signature: str = Header(None, alias="X-Signature")
):
    """Handle PixIntegra payment confirmation webhook"""

    # Get raw body for signature verification
    body = await request.body()

    # Verify signature
    if x_signature and not verify_webhook_signature(body, x_signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Log webhook
    db: Session = next(get_db())
    log_entry = Log(
        source="pixintegra_webhook",
        payload=str(data),
        level="INFO",
        message="Webhook received"
    )
    db.add(log_entry)
    db.commit()

    # Extract data
    event_type = data.get("event")
    charge_id = data.get("charge_id")
    status = data.get("status")

    if event_type != "charge.paid" or status != "paid":
        logger.info(f"Ignoring webhook event: {event_type} / {status}")
        db.close()
        return {"ok": True}

    # Find order
    order = db.query(Order).filter(Order.pixintegra_charge_id == charge_id).first()

    if not order:
        logger.warning(f"Order not found for charge_id: {charge_id}")
        db.close()
        raise HTTPException(status_code=404, detail="Order not found")

    # Check idempotency
    if order.status == OrderStatus.PAID:
        logger.info(f"Order {order.id} already paid (idempotent)")
        db.close()
        return {"ok": True}

    # Update order
    order.status = OrderStatus.PAID
    order.paid_at = datetime.utcnow()

    # Credit user balance
    user = db.query(User).filter(User.id == order.user_id).first()
    if not user:
        logger.error(f"User {order.user_id} not found")
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    credits = order.credits_amount
    user.balance += credits

    db.commit()
    db.refresh(user)

    # Send notification to user
    bot = get_bot()
    if bot:
        try:
            await bot.send_message(
                chat_id=user.tg_id,
                text=f"✅ *Pagamento Confirmado!*\n\n"
                     f"Valor: R$ {order.amount:.2f}\n"
                     f"Créditos adicionados: R$ {credits:.2f}\n"
                     f"Saldo atual: R$ {user.balance:.2f}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    logger.info(f"Order {order.id} paid successfully. User {user.tg_id} credited with {credits}")

    db.close()
    return {"ok": True}

from datetime import datetime
