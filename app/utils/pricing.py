from app.config import settings

def calculate_credits(amount: float, plan: str) -> float:
    """
    Calculate credits based on amount and plan

    Args:
        amount: Payment amount in BRL
        plan: Plan type (economic, standard, premium)

    Returns:
        Credits amount
    """

    # Get multiplier
    multipliers = {
        "economic": settings.PLAN_ECONOMIC_MULTIPLIER,
        "standard": settings.PLAN_STANDARD_MULTIPLIER,
        "premium": settings.PLAN_PREMIUM_MULTIPLIER
    }

    multiplier = multipliers.get(plan, settings.PLAN_STANDARD_MULTIPLIER)

    # Base credits (1:1)
    credits = amount * multiplier

    return round(credits, 2)

def calculate_discount(quantity: int) -> float:
    """
    Calculate discount based on quantity

    Args:
        quantity: Number of SMS numbers

    Returns:
        Discount percentage (0-1)
    """
    if quantity >= 100:
        return 0.20  # 20% off
    elif quantity >= 21:
        return 0.12  # 12% off
    elif quantity >= 5:
        return 0.05  # 5% off

    return 0.0

def calculate_final_price(base_price: float, quantity: int) -> float:
    """Calculate final price with discount applied"""
    discount = calculate_discount(quantity)
    total = base_price * quantity
    return total * (1 - discount)
