from typing import Any, Dict, List, Optional
from supabase import create_client
from util import now_str
from config import SUPABASE_URL, SUPABASE_KEY, USE_SUPABASE

_CLIENT = None

def get_client():
    global _CLIENT
    if _CLIENT is None and USE_SUPABASE:
        _CLIENT = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _CLIENT

def carregar_dados() -> List[Dict[str, Any]]:
    sb = get_client()
    if not sb:
        return []
    try:
        r = sb.table("instalacoes").select("*").order("id", desc=False).execute()
        return r.data or []
    except:
        return []

def carregar_usuarios() -> Dict[str, Dict[str, Any]]:
    sb = get_client()
    if not sb:
        return {}
    try:
        r = sb.table("usuarios").select("*").order("id", desc=False).execute()
        out: Dict[str, Dict[str, Any]] = {}
        for row in r.data or []:
            uid = str(row.get("uid") or row.get("id") or "")
            if uid:
                out[uid] = {
                    "nome": row.get("nome") or "",
                    "sobrenome": row.get("sobrenome") or "",
                    "regiao": row.get("regiao") or "",
                    "telegram": row.get("telegram") or "",
                }
        return out
    except:
        return {}

def salvar_usuario(uid: str, dados: Dict[str, Any]) -> bool:
    sb = get_client()
    if not sb:
        return False
    try:
        row = {
            "uid": uid,
            "nome": dados.get("nome") or "",
            "sobrenome": dados.get("sobrenome") or "",
            "regiao": dados.get("regiao") or "",
            "telegram": dados.get("telegram") or "",
        }
        r = sb.table("usuarios").upsert(row).execute()
        return bool(r.data)
    except:
        return False

def salvar_instalacao(inst: Dict[str, Any]) -> bool:
    sb = get_client()
    if not sb:
        return False
    try:
        r = sb.table("instalacoes").insert(inst).execute()
        return bool(r.data)
    except:
        return False

def check_health() -> bool:
    sb = get_client()
    if not sb:
        return False
    try:
        sb.table("health").select("count(*)").limit(1).execute()
        return True
    except:
        return False
