from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils import quotes
from app.database import database
import asyncio
import random
import logging
import datetime
import aiosqlite  # Import aiosqlite

# Настройка логирования

logging.basicConfig(filename='bot.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

scheduler = AsyncIOScheduler()
tasks = []  # Список для хранения всех запущенных задач

async def send_daily_quote(bot, user_id):
    time_interval = await database.get_time_interval(user_id)
    if time_interval:
        start_time, end_time = time_interval
        quote = await quotes.get_random_quote(user_id)  # Передаем user_id
        try:
            await bot.send_message(user_id, quote)
            logging.info(f"Отправлена цитата пользователю {user_id}: {quote}")

            # Запланируем перепланировку на следующий день
            await reschedule_daily_quote(bot, user_id, start_time, end_time)

        except Exception as e:
            logging.exception(f"Ошибка при отправке сообщения пользователю {user_id}:")  # Логируем трассировку ошибки
    else:
        logging.warning(f"Не установлен временной интервал для пользователя {user_id}")


async def reschedule_daily_quote(bot, user_id, start_time, end_time):
    await _schedule_quote(bot, user_id, start_time, end_time)


async def _schedule_quote(bot, user_id, start_time, end_time):
    """Вспомогательная функция для планирования отправки цитаты."""
    # Вычисляем случайное время в заданном интервале
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))

    random_hour = random.randint(start_hour, end_hour)
    random_minute = random.randint(start_minute, end_minute)

    # Получаем текущую дату и время
    now = datetime.datetime.now()

    # Создаем объект datetime для запланированного времени
    scheduled_time = datetime.datetime(now.year, now.month, now.day, random_hour, random_minute)

    # Если запланированное время уже прошло сегодня, переносим на следующий день
    if scheduled_time <= now:
        scheduled_time += datetime.timedelta(days=1)

    # Удаляем старую задачу (если она существует)
    job_id = f'send_quote_{user_id}'
    try:
        if scheduler.get_job(job_id): # Проверяем существует ли задача перед удалением
             scheduler.remove_job(job_id)
             logging.info(f"Удалена старая задача для пользователя {user_id}")
    except Exception as e:
        logging.warning(f"Не найдена задача для удаления для пользователя {user_id}: {e}")

        # Планируем отправку цитаты на определенную дату и время
    try:
        scheduler.add_job(send_daily_quote, 'date', run_date=scheduled_time,
                          args=[bot, user_id], id=job_id)
        logging.info(
            f"Запланирована отправка цитаты пользователю {user_id} на {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        logging.exception(f"Ошибка при планировании задачи для пользователя {user_id}:")  # Логируем трассировку ошибки

async def schedule_jobs(bot):
    try:
        async with aiosqlite.connect(database.DATABASE_NAME) as db:
            async with db.execute("SELECT user_id, start_time, end_time FROM users") as cursor:
                users = await cursor.fetchall()

                for user_id, start_time, end_time in users:
                    # Проверяем на корректность временного интервала
                    try:
                        await _schedule_quote(bot, user_id, start_time, end_time)
                    except Exception as e:
                        logging.exception(
                            f"Ошибка при обработке пользователя {user_id}:")  # Логируем трассировку ошибки

    except aiosqlite.Error as e:
        logging.exception(f"Ошибка при подключении к базе данных:")  # Логируем трассировку ошибки

async def reschedule_user(bot, user_id):
    """Перепланирует задачу для конкретного пользователя."""
    time_interval = await database.get_time_interval(user_id)  # await добавлено
    if time_interval:
        start_time, end_time = time_interval
        await _schedule_quote(bot, user_id, start_time, end_time)
        logging.info(f"Перепланирована задача для пользователя {user_id}")
    else:
        logging.warning(f"Не установлен временной интервал для пользователя {user_id}, перепланировка невозможна.")

async def start_scheduler(bot):
    scheduler.start()
    task = asyncio.create_task(schedule_jobs(bot))  # Запускаем schedule_jobs как задачу
    tasks.append(task)  # Добавляем задачу в список
    task.add_done_callback(lambda t: tasks.remove(t))  # Автоматически удалять из списка
    logging.info("Планировщик запущен")

async def stop_scheduler():
    logging.info("Stopping scheduler...")

    # Cancel all tasks before shutting down the scheduler
    for task in tasks:
        task.cancel()

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)  # Wait for all tasks to cancel

    scheduler.shutdown(wait=True)  # Shutdown in main thread
    logging.info("Scheduler stopped.")
