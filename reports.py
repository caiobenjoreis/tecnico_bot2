from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.reports import gerar_relatorio_mensal, gerar_relatorio_semanal, gerar_relatorio_hoje, gerar_ranking_tecnicos
from core.constants import AGUARDANDO_DATA_INICIO

async def menu_relatorios(query):
    keyboard = [
        [InlineKeyboardButton("📅 Relatório Mensal", callback_data="rel_mensal")],
        [InlineKeyboardButton("📊 Relatório Semanal", callback_data="rel_semanal")],
        [InlineKeyboardButton("📆 Relatório por Período", callback_data="rel_periodo")],
        [InlineKeyboardButton("📈 Relatório Hoje", callback_data="rel_hoje")],
        [InlineKeyboardButton("🏆 Ranking Técnicos", callback_data="rel_ranking")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="voltar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Relatórios Disponíveis", reply_markup=reply_markup)

async def comando_mensal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = gerar_relatorio_mensal()
    await update.message.reply_text(msg)

async def comando_semanal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = gerar_relatorio_semanal()
    await update.message.reply_text(msg)

async def comando_hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = gerar_relatorio_hoje()
    await update.message.reply_text(msg)
