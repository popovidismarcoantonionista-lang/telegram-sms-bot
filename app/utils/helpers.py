def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def truncate_text(text: str, max_length: int = 50) -> str:
    return text if len(text) <= max_length else text[:max_length-3] + "..."
