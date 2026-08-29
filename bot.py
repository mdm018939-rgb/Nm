import os
import requests
import telebot
import re
import time
import threading
import html
from concurrent.futures import ThreadPoolExecutor
from telebot import types

# ──────────────────────────────────────────────────────────
# কনফিগারেশন
# ──────────────────────────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
API_KEY = "MINQWI3C03A"
# 🌍 লিঙ্কটি এখানে একদম সঠিক করে দেওয়া হলো
API_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api/getnum"
OTP_API_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api/success-otp"

# 🕒 Change Number কুলডাউন কনফিগারেশন
user_last_change = {}  # {user_id: timestamp} — কুলডাউন ট্র্যাক করার জন্য
waiting_users = set()
CHANGE_COOLDOWN = 6  # সেকেন্ড

# 🔒 ফোর্স জয়েন কনফিগারেশন
CHANNEL_ID = -1002969454179          # চ্যানেলের numeric chat_id (বট এই চ্যানেলে admin থাকতে হবে)
CHANNEL_LINK = "https://t.me/+LZrutZRrpbRkNDVl"
RANGE_GROUP_LINK = "https://t.me/+4cvfxQUawuVlZTI1"
LIVEACCESS_LINK = "https://t.me/+b7Wdq0OunollYmI1"
OTP_GROUP_LINK = "https://t.me/+7RobuqxsLhJlZDdl"
OTP_GROUP_ID = -1003449804166
SUPPORT_USERNAME = "TEEM_X_FAST_SUPPORT_BOT"

# 🔧 ফিক্স: ডিফল্ট num_threads=2 হওয়ায় একসাথে ২ জন GET NUMBER করলে বটের
# সব worker thread ব্লক হয়ে বাকিদের কাছে বট চুপ হয়ে যেত। থ্রেড পুল বাড়িয়ে দেওয়া হলো।
bot = telebot.TeleBot(BOT_TOKEN, num_threads=100)

# ──────────────────────────────────────────────────────────
# 🌍 Country Flag + Service Detect (নতুন ফিচার)
# ──────────────────────────────────────────────────────────
COUNTRY_FLAGS = {
    "1": ("🇺🇸", "US"), "20": ("🇪🇬", "EG"), "27": ("🇿🇦", "ZA"), "30": ("🇬🇷", "GR"), "31": ("🇳🇱", "NL"),
    "32": ("🇧🇪", "BE"), "33": ("🇫🇷", "FR"), "34": ("🇪🇸", "ES"), "36": ("🇭🇺", "HU"), "39": ("🇮🇹", "IT"),
    "40": ("🇷🇴", "RO"), "41": ("🇨🇭", "CH"), "43": ("🇦🇹", "AT"), "44": ("🇬🇧", "GB"), "45": ("🇩🇰", "DK"),
    "46": ("🇸🇪", "SE"), "47": ("🇳🇴", "NO"), "48": ("🇵🇱", "PL"), "49": ("🇩🇪", "DE"), "51": ("🇵🇪", "PE"),
    "52": ("🇲🇽", "MX"), "53": ("🇨🇺", "CU"), "54": ("🇦🇷", "AR"), "55": ("🇧🇷", "BR"), "56": ("🇨🇱", "CL"),
    "57": ("🇨🇴", "CO"), "58": ("🇻🇪", "VE"), "60": ("🇲🇾", "MY"), "61": ("🇦🇺", "AU"), "62": ("🇮🇩", "ID"),
    "63": ("🇵🇭", "PH"), "64": ("🇳🇿", "NZ"), "65": ("🇸🇬", "SG"), "66": ("🇹🇭", "TH"), "7": ("🇷🇺", "RU"),
    "81": ("🇯🇵", "JP"), "82": ("🇰🇷", "KR"), "84": ("🇻🇳", "VN"), "86": ("🇨🇳", "CN"), "90": ("🇹🇷", "TR"),
    "91": ("🇮🇳", "IN"), "92": ("🇵🇰", "PK"), "93": ("🇦🇫", "AF"), "94": ("🇱🇰", "LK"), "95": ("🇲🇲", "MM"),
    "98": ("🇮🇷", "IR"), "211": ("🇸🇸", "SS"), "212": ("🇲🇦", "MA"), "213": ("🇩🇿", "DZ"), "216": ("🇹🇳", "TN"),
    "218": ("🇱🇾", "LY"), "220": ("🇬🇲", "GM"), "221": ("🇸🇳", "SN"), "222": ("🇲🇷", "MR"), "223": ("🇲🇱", "ML"),
    "224": ("🇬🇳", "GN"), "225": ("🇨🇮", "CI"), "226": ("🇧🇫", "BF"), "227": ("🇳🇪", "NE"), "228": ("🇹🇬", "TG"),
    "229": ("🇧🇯", "BJ"), "230": ("🇲🇺", "MU"), "231": ("🇱🇷", "LR"), "232": ("🇸🇱", "SL"), "233": ("🇬🇭", "GH"),
    "234": ("🇳🇬", "NG"), "235": ("🇹🇩", "TD"), "236": ("🇨🇫", "CF"), "237": ("🇨🇲", "CM"), "238": ("🇨🇻", "CV"),
    "239": ("🇸🇹", "ST"), "240": ("🇬🇶", "GQ"), "241": ("🇬🇦", "GA"), "242": ("🇨🇬", "CG"), "243": ("🇨🇩", "CD"),
    "244": ("🇦🇴", "AO"), "245": ("🇬🇼", "GW"), "246": ("🇮🇴", "IO"), "248": ("🇸🇨", "SC"), "249": ("🇸🇩", "SD"),
    "250": ("🇷🇼", "RW"), "251": ("🇪🇹", "ET"), "252": ("🇸🇴", "SO"), "253": ("🇩🇯", "DJ"), "254": ("🇰🇪", "KE"),
    "255": ("🇹🇿", "TZ"), "256": ("🇺🇬", "UG"), "257": ("🇧🇮", "BI"), "258": ("🇲🇿", "MZ"), "260": ("🇿🇲", "ZM"),
    "261": ("🇲🇬", "MG"), "262": ("🇷🇪", "RE"), "263": ("🇿🇼", "ZW"), "264": ("🇳🇦", "NA"), "265": ("🇲🇼", "MW"),
    "266": ("🇱🇸", "LS"), "267": ("🇧🇼", "BW"), "268": ("🇸🇿", "SZ"), "269": ("🇰🇲", "KM"), "290": ("🇸🇭", "SH"),
    "291": ("🇪🇷", "ER"), "297": ("🇦🇼", "AW"), "298": ("🇫🇴", "FO"), "299": ("🇬🇱", "GL"), "350": ("🇬🇮", "GI"),
    "351": ("🇵🇹", "PT"), "352": ("🇱🇺", "LU"), "353": ("🇮🇪", "IE"), "354": ("🇮🇸", "IS"), "355": ("🇦🇱", "AL"),
    "356": ("🇲🇹", "MT"), "357": ("🇨🇾", "CY"), "358": ("🇫🇮", "FI"), "359": ("🇧🇬", "BG"), "370": ("🇱🇹", "LT"),
    "371": ("🇱🇻", "LV"), "372": ("🇪🇪", "EE"), "373": ("🇲🇩", "MD"), "374": ("🇦🇲", "AM"), "375": ("🇧🇾", "BY"),
    "376": ("🇦🇩", "AD"), "377": ("🇲🇨", "MC"), "378": ("🇸🇲", "SM"), "379": ("🇻🇦", "VA"), "380": ("🇺🇦", "UA"),
    "381": ("🇷🇸", "RS"), "382": ("🇲🇪", "ME"), "383": ("🇽🇰", "XK"), "385": ("🇭🇷", "HR"), "386": ("🇸🇮", "SI"),
    "387": ("🇧🇦", "BA"), "389": ("🇲🇰", "MK"), "420": ("🇨🇿", "CZ"), "421": ("🇸🇰", "SK"), "423": ("🇱🇮", "LI"),
    "500": ("🇫🇰", "FK"), "501": ("🇧🇿", "BZ"), "502": ("🇬🇹", "GT"), "503": ("🇸🇻", "SV"), "504": ("🇭🇳", "HN"),
    "505": ("🇳🇮", "NI"), "506": ("🇨🇷", "CR"), "507": ("🇵🇦", "PA"), "508": ("🇵🇲", "PM"), "509": ("🇭🇹", "HT"),
    "590": ("🇬🇵", "GP"), "591": ("🇧🇴", "BO"), "592": ("🇬🇾", "GY"), "593": ("🇪🇨", "EC"), "594": ("🇬🇫", "GF"),
    "595": ("🇵🇾", "PY"), "596": ("🇲🇶", "MQ"), "597": ("🇸🇷", "SR"), "598": ("🇺🇾", "UY"), "599": ("🇧🇶", "BQ"),
    "670": ("🇹🇱", "TL"), "673": ("🇧🇳", "BN"), "674": ("🇳🇷", "NR"), "675": ("🇵🇬", "PG"), "676": ("🇹🇴", "TO"),
    "677": ("🇸🇧", "SB"), "678": ("🇻🇺", "VU"), "679": ("🇫🇯", "FJ"), "680": ("🇵🇼", "PW"), "681": ("🇼🇫", "WF"),
    "682": ("🇨🇰", "CK"), "683": ("🇳🇺", "NU"), "685": ("🇼🇸", "WS"), "686": ("🇰🇮", "KI"), "687": ("🇳🇨", "NC"),
    "688": ("🇹🇻", "TV"), "689": ("🇵🇫", "PF"), "690": ("🇹🇰", "TK"), "691": ("🇫🇲", "FM"), "692": ("🇲🇭", "MH"),
    "850": ("🇰🇵", "KP"), "852": ("🇭🇰", "HK"), "853": ("🇲🇴", "MO"), "855": ("🇰🇭", "KH"), "856": ("🇱🇦", "LA"),
    "880": ("🇧🇩", "BD"), "886": ("🇹🇼", "TW"), "960": ("🇲🇻", "MV"), "961": ("🇱🇧", "LB"), "962": ("🇯🇴", "JO"),
    "963": ("🇸🇾", "SY"), "964": ("🇮🇶", "IQ"), "965": ("🇰🇼", "KW"), "966": ("🇸🇦", "SA"), "967": ("🇾🇪", "YE"),
    "968": ("🇴🇲", "OM"), "970": ("🇵🇸", "PS"), "971": ("🇦🇪", "AE"), "972": ("🇮🇱", "IL"), "973": ("🇧🇭", "BH"),
    "974": ("🇶🇦", "QA"), "975": ("🇧🇹", "BT"), "976": ("🇲🇳", "MN"), "977": ("🇳🇵", "NP"), "992": ("🇹🇯", "TJ"),
    "993": ("🇹🇲", "TM"), "994": ("🇦🇿", "AZ"), "995": ("🇬🇪", "GE"), "996": ("🇰🇬", "KG"), "998": ("🇺🇿", "UZ"),
    "1242": ("🇧🇸", "BS"), "1246": ("🇧🇧", "BB"), "1264": ("🇦🇮", "AI"), "1268": ("🇦🇬", "AG"), "1284": ("🇻🇬", "VG"),
    "1340": ("🇻🇮", "VI"), "1441": ("🇧🇲", "BM"), "1473": ("🇬🇩", "GD"), "1649": ("🇹🇨", "TC"), "1664": ("🇲🇸", "MS"),
    "1671": ("🇬🇺", "GU"), "1684": ("🇦🇸", "AS"), "1721": ("🇸🇽", "SX"), "1758": ("🇱🇨", "LC"), "1767": ("🇩🇲", "DM"),
    "1784": ("🇻🇨", "VC"), "1809": ("🇩🇴", "DO"), "1868": ("🇹🇹", "TT"), "1869": ("🇰🇳", "KN"), "1876": ("🇯🇲", "JM"),
    "1939": ("🇵🇷", "PR"),
}

def get_country_flag(phone_number):
    """নাম্বার থেকে দেশ কোড খুঁজে বের করে (ফ্ল্যাগ, ISO কোড) রিটার্ন করে"""
    for i in [4,3,2,1]:
        code = phone_number[:i]
        if code in COUNTRY_FLAGS:
            return COUNTRY_FLAGS[code]
    return ("🌍", "")

def detect_service(message):
    """OTP মেসেজ থেকে সেবার নাম শনাক্ত করে"""
    msg = message.lower()
    
    services = [
        ("Instagram", r"\b(instagram|ig|insta)\b"),
        ("Face-Book", r"\b(facebook|fb|meta)\b"),
        ("Messenger", r"\b(messenger)\b"),
        ("WhatsApp", r"\b(whatsapp|wa)\b"),
        ("Telegram", r"\b(telegram|tg)\b"),
        ("Discord", r"\b(discord)\b"),
        ("Google", r"\b(google|gmail|g-)\b"),
        ("TikTok", r"\b(tiktok)\b"),
        ("Twitter", r"\b(twitter|x\.com)\b"),
        ("Snapchat", r"\b(snapchat)\b"),
        ("Amazon", r"\b(amazon)\b"),
        ("PayPal", r"\b(paypal)\b"),
        ("Uber", r"\b(uber)\b"),
        ("Netflix", r"\b(netflix)\b"),
        ("Apple", r"\b(apple|icloud)\b"),
        ("Microsoft", r"\b(microsoft|outlook|hotmail|live)\b"),
        ("LinkedIn", r"\b(linkedin)\b"),
        ("Yahoo", r"\b(yahoo)\b"),
        ("Binance", r"\b(binance)\b"),
        ("Coinbase", r"\b(coinbase)\b"),
        ("Steam", r"\b(steam)\b"),
        ("PlayStation", r"\b(playstation|psn)\b"),
        ("Xbox", r"\b(xbox)\b"),
        ("Airbnb", r"\b(airbnb)\b"),
        ("Booking", r"\b(booking)\b"),
        ("Spotify", r"\b(spotify)\b"),
        ("LINE", r"\b(line)\b"),
        ("WeChat", r"\b(wechat)\b"),
        ("Viber", r"\b(viber)\b"),
        ("Signal", r"\b(signal)\b"),
    ]

    for name, pattern in services:
        if re.search(pattern, msg):
            return name

    return "Other"

# ──────────────────────────────────────────────────────────
# 🔑 OTP INBOX ফিচার — নতুন যোগ করা অংশ
# ──────────────────────────────────────────────────────────
active_numbers = {}        # { "447404333228": {"user_id": 123, "time": 169...} }
user_range_number = {}     # { (user_id, rid_input): "447404333228" } ← এই ইউজার এই রেঞ্জে এখন কোন নাম্বার নিয়ে আছে
otp_lock = threading.Lock()
seen_otp_ids = set()

def save_new_number(user_id, rid_input, number):
    """📱️ GET NUMBER থেকে কল হয়: নতুন নাম্বার যোগ হয়, আগের কোনো নাম্বার (অন্য রেঞ্জেরও) ডিলিট হয় না —
    একজন ইউজার একসাথে একাধিক রেঞ্জের নাম্বার সচল রাখতে পারবে।"""
    with otp_lock:
        active_numbers[number] = {"user_id": user_id, "time": time.time()}
        user_range_number[(user_id, rid_input)] = number

def replace_number_for_range(user_id, rid_input, number):
    """🔄 Change Number থেকে কল হয়: শুধুমাত্র এই *একই রেঞ্জের* আগের নাম্বারটা ডিলিট করে
    নতুনটা বসায় — অন্য কোনো রেঞ্জের সচল নাম্বার এতে প্রভাবিত হয় না।"""
    with otp_lock:
        key = (user_id, rid_input)
        old_number = user_range_number.get(key)
        if old_number and old_number in active_numbers:
            del active_numbers[old_number]
        active_numbers[number] = {"user_id": user_id, "time": time.time()}
        user_range_number[key] = number

def extract_otp_code(message_text):
    """OTP কোড বের করে (স্পেস/হাইফেন সহ বা ছাড়া, ৩-১০ ডিজিট পর্যন্ত, সবসময় একটানা সংখ্যা হিসেবে ফেরত দেয়)"""
    # কোড মাঝখানে স্পেস বা হাইফেন দিয়ে আলাদা থাকতে পারে (যেমন: 301 726 বা 404-793)
    # অথবা টানা সংখ্যা হতে পারে (৩ থেকে ১০ সংখ্যা পর্যন্ত)
    match = re.search(r'\b\d{2,5}[\s-]\d{2,5}\b|\b\d{3,10}\b', message_text)
    if match:
        # যেভাবেই আসুক, স্পেস/হাইফেন সরিয়ে একটানা সংখ্যা বানিয়ে ফেরত দেওয়া হচ্ছে
        return re.sub(r'[\s-]', '', match.group(0))
    return "N/A"

def poll_otps():
    """ব্যাকগ্রাউন্ড থ্রেড — প্রতি ২ সেকেন্ডে /success-otp চেক করে, allocate করা
    নাম্বারে OTP এলে সেই ইউজারকে সরাসরি DM করে পাঠিয়ে দেয়।"""
    headers = {
        "mauthapi": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    while True:
        try:
            response = requests.get(OTP_API_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("meta", {}).get("code") == 200:
                    otps = res_data.get("data", {}).get("otps", [])
                    for otp in otps:
                        otp_id = otp.get("otp_id")
                        number = str(otp.get("number", ""))
                        message_text = otp.get("message", "")

                        if not otp_id or otp_id in seen_otp_ids:
                            continue

                        with otp_lock:
                            entry = active_numbers.get(number)

                        if entry:
                            code = extract_otp_code(message_text)
                            service = detect_service(message_text)
                            flag = get_country_flag(number)[0]
                            
                            safe_service = html.escape(service)
                            safe_number = html.escape(number)
                            safe_flag = html.escape(flag)

                            otp_text = f"🔔 <b>Your OTP Received</b>\n\n📱 <b>{safe_service}</b> | <code>{safe_number}</code> | {safe_flag}"

                            otp_markup = types.InlineKeyboardMarkup()
                            key_button = types.InlineKeyboardButton(
                                text=f"{code}",
                                copy_text=types.CopyTextButton(text=code),
                                style="success"
                            )
                            full_msg_button = types.InlineKeyboardButton(
                                text="Full Message",
                                copy_text=types.CopyTextButton(text=message_text),
                                style="success"
                            )
                            otp_markup.row(key_button)
                            otp_markup.row(full_msg_button)

                            max_retries = 3
                            for attempt in range(max_retries):
                                try:
                                    bot.send_message(entry["user_id"], otp_text, parse_mode="HTML", reply_markup=otp_markup)
                                    print(f"✅ OTP পাঠানো হয়েছে ইউজার {entry['user_id']} কে, নাম্বার: {number}")
                                    break
                                except Exception as send_err:
                                    err_text = str(send_err)
                                    m = re.search(r"retry after (\d+)", err_text)
                                    if m:
                                        wait_s = int(m.group(1)) + 1
                                        print(f"⏳ Flood control — {wait_s}s অপেক্ষা (চেষ্টা {attempt+1}/{max_retries})")
                                        time.sleep(wait_s)
                                        continue
                                    else:
                                        print(f"⚠️ OTP পাঠাতে ব্যর্থ: {send_err}")
                                        break

                            # FIX (ইউজারের সাজেশন অনুযায়ী): প্রথম OTP পাঠানোর পরই entry মুছে
                            # ফেলা হচ্ছে না — একই নাম্বারে যদি ২০ মিনিটের মধ্যে আরও OTP আসে
                            # (resend, একাধিক সার্ভিস ইত্যাদি), সেগুলোও যেন ইউজার পায়।
                            # otp_id ভিত্তিক dedup আগে থেকেই আছে, তাই একই OTP দুইবার যাবে না।

                        seen_otp_ids.add(otp_id)

                    if len(seen_otp_ids) > 500:
                        for old_id in list(seen_otp_ids)[:200]:
                            seen_otp_ids.discard(old_id)
            else:
                print(f"⚠️ OTP API Status Error: {response.status_code}")

        except Exception as e:
            print(f"❌ OTP পোলিং এরর: {e}")

        # ২০ মিনিটের বেশি পুরোনো (OTP আসেনি এমন) entry মুছে ফেলা — মেমোরি ক্লিন রাখতে
        with otp_lock:
            cutoff = time.time() - 1200
            expired = [num for num, v in active_numbers.items() if v["time"] < cutoff]
            for num in expired:
                del active_numbers[num]
                # user_range_number থেকেও সংশ্লিষ্ট এন্ট্রি সরানো (যদি এখনও এই নাম্বারকেই পয়েন্ট করে)
                stale_keys = [k for k, v in user_range_number.items() if v == num]
                for k in stale_keys:
                    del user_range_number[k]

        time.sleep(2)
# ──────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────
# ফোর্স জয়েন হেল্পার ফাংশন
# ──────────────────────────────────────────────────────────
def is_user_joined(user_id):
    try:
        # Main Channel check
        member1 = bot.get_chat_member(CHANNEL_ID, user_id)
        main_joined = member1.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"⚠️ Main channel check এরর (user {user_id}): {e}")
        return True  # এরর হলে ব্লক না করে যেতে দেওয়া হচ্ছে, যাতে আসল জয়েন করা ইউজার আটকে না যায়
    
    try:
        # OTP Group check  
        member2 = bot.get_chat_member(OTP_GROUP_ID, user_id)
        otp_joined = member2.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"⚠️ OTP group check এরর (user {user_id}): {e}")
        return True
    
    # দুটোতেই join করেছে কিনা check
    return main_joined and otp_joined

def join_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Main Channel", url=CHANNEL_LINK, style="primary"))
    markup.add(types.InlineKeyboardButton("🔔 OTP Group", url=OTP_GROUP_LINK, style="primary"))
    markup.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify_join", style="success"))
    return markup

def send_join_prompt(chat_id):
    bot.send_message(
        chat_id,
        "⚠️ **Channel Join Needed!**\n\nPlease join the channels below and click Verify.",
        parse_mode="Markdown",
        reply_markup=join_keyboard()
    )

def send_join_prompt(chat_id):
    bot.send_message(
        chat_id,
        "⚠️ **Channel Join Needed!**\n\nPlease join the channel below and click Verify.",
        parse_mode="Markdown",
        reply_markup=join_keyboard()
    )

def send_welcome_menu(chat_id):
    bot.send_message(
        chat_id,
        "🔥 **WELCOME ** 🔥\n━━━━━━━━━━━━\nSelect Your Service From Below Button",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )

# প্রধান মেনু কিবোর্ড
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📱 GET NUMBER", style="success"), types.KeyboardButton("🔍 View Range", style="primary"))
    markup.add(types.KeyboardButton("💬 Support", style="danger"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_user_joined(message.from_user.id):
        send_welcome_menu(message.chat.id)
    else:
        send_join_prompt(message.chat.id)

# ✅ Verify বাটন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def handle_verify(call):
    if is_user_joined(call.from_user.id):
        bot.answer_callback_query(call.id, text="✅ Verified!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_welcome_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, text="❌ You haven't joined the channel yet!", show_alert=True)

# বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # 🔒 প্রতিটা বাটন অ্যাকশনের আগে চ্যানেল জয়েন চেক
    if message.text in ("📱 GET NUMBER", "🔍 View Range", "💬 Support"):
        if not is_user_joined(message.from_user.id):
            send_join_prompt(message.chat.id)
            return

    if message.text == "📱 GET NUMBER":
        if message.from_user.id in waiting_users:
            return
        waiting_users.add(message.from_user.id)
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(
            message.chat.id,
            "🔍 Click **View Range**, copy a range, then send it here 👇\n"
            "⌨️ E.G. `123456XXX`",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_range)
        
    elif message.text == "🔍 View Range":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📊 Live access", url=LIVEACCESS_LINK, style="primary"),
            types.InlineKeyboardButton("🎯 Range Group", url=RANGE_GROUP_LINK, style="success")
        )
        bot.send_message(message.chat.id, "👇 **Click the button below to view active ranges:**", parse_mode="Markdown", reply_markup=markup)
        
    elif message.text == "💬 Support":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Support", url=f"https://t.me/TEEM_X_FAST_SUPPORT_BOT", style="success"))
        bot.send_message(
            message.chat.id,
            "আমাদের সাপোর্ট টিমের সাথে যোগাযোগ করতে নিচের বাটনে ক্লিক করুন:",
            reply_markup=markup
        )

# নাম্বার তুলে আনার মেইন ফাংশন
def request_number(rid_input, max_retries=10, retry_delay=1):
    headers = {
        "mauthapi": API_KEY, 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json={"rid": rid_input}, headers=headers, timeout=12)
            if response.status_code == 200:
                data = response.json()
                if data.get("meta", {}).get("code") == 200:
                    print(f"✅ চেষ্টা {attempt+1}/{max_retries}-এ সফল হয়েছে")
                    return data
            print(f"⚠️ চেষ্টা {attempt+1}/{max_retries} ব্যর্থ (status: {response.status_code})")
        except Exception as e:
            print(f"⚠️ চেষ্টা {attempt+1}/{max_retries} এরর: {e}")

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    print(f"❌ {max_retries} বার চেষ্টার পরও ব্যর্থ")
    return None

# 🔧 ফিক্স: আগে data ও data2 সিরিয়ালি (একটার পর একটা) নেওয়া হতো, যাতে সময় দ্বিগুণ লাগতো।
# এখন দুইটা রিকোয়েস্ট একসাথে (parallel) পাঠানো হচ্ছে, তাই মোট সময় কমে যাবে।
def request_two_numbers_parallel(rid_input):
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(request_number, rid_input)
        f2 = executor.submit(request_number, rid_input)
        return f1.result(), f2.result()

def process_range(message):
    waiting_users.discard(message.from_user.id)
    if message.chat.type != "private":
        return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Please send the range ID as text (e.g., 123456XXX).", reply_markup=main_keyboard())
        return
    if message.text == "/start":
        send_welcome(message)
        return
    if message.text in ("📱 GET NUMBER", "🔍 View Range","💬 Support"):
        handle_text(message)
        return

    # 🔧 ফিক্স: আগে re.sub(r'\D','',...) দিয়ে X অক্ষরগুলো বাদ পড়ে যেত (যেমন "123456XXX" → "123456")।
    # এখন ইউজার যেভাবে রেঞ্জ টাইপ করবে (X যত সংখ্যাই থাকুক), সেটা অবিকৃতভাবেই API-তে rid হিসেবে পাঠানো হবে।
    rid_input = message.text.strip()
    
    if not rid_input:
        bot.send_message(message.chat.id, "❌ Please enter a range ID!")
        return
    
    # ✅ নতুন Validation: Range ID Format Check
    # ফরম্যাট: ডিজিট ৩+ টা, তারপর X মিনিমাম ৩টা
    # উদাহরণ: ✅ 224655XXX, ✅ 224655XXXX, ❌ 224655XX, ❌ 224655XXXabc
    if not re.match(r'^[\d]{3,}[X]{3,}$', rid_input, re.IGNORECASE):
        bot.send_message(
            message.chat.id,
            "❌ Wrong input! Please enter correct range ID.",
            reply_markup=main_keyboard()
        )
        return

    loading = bot.send_message(message.chat.id, "🔍 Searching for a number, please wait...")

    # 🔧 ফিক্স: এই ধীরগতির (ব্লকিং) কাজটা bot-এর সীমিত worker thread pool-এ না চালিয়ে
    # আলাদা background thread-এ চালানো হচ্ছে। এতে handler সাথে সাথে thread ছেড়ে দেয়,
    # তাই একই সময়ে অন্য ইউজারদের মেসেজ/বাটন ক্লিক প্রসেস হতে বাধা পায় না।
    threading.Thread(
        target=_fetch_and_send_number,
        args=(message.chat.id, message.from_user.id, rid_input, loading.message_id),
        daemon=True
    ).start()

def _fetch_and_send_number(chat_id, user_id, rid_input, loading_message_id):
    try:
        data, data2 = request_two_numbers_parallel(rid_input)
    except Exception as e:
        print(f"❌ _fetch_and_send_number এরর: {e}")
        try:
            bot.delete_message(chat_id, loading_message_id)
        except:
            pass
        bot.send_message(chat_id, "❌ Something went wrong. Please try again.")
        return

    if data and data.get("meta", {}).get("code") == 200:
        num_data = data["data"]
        num_data2 = data2["data"] if data2 and data2.get("meta", {}).get("code") == 200 else None
        save_new_number(user_id, rid_input, num_data.get("no_plus_number", ""))
        if num_data2:
            save_new_number(user_id, rid_input + "_2", num_data2.get("no_plus_number", ""))
        result_text = (
            f"✅ **Number Assigned Successfully!**\n\n"
            f"🌐 **Country:** {get_country_flag(num_data.get('no_plus_number', ''))[0]} {num_data.get('country')} ({get_country_flag(num_data.get('no_plus_number', ''))[1]})\n"
            f"🎯 **Range:** `{rid_input}`\n\n"
            f"🌀 **OTP Forwarded Automatically."
        )
        markup = types.InlineKeyboardMarkup()
        full_num = num_data.get('full_number') or num_data.get('no_plus_number', 'N/A')
        markup.add(types.InlineKeyboardButton(
            text=full_num,
            copy_text=types.CopyTextButton(text=full_num),
            style="success"
        ))
        if num_data2:
            full_num2 = num_data2.get('full_number') or num_data2.get('no_plus_number', 'N/A')
            markup.add(types.InlineKeyboardButton(
                text=full_num2,
                copy_text=types.CopyTextButton(text=full_num2),
                style="success"
            ))
        markup.row(
            types.InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{rid_input}", style="primary")
        )
        markup.row(
            types.InlineKeyboardButton("🔔 OTP GROUP", url=OTP_GROUP_LINK, style="danger")
        )

        bot.delete_message(chat_id, loading_message_id)
        bot.send_message(chat_id, result_text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.delete_message(chat_id, loading_message_id)
        bot.send_message(chat_id, "❌ No numbers available in this range. Try a different range.", reply_markup=main_keyboard())

# 🔥 Change Number ইনলাইন বাটন ক্লিকের হ্যান্ডলার (মেসেজ এডিট হবে)
@bot.callback_query_handler(func=lambda call: call.data.startswith("change_"))
def handle_change_number(call):
    user_id = call.from_user.id
    now = time.time()
    last_time = user_last_change.get(user_id, 0)

    if now - last_time < CHANGE_COOLDOWN:
        remaining = round(CHANGE_COOLDOWN - (now - last_time), 1)
        bot.answer_callback_query(call.id, text=f"⏳ Try again after {remaining} seconds.", show_alert=True)
        return

    user_last_change[user_id] = now

    rid_input = call.data.split("_")[1]

    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    loading = bot.send_message(call.message.chat.id, "⏳ Requesting change number...")

    # 🔧 ফিক্স: এখানেও একই কারণে ভারী কাজটা background thread-এ সরানো হলো,
    # যাতে Change Number চাপলেও worker thread আটকে না থাকে।
    threading.Thread(
        target=_fetch_and_send_changed_number,
        args=(call.from_user.id, rid_input, call.message.chat.id, loading.message_id),
        daemon=True
    ).start()

def _fetch_and_send_changed_number(user_id, rid_input, chat_id, message_id):
    try:
        data, data2 = request_two_numbers_parallel(rid_input)
    except Exception as e:
        print(f"❌ _fetch_and_send_changed_number এরর: {e}")
        try:
            bot.edit_message_text("❌ Something went wrong. Please try again.", chat_id=chat_id, message_id=message_id)
        except:
            pass
        return

    if data and data.get("meta", {}).get("code") == 200:
        num_data = data["data"]
        num_data2 = data2["data"] if data2 and data2.get("meta", {}).get("code") == 200 else None
        replace_number_for_range(user_id, rid_input, num_data.get("no_plus_number", ""))
        if num_data2:
            replace_number_for_range(user_id, rid_input + "_2", num_data2.get("no_plus_number", ""))
        updated_text = (
            f"✅ **Numbers Changed Successfully!**\n\n"
            f"🌐 **Country:** {get_country_flag(num_data.get('no_plus_number', ''))[0]} {num_data.get('country')} ({get_country_flag(num_data.get('no_plus_number', ''))[1]})\n"
            f"🎯 **Range:** `{rid_input}`\n\n"
            f"🌀 **OTP Forwarded Automatically."
        )
        markup = types.InlineKeyboardMarkup()
        full_num = num_data.get('full_number') or num_data.get('no_plus_number', 'N/A')
        markup.add(types.InlineKeyboardButton(
            text=full_num,
            copy_text=types.CopyTextButton(text=full_num),
            style="success"
        ))
        if num_data2:
            full_num2 = num_data2.get('full_number') or num_data2.get('no_plus_number', 'N/A')
            markup.add(types.InlineKeyboardButton(
                text=full_num2,
                copy_text=types.CopyTextButton(text=full_num2),
                style="success"
            ))
        markup.row(
            types.InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{rid_input}", style="primary")
        )
        markup.row(
            types.InlineKeyboardButton("🔔 OTP GROUP", url=OTP_GROUP_LINK, style="danger")
        )

        bot.edit_message_text(updated_text, chat_id=chat_id, message_id=message_id, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.delete_message(chat_id, message_id)
        bot.send_message(
            chat_id,
            "❌ Sorry, no numbers available in this range. Try a different range.",
            reply_markup=main_keyboard()
        )

# 🔑 OTP INBOX: ব্যাকগ্রাউন্ড থ্রেড চালু করা হচ্ছে, এটাই OTP চেক করে DM পাঠাবে
threading.Thread(target=poll_otps, daemon=True).start()

def run_keep_alive_server():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class PingHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")

        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

        def log_message(self, format, *args):
            pass

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()


threading.Thread(target=run_keep_alive_server, daemon=True).start()
bot.infinity_polling()