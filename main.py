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

# Configure more detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Time differences for friends
FRIENDS_TIME_DIFF = {
    '@frazyamp': +3,
    '@waldemarxl': -1,
}

async def start(update: Update, context: CallbackContext):
    """Welcome message"""
    logger.info(f"Start command received from user {update.effective_user.id}")
    await update.message.reply_text('ЧЧ:ММ (например, 14:00)')

async def convert_time(update: Update, context: CallbackContext):
    """Handles time conversion commands"""
    user_time_str = update.message.text.strip()
    
    if not user_time_str.startswith('/'):
        return
    
    logger.info(f"Time conversion requested: {user_time_str}")
    try:
        user_time = datetime.strptime(user_time_str[1:], '%H:%M')
        response = f'@FA1RY07A1L,@vgk: {user_time_str[1:]}:\n\n'
        for friend, diff_hours in FRIENDS_TIME_DIFF.items():
            friend_time = user_time + timedelta(hours=diff_hours)
            response += f'{friend}: {friend_time.strftime("%H:%M")}\n'
        await update.message.reply_text(response)
        logger.info("Time conversion successful")
    except ValueError as e:
        logger.error(f"Time conversion failed: {str(e)}")
        await update.message.reply_text(
            'Пожалуйста, используйте формат ЧЧ:ММ (например, 14:00).'
        )

async def run_bot():
    """Runs the bot"""
    try:
        if not TOKEN:
            logger.error("Telegram token not found in environment variables!")
            return
        
        logger.info("Initializing Telegram bot...")
        app = Application.builder().token(TOKEN).build()
        
        logger.info("Adding command handlers...")
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.PRIVATE | filters.ChatType.GROUPS), convert_time))
        
        logger.info("Starting bot polling...")
        await app.run_polling()
    except Exception as e:
        logger.error(f"Error in run_bot: {str(e)}", exc_info=True)

# Flask server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    """Runs the Flask server"""
    try:
        port = int(os.environ.get("PORT", 10000))
        logger.info(f"Starting Flask server on port {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error starting Flask server: {str(e)}", exc_info=True)

if __name__ == '__main__':
    try:
        logger.info("Starting application...")
        
        # Create a new event loop for the bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the bot in the background
        logger.info("Setting up bot task...")
        loop.create_task(run_bot())
        
        # Run Flask in the main thread
        logger.info("Starting Flask server...")
        run_flask()
    except Exception as e:
        logger.error(f"Application startup error: {str(e)}", exc_info=True)
