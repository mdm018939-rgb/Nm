import os
import requests
import telebot
import re
import time
import threading
import html
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
CHANGE_COOLDOWN = 8  # সেকেন্ড

# 🔒 ফোর্স জয়েন কনফিগারেশন
CHANNEL_ID = -1002969454179          # চ্যানেলের numeric chat_id (বট এই চ্যানেলে admin থাকতে হবে)
CHANNEL_LINK = "https://t.me/+LZrutZRrpbRkNDVl"
RANGE_GROUP_LINK = "https://t.me/+4cvfxQUawuVlZTI1"
LIVEACCESS_LINK = "https://t.me/+b7Wdq0OunollYmI1"
OTP_GROUP_LINK = "https://t.me/+7RobuqxsLhJlZDdl"
OTP_GROUP_ID = -1003449804166
SUPPORT_USERNAME = "TEEM_X_FAST_SUPPORT_BOT"

bot = telebot.TeleBot(BOT_TOKEN)

# ──────────────────────────────────────────────────────────
# 🌍 Country Flag + Service Detect (নতুন ফিচার)
# ──────────────────────────────────────────────────────────
COUNTRY_FLAGS = {
    "1": "🇺🇸", "20": "🇪🇬", "27": "🇿🇦", "30": "🇬🇷", "31": "🇳🇱", 
    "32": "🇧🇪", "33": "🇫🇷", "34": "🇪🇸", "36": "🇭🇺", "39": "🇮🇹", 
    "40": "🇷🇴", "41": "🇨🇭", "43": "🇦🇹", "44": "🇬🇧", "45": "🇩🇰", 
    "46": "🇸🇪", "47": "🇳🇴", "48": "🇵🇱", "49": "🇩🇪", "51": "🇵🇪", 
    "52": "🇲🇽", "53": "🇨🇺", "54": "🇦🇷", "55": "🇧🇷", "56": "🇨🇱", 
    "57": "🇨🇴", "58": "🇻🇪", "60": "🇲🇾", "61": "🇦🇺", "62": "🇮🇩", 
    "63": "🇵🇭", "64": "🇳🇿", "65": "🇸🇬", "66": "🇹🇭", "7": "🇷🇺", # ৭ দিয়ে রাশিয়া ও কাজাখস্তান দুটিই ট্র্যাক হয়, আমরা গ্লোবাল রাখলাম
    "81": "🇯🇵", "82": "🇰🇷", "84": "🇻🇳", "86": "🇨🇳", "90": "🇹🇷", 
    "91": "🇮🇳", "92": "🇵🇰", "93": "🇦🇫", "94": "🇱🇰", "95": "🇲🇲", 
    "98": "🇮🇷", "211": "🇸🇸", "212": "🇲🇦", "213": "🇩🇿", "216": "🇹🇳", 
    "218": "🇱🇾", "220": "🇬🇲", "221": "🇸🇳", "222": "🇲🇷", "223": "🇲🇱", 
    "224": "🇬🇳", "225": "🇨🇮", "226": "🇧🇫", "227": "🇳🇪", "228": "🇹🇬", 
    "229": "🇧🇯", "230": "🇲🇺", "231": "🇱🇷", "232": "🇸🇱", "233": "🇬🇭", 
    "234": "🇳🇬", "235": "🇹🇩", "236": "🇨🇫", "237": "🇨🇲", "238": "🇨🇻", 
    "239": "🇸🇹", "240": "🇬🇶", "241": "🇬🇦", "242": "🇨🇬", "243": "🇨🇩", 
    "244": "🇦🇴", "245": "🇬🇼", "246": "🇮🇴", "248": "🇸🇨", "249": "🇸🇩", 
    "250": "🇷🇼", "251": "🇪🇹", "252": "🇸🇴", "253": "🇩🇯", "254": "🇰🇪", 
    "255": "🇹🇿", "256": "🇺🇬", "257": "🇧🇮", "258": "🇲🇿", "260": "🇿🇲", 
    "261": "🇲🇬", "262": "🇷🇪", "263": "🇿🇼", "264": "🇳🇦", "265": "🇲🇼", 
    "266": "🇱🇸", "267": "🇧🇼", "268": "🇸🇿", "269": "🇰🇲", "290": "🇸🇭", 
    "291": "🇪🇷", "297": "🇦🇼", "298": "🇫🇴", "299": "🇬🇱", "350": "🇬🇮", 
    "351": "🇵🇹", "352": "🇱🇺", "353": "🇮🇪", "354": "🇮🇸", "355": "🇦🇱", 
    "356": "🇲🇹", "357": "🇨🇾", "358": "🇫🇮", "359": "🇧🇬", "370": "🇱🇹", 
    "371": "🇱🇻", "372": "🇪🇪", "373": "🇲🇩", "374": "🇦🇲", "375": "🇧🇾", 
    "376": "🇦🇩", "377": "🇲🇨", "378": "🇸🇲", "379": "🇻🇦", "380": "🇺🇦", 
    "381": "🇷🇸", "385": "🇭🇷", "386": "🇸🇮", "387": "🇧🇦", "389": "🇲🇰", 
     "420": "🇨🇿", "421": "🇸🇰", "423": "🇱🇮", "500": "🇫🇰", 
    "501": "🇧🇿", "502": "🇬🇹", "503": "🇸🇻", "504": "🇭🇳", "505": "🇳🇮", 
    "506": "🇨🇷", "507": "🇵🇦", "508": "🇵🇲", "509": "🇭🇹", "590": "🇬🇵", 
    "591": "🇧🇴", "592": "🇬🇾", "593": "🇪🇨", "594": "🇬🇫", "595": "🇵🇾", 
    "596": "🇲🇶", "597": "🇸🇷", "598": "🇺🇾", "599": "🇧🇶", "670": "🇹🇱", 
    "673": "🇧🇳", "674": "🇳🇷", "675": "🇵🇬", "676": "🇹🇴", "677": "🇸🇧", 
    "678": "🇻🇺", "679": "🇫🇯", "680": "🇵🇼", "681": "🇼🇫", "682": "🇨🇰", 
    "683": "🇳🇺", "685": "🇼🇸", "686": "🇰🇮", "687": "🇳🇨", "688": "🇹🇻", 
    "689": "🇵🇫", "690": "🇹🇰", "691": "🇫🇲", "692": "🇲🇭", "850": "🇰🇵", 
    "852": "🇭🇰", "853": "🇲🇴", "855": "🇰🇭", "856": "🇱🇦", "880": "🇧🇩", 
    "886": "🇹🇼", "960": "🇲🇻", "961": "🇱🇧", "962": "🇯🇴", "963": "🇸🇾", 
    "964": "🇮🇶", "965": "🇰🇼", "966": "🇸🇦", "967": "🇾🇪", "968": "🇴🇲", 
    "970": "🇵🇸", "971": "🇦🇪", "972": "🇮🇱", "973": "🇧🇭", "974": "🇶🇦", 
    "975": "🇧🇹", "976": "🇲🇳", "977": "🇳🇵", "992": "🇹🇯", "993": "🇹🇲", 
    "994": "🇦🇿", "995": "🇬🇪", "996": "🇰🇬", "998": "🇺🇿", "1242": "🇧🇸", 
    "1246": "🇧🇧", "1264": "🇦🇮", "1268": "🇦🇬", "1284": "🇻🇬", "1340": "🇻🇮", 
    "1441": "🇧🇲", "1473": "🇬🇩", "1649": "🇹🇨", "1664": "🇲🇸", "1671": "🇬🇺", 
    "1684": "🇦🇸", "1721": "🇸🇽", "1758": "🇱🇨", "1767": "🇩🇲", "1784": "🇻🇨", 
    "1809": "🇩🇴", "1868": "🇹🇹", "1869": "🇰🇳", "1876": "🇯🇲", "1939": "🇵🇷"
}

def get_country_flag(phone_number):
    """নাম্বার থেকে দেশ কোড খুঁজে বের করে ফ্ল্যাগ রিটার্ন করে"""
    for i in [4,3,2,1]:
        code = phone_number[:i]
        if code in COUNTRY_FLAGS:
            return COUNTRY_FLAGS[code]
    return "🌍"

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
    """🛍️ GET NUMBER থেকে কল হয়: নতুন নাম্বার যোগ হয়, আগের কোনো নাম্বার (অন্য রেঞ্জেরও) ডিলিট হয় না —
    একজন ইউজার একসাথে একাধিক রেঞ্জের নাম্বার সচল রাখতে পারবে।"""
    with otp_lock:
        active_numbers[number] = {"user_id": user_id, "time": time.time()}
        user_range_number[(user_id, rid_input)] = number

def replace_number_for_range(user_id, rid_input, number):
    """🔥 Change Number থেকে কল হয়: শুধুমাত্র এই *একই রেঞ্জের* আগের নাম্বারটা ডিলিট করে
    নতুনটা বসায় — অন্য কোনো রেঞ্জের সচল নাম্বার এতে প্রভাবিত হয় না।"""
    with otp_lock:
        key = (user_id, rid_input)
        old_number = user_range_number.get(key)
        if old_number and old_number in active_numbers:
            del active_numbers[old_number]
        active_numbers[number] = {"user_id": user_id, "time": time.time()}
        user_range_number[key] = number

def extract_otp_code(message_text):
    """OTP কোড বের করে (স্পেস সহ বা ছাড়া, 3-8 ডিজিট পর্যন্ত)"""
    # 301 726 এর মতো OTP (স্পেস সহ)
    spaced_match = re.search(r'\b\d{3}\s\d{3}\b', message_text)
    if spaced_match:
        return spaced_match.group(0)

    # 123, 1234, 12345, 123456, 1234567, 12345678
    match = re.search(r'\b\d{3,8}\b', message_text)
    if match:
        return match.group(0)

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
                            flag = get_country_flag(number)
                            
                            safe_service = html.escape(service)
                            safe_number = html.escape(number)
                            safe_flag = html.escape(flag)
                            safe_code = html.escape(code)
                            
                            otp_text = (
    f"📱 <b>{safe_service}</b> | <code>{safe_number}</code> | {safe_flag}\n"
    f"🔑 <b>Key:</b> <code>{safe_code}</code>"
)

                            max_retries = 3
                            for attempt in range(max_retries):
                                try:
                                    bot.send_message(entry["user_id"], otp_text, parse_mode="HTML")
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
    except:
        main_joined = False
    
    try:
        # OTP Group check  
        member2 = bot.get_chat_member(OTP_GROUP_ID, user_id)
        otp_joined = member2.status in ("member", "administrator", "creator")
    except:
        otp_joined = False
    
    # দুটোতেই join করেছে কিনা check
    return main_joined and otp_joined

def join_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Main Channel", url=CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton("👑 OTP Group", url=OTP_GROUP_LINK))
    markup.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
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
    markup.add(types.KeyboardButton("🛍️ GET NUMBER"), types.KeyboardButton("📊 View Range"))
    markup.add(types.KeyboardButton("👨‍💻 Support"))
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
    if message.text in ("🛍️ GET NUMBER", "📊 View Range", "👨‍💻 Support"):
        if not is_user_joined(message.from_user.id):
            send_join_prompt(message.chat.id)
            return

    if message.text == "🛍️ GET NUMBER":
        msg = bot.send_message(message.chat.id, "⌨️ **Enter Range ID (e.g., 123456XXX):**", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_range)
        
    elif message.text == "📊 View Range":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📊 Live access", url=LIVEACCESS_LINK),
            types.InlineKeyboardButton("🔗 Range Group", url=RANGE_GROUP_LINK)
        )
        bot.send_message(message.chat.id, "👇 **Click the button below to view active ranges:**", parse_mode="Markdown", reply_markup=markup)
        
    elif message.text == "👨‍💻 Support":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👨‍💻 Support", url=f"https://t.me/TEEM_X_FAST_SUPPORT_BOT"))
        bot.send_message(
            message.chat.id,
            "আমাদের সাপোর্ট টিমের সাথে যোগাযোগ করতে নিচের বাটনে ক্লিক করুন:",
            reply_markup=markup
        )

# নাম্বার তুলে আনার মেইন ফাংশন
def request_number(rid_input):
    headers = {
        "mauthapi": API_KEY, 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.post(API_URL, json={"rid": rid_input}, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API Error: {e}")
    return None

def process_range(message):
    # 🔒 ফিক্স: ইউজার যদি রেঞ্জ আইডি না দিয়ে মেনু বাটন চাপে (Support/View Range/GET NUMBER আবার),
    # তাহলে সেটাকে ভুল ইনপুট না ধরে, স্বাভাবিক মেনু হ্যান্ডলারে পাঠিয়ে দাও
    if message.text in ("🛍️ GET NUMBER", "📊 View Range", "👨‍💻 Support"):
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
            "❌ Wrong input! Please enter correct range ID."
        )
        return

    loading = bot.send_message(message.chat.id, "🔍 Searching for a number, please wait...")
    
    data = request_number(rid_input)
    
    if data and data.get("meta", {}).get("code") == 200:
        num_data = data["data"]
        # 🔑 OTP INBOX: এই নাম্বারটা যোগ হচ্ছে, অন্য কোনো রেঞ্জের সচল নাম্বার ডিলিট হবে না
        save_new_number(message.from_user.id, rid_input, num_data.get("no_plus_number", ""))
        result_text = (
            f"✅ **Number Assigned Successfully!**\n\n"
            f"📊 **Range:** `{rid_input}`\n"
            f"🌐 **Country:** {num_data.get('country')}\n"
            f"📞 **Number:** `{num_data.get('full_number')}`\n\n"
            f"📬 **Keys forwarded automatically."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔥 Change Number", callback_data=f"change_{rid_input}"))
        markup.row(
            types.InlineKeyboardButton("📊 Live access", url=LIVEACCESS_LINK),
            types.InlineKeyboardButton("🔗 Range Group", url=RANGE_GROUP_LINK)
        )
        markup.add(types.InlineKeyboardButton("👑 OTP GROUP", url=OTP_GROUP_LINK))
        
        bot.delete_message(message.chat.id, loading.message_id)
        bot.send_message(message.chat.id, result_text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.delete_message(message.chat.id, loading.message_id)
        bot.send_message(message.chat.id, "❌ No numbers available in this range. Try a different range.")

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
    
    # ইনলাইন বাটনের উপরে ছোট্ট লোডিং টেক্সট দেখাবে
    bot.answer_callback_query(call.id, text="🔄 Fetching new number...")
    
    data = request_number(rid_input)
    
    if data and data.get("meta", {}).get("code") == 200:
        num_data = data["data"]
        # 🔑 OTP INBOX: শুধু এই একই রেঞ্জের পুরোনো নাম্বার সরিয়ে নতুনটা বসানো হচ্ছে (অন্য রেঞ্জ অক্ষত থাকবে)
        replace_number_for_range(call.from_user.id, rid_input, num_data.get("no_plus_number", ""))
        updated_text = (
            f"✅ **Numbers Changed Successfully!**\n\n"
            f"📊 **Range:** `{rid_input}`\n"
            f"🌐 **Country:** {num_data.get('country')}\n"
            f"📞 **Number:** `{num_data.get('full_number')}`\n\n"
            f"📬 **Keys forwarded automatically."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔥 Change Number", callback_data=f"change_{rid_input}"))
        markup.row(
            types.InlineKeyboardButton("📊 Live access", url=LIVEACCESS_LINK),
            types.InlineKeyboardButton("🔗 Range Group", url=RANGE_GROUP_LINK)
        )
        markup.add(types.InlineKeyboardButton("👑 OTP GROUP", url=OTP_GROUP_LINK))
        
        bot.edit_message_text(updated_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, text="❌ No numbers available for this range!", show_alert=True)

# 🔑 OTP INBOX: ব্যাকগ্রাউন্ড থ্রেড চালু করা হচ্ছে, এটাই OTP চেক করে DM পাঠাবে
threading.Thread(target=poll_otps, daemon=True).start()

def run_keep_alive_server():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class PingHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")

        def log_message(self, format, *args):
            pass

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()


threading.Thread(target=run_keep_alive_server, daemon=True).start()
bot.infinity_polling()
