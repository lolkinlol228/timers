import os
import logging
import asyncio
from flask import Flask
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Time differences for friends
FRIENDS_TIME_DIFF = {
    '@frazyamp': +3,
    '@waldemarxl': -1,
}

async def start(update: Update, context: CallbackContext):
    """Welcome message"""
    await update.message.reply_text('ЧЧ:ММ (например, 14:00)')

async def convert_time(update: Update, context: CallbackContext):
    """Handles time conversion commands"""
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

async def run_bot():
    """Runs the bot"""
    if not TOKEN:
        logging.error("Токен не найден! Укажите TELEGRAM_BOT_TOKEN в переменных окружения.")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.PRIVATE | filters.ChatType.GROUPS), convert_time))
    
    logging.info("Бот запущен...")
    await app.run_polling()

# Flask server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    """Runs the Flask server"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    # Create a new event loop for the bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the bot in the background
    loop.create_task(run_bot())
    
    # Run Flask in the main thread
    run_flask()
