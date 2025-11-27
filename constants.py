from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")

AGUARDANDO_SA, AGUARDANDO_GPON, AGUARDANDO_TIPO, AGUARDANDO_SERIAL, AGUARDANDO_FOTOS, AGUARDANDO_DATA_INICIO, AGUARDANDO_DATA_FIM, AGUARDANDO_NOME, AGUARDANDO_SOBRENOME, AGUARDANDO_REGIAO, AGUARDANDO_CONSULTA, AGUARDANDO_BROADCAST, AGUARDANDO_CONFIRMACAO_BROADCAST = range(13)

ADMIN_IDS = [1797158471]

PONTOS_SERVICO = {
    "defeito_banda_larga": 1.43,
    "defeito_linha": 1.43,
    "defeito_tv": 1.43,
    "instalacao": 2.28,
    "instalacao_tv": 3.58,
    "mudanca_endereco": 2.37,
    "retirada": 1.06,
    "servicos": 1.50,
    "servico": 1.50,
}

TABELA_FAIXAS = [
    {"min": 0.0, "max": 163.9, "faixa": "B", "valor": 3.10, "valor_turbo": 7.50},
    {"min": 164.0, "max": float("inf"), "faixa": "A", "valor": 3.20, "valor_turbo": 8.00},
]

