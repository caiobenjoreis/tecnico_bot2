from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from core.constants import TZ, TABELA_FAIXAS, PONTOS_SERVICO, AGUARDANDO_DATA_INICIO, AGUARDANDO_DATA_FIM
from services.supabase_client import carregar_dados

def calcular_pontos(instalacoes):
    total = 0.0
    for inst in instalacoes:
        tipo = str(inst.get("tipo", "instalacao")).lower()
        total += PONTOS_SERVICO.get(tipo, 0)
    return total

def obter_faixa_valor(pontos):
    for f in TABELA_FAIXAS:
        if f["min"] <= pontos <= f["max"]:
            return f
    return TABELA_FAIXAS[0]

async def comando_consultar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envie SA ou GPON")

async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    termo = update.message.text.strip().lower()
    dados = carregar_dados()
    resultados = []
    for d in dados:
        sa = str(d.get("sa") or "").lower()
        gpon = str(d.get("gpon") or "").lower()
        if termo in sa or termo in gpon:
            resultados.append(d)
    if not resultados:
        await update.message.reply_text("❌ Nenhuma instalação encontrada")
        return
    for r in resultados:
        await update.message.reply_text(f"SA {r.get('sa')} GPON {r.get('gpon')} {r.get('data')}")

async def iniciar_producao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Informe data início dd/mm/aaaa")
    return AGUARDANDO_DATA_INICIO

async def receber_data_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data_inicio"] = update.message.text.strip()
    await update.message.reply_text("Informe data fim dd/mm/aaaa")
    return AGUARDANDO_DATA_FIM

async def receber_data_fim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inicio = context.user_data.get("data_inicio")
    fim = update.message.text.strip()
    dados = carregar_dados()
    inicio_dt = datetime.strptime(inicio, "%d/%m/%Y").replace(tzinfo=TZ)
    fim_dt = datetime.strptime(fim, "%d/%m/%Y").replace(tzinfo=TZ) + timedelta(days=1) - timedelta(seconds=1)
    u = update.message.from_user
    r = []
    for d in dados:
        try:
            dt = datetime.strptime(d["data"], "%d/%m/%Y %H:%M").replace(tzinfo=TZ)
            if d.get("tecnico_id") == u.id and inicio_dt <= dt <= fim_dt:
                r.append(d)
        except:
            pass
    if not r:
        await update.message.reply_text("❌ Nenhuma instalação no período")
        context.user_data.pop("data_inicio", None)
        return
    pontos = calcular_pontos(r)
    tier = obter_faixa_valor(pontos)
    valor = tier["valor"]
    await update.message.reply_text(f"Instalações {len(r)} Pontos {int(pontos)} Faixa {tier['faixa']} Valor {valor:.2f}")
    context.user_data.pop("data_inicio", None)
