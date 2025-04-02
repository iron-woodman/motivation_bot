import random
from app.database import database
import logging

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_random_quote(user_id):
    quotes = await database.get_user_quotes(user_id)
    if quotes:
        return random.choice(quotes)
    else:
        return "Список принципов пуст. Добавьте свои принципы в базу данных."

async def add_quote(user_id, quote):
    quotes = await database.get_user_quotes(user_id)
    quotes.append(quote)
    await database.set_user_quotes(user_id, quotes)


async def load_quotes_from_file(user_id, filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            new_quotes = [line.strip() for line in f.readlines() if line.strip()]

        # Отфильтруем пустые строки, если вдруг они остались после strip()
        new_quotes = [quote for quote in new_quotes if quote]  # Проверяем, что строка не пустая

        # Получаем текущие цитаты пользователя из базы данных
        existing_quotes = await database.get_user_quotes(user_id)

        # Объединяем новые цитаты с существующими (без дубликатов)
        all_quotes = list(set(existing_quotes + new_quotes))

        # Сохраняем обновленный список цитат в базу данных
        await database.set_user_quotes(user_id, all_quotes)
        return True  # Успешная загрузка и сохранение
    except FileNotFoundError:
        return False  # Файл не найден
    except Exception as e:
        logging.error(f"Ошибка при загрузке принципов из файла {filename} для user_id {user_id}: {e}")
        return False  # Ошибка при обработке файла
