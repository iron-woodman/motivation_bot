from aiogram.filters import CommandStart
from aiogram import types, F, Bot, Router
from pathlib import Path
from aiogram.types import ReplyKeyboardRemove, FSInputFile, CallbackQuery
from app.keyboards.user_keyboards import main_keyboard, user_inline_menu


router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message, bot: Bot):
    """
    Этот обработчик вызывается при команде /start. Отправляет приветственное сообщение и фото.
    """
    image_path = Path("./img/start.jpg")

    if not image_path.exists():
        await message.reply("Ошибка: Файл start.jpg не найден в папке img!")
        return

    try:
        # Используем FSInputFile для указания, что это локальный файл
        photo = FSInputFile(path=str(image_path))

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,  # Передаем FSInputFile
            caption=(
                f"""Бот  "МОИ ПРИНЦИПЫ " — ежедневно, в заданное время, напоминает вам о ваших жизненных ценностях, позволяет делиться ими с близкими и оставить свои принципы как наследие детям!
Функции бота:
1. Напоминания о принципах: Бот будет ежедневно , напоминать вам о ваших жизненных принципах, чтобы вы могли оставаться на правильном пути и не забывать о том, что для вас действительно важно.
2. Создание и редактирование принципов: Вы можете легко добавлять, редактировать или удалять свои принципы.
3. Делитесь с друзьями и передавайте ваши принципы детям: Хотите, чтобы ваши друзья, дети, воспитанники тоже знали о ваших принципах? Бот позволяет делиться ими через сообщения, создавая уникальные карточки с вашими ценностями."""
            ),
            reply_markup=main_keyboard
        )
    except Exception as e:
        await message.reply(f"Ошибка при отправке фото: {e}")


@router.message(F.text.regexp(r".*Меню.*"))
async def menu_button_handler(message: types.Message):
    """
    Этот обработчик реагирует на нажатие кнопки, текст которой содержит "Меню", независимо от того, что находится до или после.
    Использует регулярное выражение.
    """
    await message.answer(
        "Вы нажали кнопку, содержащую 'Меню' (с использованием регулярного выражения).",
        reply_markup=user_inline_menu
    )


@router.message(F.text.regexp(r".*Помощь.*"))
async def help_handler(message: types.Message) -> None:
    """
    Этот обработчик вызывается при нажатии кнопки "Помощь".
    """
    await message.answer(
        "Доступные команды:\n\n"
        "/start - Начать работу с ботом\n"
        "Меню - Открыть меню с действиями\n"
        "Помощь - Получить справку\n"
        "\n"
        "**Описание пунктов меню:**\n"
        "⏳ Временной интервал - Устанавливает временной интервал для работы бота.\n\n"
        "➕ Добавить принцип - Добавляет один принцип работы в базу данных.\n\n"
        "📤 Загрузить из файла - Загружает принципы работы из файла в базу данных.\n\n"
        "💾 Получить все принципы - Отправляет файл со всеми принципами, хранящимися в базе данных.\n\n"
        "🗑 Удалить все принципы - Удаляет все принципы из базы данных (будьте осторожны!) При этом принципы отправляет вам в виде текстового файла.\n\n"
    )