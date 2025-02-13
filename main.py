import os
import logging
import asyncio
from aiohttp import web
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
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

async def web_handler(request):
    """Simple web handler for health checks"""
    return web.Response(text="Бот работает!")

async def main():
    """Main function that runs both bot and web server"""
    try:
        # Initialize bot
        if not TOKEN:
            logger.error("Telegram token not found in environment variables!")
            return

        logger.info("Initializing Telegram bot...")
        bot = Application.builder().token(TOKEN).build()
        
        # Add handlers
        logger.info("Adding command handlers...")
        bot.add_handler(CommandHandler("start", start))
        bot.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.PRIVATE | filters.ChatType.GROUPS), convert_time))

        # Initialize web app
        app = web.Application()
        app.router.add_get('/', web_handler)
        
        # Start both bot and web server
        port = int(os.environ.get("PORT", 10000))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        
        # Start everything
        await site.start()
        logger.info(f"Web server started on port {port}")
        
        await bot.initialize()
        logger.info("Bot initialized successfully")
        
        await bot.start()
        logger.info("Bot started successfully")
        
        # Run forever
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
    finally:
        # Cleanup
        if 'bot' in locals():
            await bot.shutdown()
        if 'runner' in locals():
            await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
