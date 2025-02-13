import os
import logging
import threading
from flask import Flask
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Разница во времени для друзей
FRIENDS_TIME_DIFF = {
    '@frazyamp': +3,
    '@waldemarxl': -1,
}

async def start(update: Update, context: CallbackContext):
    """Приветственное сообщение"""
    await update.message.reply_text('ЧЧ:ММ (например, 14:00),')

async def convert_time(update: Update, context: CallbackContext):
    """Обрабатывает команды для конвертации времени"""
    user_time_str = update.message.text.strip()
    
    if not user_time_str.startswith('/'):
        return  

    try:
        user_time = datetime.strptime(user_time_str[1:], '%H:%M')
        response = f'@FA1RY07A1L,@vgk: {user_time_str[1:]}:\n\n'
        for friend, diff_hours in FRIENDS_TIME_DIFF.items():
            friend_time = user_time + timedelta(hours=diff_hours)
            response += f'{friend}: {friend_time.strftime("%H:%M")}\n'
        await update.message.reply_text(response)
    except ValueError:
        await update.message.reply_text(
            'Пожалуйста, используйте формат ЧЧ:ММ (например, 14:00).'
        )

def run_bot():
    """Запускает бота в фоновом потоке"""
    if not TOKEN:
        logging.error("Токен не найден! Укажите TELEGRAM_BOT_TOKEN в переменных окружения.")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.PRIVATE | filters.ChatType.GROUPS), convert_time))

    logging.info("Бот запущен...")
    app.run_polling()

# Фейковый Flask-сервер для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 10000))  # Render требует открытый порт
    app.run(host="0.0.0.0", port=port)
