from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from constants import AGUARDANDO_DATA_INICIO, TZ, TABELA_FAIXAS, PONTOS_SERVICO
from supabase_client import carregar_dados

from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any, Tuple

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

# ==== Funções de relatório e produção (mescladas do serviço) ====

def calcular_pontos(instalacoes: List[Dict[str, Any]]) -> float:
    total = 0.0
    for inst in instalacoes:
        tipo = str(inst.get("tipo", "instalacao")).lower()
        total += PONTOS_SERVICO.get(tipo, 0)
    return total

def contar_dias_produtivos(instalacoes: List[Dict[str, Any]]) -> int:
    dias = set()
    for inst in instalacoes:
        try:
            dt = datetime.strptime(inst["data"], "%d/%m/%Y %H:%M")
            dias.add(dt.date())
        except:
            pass
    return len(dias)

def obter_faixa_valor(pontos: float):
    p = float(pontos)
    for tier in TABELA_FAIXAS:
        if tier["min"] <= p <= tier["max"]:
            return tier
    return TABELA_FAIXAS[-1]

def _formata_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

def ciclo_atual() -> Tuple[datetime, datetime]:
    agora = datetime.now(TZ)
    if agora.day >= 16:
        inicio = datetime(agora.year, agora.month, 16, tzinfo=TZ)
        ano = agora.year + 1 if agora.month == 12 else agora.year
        mes = 1 if agora.month == 12 else agora.month + 1
        fim = datetime(ano, mes, 15, 23, 59, tzinfo=TZ)
    else:
        ano_prev = agora.year - 1 if agora.month == 1 else agora.year
        mes_prev = 12 if agora.month == 1 else agora.month - 1
        inicio = datetime(ano_prev, mes_prev, 16, tzinfo=TZ)
        fim = datetime(agora.year, agora.month, 15, 23, 59, tzinfo=TZ)
    return inicio, fim

def montar_msg_producao(instalacoes_user: List[Dict[str, Any]], inicio: datetime, fim: datetime, username: str) -> str:
    dias_periodo = (fim - inicio).days + 1
    media_dia = len(instalacoes_user) / dias_periodo if dias_periodo > 0 else 0
    pontos = calcular_pontos(instalacoes_user)
    dias_produtivos = contar_dias_produtivos(instalacoes_user)
    turbo_ativo = dias_produtivos >= 24
    tier = obter_faixa_valor(pontos)
    valor_unit = tier["valor_turbo"] if turbo_ativo else tier["valor"]
    valor_total = pontos * valor_unit
    proxima_faixa = None
    for t in reversed(TABELA_FAIXAS):
        if t["min"] > pontos:
            proxima_faixa = t
            break
    if proxima_faixa:
        meta = proxima_faixa["min"]
        falta = meta - pontos
        percentual = min(100, (pontos / meta) * 100)
        blocos = int(percentual / 10)
        barra = "█" * blocos + "░" * (10 - blocos)
        inst_faltantes = int(falta / 1.5) + 1
        progresso_msg = f"\nPróxima Faixa {proxima_faixa['faixa']}\n{barra} {percentual:.1f}%\nFaltam {falta:.2f} pts (~{inst_faltantes})\n"
    else:
        progresso_msg = "\nFaixa máxima atingida\n"
    msg = (
        f"Produção {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}\n"
        f"Técnico {username}\n\n"
        f"Instalações {len(instalacoes_user)}\n"
        f"Pontos {pontos:.2f}\n"
        f"Dias Produtivos {dias_produtivos}/24\n"
        f"Média Diária {media_dia:.1f}\n"
        f"{progresso_msg}\n"
        f"Faixa {tier['faixa']} Turbo {'Ativo' if turbo_ativo else 'Inativo'}\n"
        f"Valor Ponto {_formata_brl(valor_unit)}\n"
        f"Total {_formata_brl(valor_total)}\n"
    )
    return msg

def gerar_relatorio_mensal() -> str:
    dados = carregar_dados()
    agora = datetime.now(TZ)
    mes_atual = agora.month
    ano_atual = agora.year
    instalacoes_mes: List[Dict[str, Any]] = []
    for inst in dados:
        try:
            data_inst = datetime.strptime(inst["data"], "%d/%m/%Y %H:%M")
            data_inst = data_inst.replace(tzinfo=TZ)
            if data_inst.month == mes_atual and data_inst.year == ano_atual:
                instalacoes_mes.append(inst)
        except:
            pass
    if not instalacoes_mes:
        return "❌ Nenhuma instalação registrada neste mês."
    por_tecnico = defaultdict(int)
    for inst in instalacoes_mes:
        por_tecnico[inst["tecnico_nome"]] += 1
    nome_mes = agora.strftime("%B/%Y")
    msg = f"Relatório Mensal {nome_mes}\nTotal {len(instalacoes_mes)}\n\n"
    for tecnico, qtd in sorted(por_tecnico.items(), key=lambda x: x[1], reverse=True):
        msg += f"{tecnico}: {qtd}\n"
    dias_mes = agora.day
    media_dia = len(instalacoes_mes) / dias_mes
    msg += f"\nMédia diária {media_dia:.1f}"
    return msg

def gerar_relatorio_semanal() -> str:
    dados = carregar_dados()
    agora = datetime.now(TZ)
    inicio_semana = agora - timedelta(days=agora.weekday())
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    instalacoes_semana: List[Dict[str, Any]] = []
    for inst in dados:
        try:
            data_inst = datetime.strptime(inst["data"], "%d/%m/%Y %H:%M")
            data_inst = data_inst.replace(tzinfo=TZ)
            if data_inst >= inicio_semana:
                instalacoes_semana.append(inst)
        except:
            pass
    if not instalacoes_semana:
        return "❌ Nenhuma instalação registrada nesta semana."
    por_tecnico = defaultdict(int)
    for inst in instalacoes_semana:
        por_tecnico[inst["tecnico_nome"]] += 1
    msg = f"Relatório Semanal {inicio_semana.strftime('%d/%m')} a {agora.strftime('%d/%m/%Y')}\nTotal {len(instalacoes_semana)}\n\n"
    for tecnico, qtd in sorted(por_tecnico.items(), key=lambda x: x[1], reverse=True):
        msg += f"{tecnico}: {qtd}\n"
    dias_semana = (agora - inicio_semana).days + 1
    media_dia = len(instalacoes_semana) / dias_semana
    msg += f"\nMédia diária {media_dia:.1f}"
    return msg

def gerar_relatorio_hoje() -> str:
    dados = carregar_dados()
    agora = datetime.now(TZ)
    instalacoes_hoje: List[Dict[str, Any]] = []
    for inst in dados:
        try:
            data_inst = datetime.strptime(inst["data"], "%d/%m/%Y %H:%M")
            data_inst = data_inst.replace(tzinfo=TZ)
            if data_inst.date() == agora.date():
                instalacoes_hoje.append(inst)
        except:
            pass
    if not instalacoes_hoje:
        return "❌ Nenhuma instalação registrada hoje."
    por_tecnico = defaultdict(int)
    for inst in instalacoes_hoje:
        por_tecnico[inst["tecnico_nome"]] += 1
    msg = f"Relatório de Hoje {agora.strftime('%d/%m/%Y')}\nTotal {len(instalacoes_hoje)}\n\n"
    for tecnico, qtd in sorted(por_tecnico.items(), key=lambda x: x[1], reverse=True):
        msg += f"{tecnico}: {qtd}\n"
    return msg

def gerar_ranking_tecnicos() -> str:
    dados = carregar_dados()
    if not dados:
        return "❌ Nenhuma instalação registrada ainda."
    por_tecnico = defaultdict(int)
    for inst in dados:
        por_tecnico[inst["tecnico_nome"]] += 1
    msg = f"Ranking Geral\nTotal {len(dados)}\n\n"
    i = 1
    for tecnico, qtd in sorted(por_tecnico.items(), key=lambda x: x[1], reverse=True):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
        perc = (qtd / len(dados)) * 100
        msg += f"{medal} {tecnico}\n{qtd} instalações ({perc:.1f}%)\n\n"
        i += 1
    return msg
