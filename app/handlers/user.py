
import logging
import os
import random
from datetime import datetime

from aiogram import types, F, Dispatcher, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from app.keyboards.user_keyboards import main_keyboard
from app.database.database import get_quotes, add_quote, add_quote_from_file, set_scheduled_time

# FSM States
class AddQuoteState(StatesGroup):
    waiting_for_quote = State()

class SetTimeState(StatesGroup):
    waiting_for_time = State()

# Command handlers
async def start_command(message: types.Message):
    await message.reply("Привет! Я бот для мотивации. Используй команды, чтобы настроить меня.\n"
                       "Доступные команды:\n"
                       "/time - Установить время для получения мотивационных цитат.\n"
                       "/add - Добавить новую цитату.\n"
                       "/add_file - Загрузить файл с цитатами.\n"
                       "/get_file - Получить текущий файл цитат.\n"
                        , reply_markup=main_keyboard)


async def help_command(message: types.Message):
    await message.reply("Список доступных команд:\n"
                       "/start - Запускает бота\n"
                       "/help - Показывает это сообщение\n"
                       "/time - Установить время для получения мотивационных цитат\n"
                       "/add - Добавить новую цитату\n"
                       "/add_file - Загрузить файл с цитатами\n"
                       "/get_file - Получить текущий файл цитат"
                       , reply_markup=main_keyboard)

async def set_time_command(message: types.Message, state: FSMContext):
    await message.reply("Введите время для получения цитат в формате ЧЧ:ММ (например, 08:00):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SetTimeState.waiting_for_time)

async def process_time(message: types.Message, state: FSMContext):
    time_str = message.text
    try:
        datetime.strptime(time_str, '%H:%M')  #Validate time format
        user_id = message.from_user.id
        if set_scheduled_time(user_id, time_str):
            await message.reply(f"Время получения цитат установлено на {time_str}", reply_markup=main_keyboard)
        else:
             await message.reply("Произошла ошибка при установке времени. Попробуйте еще раз.", reply_markup=main_keyboard)
        await state.clear()
    except ValueError:
        await message.reply("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:00).", reply_markup=ReplyKeyboardRemove())


async def add_quote_command(message: types.Message, state: FSMContext):
    await message.reply("Введите цитату для добавления:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddQuoteState.waiting_for_quote)


async def process_quote(message: types.Message, state: FSMContext):
    quote = message.text
    if add_quote(quote):
        await message.reply("Цитата добавлена!", reply_markup=main_keyboard)
    else:
        await message.reply("Произошла ошибка при добавлении цитаты.", reply_markup=main_keyboard)
    await state.clear()


async def add_file_command(message: types.Message):
    await message.reply("Пожалуйста, загрузите текстовый файл с цитатами (каждая цитата на новой строке).", reply_markup=ReplyKeyboardRemove())


async def process_file(message: types.Message, bot: Bot):
    if message.document.file_name.endswith('.txt'):
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "temp_quotes.txt")

        if add_quote_from_file("temp_quotes.txt"):
            os.remove("temp_quotes.txt")
            await message.reply("Цитаты из файла добавлены!", reply_markup=main_keyboard)
        else:
            os.remove("temp_quotes.txt")
            await message.reply("Произошла ошибка при добавлении цитат из файла.", reply_markup=main_keyboard)
    else:
        await message.reply("Пожалуйста, загрузите текстовый файл (.txt).", reply_markup=main_keyboard)


async def get_file_command(message: types.Message, bot: Bot):
     quotes = get_quotes()
     if not quotes:
          await message.reply("Нет цитат для выгрузки.", reply_markup=main_keyboard)
          return

     try:
          with open("quotes_output.txt", "w", encoding="utf-8") as f:
               for quote in quotes:
                    f.write(quote + "\n")

          doc = FSInputFile("quotes_output.txt")
          await bot.send_document(message.chat.id, document=doc, reply_markup=main_keyboard)
          os.remove("quotes_output.txt")
     except Exception as e:
          logging.exception("Error creating/sending file:")
          await message.reply(f"Произошла ошибка при формировании файла: {e}", reply_markup=main_keyboard)


# Error handling
async def echo(message: types.Message):
    await message.answer("Не понимаю эту команду. Используйте /help для списка команд.")

async def send_quote(bot:Bot, user_id: int):
    quotes = get_quotes()
    if quotes:
        quote = random.choice(quotes)
        await bot.send_message(user_id, quote)

def register_handlers(dp: Dispatcher, bot: Bot):
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
    dp.message.register(set_time_command, Command("time"))
    dp.message.register(process_time, SetTimeState.waiting_for_time, F.text)
    dp.message.register(add_quote_command, Command("add"))
    dp.message.register(process_quote, AddQuoteState.waiting_for_quote, F.text)
    dp.message.register(add_file_command, Command("add_file"))
    dp.message.register(process_file, F.document, lambda message: process_file(message, bot)) # Use lambda to pass bot
    dp.message.register(get_file_command, Command("get_file"))
    dp.message.register(echo)
