from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,  InlineKeyboardMarkup, InlineKeyboardButton

# --- Клавиатуры ---
# main_keyboard = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="Меню"),
#             KeyboardButton(text="Помощь"),
#         ]
#     ],
#     resize_keyboard=True,
# )


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=" ⚙️ Меню"),
            KeyboardButton(text=" ❓ Помощь"),
        ]
    ],
    resize_keyboard=True,
)



user_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏳ Временной интервал", callback_data="time_interval")],
    [InlineKeyboardButton(text="➕ Добавить принцип", callback_data="add_one")],
    [InlineKeyboardButton(text="📤 Загрузить из файла", callback_data="add_file")],
    [InlineKeyboardButton(text="💾 Получить все принципы", callback_data="get_file")],
    [InlineKeyboardButton(text="🗑️ Удалить все принципы", callback_data="clear_db")],
])


