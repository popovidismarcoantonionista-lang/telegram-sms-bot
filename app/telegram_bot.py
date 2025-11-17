"""
Bot Telegram principal com handlers de comandos e callbacks.
Usa python-telegram-bot v20+ (async).
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
import asyncio

from .config import settings
from .database import AsyncSessionLocal
from .models import User, Order, SMSRent, OrderStatus, SMSStatus
from .services.pixintegra import pixintegra_client
from .services.sms_activate import sms_activate_client
from .services.pricing import pricing_service
from .utils.logger import logger, log_to_db


class TelegramBot:
    """Gerenciador do bot Telegram"""

    def __init__(self):
        self.app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Configura todos os handlers do bot"""
        # Comandos
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("saldo", self.cmd_saldo))
        self.app.add_handler(CommandHandler("comprar_creditos", self.cmd_comprar_creditos))
        self.app.add_handler(CommandHandler("comprar_sms", self.cmd_comprar_sms))
        self.app.add_handler(CommandHandler("comprar_seguidores", self.cmd_comprar_seguidores))
        self.app.add_handler(CommandHandler("historico", self.cmd_historico))

        # Callbacks
        self.app.add_handler(CallbackQueryHandler(self.callback_handler))

    async def get_or_create_user(self, update: Update) -> User:
        """Obtém ou cria usuário no banco"""
        async with AsyncSessionLocal() as db:
            tg_id = str(update.effective_user.id)
            username = update.effective_user.username

            result = await db.execute(
                select(User).where(User.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    tg_id=tg_id,
                    username=username,
                    balance=Decimal("0.00")
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

                logger.info("new_user_created", tg_id=tg_id, username=username)

            return user

    # ========== HANDLERS DE COMANDOS ==========

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /start"""
        user = await self.get_or_create_user(update)

        welcome_message = f"""
🤖 *Bem-vindo ao Bot de SMS e Seguidores!*

Olá, {update.effective_user.first_name}!

*Serviços disponíveis:*
📱 Números SMS descartáveis (SMS-Activate)
👥 Compra de seguidores (Apex Seguidores)

*Comandos:*
/comprar_creditos - Adicionar créditos via PIX
/comprar_sms - Alugar número para receber SMS
/comprar_seguidores - Comprar seguidores
/saldo - Ver seu saldo atual
/historico - Ver histórico de compras
/help - Ajuda

💰 Seu saldo atual: R$ {user.balance:.2f}

_Pagamentos processados automaticamente via PIX!_
        """

        await update.message.reply_text(
            welcome_message,
            parse_mode="Markdown"
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /help"""
        help_text = """
📚 *Ajuda - Como usar o bot*

*1️⃣ Comprar Créditos:*
Use /comprar_creditos e escolha um pacote:
• 💚 Econômico (×1.7)
• 🔵 Padrão (×2.2)
• 🟡 Premium (×3.5 + SLA 99%)

Após gerar o PIX, pague e seu saldo será creditado automaticamente!

*2️⃣ Comprar SMS:*
Use /comprar_sms, escolha serviço e país.
Você receberá o número e o código SMS chegará em até 10 min.

*3️⃣ Comprar Seguidores:*
Use /comprar_seguidores, informe plataforma, quantidade e URL.
Seguidores chegam em até 24h.

*💡 Descontos Progressivos (SMS):*
• 5-20 números: 5% OFF
• 21-100 números: 12% OFF
• 100+ números: 20% OFF

_Dúvidas? Entre em contato com o suporte._
        """

        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def cmd_saldo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /saldo"""
        user = await self.get_or_create_user(update)

        saldo_text = f"""
💰 *Seu Saldo Atual*

Créditos disponíveis: *R$ {user.balance:.2f}*

Para adicionar mais créditos, use /comprar_creditos
        """

        await update.message.reply_text(saldo_text, parse_mode="Markdown")


    async def cmd_comprar_creditos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /comprar_creditos"""
        keyboard = [
            [
                InlineKeyboardButton("💚 Econômico (×1.7)", callback_data="buy_credits:economico"),
                InlineKeyboardButton("🔵 Padrão (×2.2)", callback_data="buy_credits:padrao")
            ],
            [
                InlineKeyboardButton("🟡 Premium (×3.5 + SLA)", callback_data="buy_credits:premium")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        packages_text = """
💳 *Escolha seu Pacote de Créditos*

*Pacotes disponíveis:*

💚 *Econômico* (margem ×1.7)
   └ Ideal para uso básico

🔵 *Padrão* (margem ×2.2)
   └ Melhor custo-benefício

🟡 *Premium* (margem ×3.5)
   └ SLA 99% + Suporte prioritário

_Mínimo: R$ 5,00_
_Após escolher o pacote, informe o valor desejado._
        """

        await update.message.reply_text(
            packages_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def cmd_comprar_sms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /comprar_sms"""
        user = await self.get_or_create_user(update)

        if user.balance < Decimal("0.50"):
            await update.message.reply_text(
                "❌ Saldo insuficiente! Use /comprar_creditos para adicionar créditos.",
                parse_mode="Markdown"
            )
            return

        # Keyboard com serviços populares
        keyboard = [
            [
                InlineKeyboardButton("📱 WhatsApp", callback_data="sms_service:wa"),
                InlineKeyboardButton("✈️ Telegram", callback_data="sms_service:tg")
            ],
            [
                InlineKeyboardButton("🔍 Google", callback_data="sms_service:go"),
                InlineKeyboardButton("📘 Facebook", callback_data="sms_service:fb")
            ],
            [
                InlineKeyboardButton("📸 Instagram", callback_data="sms_service:ig"),
                InlineKeyboardButton("🐦 Twitter", callback_data="sms_service:tw")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sms_text = f"""
📱 *Comprar Número SMS*

💰 Saldo disponível: R$ {user.balance:.2f}

*Selecione o serviço:*
_O número será fornecido imediatamente após a compra._
_Você terá 10 minutos para receber o código._

💡 *Descontos progressivos:*
• 5-20 números: 5% OFF
• 21-100 números: 12% OFF
• 100+ números: 20% OFF
        """

        await update.message.reply_text(
            sms_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def cmd_comprar_seguidores(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /comprar_seguidores"""
        user = await self.get_or_create_user(update)

        keyboard = [
            [
                InlineKeyboardButton("📸 Instagram", callback_data="followers:instagram"),
                InlineKeyboardButton("🎵 TikTok", callback_data="followers:tiktok")
            ],
            [
                InlineKeyboardButton("📺 YouTube", callback_data="followers:youtube"),
                InlineKeyboardButton("🐦 Twitter", callback_data="followers:twitter")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        followers_text = f"""
👥 *Comprar Seguidores*

💰 Saldo disponível: R$ {user.balance:.2f}

*Selecione a plataforma:*
_Após selecionar, informe a URL do perfil e quantidade desejada._

📊 *Preços estimados (por 1000):*
• Instagram: R$ 10,00
• TikTok: R$ 8,00
• YouTube: R$ 15,00
• Twitter: R$ 12,00

⏱ Entrega em até 24 horas
        """

        await update.message.reply_text(
            followers_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def cmd_historico(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler do comando /historico"""
        user = await self.get_or_create_user(update)

        async with AsyncSessionLocal() as db:
            # Buscar últimas compras
            result = await db.execute(
                select(Order)
                .where(Order.user_id == user.id)
                .order_by(Order.created_at.desc())
                .limit(10)
            )
            orders = result.scalars().all()

            if not orders:
                await update.message.reply_text(
                    "📭 Você ainda não fez nenhuma compra."
                )
                return

            historico_text = "📊 *Histórico de Compras*\n\n"

            for order in orders:
                status_emoji = {
                    OrderStatus.PENDING: "⏳",
                    OrderStatus.PAID: "✅",
                    OrderStatus.EXPIRED: "❌",
                    OrderStatus.CANCELLED: "🚫"
                }.get(order.status, "❓")

                historico_text += f"{status_emoji} R$ {order.amount:.2f} - {order.status.value}\n"
                historico_text += f"   📅 {order.created_at.strftime('%d/%m/%Y %H:%M')}\n\n"

            await update.message.reply_text(historico_text, parse_mode="Markdown")
