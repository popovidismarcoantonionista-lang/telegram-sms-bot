from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from sqlalchemy.orm import Session
from datetime import datetime
import qrcode
from io import BytesIO
import asyncio

from app.config import get_settings
from app.database import SessionLocal, User, Order, SMSRent, FollowerOrder
from app.services.pluggy_service import PluggyService
from app.services.sms_activate import SMSActivateService
from app.services.apex_service import ApexService
from app.services.pricing import PricingService
from app.utils.logger import logger, log_to_db

settings = get_settings()
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

pluggy = PluggyService()
sms_service = SMSActivateService()
apex_service = ApexService()
pricing = PricingService()

USER_STATES = {}

def get_db_session():
    return SessionLocal()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = get_db_session()
    db_user = db.query(User).filter(User.tg_id == str(user.id)).first()
    if not db_user:
        db_user = User(tg_id=str(user.id), username=user.username, balance=0.0)
        db.add(db_user)
        db.commit()
        log_to_db(db, "telegram_bot", "info", f"Novo usuário: {user.id}")

    text = f"🤖 *Bem-vindo ao Bot SMS & Seguidores!*\n\nOlá, {user.first_name}!\n\n💰 *Saldo:* R$ {db_user.balance:.2f}\n\n*Comandos:*\n/comprar_creditos - Comprar créditos PIX\n/comprar_sms - Número SMS descartável\n/comprar_seguidores - Seguidores para redes\n/saldo - Ver saldo e histórico\n\n🎯 Comece comprando créditos!"
    await update.message.reply_text(text, parse_mode="Markdown")
    db.close()

async def comprar_creditos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💵 Econômico (×1.7)", callback_data="package_economic"), InlineKeyboardButton("💳 Padrão (×2.2)", callback_data="package_standard")],
        [InlineKeyboardButton("💎 Premium (×3.5)", callback_data="package_premium")]
    ]
    text = "💰 *COMPRAR CRÉDITOS VIA PIX*\n\n🔹 *Econômico* (×1.7) - Melhor preço\n🔹 *Padrão* (×2.2) - Suporte chat, SLA 24h\n🔹 *Premium* (×3.5) - SLA 99%, suporte prioritário\n\n📦 Mínimo: R$ 5,00"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def package_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    package_type = query.data.replace("package_", "")
    USER_STATES[query.from_user.id] = {"package": package_type, "step": "awaiting_amount"}
    package_info = pricing.get_package_info(package_type)
    text = f"✅ *Pacote:* {package_info['name']}\n📊 *Multiplicador:* ×{package_info['multiplier']}\n\n💵 *Digite o valor (mínimo R$ 5):*\nExemplo: `10` ou `25.50`"
    await query.edit_message_text(text, parse_mode="Markdown")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_state = USER_STATES.get(user.id)
    if not user_state:
        return

    if user_state.get("step") == "awaiting_amount":
        try:
            amount = float(update.message.text.replace(",", "."))
            if amount < settings.MIN_PURCHASE_BRL:
                await update.message.reply_text(f"❌ Mínimo é R$ {settings.MIN_PURCHASE_BRL:.2f}")
                return

            db = get_db_session()
            db_user = db.query(User).filter(User.tg_id == str(user.id)).first()
            package_type = user_state["package"]
            pricing_info = pricing.calculate_price(amount, package_type, 1)

            order = Order(user_id=db_user.id, amount=amount, credits=pricing_info["credits"], package_type=package_type, status="pending")
            db.add(order)
            db.commit()
            db.refresh(order)

            try:
                charge = await pluggy.create_pix_charge(amount, str(order.id), f"Créditos SMS Bot - {package_type.title()}")
                order.pluggy_charge_id = charge["charge_id"]
                order.qr_code_text = charge["qr_code_text"]
                db.commit()

                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(charge["qr_code_text"])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                bio = BytesIO()
                bio.name = 'qrcode.png'
                img.save(bio, 'PNG')
                bio.seek(0)

                text = f"✅ *Cobrança PIX criada!*\n\n💰 *Valor:* R$ {amount:.2f}\n💎 *Créditos:* {pricing_info['credits']:.2f}\n📦 *Pacote:* {package_type.title()}\n\n*PIX Copia e Cola:*\n`{charge['qr_code_text']}`\n\n⏱️ *Expira em:* 15min\n\n🔔 Você receberá confirmação automática!"
                await update.message.reply_photo(photo=bio, caption=text, parse_mode="Markdown")
                log_to_db(db, "telegram_bot", "info", f"PIX criado: R$ {amount} para {user.id}")
            except Exception as e:
                logger.error(f"Erro ao criar PIX: {str(e)}")
                await update.message.reply_text("❌ Erro ao gerar PIX. Tente novamente.")
                order.status = "error"
                db.commit()

            USER_STATES.pop(user.id, None)
            db.close()
        except ValueError:
            await update.message.reply_text("❌ Valor inválido. Digite apenas números")

async def comprar_sms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔜 *Compra de SMS em desenvolvimento*\n\nFuncionalidade completa sendo implementada!\n\nIncluirá:\n• Seleção de país\n• Escolha de serviço\n• Recebimento automático de código", parse_mode="Markdown")

async def comprar_seguidores_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔜 *Compra de Seguidores em desenvolvimento*\n\nFuncionalidade completa sendo implementada!\n\nIncluirá:\n• Instagram\n• TikTok\n• YouTube\n• Facebook", parse_mode="Markdown")

async def saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = get_db_session()
    db_user = db.query(User).filter(User.tg_id == str(user.id)).first()

    if not db_user:
        await update.message.reply_text("❌ Usuário não encontrado. Use /start")
        db.close()
        return

    recent_orders = db.query(Order).filter(Order.user_id == db_user.id).order_by(Order.created_at.desc()).limit(5).all()

    text = f"💰 *SEU SALDO*\n\n💎 *Disponível:* R$ {db_user.balance:.2f}\n👤 *Usuário:* {db_user.username or 'N/A'}\n📅 *Membro desde:* {db_user.created_at.strftime('%d/%m/%Y')}\n\n"

    if recent_orders:
        text += "📜 *Últimas Compras:*\n"
        for order in recent_orders:
            status_emoji = "✅" if order.status == "paid" else "⏳" if order.status == "pending" else "❌"
            text += f"{status_emoji} R$ {order.amount:.2f} - {order.package_type.title()} - {order.created_at.strftime('%d/%m %H:%M')}\n"
    else:
        text += "📜 *Nenhuma compra ainda*\n\nUse /comprar_creditos para começar!"

    await update.message.reply_text(text, parse_mode="Markdown")
    db.close()

async def ajuda_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "ℹ️ *AJUDA - Bot SMS & Seguidores*\n\n*Comandos:*\n/start - Menu principal\n/comprar_creditos - Comprar créditos via PIX\n/comprar_sms - Número SMS descartável\n/comprar_seguidores - Seguidores para redes\n/saldo - Ver saldo e histórico\n\n*Como funciona:*\n1️⃣ Compre créditos via PIX\n2️⃣ Use créditos para SMS ou seguidores\n3️⃣ Receba tudo automaticamente!\n\n*Suporte:* @seu_suporte"
    await update.message.reply_text(text, parse_mode="Markdown")

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("comprar_creditos", comprar_creditos_command))
application.add_handler(CommandHandler("comprar_sms", comprar_sms_command))
application.add_handler(CommandHandler("comprar_seguidores", comprar_seguidores_command))
application.add_handler(CommandHandler("saldo", saldo_command))
application.add_handler(CommandHandler("ajuda", ajuda_command))
application.add_handler(CallbackQueryHandler(package_callback, pattern="^package_"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

async def start_bot():
    await application.initialize()
    await application.start()
    logger.info("Bot Telegram iniciado")

async def stop_bot():
    await application.stop()
    await application.shutdown()
    logger.info("Bot Telegram encerrado")
