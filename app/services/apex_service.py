import httpx
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()

class ApexService:
    def __init__(self):
        self.api_url = settings.APEX_API_URL
        self.api_key = settings.APEX_API_KEY
        self.create_order_path = settings.APEX_CREATE_ORDER_PATH

    async def create_order(self, platform: str, quantity: int, profile_url: str, user_id: str) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"platform": platform, "quantity": quantity, "url": profile_url, "user_id": user_id, "callback_url": f"{settings.TELEGRAM_WEBHOOK_URL.replace('/telegram', '/apex')}"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.api_url}{self.create_order_path}", headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Pedido Apex criado: {data.get('order_id')} - {quantity} seguidores para {platform}")
                return {"success": True, "order_id": data.get("order_id"), "status": data.get("status"), "estimated_completion": data.get("estimated_completion"), "price": data.get("price", 0)}
            except httpx.HTTPError as e:
                logger.error(f"Erro ao criar pedido Apex: {str(e)}")
                return {"success": False, "error": str(e)}

    async def check_order_status(self, order_id: str) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_url}{self.create_order_path}/{order_id}", headers=headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Erro ao verificar status Apex: {str(e)}")
                return {"success": False, "error": str(e)}
