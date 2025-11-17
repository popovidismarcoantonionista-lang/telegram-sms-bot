"""
Endpoint webhook para receber confirmações de pagamento do PixIntegra.
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
import json

from ..database import get_db
from ..models import Order, User, OrderStatus
from ..utils.security import security_utils
from ..utils.idempotency import idempotency_manager
from ..utils.logger import logger, log_to_db
from ..config import settings

router = APIRouter(prefix="/pixintegra", tags=["webhooks"])


@router.post("/webhook")
async def pixintegra_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook para receber confirmações de pagamento do PixIntegra.

    Fluxo:
    1. Valida assinatura HMAC
    2. Verifica idempotência
    3. Atualiza pedido
    4. Credita saldo do usuário
    5. Envia notificação via Telegram
    """
    # Obter payload
    body = await request.body()
    payload = await request.json()

    # Validar assinatura HMAC
    signature = request.headers.get("X-Signature") or request.headers.get("Signature")
    if signature:
        if not security_utils.verify_hmac_signature(
            body,
            signature,
            settings.PIXINTEGRA_WEBHOOK_SECRET
        ):
            logger.warning("pixintegra_webhook_invalid_signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Extrair dados do webhook
    charge_id = payload.get("charge_id") or payload.get("id")
    status = payload.get("status")
    paid_amount = payload.get("paid_amount") or payload.get("amount")

    if not charge_id:
        raise HTTPException(status_code=400, detail="Missing charge_id")

    logger.info(
        "pixintegra_webhook_received",
        charge_id=charge_id,
        status=status,
        amount=paid_amount
    )

    # Verificar idempotência
    idempotency_key = f"pixintegra_payment_{charge_id}"

    # Tentar obter resultado já processado
    existing_result = await idempotency_manager.get_result(idempotency_key)
    if existing_result:
        logger.info("pixintegra_webhook_already_processed", charge_id=charge_id)
        return existing_result

    # Criar lock de idempotência
    can_process = await idempotency_manager.check_and_lock(idempotency_key, ttl_seconds=300)
    if not can_process:
        logger.warning("pixintegra_webhook_concurrent_processing", charge_id=charge_id)
        raise HTTPException(status_code=409, detail="Already processing")

    try:
        # Buscar pedido no banco
        result = await db.execute(
            select(Order).where(Order.pixintegra_charge_id == charge_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            logger.error("pixintegra_webhook_order_not_found", charge_id=charge_id)
            await idempotency_manager.release_lock(idempotency_key)
            raise HTTPException(status_code=404, detail="Order not found")

        # Verificar se já foi pago
        if order.status == OrderStatus.PAID:
            logger.info("pixintegra_webhook_already_paid", order_id=order.id)
            result_data = {"message": "Already paid", "order_id": order.id}
            await idempotency_manager.mark_completed(idempotency_key, result_data)
            return result_data

        # Processar pagamento confirmado
        if status in ["paid", "completed", "approved"]:
            # Atualizar pedido
            order.status = OrderStatus.PAID
            order.pixintegra_response = json.dumps(payload)

            # Buscar usuário
            result_user = await db.execute(
                select(User).where(User.id == order.user_id)
            )
            user = result_user.scalar_one()

            # Creditar saldo (1 BRL = 1 crédito)
            credits_to_add = Decimal(str(paid_amount))
            user.balance += credits_to_add

            await db.commit()

            logger.info(
                "payment_processed",
                order_id=order.id,
                user_id=user.id,
                amount=paid_amount,
                new_balance=float(user.balance)
            )

            await log_to_db(
                db,
                source="pixintegra",
                level="info",
                message=f"Pagamento confirmado: R$ {paid_amount}",
                payload=payload,
                user_id=user.id
            )

            # Enviar notificação via Telegram (implementar)
            # await send_telegram_notification(user.tg_id, credits_to_add)

            result_data = {
                "message": "Payment processed",
                "order_id": order.id,
                "credits_added": float(credits_to_add),
                "new_balance": float(user.balance)
            }

            await idempotency_manager.mark_completed(idempotency_key, result_data)
            return result_data

        else:
            # Outros status (expired, cancelled, etc)
            if status in ["expired", "cancelled"]:
                order.status = OrderStatus.EXPIRED if status == "expired" else OrderStatus.CANCELLED
                await db.commit()

            result_data = {"message": f"Status updated to {status}", "order_id": order.id}
            await idempotency_manager.mark_completed(idempotency_key, result_data)
            return result_data

    except Exception as e:
        logger.error("pixintegra_webhook_processing_error", error=str(e), charge_id=charge_id)
        await idempotency_manager.release_lock(idempotency_key)
        raise HTTPException(status_code=500, detail="Processing error")
