import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных окружения (токена бота)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Разница во времени для друзей
FRIENDS_TIME_DIFF = {
    '@frazyamp': +3,
    '@waldemar': -1,
}

async def start(update: Update, context: CallbackContext):
    """Приветственное сообщение"""
    await update.message.reply_text(
        'ЧЧ:ММ (например, 14:00),'
    )

async def convert_time(update: Update, context: CallbackContext):
    """..."""
    user_time_str = update.message.text.strip()
    try:
        user_time = datetime.strptime(user_time_str, '%H:%M')
        response = f'время мск:{user_time_str}:\n\n'
        for friend, diff_hours in FRIENDS_TIME_DIFF.items():
            friend_time = user_time + timedelta(hours=diff_hours)
            response += f'{friend}: {friend_time.strftime("%H:%M")}\n'
        await update.message.reply_text(response)
    except ValueError:
        await update.message.reply_text(
            'Пожалуйста, используйте формат ЧЧ:ММ (например, 14:00).'
        )

def main():
    """Запускает бота"""
    if not TOKEN:
        logging.error("Токен не найден! Укажите TELEGRAM_BOT_TOKEN в переменных окружения.")
        return

    app = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд и сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & (filters.ChatType.PRIVATE | filters.ChatType.GROUPS),
            convert_time
        )
    )

    logging.info("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
