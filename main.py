import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = f"https://your-render-url.onrender.com/{TOKEN}"

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
    asyncio.run(telegram_app.process_update(update))  # Запуск в асинхронном режиме
    return "OK", 200

async def set_webhook():
    await bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    asyncio.run(set_webhook())  # Теперь set_webhook вызывается корректно
    app.run(host="0.0.0.0", port=10000)
