from keep_alive import keep_alive
import telebot
import os

# دریافت توکن از متغیر محیطی
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("لطفاً توکن ربات را در محیط (environment) قرار دهید.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "سلام! به ربات خوش آمدید.")

keep_alive()
bot.infinity_polling()
