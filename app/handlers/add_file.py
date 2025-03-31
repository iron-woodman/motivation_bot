import os
from aiogram.fsm.state import State, StatesGroup
from aiogram import types, F, Dispatcher, Bot, Router
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, FSInputFile, CallbackQuery
from app.keyboards.user_keyboards import main_keyboard
from app.utils import quotes


router = Router()

class AddQuoteFileState(StatesGroup):
    waiting_for_txtFile = State()


@router.message(AddQuoteFileState.waiting_for_txtFile, F.document)
async def process_file(message: types.Message, bot: Bot, state: FSMContext):
    if message.document.file_name.endswith('.txt'):
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"data/{message.from_user.id}_quotes.txt"
        await bot.download_file(file_path, file_name)

        # Обновляем список цитат для пользователя
        if await quotes.load_quotes_from_file(message.from_user.id, file_name):
            await message.answer("Файл с цитатами успешно загружен и обновлен.", reply_markup=main_keyboard)
        else:
            await message.answer("Не удалось загрузить файл с цитатами.")

        # Удаляем временный файл
        os.remove(file_name)
    else:
        await message.answer("Пожалуйста, отправьте текстовый файл (*.txt) с цитатами.")

    await state.clear()



@router.callback_query(F.data == "add_file")
async def add_file_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Пожалуйста, загрузите текстовый файл (*.txt) с принципами (каждый принцип на новой строке).",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddQuoteFileState.waiting_for_txtFile)
    await callback.answer()  #  убрать "кнопка нажата"