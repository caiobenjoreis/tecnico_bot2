import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

def _clean_token(s: str) -> str:
    s = s.strip()
    for ch in ("`", '"', "'", "\r", "\n"):
        s = s.replace(ch, "")
    return s

def get_token() -> str:
    t = os.getenv("TELEGRAM_TOKEN")
    if t:
        return _clean_token(t)
    for p in ("/etc/secrets/TELEGRAM_TOKEN", "TELEGRAM_TOKEN"):
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    c = _clean_token(f.read())
                    if c:
                        return c
        except:
            pass
    raise RuntimeError("TELEGRAM_TOKEN não definido nas variáveis de ambiente ou secret file")

