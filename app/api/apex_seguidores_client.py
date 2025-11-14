import logging
import httpx
from typing import Optional, Dict

from app.config import settings

logger = logging.getLogger(__name__)

class ApexSeguidoresClient:
    def __init__(self):
        self.base_url = settings.APEX_BASE_URL
        self.api_key = settings.APEX_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_services(self) -> Optional[Dict]:
        """Get available services"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/services",
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()

                logger.error(f"Apex API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting Apex services: {e}")
            return None

    async def create_order(
        self,
        service_id: int,
        link: str,
        quantity: int
    ) -> Optional[Dict]:
        """
        Create a new order for followers/likes/views

        Args:
            service_id: Service ID from get_services()
            link: Target URL (profile, post, video)
            quantity: Number of followers/likes/views

        Returns:
            Dict with order_id and status
        """
        try:
            payload = {
                "service": service_id,
                "link": link,
                "quantity": quantity
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/order",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Apex order created: {data.get('order')}")
                    return {
                        "order_id": data.get("order"),
                        "status": "pending"
                    }

                logger.error(f"Apex API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating Apex order: {e}")
            return None

    async def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Check order status"""
        try:
            params = {"order": order_id}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/status",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()

                logger.error(f"Apex API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting Apex order status: {e}")
            return None

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            payload = {"order": order_id}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/cancel",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"Error cancelling Apex order: {e}")
            return False

    async def get_balance(self) -> Optional[float]:
        """Get account balance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/balance",
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return float(data.get("balance", 0))

                return None

        except Exception as e:
            logger.error(f"Error getting Apex balance: {e}")
            return None
