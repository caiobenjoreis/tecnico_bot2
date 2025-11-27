from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from constants import AGUARDANDO_SA, AGUARDANDO_GPON, AGUARDANDO_TIPO, AGUARDANDO_SERIAL, AGUARDANDO_FOTOS, PONTOS_SERVICO
from supabase_client import salvar_instalacao
from util import now_str

def tipos_keyboard():
    k = [
        [InlineKeyboardButton("Instalação", callback_data="tipo_instalacao")],
        [InlineKeyboardButton("Instalação TV", callback_data="tipo_instalacao_tv")],
        [InlineKeyboardButton("Defeito Banda Larga", callback_data="tipo_defeito_banda_larga")],
        [InlineKeyboardButton("Defeito Linha", callback_data="tipo_defeito_linha")],
        [InlineKeyboardButton("Defeito TV", callback_data="tipo_defeito_tv")],
        [InlineKeyboardButton("Mudança Endereço", callback_data="tipo_mudanca_endereco")],
        [InlineKeyboardButton("Retirada", callback_data="tipo_retirada")],
        [InlineKeyboardButton("Serviço", callback_data="tipo_servico")],
    ]
    return InlineKeyboardMarkup(k)

async def receber_sa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sa = update.message.text.strip()
    context.user_data["sa"] = sa
    await update.message.reply_text("Envie o GPON:")
    return AGUARDANDO_GPON

async def receber_gpon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gpon = update.message.text.strip()
    context.user_data["gpon"] = gpon
    context.user_data["fotos"] = []
    await update.message.reply_text("Escolha o tipo:", reply_markup=tipos_keyboard())
    return AGUARDANDO_TIPO

async def receber_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d = query.data
    tipo = d.replace("tipo_", "")
    context.user_data["tipo"] = tipo
    await query.edit_message_text("Informe o serial do equipamento:")
    return AGUARDANDO_SERIAL

async def receber_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    serial = update.message.text.strip()
    context.user_data["serial"] = serial
    await update.message.reply_text("Envie fotos e use /finalizar quando terminar")
    return AGUARDANDO_FOTOS

async def receber_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = update.message.photo
    if photos:
        file_id = photos[-1].file_id
        context.user_data.setdefault("fotos", []).append(file_id)

async def finalizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.message.from_user
    inst = {
        "sa": context.user_data.get("sa"),
        "gpon": context.user_data.get("gpon"),
        "tipo": context.user_data.get("tipo"),
        "serial": context.user_data.get("serial"),
        "fotos": context.user_data.get("fotos", []),
        "tecnico_id": u.id,
        "tecnico_nome": u.username or u.first_name,
        "data": now_str(),
    }
    ok = salvar_instalacao(inst)
    if ok:
        await update.message.reply_text("✅ Instalação registrada")
    else:
        await update.message.reply_text("❌ Falha ao salvar")
    context.user_data.clear()

async def comando_reparo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["modo_registro"] = "reparo"
    await update.message.reply_text("Envie o número da SA:")
    return AGUARDANDO_SA
