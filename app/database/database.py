import aiosqlite
import json
import logging

DATABASE_NAME = "bot.db"

# Настройка логирования
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


async def create_db():
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        start_time TEXT,
                        end_time TEXT,
                        quotes TEXT DEFAULT '[]'
                    )
                """)
            await conn.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при создании базы данных: {e}")


async def set_time_interval(user_id, start_time, end_time):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    UPDATE users
                    SET start_time = ?, end_time = ?
                    WHERE user_id = ?
                """, (start_time, end_time, user_id))

                if cursor.rowcount == 0:
                    await cursor.execute("""
                        INSERT INTO users (user_id, start_time, end_time, quotes)
                        VALUES (?, ?, ?, '[]')
                    """, (user_id, start_time, end_time))

            await conn.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при установке временного интервала для user_id {user_id}: {e}")


async def get_time_interval(user_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT start_time, end_time FROM users WHERE user_id = ?", (user_id,))
                result = await cursor.fetchone()
                return result
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при получении временного интервала для user_id {user_id}: {e}")
        return None


async def get_user_quotes(user_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT quotes FROM users WHERE user_id = ?", (user_id,))
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])  # Преобразуем JSON в список
                return []
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при получении цитат для user_id {user_id}: {e}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка при декодировании JSON для user_id {user_id}: {e}")
        return []


async def set_user_quotes(user_id, quotes):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            async with conn.cursor() as cursor:
                quotes_json = json.dumps(quotes)  # Преобразуем список в JSON
                await cursor.execute("UPDATE users SET quotes = ? WHERE user_id = ?", (quotes_json, user_id))
            await conn.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при установке принципов для user_id {user_id}: {e}")


async def clear_user_quotes(user_id):
    """Удаляет все цитаты для указанного user_id, заменяя их на пустой список."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("UPDATE users SET quotes = '[]' WHERE user_id = ?", (user_id,))
            await conn.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при очистке цитат для user_id {user_id}: {e}")


async def main():
    # Пример использования
    await create_db()
    user_id = 12345
    await set_time_interval(user_id, "08:00", "20:00")
    time_interval = await get_time_interval(user_id)
    print(f"Временной интервал для user_id {user_id}: {time_interval}")

    quotes = ["Будьте лучшей версией себя!", "Не сдавайтесь!"]
    await set_user_quotes(user_id, quotes)
    user_quotes = await get_user_quotes(user_id)
    print(f"Цитаты для user_id {user_id}: {user_quotes}")

    await clear_user_quotes(user_id)
    updated_quotes = await get_user_quotes(user_id)
    print(f"Цитаты после очистки для user_id {user_id}: {updated_quotes}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
