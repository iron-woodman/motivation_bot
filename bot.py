# bot.py
import asyncio
import logging
import os
from datetime import datetime
import aioschedule

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.database.database import create_db_connection, create_tables, get_scheduled_time
from app.handlers.user import register_handlers

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    exit("No token provided")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Scheduler
async def send_scheduled_quote(bot: Bot, user_id: int):
    from app.handlers.user import send_quote  # Import here to avoid circular import
    await send_quote(bot, user_id)


async def scheduler(bot: Bot):
    while True:
        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]  # Fetch all user_ids
        conn.close()

        for user_id in user_ids:
            scheduled_time_str = get_scheduled_time(user_id)
            if scheduled_time_str:
                try:
                    scheduled_time = datetime.strptime(scheduled_time_str, '%H:%M').time()
                    aioschedule.every().day.at(scheduled_time_str).do(send_scheduled_quote, bot, user_id)
                except ValueError as e:
                     logging.error(f"Invalid time format for user {user_id}: {e}")

        await aioschedule.run_pending()
        await asyncio.sleep(60)  # Check every minute


# Main function
async def main():
    create_tables()  # Create tables on startup
    register_handlers(dp, bot)  # Register handlers

    # Run scheduler in background
    asyncio.create_task(scheduler(bot))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
