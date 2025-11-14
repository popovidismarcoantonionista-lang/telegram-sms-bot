from app.config import get_settings

settings = get_settings()

class PricingService:
    @staticmethod
    def calculate_price(base_cost: float, package_type: str, quantity: int = 1) -> dict:
        multipliers = {
            "economic": settings.ECONOMIC_MULTIPLIER,
            "standard": settings.STANDARD_MULTIPLIER,
            "premium": settings.PREMIUM_MULTIPLIER
        }
        multiplier = multipliers.get(package_type, settings.STANDARD_MULTIPLIER)
        price = base_cost * multiplier
        discount = 0.0
        if 5 <= quantity <= 20:
            discount = settings.DISCOUNT_5_20
        elif 21 <= quantity <= 100:
            discount = settings.DISCOUNT_21_100
        elif quantity > 100:
            discount = settings.DISCOUNT_100_PLUS
        final_price = price * quantity * (1 - discount)
        if final_price < settings.MIN_PURCHASE_BRL:
            final_price = settings.MIN_PURCHASE_BRL
        return {
            "base_cost": base_cost,
            "multiplier": multiplier,
            "price_per_unit": price,
            "quantity": quantity,
            "discount_percent": discount * 100,
            "discount_amount": price * quantity * discount,
            "final_price": round(final_price, 2),
            "credits": round(final_price, 2)
        }

    @staticmethod
    def get_package_info(package_type: str) -> dict:
        packages = {
            "economic": {"name": "Econômico", "multiplier": settings.ECONOMIC_MULTIPLIER, "sla": "Melhor esforço", "support": "Email"},
            "standard": {"name": "Padrão", "multiplier": settings.STANDARD_MULTIPLIER, "sla": "24h", "support": "Chat"},
            "premium": {"name": "Premium", "multiplier": settings.PREMIUM_MULTIPLIER, "sla": "99% uptime", "support": "Prioritário + Reembolso"}
        }
        return packages.get(package_type, packages["standard"])
