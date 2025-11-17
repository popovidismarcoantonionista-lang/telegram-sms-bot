"""
Sistema de precificação com margens dinâmicas e descontos progressivos.
"""
from decimal import Decimal
from typing import Dict
from ..config import settings


class PricingService:
    """Serviço de cálculo de preços"""

    # Taxas base (simuladas - ajustar com valores reais)
    PIXINTEGRA_FEE_PERCENT = Decimal("0.99")  # 0.99%
    SMS_ACTIVATE_BASE_COST = Decimal("0.50")  # R$ 0.50 por número (exemplo)

    MARGINS = {
        "economico": settings.MARGIN_ECONOMICO,
        "padrao": settings.MARGIN_PADRAO,
        "premium": settings.MARGIN_PREMIUM
    }

    @classmethod
    def calculate_credit_price(
        cls,
        amount: Decimal,
        package_type: str = "padrao"
    ) -> Dict[str, Decimal]:
        """
        Calcula preço final dos créditos com base no pacote.
        Retorna dicionário com breakdown de custos.
        """
        margin = cls.MARGINS.get(package_type, cls.MARGINS["padrao"])

        # Cálculo: (valor base + taxa PixIntegra) × margem
        pixintegra_fee = amount * (cls.PIXINTEGRA_FEE_PERCENT / 100)
        base_cost = amount + pixintegra_fee
        final_price = base_cost * margin

        return {
            "amount": amount,
            "pixintegra_fee": pixintegra_fee,
            "margin": margin,
            "final_price": final_price.quantize(Decimal("0.01")),
            "credits": amount  # Simplificado: 1 BRL = 1 crédito
        }

    @classmethod
    def calculate_sms_cost(
        cls,
        quantity: int,
        base_price_per_sms: Decimal = None
    ) -> Dict[str, Decimal]:
        """
        Calcula custo de números SMS com descontos progressivos.

        Descontos:
        - 5-20 números: 5%
        - 21-100 números: 12%
        - 100+: 20%
        """
        if base_price_per_sms is None:
            base_price_per_sms = cls.SMS_ACTIVATE_BASE_COST

        total_before_discount = base_price_per_sms * quantity

        # Aplicar desconto progressivo
        if quantity >= 100:
            discount = Decimal("0.20")  # 20%
        elif quantity >= 21:
            discount = Decimal("0.12")  # 12%
        elif quantity >= 5:
            discount = Decimal("0.05")  # 5%
        else:
            discount = Decimal("0")

        discount_amount = total_before_discount * discount
        final_cost = total_before_discount - discount_amount

        return {
            "quantity": quantity,
            "price_per_unit": base_price_per_sms,
            "subtotal": total_before_discount,
            "discount_percent": discount * 100,
            "discount_amount": discount_amount,
            "final_cost": final_cost.quantize(Decimal("0.01"))
        }

    @classmethod
    def calculate_followers_price(
        cls,
        platform: str,
        quantity: int,
        base_price_per_1k: Decimal = Decimal("10.00")
    ) -> Dict[str, Decimal]:
        """
        Calcula preço para compra de seguidores.
        Preço varia por plataforma e quantidade.
        """
        # Preços base por 1000 seguidores (ajustar conforme API Apex)
        platform_multipliers = {
            "instagram": Decimal("1.0"),
            "tiktok": Decimal("0.8"),
            "youtube": Decimal("1.5"),
            "twitter": Decimal("1.2"),
            "facebook": Decimal("1.1")
        }

        multiplier = platform_multipliers.get(platform.lower(), Decimal("1.0"))
        price_per_1k = base_price_per_1k * multiplier
        total_price = (price_per_1k / 1000) * quantity

        return {
            "platform": platform,
            "quantity": quantity,
            "price_per_1k": price_per_1k,
            "total_price": total_price.quantize(Decimal("0.01"))
        }

    @classmethod
    def validate_minimum_purchase(cls, amount: Decimal) -> bool:
        """Valida se o valor atinge o mínimo de compra"""
        return amount >= settings.MIN_PURCHASE_BRL


pricing_service = PricingService()
