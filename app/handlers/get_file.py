import os
from aiogram import F, Bot, Router
from aiogram.types import FSInputFile, CallbackQuery
from app.keyboards.user_keyboards import main_keyboard
from app.database import database
import aiosqlite

router = Router()

@router.callback_query(F.data == "get_file")
async def get_file_callback(callback: CallbackQuery, bot: Bot):
    user_quotes = await database.get_user_quotes(callback.from_user.id)
    if not user_quotes:
        await callback.message.answer("Нет принципов для выгрузки.", reply_markup=main_keyboard)
        await callback.answer()
        return
    try:
        # Create the data directory if it doesn't exist
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Create a temporary file with the user's quotes
        file_path = os.path.join(data_dir, f"{callback.from_user.id}_quotes.txt")

        async with aiosqlite.connect(database.DATABASE_NAME) as db:
            async with db.cursor() as cursor:
                with open(file_path, "w", encoding="utf-8") as f:
                    for quote in user_quotes:
                        f.write(quote + "\n")
            await db.commit()

        file = FSInputFile(file_path)
        await bot.send_document(callback.message.chat.id, document=file, reply_markup=main_keyboard)
        os.remove(file_path)
    except Exception as e:
        # logging.exception("Error creating/sending file:")
        await callback.message.answer(f"Произошла ошибка при формировании файла: {e}", reply_markup=main_keyboard)
    await callback.answer()
