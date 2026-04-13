import time
import requests
from typing import Dict

cooldowns = {}
ALERT_THRESHOLD = 80  # %
TELEGRAM_TOKEN = "your_token"  # Optional
CHAT_ID = "your_chat_id"

def send_alert(message: str, method='print'):
    now = time.time()
    key = hash(message) % 10000
    if cooldowns.get(key, 0) + 300 > now:  # 5min cooldown
        return
    cooldowns[key] = now
    
    if method == 'print':
        print(f"[ALERT] {time.ctime()}: {message}")
    elif method == 'telegram':
        if TELEGRAM_TOKEN and CHAT_ID:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': message})

