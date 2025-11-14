import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import httpx
from app.config import settings
from app.database import SessionLocal
from sqlalchemy import text

logger = logging.getLogger(__name__)

class PixPollingService:
    """
    Serviço que verifica automaticamente o status de pagamentos PIX pendentes.
    Consulta a API da PixIntegra a cada X segundos até confirmar o pagamento.
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.active_payments: Dict[str, dict] = {}  # {transaction_id: {data}}
        self.polling_interval = 10  # Verifica a cada 10 segundos
        self.max_attempts = 360  # 360 * 10s = 1 hora máximo

    async def check_payment_status(self, transaction_id: str) -> Optional[dict]:
        """
        Consulta o status de um pagamento na API da PixIntegra

        Args:
            transaction_id: ID da transação gerado pela PixIntegra

        Returns:
            Dict com status do pagamento ou None se erro
        """
        try:
            url = f"{settings.PIXINTEGRA_BASE_URL}/consultar_pagamento"

            payload = {
                "api_token": settings.PIXINTEGRA_API_TOKEN,
                "api_key": settings.PIXINTEGRA_API_KEY,
                "identificador": transaction_id
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Status pagamento {transaction_id}: {data}")

            return data

        except Exception as e:
            logger.error(f"Erro ao verificar pagamento {transaction_id}: {e}")
            return None

    async def start_polling(
        self, 
        transaction_id: str, 
        user_id: int, 
        amount: float,
        product_type: str,
        product_data: dict
    ):
        """
        Inicia o polling para uma transação específica

        Args:
            transaction_id: ID da transação PixIntegra
            user_id: ID do usuário no bot
            amount: Valor da transação
            product_type: Tipo de produto (sms, follower, etc)
            product_data: Dados do produto comprado
        """

        payment_info = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "product_type": product_type,
            "product_data": product_data,
            "created_at": datetime.utcnow(),
            "attempts": 0
        }

        self.active_payments[transaction_id] = payment_info

        # Inicia task assíncrona de verificação
        asyncio.create_task(self._poll_payment(transaction_id))

        logger.info(f"Polling iniciado para transação {transaction_id}")

    async def _poll_payment(self, transaction_id: str):
        """
        Loop de verificação do pagamento
        """
        payment_info = self.active_payments.get(transaction_id)
        if not payment_info:
            return

        while payment_info["attempts"] < self.max_attempts:
            payment_info["attempts"] += 1

            # Aguarda intervalo entre verificações
            await asyncio.sleep(self.polling_interval)

            # Verifica status
            status_data = await self.check_payment_status(transaction_id)

            if not status_data:
                continue

            # Verifica se pagamento foi confirmado
            if status_data.get("status") == "pago" or status_data.get("pago") == True:
                logger.info(f"✅ Pagamento CONFIRMADO: {transaction_id}")
                await self._process_confirmed_payment(payment_info)
                del self.active_payments[transaction_id]
                return

            # Verifica se expirou ou foi cancelado
            if status_data.get("status") in ["expirado", "cancelado"]:
                logger.info(f"❌ Pagamento EXPIRADO/CANCELADO: {transaction_id}")
                await self._process_expired_payment(payment_info)
                del self.active_payments[transaction_id]
                return

        # Timeout atingido
        logger.warning(f"⏰ Timeout atingido para pagamento {transaction_id}")
        await self._process_timeout_payment(payment_info)
        del self.active_payments[transaction_id]

    async def _process_confirmed_payment(self, payment_info: dict):
        """
        Processa pagamento confirmado - libera créditos/produtos
        """
        try:
            from app.bot.telegram_bot import send_message_to_user

            user_id = payment_info["user_id"]
            product_type = payment_info["product_type"]
            product_data = payment_info["product_data"]

            # Atualiza saldo no banco de dados
            db = SessionLocal()
            try:
                if product_type == "sms":
                    # Adiciona créditos SMS
                    quantity = product_data.get("quantity", 0)
                    db.execute(
                        text("UPDATE users SET sms_credits = sms_credits + :qty WHERE telegram_id = :uid"),
                        {"qty": quantity, "uid": user_id}
                    )

                elif product_type == "follower":
                    # Processa pedido de seguidores
                    # Aqui você chamaria a API da Apex Seguidores
                    pass

                db.commit()
                logger.info(f"✅ Créditos liberados para usuário {user_id}")

                # Envia mensagem de confirmação
                await send_message_to_user(
                    user_id, 
                    f"✅ *Pagamento Confirmado!*\n\n"
                    f"Seu pedido foi processado com sucesso!\n"
                    f"Produto: {product_type}\n"
                    f"Quantidade: {product_data.get('quantity', 'N/A')}"
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Erro ao processar pagamento confirmado: {e}")

    async def _process_expired_payment(self, payment_info: dict):
        """
        Processa pagamento expirado
        """
        try:
            from app.bot.telegram_bot import send_message_to_user

            await send_message_to_user(
                payment_info["user_id"],
                "❌ *Pagamento Expirado*\n\n"
                "O tempo para pagamento expirou. "
                "Se você ainda deseja comprar, por favor gere um novo PIX."
            )
        except Exception as e:
            logger.error(f"Erro ao processar pagamento expirado: {e}")

    async def _process_timeout_payment(self, payment_info: dict):
        """
        Processa timeout de verificação (1 hora sem confirmação)
        """
        logger.info(f"Timeout para pagamento {payment_info['transaction_id']}")
        # Similar ao expirado

# Instância global do serviço
pix_polling_service = PixPollingService()
