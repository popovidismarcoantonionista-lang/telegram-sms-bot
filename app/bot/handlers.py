import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from app.database import get_db, User, OrderStatus
from app.bot.keyboards import get_main_menu, get_plans_keyboard, get_sms_services_keyboard
from app.utils.pricing import calculate_credits
from app.api.pixintegra_client import PixIntegraClient

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    # Create or get user
    db = next(get_db())
    db_user = db.query(User).filter(User.tg_id == str(user.id)).first()

    if not db_user:
        db_user = User(tg_id=str(user.id), username=user.username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        welcome_text = f"""
🎉 *Bem-vindo ao Bot de Créditos SMS!*

Olá {user.first_name}! 

Este bot permite:
✅ Comprar créditos com PIX automático
✅ Alugar números SMS descartáveis
✅ Comprar seguidores para redes sociais

Use /ajuda para ver todos os comandos disponíveis.
"""
    else:
        welcome_text = f"""
👋 *Bem-vindo de volta, {user.first_name}!*

Seu saldo atual: *R$ {db_user.balance:.2f}*

O que deseja fazer hoje?
"""

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )
    db.close()

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /saldo command"""
    user = update.effective_user
    db = next(get_db())

    db_user = db.query(User).filter(User.tg_id == str(user.id)).first()

    if not db_user:
        await update.message.reply_text("❌ Erro: usuário não encontrado. Use /start primeiro.")
        db.close()
        return

    text = f"""
💰 *Seu Saldo*

Saldo disponível: *R$ {db_user.balance:.2f}*

Use /comprar_creditos para adicionar mais créditos!
"""

    await update.message.reply_text(text, parse_mode="Markdown")
    db.close()

async def buy_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /comprar_creditos command"""
    text = """
💳 *Escolha seu Plano de Créditos*

*Econômico* (×1.7)
→ Melhor custo-benefício

*Padrão* (×2.2)
→ Valor equilibrado

*Premium* (×3.5)
→ SLA 99% + Suporte prioritário

Mínimo: R$ 5,00
Descontos progressivos:
• 5-20 números: 5% off
• 21-100 números: 12% off
• 100+ números: 20% off
"""

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_plans_keyboard()
    )

async def buy_sms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /comprar_sms command"""
    user = update.effective_user
    db = next(get_db())

    db_user = db.query(User).filter(User.tg_id == str(user.id)).first()

    if not db_user or db_user.balance < 1.0:
        await update.message.reply_text(
            "❌ Saldo insuficiente! Use /comprar_creditos para adicionar créditos.",
            parse_mode="Markdown"
        )
        db.close()
        return

    text = """
📱 *Comprar Número SMS*

Escolha o serviço desejado:
"""

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_sms_services_keyboard()
    )
    db.close()

async def buy_followers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /comprar_seguidores command"""
    user = update.effective_user
    db = next(get_db())

    db_user = db.query(User).filter(User.tg_id == str(user.id)).first()

    if not db_user:
        await update.message.reply_text("❌ Use /start primeiro.")
        db.close()
        return

    text = """
👥 *Comprar Seguidores*

Para comprar seguidores, envie as informações neste formato:

`plataforma quantidade url`

Exemplo:
`instagram 1000 https://instagram.com/seuusuario`

Plataformas disponíveis:
• instagram
• tiktok
• youtube
• twitter
"""

    await update.message.reply_text(text, parse_mode="Markdown")
    context.user_data['awaiting_followers_order'] = True
    db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ajuda command"""
    text = """
📚 *Comandos Disponíveis*

/start - Iniciar o bot
/saldo - Ver seu saldo
/comprar_creditos - Adicionar créditos via PIX
/comprar_sms - Alugar número SMS
/comprar_seguidores - Comprar seguidores
/ajuda - Mostrar esta mensagem

*Como funciona?*

1️⃣ Compre créditos com PIX
2️⃣ Use os créditos para SMS ou seguidores
3️⃣ Receba o número/serviço instantaneamente

*Suporte:* @seu_suporte
"""

    await update.message.reply_text(text, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("plan_"):
        plan = data.split("_")[1]
        context.user_data['selected_plan'] = plan

        await query.edit_message_text(
            f"💳 Você selecionou o plano *{plan.upper()}*\n\n"
            f"Agora, envie o valor em reais que deseja adicionar (mínimo R$ 5,00):",
            parse_mode="Markdown"
        )
        context.user_data['awaiting_amount'] = True

    elif data.startswith("sms_"):
        service = data.split("_")[1]
        context.user_data['selected_service'] = service

        await query.edit_message_text(
            f"📱 Serviço selecionado: *{service}*\n\n"
            f"Enviando solicitação...",
            parse_mode="Markdown"
        )

        # Process SMS rent (será implementado)
        await query.edit_message_text(
            "✅ Número SMS alugado com sucesso!\n\n"
            "📱 Número: +1234567890\n"
            "⏰ Aguardando SMS...",
            parse_mode="Markdown"
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user = update.effective_user
    text = update.message.text

    # Check if awaiting amount for credit purchase
    if context.user_data.get('awaiting_amount'):
        try:
            amount = float(text.replace(",", "."))

            if amount < 5.0:
                await update.message.reply_text("❌ Valor mínimo: R$ 5,00")
                return

            plan = context.user_data.get('selected_plan', 'standard')

            # Create PIX charge
            pix_client = PixIntegraClient()
            result = await pix_client.create_charge(
                amount=amount,
                user_tg_id=str(user.id),
                plan=plan
            )

            if result:
                await update.message.reply_text(
                    f"✅ *Pagamento PIX Gerado!*\n\n"
                    f"Valor: R$ {amount:.2f}\n"
                    f"Plano: {plan.upper()}\n\n"
                    f"Pague o QR Code abaixo:\n"
                    f"`{result['pix_code']}`\n\n"
                    f"⏰ Aguardando pagamento...",
                    parse_mode="Markdown"
                )

            context.user_data['awaiting_amount'] = False

        except ValueError:
            await update.message.reply_text("❌ Por favor, envie um valor numérico válido.")

    # Check if awaiting followers order
    elif context.user_data.get('awaiting_followers_order'):
        parts = text.split()

        if len(parts) != 3:
            await update.message.reply_text(
                "❌ Formato inválido. Use:\n`plataforma quantidade url`",
                parse_mode="Markdown"
            )
            return

        platform, quantity, url = parts

        try:
            quantity = int(quantity)

            await update.message.reply_text(
                f"✅ Pedido recebido!\n\n"
                f"Plataforma: {platform}\n"
                f"Quantidade: {quantity}\n"
                f"URL: {url}\n\n"
                f"Processando...",
                parse_mode="Markdown"
            )

            context.user_data['awaiting_followers_order'] = False

        except ValueError:
            await update.message.reply_text("❌ Quantidade deve ser um número.")
