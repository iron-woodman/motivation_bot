from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/time"),
            KeyboardButton(text="/add"),
        ],
        [
            KeyboardButton(text="/add_file"),
            KeyboardButton(text="/get_file")
        ]
    ],
    resize_keyboard=True
)
