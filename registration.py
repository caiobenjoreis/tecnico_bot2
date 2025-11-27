from telegram import Update
from telegram.ext import ContextTypes
from core.constants import AGUARDANDO_NOME, AGUARDANDO_SOBRENOME, AGUARDANDO_REGIAO
from services.supabase_client import carregar_usuarios, salvar_usuario
from ui.keyboards import main_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    usuarios = carregar_usuarios()
    if str(user_id) not in usuarios:
        context.user_data["ident"] = {}
        await update.message.reply_text("Informe seu nome:")
        return AGUARDANDO_NOME
    await update.message.reply_text("🛠️ Bot de Registro de Instalações\n\nBem-vindo! Escolha uma opção:", reply_markup=main_menu())

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("ident", {})
    context.user_data["ident"]["nome"] = update.message.text.strip()
    await update.message.reply_text("Informe seu sobrenome:")
    return AGUARDANDO_SOBRENOME

async def receber_sobrenome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("ident", {})
    context.user_data["ident"]["sobrenome"] = update.message.text.strip()
    await update.message.reply_text("Informe sua região de atuação:")
    return AGUARDANDO_REGIAO

async def receber_regiao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    regiao = update.message.text.strip()
    user_id = update.message.from_user.id
    ident = context.user_data.get("ident", {})
    dados_usuario = {
        "nome": ident.get("nome", ""),
        "sobrenome": ident.get("sobrenome", ""),
        "regiao": regiao,
        "telegram": update.message.from_user.username or update.message.from_user.first_name,
    }
    salvar_usuario(str(user_id), dados_usuario)
    await update.message.reply_text("✅ Perfil salvo!", reply_markup=main_menu())
    context.user_data.pop("ident", None)
