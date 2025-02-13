import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = Bot(token=TOKEN)

telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("ЧЧ:ММ (например, 14:00)")

async def convert_time(update: Update, context):
    await update.message.reply_text("Обработка времени...")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT, convert_time))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    telegram_app.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    # Устанавливаем вебхук
    webhook_url = f"https://your-render-url.onrender.com/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=10000)
