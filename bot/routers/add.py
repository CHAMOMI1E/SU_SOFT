from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.states.states import MainStates
from bot.keyboards.main_menu import main_kb
from db.requests.link import add_url

add_router = Router()


@add_router.message(F.text, MainStates.add_url)
async def complete_add_url(message: types.Message, state: FSMContext):
    data = message.text
    await add_url(data)
    await message.answer(
        f"Ссылка {data} добавлена в базу. Вы сейчас в главном меню",
        reply_markup=main_kb(),
    )
