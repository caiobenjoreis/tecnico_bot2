from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🆘 Central de Ajuda\n\n"
        "Comandos disponíveis:\n\n"
        "/start, /ajuda, /cancelar, /meuid, /admin, /mensal, /semanal, /hoje, /consultar, /reparo, /producao"
    )
    await update.message.reply_text(msg)

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Operação cancelada")

async def meu_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(update.message.from_user.id))

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠️ Bot de Registro de Instalações\n\nBem-vindo! Escolha uma opção:", reply_markup=main_menu())
