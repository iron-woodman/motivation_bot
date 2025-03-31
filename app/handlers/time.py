from aiogram.fsm.state import State, StatesGroup
from aiogram import types, F, Router, Bot
from app.keyboards.user_keyboards import main_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from app.utils.scheduler import reschedule_daily_quote


router = Router()


class SetTimeState(StatesGroup):
    waiting_for_start_time = State()
    waiting_for_end_time = State()

# --- Inline Keyboard Handlers ---
@router.callback_query(F.data == "time_interval")
async def time_interval_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.reply(
        "Введите удобный для вас временной интервал (Московское время). Введите время начала получения принципов (пример: 07:00):",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(SetTimeState.waiting_for_start_time)
    await callback.answer()  #  убрать "кнопка нажата"


@router.message(SetTimeState.waiting_for_start_time, F.text)
async def get_start_time(message: types.Message, state: FSMContext):
    await state.update_data(start_time=message.text)
    await message.answer("Укажите время окончания (например, 18:00):")
    await state.set_state(SetTimeState.waiting_for_end_time)

@router.message(SetTimeState.waiting_for_end_time)
async def get_end_time(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(end_time=message.text)
    data = await state.get_data()
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    # Сохраняем время в базу данных для пользователя
    from app.database import database
    await database.set_time_interval(message.from_user.id, start_time, end_time)
    await message.answer(f"Временной интервал установлен: с {start_time} до {end_time}", reply_markup=main_keyboard)
    await state.clear()
    await reschedule_daily_quote(bot, message.from_user.id, start_time, end_time)
