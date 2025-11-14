import httpx
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()

class PluggyService:
    def __init__(self):
        self.base_url = settings.PLUGGY_API_URL
        self.client_id = settings.PLUGGY_CLIENT_ID
        self.client_secret = settings.PLUGGY_CLIENT_SECRET
        self.access_token = None

    async def get_access_token(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/auth", json={"clientId": self.client_id, "clientSecret": self.client_secret})
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("accessToken")
            return self.access_token

    async def create_pix_charge(self, amount: float, order_id: str, description: str) -> dict:
        if not self.access_token:
            await self.get_access_token()
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        payload = {"amount": amount, "currency": "BRL", "paymentMethod": "PIX", "description": description, "externalId": order_id, "callbackUrl": f"{settings.TELEGRAM_WEBHOOK_URL.replace('/telegram', '/pluggy')}"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/payment-initiations", headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Cobrança PIX criada: {data.get('id')} para R$ {amount}")
                return {"charge_id": data.get("id"), "qr_code": data.get("qrCode"), "qr_code_text": data.get("qrCodeText"), "expires_at": data.get("expiresAt"), "status": data.get("status")}
            except httpx.HTTPError as e:
                logger.error(f"Erro ao criar cobrança PIX: {str(e)}")
                raise

    async def check_payment_status(self, charge_id: str) -> dict:
        if not self.access_token:
            await self.get_access_token()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/payment-initiations/{charge_id}", headers=headers)
            response.raise_for_status()
            return response.json()
