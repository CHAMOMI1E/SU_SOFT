from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.keyboards.main_menu import main_kb, del_url_kb
from bot.states.states import MainStates
from db.requests.link import delete_link, get_link_by_id

delete_router = Router()


@delete_router.callback_query(F.data.startswith("del_"))
async def confirm_delete_link(callback: types.CallbackQuery):
    id_link = callback.data.split("_")[1]
    url = await get_link_by_id(int(id_link))
    await callback.message.edit_text(f"Готовы удалить ссылку {url.url}?", reply_markup=del_url_kb(url_id=id_link))


@delete_router.callback_query(F.data.startswith("del-url_"))
async def process_del_link(callback: types.CallbackQuery):
    id_link = callback.data.split("_")[1]
    try:
        await delete_link(int(id_link))
        await callback.message.edit_text(
            "Ссылка успешно удалена.", reply_markup=main_kb()
        )
    except Exception as e:
        await callback.message.answer(
            f"Ошибка при удалении ссылки: {str(e)}", reply_markup=main_kb()
        )