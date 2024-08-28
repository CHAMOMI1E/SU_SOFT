from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.keyboards.main_menu import back_kb, main_kb
from bot.states.states import MainStates

from db.requests.link import update_link

edit_router = Router()


@edit_router.callback_query(F.data.startswith("edit_"))
async def edit_link(callback: types.CallbackQuery, state: FSMContext):
    link_id = int(callback.data.split("_")[1])
    await callback.message.edit_text("Введите новую ссылку", reply_markup=back_kb())
    await state.set_state(MainStates.edit_url)
    await state.update_data(edit_url=link_id)


@edit_router.message(MainStates.edit_url, F.text)
async def complete_edit_url(message: types.Message, state: FSMContext):
    link_id = await state.get_data()
    try:
        new_url = message.text
        await update_link(int(link_id["edit_url"]), new_url)
        await message.answer(
            f"Ссылка успешно изменена: {new_url}", reply_markup=main_kb()
        )
    except Exception as e:
        await message.answer(
            f"Не удалось изменить ссылку. Вы сейчас в главном меню",
            reply_markup=main_kb(),
        )
