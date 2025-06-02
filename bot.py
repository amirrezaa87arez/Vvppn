import telebot
from telebot import types
import os
import json

# دریافت توکن و آیدی ادمین‌ها از ENV
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")
CARD_NUMBER = os.getenv("CARD_NUMBER", "6277-6013-6877-6066")
CARD_OWNER = os.getenv("CARD_OWNER", "رضوانی")

bot = telebot.TeleBot(TOKEN)

USERS_FILE = 'users.json'
PLANS_FILE = 'plans.json'

# لود یا ساخت لیست کاربران
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def get_or_create_user_id(telegram_id):
    users = load_users()
    for uid, tid in users.items():
        if tid == telegram_id:
            return uid
    new_id = str(1000 + len(users) + 1)
    users[new_id] = telegram_id
    save_users(users)
    return new_id

# لود پلن‌ها
def load_plans():
    if not os.path.exists(PLANS_FILE):
        default_plans = {
            "1": {"title": "تک کاربره یک ماهه", "price": "85 تومن", "duration": "1 ماه", "users": "1"},
            "2": {"title": "دو کاربره یک ماهه", "price": "115 تومن", "duration": "1 ماه", "users": "2"},
            "3": {"title": "سه کاربره یک ماهه", "price": "169 تومن", "duration": "1 ماه", "users": "3"},
            "4": {"title": "تک کاربره دو ماهه", "price": "140 تومن", "duration": "2 ماه", "users": "1"},
            "5": {"title": "دو کاربره دو ماهه", "price": "165 تومن", "duration": "2 ماه", "users": "2"},
            "6": {"title": "سه کاربره دو ماهه", "price": "185 تومن", "duration": "2 ماه", "users": "3"},
            "7": {"title": "تک کاربره سه ماهه", "price": "174 تومن", "duration": "3 ماه", "users": "1"},
            "8": {"title": "دو کاربره سه ماهه", "price": "234 تومن", "duration": "3 ماه", "users": "2"},
            "9": {"title": "سه کاربره سه ماهه", "price": "335 تومن", "duration": "3 ماه", "users": "3"}
        }
        with open(PLANS_FILE, 'w') as f:
            json.dump(default_plans, f, ensure_ascii=False)
    with open(PLANS_FILE, 'r') as f:
        return json.load(f)

# منوی اصلی
def main_menu(is_admin=False):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💳 خرید اشتراک", "📘 آموزش اتصال")
    kb.row("🛠 پشتیبانی")
    if is_admin:
        kb.row("📤 ارسال کانفیگ", "🛎 اطلاع‌رسانی")
        kb.row("✏️ ویرایش پلن", "➕ افزودن ادمین")
    return kb

# هندلر استارت
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = get_or_create_user_id(message.from_user.id)
    is_admin = str(message.from_user.id) in ADMIN_IDS
    bot.send_message(message.chat.id, f"🌟 خوش آمدید!\nآیدی عددی شما: {user_id}", reply_markup=main_menu(is_admin))

# هندلر آموزش اتصال
@bot.message_handler(func=lambda m: m.text == "📘 آموزش اتصال")
def handle_amozesh(message):
    bot.send_message(message.chat.id, "📘 آموزش اتصال:\nhttps://t.me/amuzesh_dragonvpn")

# هندلر پشتیبانی
@bot.message_handler(func=lambda m: m.text == "🛠 پشتیبانی")
def handle_support(message):
    bot.send_message(message.chat.id, "🔧 پشتیبانی:\n@Psycho_remix1")

# هندلر خرید اشتراک
@bot.message_handler(func=lambda m: m.text == "💳 خرید اشتراک")
def handle_buy(message):
    plans = load_plans()
    kb = types.InlineKeyboardMarkup()
    for pid, p in plans.items():
        kb.add(types.InlineKeyboardButton(f"{pid}️⃣ {p['title']} - {p['price']}", callback_data=f"buy_{pid}"))
    bot.send_message(message.chat.id, "💳 لطفاً یکی از پلن‌ها را انتخاب کنید:", reply_markup=kb)

# کال‌بک پلن انتخابی
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_plan_selection(call):
    plan_id = call.data.split("_")[1]
    plans = load_plans()
    plan = plans.get(plan_id)
    if not plan:
        bot.answer_callback_query(call.id, "❌ پلن نامعتبر است.")
        return
    info = f"""📦 پلن انتخابی شما:

✅ نام پلن: {plan['title']}
⏳ مدت: {plan['duration']}
👥 تعداد کاربران: {plan['users']}
💰 قیمت: {plan['price']}

💳 شماره کارت: {CARD_NUMBER}
🔹 به نام: {CARD_OWNER}

لطفاً پس از واریز، فیش را برای بررسی ارسال کنید.
"""
    bot.send_message(call.message.chat.id, info)

# دریافت فیش و ارسال به مدیر
@bot.message_handler(content_types=['photo', 'document'])
def handle_receipt(message):
    user_id = get_or_create_user_id(message.from_user.id)
    caption = f"🧾 کاربر با آیدی عددی {user_id} یک فیش ارسال کرد."
    if message.content_type == 'photo':
        for admin_id in ADMIN_IDS:
            bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption)
    elif message.content_type == 'document':
        for admin_id in ADMIN_IDS:
            bot.send_document(admin_id, message.document.file_id, caption=caption)
    bot.reply_to(message, "✅ فیش دریافت شد. لطفاً منتظر بررسی توسط ادمین باشید.")

# TODO: بخش مدیریت (ارسال کانفیگ، ویرایش پلن‌ها، اضافه کردن ادمین، اطلاع‌رسانی) را بعداً اضافه می‌کنم

# اجرای ربات
bot.infinity_polling()
