from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.keyboards.main_menu import main_kb, list_of_urls, page_of_urls, back_kb
from bot.states.states import MainStates
from db.requests.link import get_all_links
from texts import start

main_router = Router()


@main_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    # await message.answer(f"{message.from_user}")
    await message.answer(start, reply_markup=main_kb())


@main_router.callback_query(F.data == "func_add_url")
async def start_add_url(callback: types.callback_query, state: FSMContext):
    await callback.message.edit_text(
        "Начинаем добавление ссылки. Введите новую ссылку", reply_markup=back_kb()
    )
    await state.set_state(MainStates.add_url)


@main_router.callback_query(F.data == "func_edit_url")
async def func_edit_url(callback: types.callback_query):
    data = await get_all_links()
    kb = list_of_urls(urls=data, router=main_router, action="edit")

    await callback.message.edit_text("Выберите ссылку для изменения", reply_markup=kb)


@main_router.callback_query(F.data == "func_del_url")
async def func_del_url(callback: types.callback_query):
    data = await get_all_links()
    kb = list_of_urls(urls=data, router=main_router, action="del")
    await callback.message.edit_text("func_add_url", reply_markup=kb)


@main_router.callback_query(F.data == "func_del_url")
async def func_del_url(callback: types.callback_query):
    data = await get_all_links()
    kb = (
        list_of_urls(urls=data, router=main_router, action="del")
        if len(data) > 20
        else list_of_urls(urls=data, router=main_router, action="del")
    )
    await callback.message.edit_text("Выберите функцию для удаления ссылки", reply_markup=kb)


@main_router.callback_query(F.data == "home")
async def start_home(callback: types.callback_query, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Вы сейчас в главном меню", reply_markup=main_kb())
