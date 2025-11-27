from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import AGUARDANDO_BROADCAST, AGUARDANDO_CONFIRMACAO_BROADCAST
from services.supabase_client import carregar_usuarios

async def admin_broadcast_start(query):
    await query.edit_message_text("Envie a mensagem para todos")
    return AGUARDANDO_BROADCAST

async def admin_send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    from .admin import is_admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Acesso negado")
        return AGUARDANDO_BROADCAST
    bd = {}
    if update.message.photo:
        bd["type"] = "photo"
        bd["file_id"] = update.message.photo[-1].file_id
        bd["caption"] = update.message.caption or ""
        preview_type = "📷 Foto"
    elif update.message.video:
        bd["type"] = "video"
        bd["file_id"] = update.message.video.file_id
        bd["caption"] = update.message.caption or ""
        preview_type = "🎥 Vídeo"
    elif update.message.document:
        bd["type"] = "document"
        bd["file_id"] = update.message.document.file_id
        bd["caption"] = update.message.caption or ""
        preview_type = "📄 Documento"
    elif update.message.text:
        bd["type"] = "text"
        bd["text"] = update.message.text.strip()
        preview_type = "📝 Texto"
    else:
        await update.message.reply_text("❌ Tipo de mensagem não suportado")
        return AGUARDANDO_BROADCAST
    context.user_data["broadcast_data"] = bd
    usuarios = carregar_usuarios()
    total = len(usuarios)
    preview_content = bd.get("text", bd.get("caption", ""))
    if len(preview_content) > 200:
        preview_content = preview_content[:200] + "..."
    msg = f"Preview\nTipo {preview_type}\nDestinatários {total}\n\n{preview_content}"
    keyboard = [
        [InlineKeyboardButton("✅ Enviar", callback_data="broadcast_send")],
        [InlineKeyboardButton("📌 Enviar e Fixar", callback_data="broadcast_send_pin")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="broadcast_cancel")],
    ]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    return AGUARDANDO_CONFIRMACAO_BROADCAST

async def confirmar_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "broadcast_cancel":
        await query.edit_message_text("❌ Broadcast cancelado")
        context.user_data.pop("broadcast_data", None)
        return None
    pin_message = query.data == "broadcast_send_pin"
    bd = context.user_data.get("broadcast_data")
    usuarios = carregar_usuarios()
    await query.edit_message_text("Enviando...")
    enviados = 0
    falhas = 0
    fixados = 0
    for uid in usuarios.keys():
        try:
            if bd["type"] == "text":
                m = await context.bot.send_message(chat_id=int(uid), text=bd["text"]) 
            elif bd["type"] == "photo":
                m = await context.bot.send_photo(chat_id=int(uid), photo=bd["file_id"], caption=bd.get("caption", ""))
            elif bd["type"] == "video":
                m = await context.bot.send_video(chat_id=int(uid), video=bd["file_id"], caption=bd.get("caption", ""))
            elif bd["type"] == "document":
                m = await context.bot.send_document(chat_id=int(uid), document=bd["file_id"], caption=bd.get("caption", ""))
            enviados += 1
            if pin_message:
                try:
                    await context.bot.pin_chat_message(chat_id=int(uid), message_id=m.message_id, disable_notification=True)
                    fixados += 1
                except:
                    pass
        except:
            falhas += 1
    msg = f"Concluído. Enviados {enviados} Falhas {falhas}"
    if pin_message:
        msg += f" Fixados {fixados}"
    await query.edit_message_text(msg)
    context.user_data.pop("broadcast_data", None)
    return None
