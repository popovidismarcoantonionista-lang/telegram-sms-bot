"""
Cliente para integração com a API PixIntegra.
Documentação: https://pixintegra-api.readme.io/reference/documenta%C3%A7%C3%A3o-da-api-pixintegra
"""
import httpx
from typing import Dict, Optional
from decimal import Decimal
import uuid
from ..config import settings
from ..utils.logger import logger


class PixIntegraClient:
    """Cliente da API PixIntegra"""

    def __init__(self):
        self.base_url = settings.PIXINTEGRA_BASE_URL
        self.api_token = settings.PIXINTEGRA_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    async def create_charge(
        self,
        amount: Decimal,
        customer_name: str,
        customer_tax_id: Optional[str] = None,
        description: str = "Compra de créditos",
        external_reference: Optional[str] = None
    ) -> Dict:
        """
        Cria uma cobrança PIX.

        Retorna:
        {
            "charge_id": "...",
            "qr_code": "...",
            "qr_code_image": "...",
            "pix_key": "...",
            "expires_at": "..."
        }
        """
        if external_reference is None:
            external_reference = str(uuid.uuid4())

        payload = {
            "amount": float(amount),
            "customer": {
                "name": customer_name,
                "tax_id": customer_tax_id
            },
            "description": description,
            "external_reference": external_reference,
            "callback_url": f"{settings.TELEGRAM_WEBHOOK_URL.replace('/telegram/webhook', '')}/pixintegra/webhook"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/charges",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                logger.info(
                    "pixintegra_charge_created",
                    charge_id=data.get("id"),
                    amount=amount,
                    reference=external_reference
                )

                return {
                    "success": True,
                    "charge_id": data.get("id"),
                    "qr_code": data.get("qr_code"),
                    "qr_code_image": data.get("qr_code_image_url"),
                    "pix_key": data.get("pix_key"),
                    "expires_at": data.get("expires_at"),
                    "raw_response": data
                }

            except httpx.HTTPStatusError as e:
                logger.error(
                    "pixintegra_charge_failed",
                    error=str(e),
                    status_code=e.response.status_code,
                    response=e.response.text
                )
                return {
                    "success": False,
                    "error": f"HTTP {e.response.status_code}: {e.response.text}"
                }
            except Exception as e:
                logger.error("pixintegra_request_failed", error=str(e))
                return {
                    "success": False,
                    "error": str(e)
                }

    async def get_charge_status(self, charge_id: str) -> Dict:
        """Consulta status de uma cobrança"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/charges/{charge_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "success": True,
                    "status": data.get("status"),
                    "paid_at": data.get("paid_at"),
                    "data": data
                }
            except Exception as e:
                logger.error("pixintegra_status_check_failed", error=str(e))
                return {
                    "success": False,
                    "error": str(e)
                }

    async def cancel_charge(self, charge_id: str) -> Dict:
        """Cancela uma cobrança pendente"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/charges/{charge_id}/cancel",
                    headers=self.headers
                )
                response.raise_for_status()
                return {"success": True}
            except Exception as e:
                logger.error("pixintegra_cancel_failed", error=str(e))
                return {
                    "success": False,
                    "error": str(e)
                }


pixintegra_client = PixIntegraClient()
