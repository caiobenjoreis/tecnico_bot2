from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from keyboards import main_menu
from constants import AGUARDANDO_SA, AGUARDANDO_TIPO, AGUARDANDO_FOTOS, AGUARDANDO_DATA_INICIO, TZ
from supabase_client import carregar_dados
from reports import ciclo_atual, montar_msg_producao, gerar_relatorio_mensal, gerar_relatorio_semanal, gerar_relatorio_hoje, gerar_ranking_tecnicos, menu_relatorios

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "registrar":
        context.user_data["modo_registro"] = "instalacao"
        await query.edit_message_text("Informe a SA")
        return AGUARDANDO_SA
    if query.data == "registrar_reparo":
        context.user_data["modo_registro"] = "reparo"
        await query.edit_message_text("Informe a SA")
        return AGUARDANDO_SA
    if query.data == "consultar":
        await query.edit_message_text("Envie SA ou GPON")
        return None
    if query.data == "minhas":
        dados = carregar_dados()
        user_id = query.from_user.id
        instalacoes_user = [d for d in dados if d.get("tecnico_id") == user_id]
        if not instalacoes_user:
            await query.edit_message_text("Você ainda não registrou nenhuma instalação.")
            return None
        msg = f"Suas Instalações ({len(instalacoes_user)})\n\n"
        for i, inst in enumerate(instalacoes_user[-10:], 1):
            msg += f"{i}. SA {inst['sa']} GPON {inst['gpon']}\n"
            msg += f"   Data {inst['data']}\n\n"
        await query.edit_message_text(msg)
        return None
    if query.data == "consulta_producao":
        dados = carregar_dados()
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        inicio_dt, fim_dt = ciclo_atual()
        instalacoes_user = []
        for d in dados:
            try:
                from datetime import datetime as _dt
                data_inst = _dt.strptime(d["data"], "%d/%m/%Y %H:%M").replace(tzinfo=None)
                if d.get("tecnico_id") == user_id:
                    instalacoes_user.append(d)
            except:
                pass
        if not instalacoes_user:
            await query.edit_message_text(f"Nenhuma instalação entre {inicio_dt.strftime('%d/%m/%Y')} e {fim_dt.strftime('%d/%m/%Y')}")
            return None
        msg = montar_msg_producao(instalacoes_user, inicio_dt, fim_dt, username)
        keyboard = [[InlineKeyboardButton("📄 Ver Detalhes", callback_data="detalhes_producao")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return None
    if query.data == "relatorios":
        await menu_relatorios(query)
        return None
    if query.data == "rel_mensal":
        await query.edit_message_text(gerar_relatorio_mensal())
        return None
    if query.data == "rel_semanal":
        await query.edit_message_text(gerar_relatorio_semanal())
        return None
    if query.data == "rel_hoje":
        await query.edit_message_text(gerar_relatorio_hoje())
        return None
    if query.data == "rel_periodo":
        await query.edit_message_text("Envie a data inicial dd/mm/aaaa")
        return AGUARDANDO_DATA_INICIO
    if query.data == "rel_ranking":
        await query.edit_message_text(gerar_ranking_tecnicos())
        return None
    if query.data == "detalhes_producao":
        dados = carregar_dados()
        user_id = query.from_user.id
        inicio_dt, fim_dt = ciclo_atual()
        instalacoes_user = []
        for d in dados:
            try:
                from datetime import datetime as _dt
                dt = _dt.strptime(d["data"], "%d/%m/%Y %H:%M")
                if d.get("tecnico_id") == user_id and inicio_dt <= dt.replace(tzinfo=TZ) <= fim_dt:
                    instalacoes_user.append(d)
            except:
                pass
        if not instalacoes_user:
            await query.answer("Nenhuma instalação encontrada.", show_alert=True)
            return None
        from constants import PONTOS_SERVICO
        msg = f"Detalhes do Ciclo ({inicio_dt.strftime('%d/%m')} - {fim_dt.strftime('%d/%m')})\n\n"
        for inst in sorted(instalacoes_user, key=lambda x: x["data"], reverse=True):
            tipo = inst.get("tipo", "Instalação")
            pontos = PONTOS_SERVICO.get(str(tipo).lower(), 0)
            msg += f"{inst['data']} | {pontos} pts\n"
            msg += f"{tipo} | SA {inst['sa']}\n"
            msg += f"──────────────────\n"
        if len(msg) > 4000:
            msg = msg[:4000] + "\n\n(Lista truncada)"
        await query.edit_message_text(msg)
        return None
    await query.edit_message_text("Menu", reply_markup=main_menu())
