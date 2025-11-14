from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💳 Comprar Créditos", callback_data="menu_credits")],
        [InlineKeyboardButton("📱 Comprar SMS", callback_data="menu_sms")],
        [InlineKeyboardButton("👥 Comprar Seguidores", callback_data="menu_followers")],
        [InlineKeyboardButton("💰 Ver Saldo", callback_data="menu_balance")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_plans_keyboard():
    keyboard = [
        [InlineKeyboardButton("💚 Econômico (×1.7)", callback_data="plan_economic")],
        [InlineKeyboardButton("💙 Padrão (×2.2)", callback_data="plan_standard")],
        [InlineKeyboardButton("💎 Premium (×3.5)", callback_data="plan_premium")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sms_services_keyboard():
    keyboard = [
        [InlineKeyboardButton("WhatsApp", callback_data="sms_whatsapp")],
        [InlineKeyboardButton("Telegram", callback_data="sms_telegram")],
        [InlineKeyboardButton("Instagram", callback_data="sms_instagram")],
        [InlineKeyboardButton("Facebook", callback_data="sms_facebook")],
        [InlineKeyboardButton("Google", callback_data="sms_google")],
        [InlineKeyboardButton("Twitter", callback_data="sms_twitter")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard(action_id: str):
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{action_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{action_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
