import httpx
import asyncio
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()

class SMSActivateService:
    def __init__(self):
        self.api_url = settings.SMS_ACTIVATE_API_URL
        self.api_key = settings.SMS_ACTIVATE_API_KEY

    async def get_number(self, country: str, service: str) -> dict:
        params = {"api_key": self.api_key, "action": "getNumber", "service": service, "country": country}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.api_url, params=params, timeout=10.0)
                response_text = response.text
                if response_text.startswith("ACCESS_NUMBER"):
                    parts = response_text.split(":")
                    activation_id = parts[1]
                    phone = parts[2]
                    cost = await self.get_service_cost(country, service)
                    logger.info(f"Número obtido: {phone} (ID: {activation_id})")
                    return {"success": True, "activation_id": activation_id, "phone": phone, "cost": cost}
                else:
                    return {"success": False, "error": response_text}
            except httpx.HTTPError as e:
                logger.error(f"Erro ao obter número: {str(e)}")
                return {"success": False, "error": str(e)}

    async def get_status(self, activation_id: str) -> dict:
        params = {"api_key": self.api_key, "action": "getStatus", "id": activation_id}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url, params=params, timeout=10.0)
            response_text = response.text
            if response_text.startswith("STATUS_OK"):
                code = response_text.split(":")[1]
                return {"status": "completed", "code": code}
            elif response_text == "STATUS_WAIT_CODE":
                return {"status": "waiting", "code": None}
            elif response_text == "STATUS_CANCEL":
                return {"status": "cancelled", "code": None}
            else:
                return {"status": response_text.lower(), "code": None}

    async def set_status(self, activation_id: str, status: int) -> bool:
        params = {"api_key": self.api_key, "action": "setStatus", "id": activation_id, "status": status}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url, params=params, timeout=10.0)
            return response.text == "ACCESS_READY" or response.text == "ACCESS_CANCEL"

    async def get_service_cost(self, country: str, service: str) -> float:
        params = {"api_key": self.api_key, "action": "getPrices", "country": country, "service": service}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url, params=params, timeout=10.0)
            data = response.json()
            return float(data.get(country, {}).get(service, {}).get("cost", 0.5))

    async def poll_for_sms(self, activation_id: str, timeout: int = 600, interval: int = 10) -> dict:
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            result = await self.get_status(activation_id)
            if result["status"] == "completed":
                await self.set_status(activation_id, 1)
                return result
            elif result["status"] in ["cancelled", "timeout"]:
                return result
            await asyncio.sleep(interval)
        await self.set_status(activation_id, 6)
        return {"status": "timeout", "code": None}
