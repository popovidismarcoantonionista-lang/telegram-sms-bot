import logging
import httpx
import asyncio
from typing import Optional, Dict

from app.config import settings

logger = logging.getLogger(__name__)

class SMSActivateClient:
    def __init__(self):
        self.base_url = settings.SMSACTIVATE_BASE_URL
        self.api_key = settings.SMSACTIVATE_API_KEY

    async def get_number(self, service: str, country: str = "0") -> Optional[Dict]:
        """
        Rent a number from SMS-Activate

        Args:
            service: Service code (e.g., 'wa' for WhatsApp, 'tg' for Telegram)
            country: Country code (0 for Russia by default)

        Returns:
            Dict with activation_id and phone_number
        """
        try:
            params = {
                "api_key": self.api_key,
                "action": "getNumber",
                "service": service,
                "country": country
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0
                )

                text = response.text.strip()

                if text.startswith("ACCESS_NUMBER"):
                    parts = text.split(":")
                    activation_id = parts[1]
                    phone_number = parts[2]

                    logger.info(f"Number rented: {phone_number} (ID: {activation_id})")

                    return {
                        "activation_id": activation_id,
                        "phone_number": phone_number
                    }
                else:
                    logger.error(f"SMS-Activate error: {text}")
                    return None

        except Exception as e:
            logger.error(f"Error getting SMS number: {e}")
            return None

    async def get_status(self, activation_id: str) -> Optional[str]:
        """
        Check the status of an activation

        Returns:
            SMS code if received, or status string
        """
        try:
            params = {
                "api_key": self.api_key,
                "action": "getStatus",
                "id": activation_id
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0
                )

                text = response.text.strip()

                if text.startswith("STATUS_OK"):
                    code = text.split(":")[1]
                    logger.info(f"SMS code received for {activation_id}: {code}")
                    return code

                return text

        except Exception as e:
            logger.error(f"Error getting SMS status: {e}")
            return None

    async def set_status(self, activation_id: str, status: int) -> bool:
        """
        Set activation status

        Args:
            activation_id: The activation ID
            status: 1 (ready to receive), 3 (request another SMS), 6 (complete), 8 (cancel)
        """
        try:
            params = {
                "api_key": self.api_key,
                "action": "setStatus",
                "id": activation_id,
                "status": status
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0
                )

                return "ACCESS_" in response.text

        except Exception as e:
            logger.error(f"Error setting SMS status: {e}")
            return False

    async def wait_for_sms(self, activation_id: str, max_wait: int = 600) -> Optional[str]:
        """
        Poll for SMS code with timeout

        Args:
            activation_id: The activation ID
            max_wait: Maximum wait time in seconds (default 10 minutes)

        Returns:
            SMS code if received, None if timeout
        """
        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            status = await self.get_status(activation_id)

            if status and status.startswith("STATUS_OK"):
                return status.split(":")[1]
            elif status == "STATUS_CANCEL":
                logger.warning(f"Activation {activation_id} was cancelled")
                return None

            await asyncio.sleep(5)  # Check every 5 seconds

        logger.warning(f"Timeout waiting for SMS on activation {activation_id}")
        await self.set_status(activation_id, 8)  # Cancel
        return None

    async def get_prices(self, service: str, country: str = "0") -> Optional[Dict]:
        """Get prices for a service in a country"""
        try:
            params = {
                "api_key": self.api_key,
                "action": "getPrices",
                "service": service,
                "country": country
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0
                )

                return response.json()

        except Exception as e:
            logger.error(f"Error getting SMS prices: {e}")
            return None
