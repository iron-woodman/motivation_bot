import os
from aiogram import F, Bot, Router
from aiogram.types import FSInputFile, CallbackQuery
from app.keyboards.user_keyboards import main_keyboard
from app.database import database

router = Router()


@router.callback_query(F.data == "clear_db")
async def get_file_callback(callback: CallbackQuery, bot: Bot):
    user_quotes = await database.get_user_quotes(callback.from_user.id)
    if not user_quotes:
        await callback.message.answer("Нет принципов для выгрузки.", reply_markup=main_keyboard)
        await callback.answer()  # убрать "кнопка нажата"
        return
    try:
        # Создаем временный файл с цитатами пользователя
        with open(f"data/{callback.message.from_user.id}_quotes.txt", "w", encoding="utf-8") as f:
            for quote in user_quotes:
                f.write(quote + "\n")

        file = FSInputFile(f"data/{callback.message.from_user.id}_quotes.txt")
        await bot.send_document(callback.message.chat.id, document=file, reply_markup=main_keyboard)
        os.remove(f"data/{callback.message.from_user.id}_quotes.txt")
        await database.clear_user_quotes(callback.from_user.id)
        await callback.message.answer(f"Все принципы удалены из базы данных.", reply_markup=main_keyboard)
    except Exception as e:
        # logging.exception("Error creating/sending file:")
        await callback.message.answer(f"Произошла ошибка при формировании файла: {e}", reply_markup=main_keyboard)
    await callback.answer()  #  убрать "кнопка нажата"

