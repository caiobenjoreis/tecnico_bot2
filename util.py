from datetime import datetime
from constants import TZ

def now_str() -> str:
    return datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
