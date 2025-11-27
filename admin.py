from collections import defaultdict
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ContextTypes
from core.constants import TZ, ADMIN_IDS
from services.supabase_client import carregar_dados, carregar_usuarios
from ui.keyboards import admin_menu
from handlers.admin_broadcast import admin_broadcast_start

def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ Acesso negado")
        return
    await update.message.reply_text("Painel de Administração", reply_markup=admin_menu())

async def admin_stats(query):
    dados = carregar_dados()
    usuarios = carregar_usuarios()
    total_tecnicos = len(usuarios)
    total_instalacoes = len(dados)
    por_tipo = defaultdict(int)
    por_tecnico = defaultdict(int)
    agora = datetime.now(TZ)
    sete = agora - timedelta(days=7)
    semana = 0
    for d in dados:
        por_tipo[d.get("tipo", "instalacao")] += 1
        por_tecnico[d.get("tecnico_nome", "")] += 1
        try:
            dt = datetime.strptime(d["data"], "%d/%m/%Y %H:%M").replace(tzinfo=TZ)
            if dt >= sete:
                semana += 1
        except:
            pass
    msg = f"Técnicos {total_tecnicos}\nInstalações {total_instalacoes}\nÚltimos 7 dias {semana}"
    await query.edit_message_text(msg)

async def admin_list_users(query):
    usuarios = carregar_usuarios()
    dados = carregar_dados()
    por_tecnico_id = defaultdict(int)
    for d in dados:
        tid = str(d.get("tecnico_id", ""))
        if tid:
            por_tecnico_id[tid] += 1
    msg = f"Técnicos Cadastrados {len(usuarios)}\n\n"
    for uid, du in sorted(usuarios.items(), key=lambda x: por_tecnico_id.get(x[0], 0), reverse=True):
        nome = f"{du.get('nome','')} {du.get('sobrenome','')}".strip()
        regiao = du.get("regiao", "N/A")
        qtd = por_tecnico_id.get(uid, 0)
        msg += f"{nome}\nID {uid}\nRegião {regiao}\nInstalações {qtd}\n\n"
    await query.edit_message_text(msg)

async def admin_all_installations(query):
    dados = carregar_dados()
    ultimas = dados[-20:] if len(dados) > 20 else dados
    ultimas.reverse()
    msg = f"Últimas Instalações {len(ultimas)}/{len(dados)}\n\n"
    for inst in ultimas:
        msg += f"{inst['data']} SA {inst['sa']} GPON {inst['gpon']} {inst.get('tipo','instalacao')}\n"
    await query.edit_message_text(msg)

async def admin_export_data(query):
    dados = carregar_dados()
    usuarios = carregar_usuarios()
    agora = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    msg = f"Exportação de Dados\nData {agora}\n\nInstalações {len(dados)} Técnicos {len(usuarios)}\n"
    await query.edit_message_text(msg)

async def admin_manage_admins(query):
    msg = (
        "Gerenciar Administradores\n\n"
        "Edite a lista ADMIN_IDS em novo_bot/core/constants.py e faça deploy.\n"
        "Para descobrir um ID use /meuid."
    )
    await query.edit_message_text(msg)

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if not is_admin(uid):
        await query.answer("❌ Acesso negado", show_alert=True)
        return
    await query.answer()
    if query.data == "admin_stats":
        await admin_stats(query)
        return
    if query.data == "admin_users":
        await admin_list_users(query)
        return
    if query.data == "admin_all_installs":
        await admin_all_installations(query)
        return
    if query.data == "admin_broadcast":
        return await admin_broadcast_start(query)
    if query.data == "admin_export":
        await admin_export_data(query)
        return
    if query.data == "admin_manage":
        await admin_manage_admins(query)
        return
