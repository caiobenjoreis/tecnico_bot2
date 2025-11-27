from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🆕 Registrar Instalação", callback_data="registrar")],
        [InlineKeyboardButton("🛠️ Registrar Reparo", callback_data="registrar_reparo")],
        [InlineKeyboardButton("🔎 Consultar SA/GPON", callback_data="consultar")],
        [InlineKeyboardButton("📂 Minhas Instalações", callback_data="minhas")],
        [InlineKeyboardButton("📅 Consulta Produção", callback_data="consulta_producao")],
        [InlineKeyboardButton("📊 Relatórios", callback_data="relatorios")],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu():
    keyboard = [
        [InlineKeyboardButton("📈 Estatísticas", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Técnicos", callback_data="admin_users")],
        [InlineKeyboardButton("📋 Instalações", callback_data="admin_all_installs")],
        [InlineKeyboardButton("📤 Exportar", callback_data="admin_export")],
        [InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚙️ Admins", callback_data="admin_manage")],
    ]
    return InlineKeyboardMarkup(keyboard)

