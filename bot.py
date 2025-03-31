import asyncio
import logging
import os
import sys
import signal
import gc

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from app.handlers import start, time, add_file, add_one, get_file, clear_data
from app.database import database
from app.utils import scheduler
from aiogram.enums import ParseMode

# Global flag to indicate shutdown
shutdown_flag = False

async def main():
    global shutdown_flag
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        exit("Error: No token provided")

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(time.router)
    dp.include_router(add_file.router)
    dp.include_router(get_file.router)
    dp.include_router(add_one.router)
    dp.include_router(clear_data.router)

    await database.create_db()
    await scheduler.start_scheduler(bot)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception("Exception during polling:")
    finally:
        shutdown_flag = True  # Set the shutdown flag

        logging.info("Shutting down...")

        # Try to cancel all pending tasks
        current_task = asyncio.current_task()
        tasks = asyncio.all_tasks()
        for task in tasks:
            if task is not current_task and not task.done():
                task.cancel()
                try:
                    await task  # Wait for cancellation
                except asyncio.CancelledError:
                    pass  # Expected during shutdown

        try:
            await scheduler.stop_scheduler()
            logging.info("Scheduler stopped.")
        except Exception as e:
            logging.exception("Error stopping scheduler:")

        try:
            await bot.session.close()
            logging.info("Bot session closed.")
        except Exception as e:
            logging.exception("Error closing bot session:")

        gc.collect()
        logging.info("Garbage collection complete.")

        logging.info("Shutdown complete.")
        await asyncio.sleep(0.1)  # Give it a tiny pause to flush logs


    logging.info("Main function finished.")


def signal_handler(sig, frame):
    global shutdown_flag
    print('Бот выключен.')
    shutdown_flag = True # Signal the bot to shut down


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    signal.signal(signal.SIGINT, signal_handler) # Register the signal handler

    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception(f"Произошла ошибка при запуске бота: {e}")

