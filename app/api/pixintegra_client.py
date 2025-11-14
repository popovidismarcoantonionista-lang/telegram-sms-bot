import logging
import httpx
import uuid
from typing import Optional, Dict

from app.config import settings
from app.database import get_db, User, Order, OrderStatus
from app.utils.pricing import calculate_credits

logger = logging.getLogger(__name__)

class PixIntegraClient:
    def __init__(self):
        self.base_url = settings.PIXINTEGRA_BASE_URL
        self.api_token = settings.PIXINTEGRA_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    async def create_charge(
        self,
        amount: float,
        user_tg_id: str,
        plan: str
    ) -> Optional[Dict]:
        """Create a PIX charge via PixIntegra API"""

        db = next(get_db())

        try:
            # Get user
            user = db.query(User).filter(User.tg_id == user_tg_id).first()
            if not user:
                logger.error(f"User {user_tg_id} not found")
                return None

            # Calculate credits
            credits = calculate_credits(amount, plan)

            # Create idempotency key
            idempotency_key = str(uuid.uuid4())

            # Prepare request
            payload = {
                "value": amount,
                "description": f"Créditos SMS - Plano {plan.upper()}",
                "external_reference": idempotency_key,
                "payer": {
                    "name": user.username or f"User {user.tg_id}",
                    "tax_id": ""  # Optional
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/charges",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code != 201:
                    logger.error(f"PixIntegra API error: {response.status_code} - {response.text}")
                    return None

                data = response.json()

                # Create order in database
                order = Order(
                    user_id=user.id,
                    amount=amount,
                    plan_type=plan,
                    status=OrderStatus.PENDING,
                    pixintegra_charge_id=data.get("id"),
                    pix_qrcode=data.get("qr_code_image"),
                    pix_code=data.get("qr_code"),
                    credits_amount=credits,
                    idempotency_key=idempotency_key
                )

                db.add(order)
                db.commit()

                logger.info(f"PIX charge created: {data.get('id')} for user {user_tg_id}")

                return {
                    "charge_id": data.get("id"),
                    "pix_code": data.get("qr_code"),
                    "qr_code_image": data.get("qr_code_image"),
                    "credits": credits
                }

        except Exception as e:
            logger.error(f"Error creating PIX charge: {e}")
            return None

        finally:
            db.close()
