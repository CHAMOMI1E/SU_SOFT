from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton
from aiogram_widgets.pagination import KeyboardPaginator

from bot.keyboards.main_menu import main_kb, list_of_url
from texts import start

main_router = Router()


@main_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(start, reply_markup=main_kb())


@main_router.callback_query(F.data == "func_add_url")
async def start_add_url(callback: types.callback_query):
    data = {f'{key}': f'{key}' for key in range(50)}
    buttons = [
        InlineKeyboardButton(text=f'{url}', callback_data=f'add_{id_url}')
        for id_url, url in data.items()
    ]
    paginator = KeyboardPaginator(
        data=buttons,
        per_page=20,
        per_row=2,
    )
    await callback.message.edit_text("func_add_url", reply_markup=paginator.as_markup())
