import re
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from keep_alive import keep_alive
from config import get_token, USE_SUPABASE
from constants import AGUARDANDO_SA, AGUARDANDO_GPON, AGUARDANDO_TIPO, AGUARDANDO_SERIAL, AGUARDANDO_FOTOS, AGUARDANDO_DATA_INICIO, AGUARDANDO_DATA_FIM, AGUARDANDO_NOME, AGUARDANDO_SOBRENOME, AGUARDANDO_REGIAO, AGUARDANDO_CONSULTA, AGUARDANDO_BROADCAST, AGUARDANDO_CONFIRMACAO_BROADCAST
from common import ajuda, cancelar, meu_id
from registration import start, receber_nome, receber_sobrenome, receber_regiao
from installation import receber_sa, receber_gpon, receber_tipo, receber_serial, receber_foto, finalizar, comando_reparo
from query_prod import comando_consultar, consultar, iniciar_producao, receber_data_inicio, receber_data_fim
from buttons import button_callback
from admin import admin_panel, admin_callback_handler
from admin_broadcast import admin_send_broadcast, confirmar_broadcast

async def post_init(application: Application) -> None:
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_my_commands([
        BotCommand("start", "Menu principal"),
        BotCommand("ajuda", "Como usar o bot"),
        BotCommand("cancelar", "Cancelar operação atual"),
        BotCommand("meuid", "Descobrir meu ID"),
        BotCommand("admin", "Painel de administração"),
        BotCommand("mensal", "Relatório mensal"),
        BotCommand("semanal", "Relatório semanal"),
        BotCommand("hoje", "Relatório de hoje"),
        BotCommand("consultar", "Consultar instalação"),
        BotCommand("reparo", "Registrar reparo"),
        BotCommand("producao", "Produção por período"),
    ])

def main():
    token = get_token()
    if not re.match(r"^\d+:[A-Za-z0-9_-]+$", token):
        raise RuntimeError("TELEGRAM_TOKEN inválido")
    if not USE_SUPABASE:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY não definidos")
    app = Application.builder().token(token).post_init(post_init).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("producao", iniciar_producao), CommandHandler("consultar", comando_consultar), CallbackQueryHandler(button_callback)],
        states={
            AGUARDANDO_NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            AGUARDANDO_SA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_sa)],
            AGUARDANDO_GPON: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_gpon)],
            AGUARDANDO_TIPO: [CallbackQueryHandler(receber_tipo)],
            AGUARDANDO_SERIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_serial)],
            AGUARDANDO_FOTOS: [MessageHandler(filters.PHOTO, receber_foto), CommandHandler("finalizar", finalizar)],
            AGUARDANDO_DATA_INICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_inicio)],
            AGUARDANDO_DATA_FIM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_fim)],
            AGUARDANDO_SOBRENOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_sobrenome)],
            AGUARDANDO_REGIAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_regiao)],
            AGUARDANDO_CONSULTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultar)],
            AGUARDANDO_BROADCAST: [MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL, admin_send_broadcast)],
            AGUARDANDO_CONFIRMACAO_BROADCAST: [CallbackQueryHandler(confirmar_broadcast)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    from reports import comando_mensal, comando_semanal, comando_hoje
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("meuid", meu_id))
    app.add_handler(CommandHandler("mensal", comando_mensal))
    app.add_handler(CommandHandler("semanal", comando_semanal))
    app.add_handler(CommandHandler("hoje", comando_hoje))
    app.add_handler(CommandHandler("reparo", comando_reparo))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern=r"^(admin_|broadcast_)"))
    keep_alive()
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
