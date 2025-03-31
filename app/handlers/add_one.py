from aiogram.fsm.state import State, StatesGroup
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from app.keyboards.user_keyboards import main_keyboard
from app.utils import quotes


router = Router()

# FSM States
class AddQuoteState(StatesGroup):
    waiting_for_quote = State()


@router.message(AddQuoteState.waiting_for_quote, F.text)
async def process_quote(message: types.Message, state: FSMContext):
    quote = message.text.strip()
    if quote:
        await quotes.add_quote(message.from_user.id, quote)
        await message.reply("Ваш новый принцип добавлен!", reply_markup=main_keyboard)
        # else:
        #     await message.reply("Произошла ошибка при добавлении нового принципа.", reply_markup=main_keyboard)
        await state.clear()

    else:
        await message.answer("Пожалуйста, укажите принцип для добавления.")


@router.callback_query(F.data == "add_one")
async def add_quote_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите принцип для добавления:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddQuoteState.waiting_for_quote)
    await callback.answer()  #  убрать "кнопка нажата"