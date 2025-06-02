import telebot
from telebot import types
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

ADMIN_IDS = [7935344235, 5993860770]

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'
CONFIGS_FILE = 'configs.json'
CARD_FILE = 'card_info.json'

# ========== مدیریت کاربران ==========
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

# ========== شماره کارت ==========
def load_card_info():
    if os.path.exists(CARD_FILE):
        with open(CARD_FILE, 'r') as f:
            return json.load(f)
    return {"number": "6277-6013-6877-6066", "name": "رضوانی"}

def save_card_info(info):
    with open(CARD_FILE, 'w') as f:
        json.dump(info, f)

# ========== دکمه‌ها ==========
def user_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("خرید اشتراک 💳")
    kb.row("آموزش اتصال 📘", "پشتیبانی 🛠")
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📤 ارسال کانفیگ", "📣 اطلاع‌رسانی")
    kb.row("➕ افزودن ادمین", "📝 ویرایش پلن‌ها")
    kb.row("💳 ویرایش کارت", "🔙 منوی کاربر")
    return kb

PLANS = {
    "1": {"title": "پلن 1", "desc": "تک کاربره یک ماهه", "price": "85"},
    "2": {"title": "پلن 2", "desc": "دو کاربره یک ماهه", "price": "115"},
    "3": {"title": "پلن 3", "desc": "سه کاربره یک ماهه", "price": "169"},
    "4": {"title": "پلن 4", "desc": "تک کاربره دو ماهه", "price": "140"},
    "5": {"title": "پلن 5", "desc": "دو کاربره دو ماهه", "price": "165"},
    "6": {"title": "پلن 6", "desc": "سه کاربره دو ماهه", "price": "185"},
    "7": {"title": "پلن 7", "desc": "تک کاربره سه ماهه", "price": "174"},
    "8": {"title": "پلن 8", "desc": "دو کاربره سه ماهه", "price": "234"},
    "9": {"title": "پلن 9", "desc": "سه کاربره سه ماهه", "price": "335"}
}

# ========== استارت ==========
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = get_or_create_user_id(message.from_user.id)
    if message.from_user.id in ADMIN_IDS:
        bot.send_message(message.chat.id, f"🎛 پنل مدیریت", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, f"🎉 خوش آمدید! آیدی شما: {user_id}", reply_markup=user_menu())

# ========== کاربر عادی ==========
@bot.message_handler(func=lambda m: m.text == "آموزش اتصال 📘")
def send_tutorial(message):
    bot.send_message(message.chat.id, "📘 آموزش اتصال: https://t.me/amuzesh_dragonvpn")

@bot.message_handler(func=lambda m: m.text == "پشتیبانی 🛠")
def support_info(message):
    bot.send_message(message.chat.id, "💬 برای پشتیبانی به آیدی زیر پیام دهید:\n@Psycho_remix1")

@bot.message_handler(func=lambda m: m.text == "خرید اشتراک 💳")
def buy_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, 10):
        markup.add(f"پلن {i}")
    bot.send_message(message.chat.id, "💳 یکی از پلن‌ها را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith("پلن "))
def show_invoice(message):
    user_id = get_or_create_user_id(message.from_user.id)
    plan_id = message.text.split()[-1]
    if plan_id in PLANS:
        plan = PLANS[plan_id]
        card = load_card_info()
        info = (
            f"🧾 فاکتور:\n"
            f"📦 پلن انتخابی: {plan['title']}\n"
            f"⌛ مدت: {plan['desc']}\n"
            f"💵 قیمت: {plan['price']} هزار تومان\n\n"
            f"لطفاً مبلغ را به شماره کارت زیر واریز کنید:\n"
            f"{card['number']} به نام {card['name']}\n\n"
            f"سپس فیش واریزی را ارسال نمایید."
        )
        bot.send_message(message.chat.id, info)

@bot.message_handler(content_types=['photo', 'document'])
def handle_receipt(message):
    user_id = get_or_create_user_id(message.from_user.id)
    bot.reply_to(message, "🕐 فیش شما دریافت شد، منتظر تایید ادمین باشید.")
    caption = f"🧾 کاربر با آیدی عددی {user_id} فیش ارسال کرد."
    for admin in ADMIN_IDS:
        if message.content_type == 'photo':
            bot.send_photo(admin, message.photo[-1].file_id, caption=caption)
        elif message.content_type == 'document':
            bot.send_document(admin, message.document.file_id, caption=caption)

# ========== مدیر ==========
pending_configs = {}

@bot.message_handler(func=lambda m: m.text == "📤 ارسال کانفیگ")
def ask_user_id(message):
    if message.from_user.id not in ADMIN_IDS: return
    bot.send_message(message.chat.id, "🆔 آیدی عددی کاربر:")
    bot.register_next_step_handler(message, ask_config_text)

def ask_config_text(message):
    pending_configs[message.chat.id] = message.text.strip()
    bot.send_message(message.chat.id, "📄 کانفیگ را وارد کنید:")
    bot.register_next_step_handler(message, send_config)

def send_config(message):
    user_code = pending_configs.get(message.chat.id)
    users = load_users()
    if user_code not in users:
        bot.send_message(message.chat.id, "❌ آیدی یافت نشد.")
        return
    target = users[user_code]
    bot.send_message(target, f"🔐 کانفیگ شما:\n{message.text}")
    bot.send_message(message.chat.id, "✅ ارسال شد.")

@bot.message_handler(func=lambda m: m.text == "📣 اطلاع‌رسانی")
def notify_all(message):
    if message.from_user.id not in ADMIN_IDS: return
    bot.send_message(message.chat.id, "✉️ پیام را بنویسید:")
    bot.register_next_step_handler(message, broadcast)

def broadcast(message):
    users = load_users()
    for tid in users.values():
        try:
            bot.send_message(tid, f"📢 اطلاعیه:\n{message.text}")
        except: pass
    bot.send_message(message.chat.id, "✅ ارسال شد.")

# بقیه گزینه‌های مدیریتی مانند افزودن ادمین، ویرایش کارت و پلن در نسخه بعدی اضافه می‌شود...

bot.infinity_polling()
